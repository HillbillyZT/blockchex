from hashlib import sha256
import logging
import time
import json
from flask import Flask, jsonify, request


class Block:
    def __init__(self, index, hash, previous_hash, timestamp, data, difficulty, nonce=0):
        self.index = index
        self.hash: str = hash
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.difficulty = difficulty
        self.nonce = nonce

    #TODO(Chris) __dict__ string implementation + JSON interaction
    def __str__(self):
        return str(self.index) + str(self.hash) + str(self.previous_hash) + str(self.timestamp) + str(self.data) + str(self.difficulty) + str(self.nonce)
        
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)

def calculate_hash_block(block: Block) -> str:
    block_string = str(block)
    return sha256(block_string.encode()).hexdigest()

Blockchain = list[Block]

timestamp = time.time()
new_genesis = Block(0, "0" * 64, "", time.time(), "Genesis", 0)
new_genesis.hash = calculate_hash_block(new_genesis)

genesis_block = new_genesis

#Global difficulty controls how hard it is to find a correct nonce to solve the hash
#TODO make the difficulty scale based on how fast the previous block was solved
#Maybe aim for 10-15 minute block times?
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

def get_chain_as_json():
    response = []
    for b in blockchain:
        response.append(json.loads(b.toJSON()))
    #return str(jsonify(response).data.decode("utf-8"))
    return json.dumps(blockchain, default=lambda o: o.__dict__, sort_keys=False, indent=4)

#Confirms block is valid before appending it
def add_block(block):
    if is_valid_block(block, get_latest_block()):
        blockchain.append(block)

def generate_next_block(data: str):
    previous = get_latest_block()
    block = Block(previous.index + 1, "", previous.hash, time.time(), data, GL_DIFFICULTY)
    
    #Calculates nonce and hash
    solve_block(block)

    #Print the block to the console and add it to the chain
    print(block)
    add_block(block)
    return block


def is_valid_block(block, previous):
    if (block.index != previous.index + 1):
        logging.Logger.critical("The index of block {block.index} is not one greater than block {previous.index}")
        return False
    elif (previous.hash != block.previous_hash):
        logging.Logger.critical("previous_hash field does not match previous hash")
        return False
    elif (calculate_hash_block(block) != block.hash):
        logging.Logger.critical("Hash field is invalid")
        return False
    elif (not confirm_difficulty(block)):
        return False
    else:
        return True


def is_block_structure_valid(block):
    return type(block.index) is int \
           and type(block.hash) is str \
           and type(block.previous_hash) is str \
           and type(block.timestamp) is float \
           and type(block.data) is str \
           and type(block) is Block


def is_blockchain_valid(b):
    if (str(b[0]) != str(genesis_block)):
        return False

    for i in range(1, len(b)):
        if not is_valid_block(b[i], b[i - 1]):
            return False

    return True

# On average, how many attempts does it take to get 3 leading 0s?
def calculate_difficulty_attempts(runc: int) -> float: 
    avg = 0
    for i in range(0, runc):
        generate_next_block(str(i))
        avg += get_latest_block().nonce
    return avg / runc

# Consensus replacement
# def replace_chain(newchain: Blockchain) -> None:
#     if is_blockchain_valid(newchain) and len(newchain) > len(blockchain):
#         print("The new blockchain is valid and longer than the current chain. The chain will be replaced")
#         global blockchain
#         blockchain = newchain
#     else:
#         print("The new blockchain is either invalid or shorter than the current chain. It will be discarded.")
