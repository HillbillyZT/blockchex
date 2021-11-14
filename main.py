from werkzeug.wrappers import request
import blockchain as blockchain
import json
from flask import Flask, request, jsonify
import client
import p2p_http
from threading import Thread
import time

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


# TODO ensure hashing consistency between pure dumps and JSON dumps
# TODO p2p node conversations
# TODO scaling block difficulty
# TODO start PoS implementation


# Calling /mine with a post method generates a new block
@app.route('/mine', methods=['POST'])
def mine():
    b = blockchain.generate_next_block(str(request.get_data().decode("utf-8")))

    response = {
        'message': "New Block Created",
        'block': json.loads(b.toJSON())
    }

    return jsonify(response), 200


# Calling /chain with GET returns the current blockchain as json
@app.route('/chain', methods=['GET'])
def full_chain():
    return blockchain.get_chain_as_json(), 200


# Calling /newPeer with POST initiates a new p2p connection
@app.route('/newPeer', methods=['POST'])
def add_new_peer():
    p2p_http.init_target(request.data.decode("utf-8"))
    return "", 200


# Calling /getPeers with GET returns all currently connected peers
@app.route('/getPeers', methods=['GET'])
def get_peers():
    return p2p_http.targets, 200


# Calling /queryLatest with GET returns the latest block on our blockchain as json
@app.route('/queryLatest', methods=['GET'])
def receive_query_latest():
    return blockchain.get_latest_block().toJSON(), 200


# Calling /queryAll with GET returns an updated blockchain after checking with our peers
@app.route('/queryAll', methods=['GET'])
def receive_query_all():
    # Check if the address is not in our targets and add if necessary
    # init_target does all the heavy lifting here
    if request.remote_addr not in p2p_http.targets:
        p2p_http.init_target(request.remote_addr)
    return blockchain.get_chain_as_json(), 200


# TODO test this function
# Handle blocks as we receive them from peers
@app.route('/receiveBlock', methods=['POST'])
def receive_broadcast_block():
    if request.remote_addr not in p2p_http.targets:
        p2p_http.targets.add(request.remote_addr)
    
    # Check if received block is just +1, or on different chain
    print(request.data.decode())
    block: dict = json.loads(request.data.decode())
    block_obj: blockchain.Block = blockchain.deserialize_block(block)
    p2p_http.compare_heights(block_obj, request.remote_addr)
    return "", 200


# Calling /queryHeight with GET returns our latest block index as a string
@app.route('/queryHeight', methods=['GET'])
def receive_block_height():
    return str(blockchain.get_latest_block().index), 200


# Calling /block with a hash returns the block with the hash value input
@app.route('/blockHash/<findHash>', methods=['GET'])
def get_block_by_hash(findHash: str):
    b = blockchain.lookup_block_by_hash(findHash)
    return blockchain.convert_block_to_json(b), 200


# Calling /block with a height returns the block with the height value input
@app.route('/blockHeight/<findHeight>', methods=['GET'])
def get_block_by_height(findHeight: int):
    b = blockchain.lookup_block_by_height(findHeight)
    return blockchain.convert_block_to_json(b), 200


# This function starts our flask server
# and lets our local host determine the address to run it on
# Necessary to be a separate function so we can run it on a thread in Main
def start_flask():
    app.run(host='0.0.0.0', port=5000)


# Main
if __name__ == '__main__':
    # Check if we have a local copy stored
    if blockchain.does_local_copy_exist():
        blockchain.replace_chain(blockchain.load_local_copy())
        print("local copy loaded")

    # Flask server url is hardcoded until we can figure out how to automatically retrieve it
    serverURL = 'http://192.168.0.4:5000'

    # Run server and client on separate threads
    Thread(target=start_flask).start()
    Thread(target=client.runClient(serverURL)).start()

    # Run an infinite loop of init_p2p
    while True:
        p2p_http.init_P2P()
        time.sleep(60)
