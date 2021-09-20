import websockets
import asyncio
import json
from enum import Enum

class MessageType(Enum):
    QUERY_LATEST = 0
    QUERY_ALL = 1
    RESPONSE_BLOCKCHAIN = 2

class Message:
    def __init__(self, type: MessageType, data: str):
        self.type = type
        self.data = data

# We have a server waiting for incoming connection requests
def init_P2P(websocket) -> None:
    pass
    




