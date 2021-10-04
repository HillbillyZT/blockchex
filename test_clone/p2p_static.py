from typing import Any
import websockets
import asyncio
import json
import blockchain
import logging
from enum import Enum
from websockets import WebSocketServerProtocol

logging.basicConfig(level=logging.INFO)

# See comments above class: Server for more information on these cases
class MessageType(Enum):
    QUERY_LATEST = 0
    QUERY_ALL = 1
    RESPONSE = 2

class Message:
    def __init__(self, type: MessageType, data: str):
        self.type = type
        self.data = data

# The object which will handle incoming messages and process outgoing messages
# This also keeps track of all websocket connections
# There are 3 cases our P2P server will handle for the moment:
# 1. When "our" node generates a block, we will broadcast it to all peers
# 2. When "our" node connects to a new peer, we will query their latest block
# 3. When "our" node finds a block that surpasses our chain, our node will
#    determine whether to add the new block to our chain, or check the integrity
#    of the peer's chain

# Maintain list of current socket connections
connections: list = set()

async def register(ws: WebSocketServerProtocol) -> None:
    connections.add(ws)
    logging.info(f"{ws.remote_address} has connected.")

async def unregister(ws: WebSocketServerProtocol) -> None:
    connections.remove(ws)
    logging.info(f"{ws.remote_address} has disconnected.")

# Gets latest block, convert to JSON, encode as Message 
def response_latest_as_message() -> Message:
    return Message(MessageType.RESPONSE, blockchain.get_latest_block().toJSON())

# Gets full chain, in JSON, encoded as Message
def response_blockchain_as_message() -> Message:
    return Message(MessageType.RESPONSE, blockchain.get_chain_as_json())

def query_latest_as_message() -> Message:
    return Message(MessageType.QUERY_LATEST, None)

async def message_printer(ws: WebSocketServerProtocol):
    async for message in ws:
        print(message)

# This will handle all incoming and outgoing connections
async def ws_handler(ws: WebSocketServerProtocol, host: str) -> None:
    # Add all new connections to the list of current live sockets
    await register(ws)
    print(connections)
    print(host)
        
    # Meat of the handler, TODO(Chris)
    try:
        await message_printer(ws)
    
    # When a connection ends, remove it from the list
    finally:
        await unregister(ws)    

async def connect_to_peer(hostname: str, port: int) -> None:
    url = f"ws://{hostname}:{port}"
    async with websockets.connect(url) as websocket:
        await register(websocket)
    
# We have a server waiting for incoming connection requests
#def init_P2P(websocket) -> None:
start_server: Any
def init_P2P():
    global start_server
    start_server = websockets.serve(ws_handler, host='localhost', port=4001)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server)
    loop.run_forever()




