from werkzeug.wrappers import request
import blockchain
import json
from flask import Flask, request, jsonify
import p2p_static
from threading import Thread
import asyncio


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
async def add_new_peer():
    await p2p_static.new_client_connection("ws://localhost:4001")
    # Thread(target=p2p_static.new_client_connection("ws://localhost:4001")).start()
    
    print(p2p_static.connection_queue, p2p_static.connections_outgoing)
    #socketio.emit('my_event')
    return "", 200

@app.route('/getPeers', methods=['GET'])
def get_peers():
    print(p2p_static.connections)
    return str(p2p_static.connections), 200

@app.route('/checkConn', methods=['GET'])
async def check_conn():
    await p2p_static.connections[0].send("test")


def start_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    Thread(target=start_flask).start()
    # Thread(target=p2p_static.test_P2P()).start()
    p2p_static.init_P2P()
    
    