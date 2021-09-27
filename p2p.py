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
class Server:
    def __init__(self):
        # Maintain list of current socket connections
        self.connections: list = set()

    async def register(self, ws: WebSocketServerProtocol) -> None:
        self.connections.add(ws)
        logging.info(f"{ws.remote_address} has connected.")
    
    async def unregister(self, ws: WebSocketServerProtocol) -> None:
        self.connections.remove(ws)
    
    # Gets latest block, convert to JSON, encode as Message 
    def get_latest_as_message() -> Message:
        return Message(MessageType.RESPONSE, blockchain.get_latest_block().toJSON())
    
    # Gets full chain, in JSON, encoded as Message
    def get_blockchain_as_message() -> Message:
        return Message(MessageType.RESPONSE, blockchain.get_chain_as_json())
    
    # This will handle all incoming and outgoing connections
    async def ws_handler(self, ws: WebSocketServerProtocol, host: str) -> None:
        # Add all new connections to the list of current live sockets
        await self.register(ws)
        
        # Meat of the handler, TODO(Chris)
        try:
            pass
        
        # When a connection ends, remove it from the list
        finally:
            await self.unregister(ws)    

# We have a server waiting for incoming connection requests
def init_P2P(websocket) -> None:
    if __name__ == '__main__':
        server = Server()
        start_server = websockets.serve(server.ws_handler, 'localhost', 4000)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_server)
        loop.run_forever()




