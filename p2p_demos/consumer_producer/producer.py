import asyncio
import websockets

async def produce(host: str, port: int) -> None:
    async with websockets.connect(f"ws://{host}:{port}") as ws:
        message: str = input("What message would you like to send? ")
        await ws.send(message)
        await ws.recv()

loop = asyncio.get_event_loop()
loop.run_until_complete(produce("localhost", 4000))

# asyncio.run(produce("hi", "localhost", 4000))