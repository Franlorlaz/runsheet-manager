from enum import Enum


class RunsheetState(str, Enum):
    edit = "edit",
    review = "review",
    accepted = "accepted",
    running = "running",
    finished = "finished",


runsheet_state_info_dict = {
    RunsheetState.edit: {
        "nextState": RunsheetState.review,
        "nextButtonLabel": "To Review",
        "nextButtonStyle": "warning",
        "badgeStyle": "info",
    },
    RunsheetState.review: {
        "nextState": RunsheetState.accepted,
        "nextButtonLabel": "Approve Runsheet",
        "nextButtonStyle": "success",
        "badgeStyle": "warning",
    },
    RunsheetState.accepted: {
        "nextState": RunsheetState.running,
        "nextButtonLabel": "Start Runsheet",
        "nextButtonStyle": "info",
        "badgeStyle": "success",
    },
    RunsheetState.running: {
        "nextState": RunsheetState.finished,
        "nextButtonLabel": "Finish Runsheet",
        "nextButtonStyle": "danger",
        "badgeStyle": "danger",
    },
    RunsheetState.finished: {
        "nextState": RunsheetState.finished,
        "nextButtonLabel": "Download Runsheet",
        "nextButtonStyle": "primary",
        "badgeStyle": "dark",
    },
}
