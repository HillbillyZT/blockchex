from hashlib import sha256
import logging
import time
import json
from typing import Union

from flask import Flask, jsonify, request
from os.path import exists


class Block:
    def __init__(self, index, hash, previous_hash, timestamp, data, difficulty, nonce=0):
        self.index = index
        self.hash: str = hash
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.difficulty = difficulty
        self.nonce = nonce

    # TODO(Chris) __dict__ string implementation + JSON interaction
    def __str__(self):
        return str(self.index) + str(self.hash) + str(self.previous_hash) + str(self.timestamp) + str(self.data) + str(
            self.difficulty) + str(self.nonce)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)


Blockchain = list[Block]

# timestamp = time.time()
# new_genesis = Block(0, "0" * 64, "", time.time(), "Genesis", 0)
# new_genesis.hash = calculate_hash_block(new_genesis)

# genesis_block = new_genesis

# Added 0,0 for diff,nonce
genesis_block = Block(0, "3ea9cb91d5ac70f93f00370ddb01661e2a3a16bcbac6a5412b0d5b66ee4ffa00", "", 1631511032.099209,
                      "Genesis", 0, 0)

# Global difficulty controls how hard it is to find a correct nonce to solve the hash
# TODO make the difficulty scale based on how fast the previous block was solved
# Maybe aim for 10-15 minute block times?
GL_DIFFICULTY = 3

blockchain: Blockchain = [genesis_block]


def calculate_hash(index, previous_hash, timestamp, data, difficulty, nonce):
    block_string = str(index)+str(previous_hash)+str(timestamp)+str(data) + str(difficulty) + str(nonce)
    return sha256(block_string.encode()).hexdigest()


def calculate_hash_block(block: Block) -> str:
    return calculate_hash(
        block.index, block.previous_hash, block.timestamp, block.data, block.difficulty, block.nonce
        )


# previously is_hash_correct, new name is less confusing
def confirm_difficulty(block: Block) -> bool:
    return block.hash.startswith('0' * GL_DIFFICULTY)


# Previously the new calculate_hash, now separate.
# Defines the nonce and hash values for a new block
def solve_block(block: Block) -> None:
    while not confirm_difficulty(block):
        block.nonce = block.nonce + 1
        block.hash = calculate_hash_block(block)


def get_latest_block():
    return blockchain[-1]


def convert_block_to_json(block: Block) -> str:
    return json.dumps(block, default=lambda o: o.__dict__, sort_keys=False, indent=4)


def convert_chain_to_json(chain: Blockchain) -> str:
    return json.dumps(chain, default=lambda o: o.__dict__, sort_keys=False, indent=4)


def get_chain_as_json():
    return convert_chain_to_json(blockchain)


def deserialize_block(d: dict) -> Block:
    b = Block(d['index'], d['hash'], d['previous_hash'], d['timestamp'], d['data'], d['difficulty'], d['nonce'])
    return b


def deserialize_blockchain(bclist: list) -> Blockchain:
    bc_ds: Blockchain = []
    for block_dict in bclist:
        bc_ds.append(deserialize_block(block_dict))
    return bc_ds


def add_block(block):
    if is_valid_block(block, get_latest_block()):
        blockchain.append(block)


def generate_next_block(data: str):
    previous = get_latest_block()
    block = Block(previous.index + 1, "", previous.hash, time.time(), data, GL_DIFFICULTY)

    # Calculates nonce and hash
    solve_block(block)

    # Print the block to the console and add it to the chain
    print(block)
    add_block(block)
    return block


# New block is <60s behind the previous block
# TODO handle future block ?
def is_valid_timestamp(block: Block, new_block: Block) -> bool:
    return (block.timestamp - 60 < new_block.timestamp)


def is_valid_block(block, previous):
    if (block.index != previous.index + 1):
        logging.info("The index of block {block.index} is not one greater than block {previous.index}")
        return False
    elif (previous.hash != block.previous_hash):
        logging.info("previous_hash field does not match previous hash")
        return False
    elif (calculate_hash_block(block) != block.hash):
        logging.info("Hash field is invalid")
        return False
    elif (not confirm_difficulty(block)):
        logging.info("The block is of insufficient difficulty.")
        return False
    elif (not is_valid_timestamp(previous, block)):
        logging.info("The block is too far behind the previous block.")
        return False
    else:
        return True


def is_block_structure_valid(block: Block):
    return type(block.index) is int \
           and type(block.hash) is str \
           and type(block.previous_hash) is str \
           and type(block.timestamp) is float \
           and type(block.data) is str \
           and type(block.difficulty) is int \
           and type(block.nonce) is int \
           and type(block) is Block


def is_blockchain_valid(b):
    if len(b) == 0:
        return False
    if (str(b[0]) != str(genesis_block)):
        return False

    for i in range(1, len(b)):
        if not is_valid_block(b[i], b[i - 1]):
            return False

    return True


# Return a boolean value based on whether or not the specified file exists
def does_local_copy_exist():
    return exists('chain.txt')


# Load local copy from chain.txt
def load_local_copy() -> Blockchain:
    with open('chain.txt', 'r') as outfile:
        for b in outfile:
            data = json.loads(b)

    # Use our deserialization function to turn the data into a blockchain structure
    load_chain = deserialize_blockchain(data)
    return load_chain


def get_cumulative_difficulty(chain: Blockchain) -> int:
    sum = 0
    for b in chain:
        sum += 2 ** b.difficulty
    return sum


# Consensus replacement
def replace_chain(newchain: Blockchain) -> bool:
    global blockchain
    if is_blockchain_valid(newchain) and get_cumulative_difficulty(newchain) > get_cumulative_difficulty(blockchain):
        print("The new blockchain is valid and longer than the current chain. The chain will be replaced")

        blockchain = newchain
        return True
    else:
        print("The new blockchain is either invalid or shorter than the current chain. It will be discarded.")
        return False


# Input hash value, return either a block or string
def lookup_block_by_hash(findHash: str) -> Union[Block, str]:
    for b in blockchain:
        if b.hash == findHash:
            return b
    not_found = "No block found with that hash"
    return not_found


# Input a height value, return either a block or a string
def lookup_block_by_height(findBlockHeight: int) -> Union[Block, str]:
    if 0 <= int(findBlockHeight) <= len(blockchain):
        return blockchain[int(findBlockHeight)]
    invalid_input = "Please input a valid block height between 0 and " + str(len(blockchain))
    return invalid_input
