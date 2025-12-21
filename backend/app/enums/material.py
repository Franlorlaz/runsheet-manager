from enum import Enum


class Material(str, Enum):
    graphene = "graphene"
    mos2 = "MoS2"
    ws2 = "WS2"
    silicon = "silicon"
    other = "other"
