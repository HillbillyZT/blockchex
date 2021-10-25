from werkzeug.wrappers import request
import blockchain as blockchain
import json
from flask import Flask, request, jsonify
import p2p_http
from threading import Thread
import time

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

#TODO ensure hashing consistency between pure dumps and JSON dumps
#TODO p2p node conversations
#TODO scaling block difficulty
#TODO start PoS implementation

@app.route('/mine', methods=['POST'])
def mine():
    b = blockchain.generate_next_block(str(request.get_data().decode("utf-8")))

    response = {
        'message': "New Block Created",
        'block': json.loads(b.toJSON())
    }

    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    return blockchain.get_chain_as_json(), 200


@app.route('/newPeer', methods=['POST'])
def add_new_peer():
    p2p_http.init_target(request.data.decode("utf-8"))
    return "", 200


@app.route('/getPeers', methods=['GET'])
def get_peers():
    return p2p_http.targets, 200


# End-points for P2P communications    
@app.route('/queryLatest', methods=['GET'])
def receive_query_latest():
    return blockchain.get_latest_block().toJSON(), 200


@app.route('/queryAll', methods=['GET'])
def receive_query_all():
    if request.remote_addr not in p2p_http.targets:
        p2p_http.init_target(request.remote_addr)
    return blockchain.get_chain_as_json(), 200


@app.route('/receiveBlock', methods=['POST'])
def receive_broadcast_block():
    return "", 200


@app.route('/queryHeight', methods=['GET'])
def receive_block_height():
    return str(blockchain.get_latest_block().index), 200


def start_flask():
    app.run(host='0.0.0.0', port=5000)


# TODO Query functions are handled in init, just attempt load chain
if __name__ == '__main__':
    Thread(target=start_flask).start()
    # Check if we have a local copy stored
    # if blockchain.does_local_copy_exist():
    #     blockchain.replace_chain(blockchain.load_local_copy())
    #     print("local copy loaded")
    #     # Query peers for their block height and compare to ours
    #     # if int(receive_block_height()) != query_latest().index:
    #     #     # Request their chain if block height isn't equal
    #     #     blockchain = query_all()
    # # If we don't have a local copy, create one and load chain from peers into it
    # else:
    #     peer_chain = []
    #     # peer_chain = query_all()
    #     with open('chain.txt', 'w') as outfile:
    #         for b in peer_chain:
    #             outfile.write(b)


    while True:
        p2p_http.init_P2P()
        time.sleep(60)
