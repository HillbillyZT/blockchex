import hashlib
import logging
import time
import json
from flask import Flask, jsonify, request



class Block:
    def __init__(self, index, hash, previous_hash, timestamp, data):
        self.index = index
        self.hash = hash
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
    
    def __str__(self):
        return str(self.index)+str(self.hash)+str(self.previous_hash)+str(self.timestamp)+str(self.data)
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)
        
        
Blockchain = list[Block]

genesis_block = Block(0, "3ea9cb91d5ac70f93f00370ddb01661e2a3a16bcbac6a5412b0d5b66ee4ffa00", "", 1631511032.099209, "Genesis")

blockchain: Blockchain = [genesis_block]

def calculate_hash(index, previous_hash, timestamp, data):
    block_string = str(index)+str(previous_hash)+str(timestamp)+str(data)
    return hashlib.sha256(block_string.encode()).hexdigest()

def calculate_hash_block(block: Block):
    return calculate_hash(block.index, block.previous_hash, block.timestamp, block.data)

def get_latest_block():
    return blockchain[-1]

def convert_chain_to_json(chain: Blockchain) -> str:
    return json.dumps(chain, default=lambda o: o.__dict__, sort_keys=False, indent=4)

def get_chain_as_json():
    return convert_chain_to_json(blockchain)

def deserialize_block(d: dict) -> Block:
    b = Block(d['index'], d['hash'], d['previous_hash'], d['timestamp'], d['data'])
    return b

def deserialize_blockchain(bclist: list) -> Blockchain:
    bc_ds: Blockchain = []
    for block_dict in bclist:
        bc_ds.append(deserialize_block(block_dict))
    return bc_ds

def add_block(block):
    if is_valid_block(block, get_latest_block()):
        blockchain.append(block)

def generate_next_block(data):
    previous = get_latest_block()
    block = Block(previous.index+1, None, previous.hash, time.time(), data)
    block.hash = calculate_hash_block(block)
    print(block)
    add_block(block)
    return block

def is_valid_block(block, previous):
    if(block.index != previous.index+1):
        logging.Logger.critical("The index of block {block.index} is not one greater than block {previous.index}")
        return False
    elif(previous.hash != block.previous_hash):
        logging.Logger.critical("previous_hash field does not match previous hash")
        return False
    elif(calculate_hash_block(block) != block.hash):
        logging.Logger.critical("Hash field is invalid")
    return True

def is_block_structure_valid(block):
    return type(block.index) is int \
        and type(block.hash) is str \
        and type(block.previous_hash) is str \
        and type(block.timestamp) is float \
        and type(block.data) is str \
        and type(block) is Block

def is_blockchain_valid(b):
    if(str(b[0]) != str(genesis_block)):
        return False;
    
    for i in range(1,len(b)):
        if not is_valid_block(b[i], b[i-1]):
            return False
    
    return True



# Consensus replacement
# def replace_chain(newchain: Blockchain) -> bool:
#     if is_blockchain_valid(newchain) and len(newchain) > len(blockchain):
#         print("The new blockchain is valid and longer than the current chain. The chain will be replaced")
#         # global blockchain 
#         blockchain = newchain
#         return True
#     else:
#         print("The new blockchain is either invalid or shorter than the current chain. It will be discarded.")
#         return False