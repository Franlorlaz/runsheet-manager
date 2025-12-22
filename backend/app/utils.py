import logging
from calendar import month_abbr
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import emails  # type: ignore
import jwt
from jinja2 import Template
from jwt.exceptions import InvalidTokenError

from app.core import security
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EmailData:
    html_content: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (
        Path(__file__).parent / "email-templates" / "build" / template_name
    ).read_text()
    html_content = Template(template_str).render(context)
    return html_content


def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    assert settings.emails_enabled, "no provided configuration for email variables"
    message = emails.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    elif settings.SMTP_SSL:
        smtp_options["ssl"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, smtp=smtp_options)
    logger.info(f"send email result: {response}")


def generate_test_email(email_to: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    html_content = render_email_template(
        template_name="test_email.html",
        context={"project_name": settings.PROJECT_NAME, "email": email_to},
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_reset_password_email(email_to: str, email: str, token: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    html_content = render_email_template(
        template_name="reset_password.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_new_account_email(
    email_to: str, username: str, password: str
) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    html_content = render_email_template(
        template_name="new_account.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": settings.FRONTEND_HOST,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.now(timezone.utc)
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> str | None:
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        return str(decoded_token["sub"])
    except InvalidTokenError:
        return None


def generate_citic_id_for_runsheet(citic_ids: Sequence[str], prefix: str | None = None, prefix_only: bool = False) -> str:
    """Generate a unique citic_id for a runsheet.

    Format of citic_id: YYmmm-000
        YY - last two digits of the year
        mmm - three-letter month abbreviation in lowercase
        000 - counter starting from 001 for each month

    Example:
        25dic-001, 25dic-002, 25feb-001
    """
    if prefix:
        date_prefix = prefix
    else:
        today = datetime.today()
        year = today.strftime("%y")
        month = month_abbr[today.month].lower()
        date_prefix = f"{year}{month}-"

    if not prefix_only:
        max_counter = 0
        for citic_id in citic_ids:
            if not citic_id.startswith(date_prefix):
                continue
            try:
                counter_part = citic_id.split("-")[1]
                counter = int(counter_part)
            except (IndexError, ValueError):
                continue
            max_counter = max(max_counter, counter)
        next_counter = max_counter + 1
        return f"{date_prefix}{next_counter:003d}"
    else:
        return date_prefix


def generate_citic_id_for_sample(citic_ids: Sequence[str], prefix: str | None = None, prefix_only: bool = False) -> str:  # TODO: check function
    """Generate a unique citic_id for a sample.

    Format of citic_id: YYMMDD-000
        YY - last two digits of the year
        MM - two-digit month number
        DD - two-digit day of the month
        000 - counter starting from 001 for each day

    Example:
        251201-001, 251201-002, 251202-001
    """
    if prefix:
        date_prefix = prefix
    else:
        today = datetime.today()
        year = today.strftime("%y")
        month = today.month
        day = today.day
        date_prefix = f"{year}{month:02d}{day:02d}-"
    
    counter = 1
    citic_id = f"{date_prefix}{counter:003d}"

    if not prefix_only:
        max_counter = 0
        for citic_id in citic_ids:
            if not citic_id.startswith(date_prefix):
                continue
            try:
                counter_part = citic_id.split("-")[1]
                counter = int(counter_part)
            except (IndexError, ValueError):
                continue
            max_counter = max(max_counter, counter)
        next_counter = max_counter + 1
        return f"{date_prefix}{next_counter:003d}"
    else:
        return date_prefix
