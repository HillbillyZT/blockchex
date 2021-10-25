import blockchain as bc
import logging
import requests

logging.basicConfig(level=logging.INFO)

# TODO(Chris) add maximum connection limit

# List of broadcast targets
targets = set()


# TODO(Chris)
def broadcast_block(b: bc.Block) -> None:
    for target in targets:
        # we do some POST requests
        r = requests.post(f"{target}/receiveBlock", data=b.toJSON())


def query_latest(target: str) -> bc.Block:
    # implement request for latest, handle data
    r = requests.get(f"{target}/queryLatest")
    j = r.json()
    b = bc.Block(j['index'], j['hash'], j['previous_hash'], j['timestamp'], j['data'], j['difficulty'], j['nonce'])
    return b


# TODO(Chris)
def query_all(target: str) -> bc.Blockchain:
    r = requests.get(f"{target}/queryAll")
    j = r.json()
    j_s: bc.Blockchain = bc.deserialize_blockchain(j)
    return j_s


def add_block_to_chain(b: bc.Block) -> bool:
    if bc.is_valid_block(b, bc.get_latest_block()):
        bc.add_block(b)
        return True
    else:
        return False


# When we request just the top block
def handle_query_latest(target):
    peer_latest = query_latest(target)
    compare_heights(peer_latest, target)


# When we need to request full blockchain
def handle_query_all(target):
    chain = query_all(target)
    bc.replace_chain(chain)


def compare_heights(peer_latest: bc.Block, target: str) -> None:
    self_latest = bc.get_latest_block()

    if not bc.is_block_structure_valid(peer_latest):
        logging.info("Block structure not valid.")
        return

    peer_height = peer_latest.index
    self_height = bc.get_latest_block().index

    if peer_height > self_height:
        if peer_latest.previous_hash == self_latest.hash:
            logging.info("Peer ahead one block, attempting to validate and add...")
            if add_block_to_chain(peer_latest):
                logging.info("Block successfully added.")

                # This call may be unnecessary, handled by add_block_to_chain()
                broadcast_block(peer_latest)
            else:
                logging.info("Block addition failed. Structure likely invalid.")
        else:
            logging.info("Block not valid on our chain, querying full blockchain.")
            handle_query_all(target)
    else:
        logging.info("The peer's blockchain is not longer than ours: ignore.")


def init_target(target: str) -> None:
    targets.add(target)
    try:
        handle_query_latest(target)
    except Exception as e:
        print(e)
        targets.remove(target)


def init_P2P():
    print("got here!")
    for target in targets.copy():
        # Run Connection Startup Tasks
        try:
            init_target(target)
        except Exception as e:
            logging.info(e)

# Testing
# query_all("http://localhost:5001")
