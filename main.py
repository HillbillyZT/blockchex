from werkzeug.wrappers import request
import blockchain as blockchain
import json
from flask import Flask, request, jsonify
import p2p_http
from threading import Thread
import time


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

#TODO p2p node conversations


@app.route('/mine', methods=['POST'])
def mine():
    b = blockchain.generate_next_block(str(request.get_data().decode("utf-8")))
    
    response = {
        'message': "New Block Created"
    }
    response = {**response, **json.loads(b.toJSON())}
    
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    response = []
    for b in blockchain.blockchain:
        response.append(json.loads(b.toJSON()))
    
    print(blockchain.get_chain_as_json())
    return jsonify(response), 200

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

if __name__ == '__main__':
    Thread(target=start_flask).start()
    while True:
        p2p_http.init_P2P()
        time.sleep(60)