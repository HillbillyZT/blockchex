from __future__ import annotations
from typing import TYPE_CHECKING
import blockchain as bc
import logging
import requests
import crypto
if TYPE_CHECKING:
    from blockchain import Block, Blockchain



logging.basicConfig(level=logging.INFO)

# TODO(Chris) add maximum connection limit

# List of broadcast targets
targets = set()


# Send the block to every open connection
def broadcast_block(b: Block) -> None:
    for target in targets:
        # we do some POST requests
        r = requests.post(f"{target}/receiveBlock", data=b.toJSON())


# Calls /queryLatest from main.py to return the latest block on our local chain
def query_latest(target: str) -> Block:
    # implement request for latest, handle data
    r = requests.get(f"{target}/queryLatest")
    j = r.json()
    # b = bc.Block(j['index'], j['hash'], j['previous_hash'], j['timestamp'], j['data'], j['difficulty'], j['nonce'])
    b = bc.deserialize_block(j)
    return b


# Calls /queryAll from main.py to get an updated blockchain from our peers
def query_all(target: str) -> Blockchain:
    r = requests.get(f"{target}/queryAll")
    j = r.json()
    j_s: bc.Blockchain = bc.deserialize_blockchain(j)
    return j_s


# Adds block to chain if it is valid and returns a Boolean based on the result
def add_block_to_chain(b: Block) -> bool:
    if bc.is_valid_block(b, bc.get_latest_block()):
        bc.add_block(b)
        return True
    else:
        return False


# When we request just the top block and compare it
def handle_query_latest(target):
    peer_latest = query_latest(target)
    compare_heights(peer_latest, target)


# When we need to request full blockchain
def handle_query_all(target):
    chain = query_all(target)
    bc.replace_chain(chain)


# Compare height of peer vs our chain
def compare_heights(peer_latest: Block, target: str) -> None:
    self_latest = bc.get_latest_block()

    # Verify the block structure
    if not bc.is_block_structure_valid(peer_latest):
        logging.info("Block structure not valid.")
        return

    # Fetch heights for comparison
    peer_height = peer_latest.index
    self_height = bc.get_latest_block().index

    # Compare heights and react accordingly
    if peer_height > self_height:
        if peer_latest.previous_hash == self_latest.hash:
            logging.info("Peer ahead one block, attempting to validate and add...")
            if add_block_to_chain(peer_latest):
                logging.info("Block successfully added.")
            else:
                logging.info("Block addition failed. Structure likely invalid.")
        else:
            logging.info("Block not valid on our chain, querying full blockchain.")
            handle_query_all(target)
    else:
        logging.info("The peer's blockchain is not longer than ours: ignore.")


# Add new target and then try to query their latest block
def init_target(target: str) -> None:
    targets.add(target)
    try:
        handle_query_latest(target)
    except Exception as e:
        print(e)
        targets.remove(target)


# This function does most of the heavy lifting for our p2p functionality
def init_P2P():
    #print("got here!")
    for target in targets.copy():
        # Run Connection Startup Tasks
        try:
            init_target(target)
        except Exception as e:
            logging.info(e)

# Testing
# query_all("http://localhost:5001")
