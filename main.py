from flask.app import Flask
from werkzeug.wrappers import request
import blockchain
import json
from flask import Flask, request, jsonify

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
    blockchain.calculate_difficulty_attempts(100)

    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    response = []
    for b in blockchain.blockchain:
        response.append(json.loads(b.toJSON()))
    
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
    