from flask.app import Flask
from werkzeug.wrappers import request
import blockchain
import json
from flask import Flask, request, jsonify
import p2p_static

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

p2p_static.init_P2P()

#TODO ensure hashing consistency between pure dumps and JSON dumps
#TODO p2p node conversations
#TODO PoW


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
    p2p_static.connect_to_peer("localhost", 4000)
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
    
    