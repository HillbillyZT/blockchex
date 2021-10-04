from flask import Flask, request, jsonify
from flask.templating import render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abcdf'
socketio = SocketIO(app)

@app.route('/')
def sessions():
    return render_template('session.html')

@app.route('/test', methods=['POST'])
def test():
    
    return "reached", 200

def message_received(methods=['GET', 'POST']):
    print('message was received!')

@socketio.on('my_event')
def handle_my_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=message_received)

if __name__ == "__main__":
    socketio.run(app, port=5001, debug=True)