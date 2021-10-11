from typing import Any
import websockets
import asyncio
import blockchain
import logging
import json
from enum import Enum
from websockets.legacy.server import WebSocketServerProtocol

logging.basicConfig(level=logging.INFO)

# TODO(Chris) add maximum connection limit

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

# Set of incoming connection objects
connections: list = set()

# List of host URLs to receive active client connections
connection_queue: list = []

# Set of outgoing connection objects
connections_outgoing = set()

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

# Server side handler
# This will handle all incoming connections
async def ws_handler(ws: WebSocketServerProtocol, host: str) -> None:
    # Add all new connections to the list of current live sockets
    #await register(ws)
    
    
        
    # Meat of the handler, TODO(Chris)
    try:
        for message in ws:
            print(message)
    
    # When a connection ends, remove it from the list
    finally:
        await unregister(ws)    


async def client_handler_loop() -> None:
    while True:
        # For any inbound connections that we haven't reciprocated
        while connection_queue:
            conn = await websockets.connect(connection_queue.pop(0))
            
            # Register new current connection
            connections_outgoing.add(conn)
            logging.info(f"{conn.remote_address} has connected.")
            
            # Do all initial connection items here
            # This includes sending blockchain queries, etc
            # This is outgoing connections; no blockchain responses will be produced from here
            # Blockchain responses will, however, be handled here
        
        
        # Here, handle looped behavior for all outgoing connections
        while connections_outgoing:
            for socket in connections_outgoing:
                if socket.closed:
                    connections_outgoing.remove(socket)
                    
                    # Unregister connection if terminated
                    logging.info(f"{socket.remote_address} has disconnected.")
                
                await socket.send("ping")
                # pong = await socket.recv()
                # print(pong)
                
                async for message in socket:
                    if(message == "pong"):
                        logging.info(message)
                    else:
                        print(message)
                
                pass

start_server: Any
async def connect_to_peer(hostname: str, port: int) -> None:
    url = f"ws://{hostname}:{port}"
    
    # TODO(Chris) try block here, finally block to unreg
    try:
        async with websockets.connect(url) as websocket:
            await register(websocket)
            await websocket.send("test")
            
    finally:
        await unregister(websocket)
    
# We have a server waiting for incoming connection requests

def init_P2P():
    global start_server
    start_server = websockets.serve(ws_handler, 'localhost', 4000)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server)
    loop.run_forever()

# Testing client loop routine
loop = asyncio.get_event_loop()

connection_queue.append("ws://localhost:4001")
loop.run_until_complete(client_handler_loop())
#loop.run_forever()

