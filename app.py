# app.py
import time
from typing import Dict

from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
import eventlet
from game import CardGame

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')

# Game state
games: Dict[str, CardGame] = {}


@app.route('/')
def index():
    return render_template('index.html', timestamp=time.time())


@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']

    if room not in games:
        games[room] = CardGame()

    join_room(room)

    if username not in games[room].players:
        games[room].deal_cards(username)

    emit(
        'status',
        {'msg': f"{username} has entered the room."}, room=room
    )
    print(games[room].players[username].cards_on_table)
    emit(
        'tablecards',
        {'username': username,
         'tablecards': list(map(lambda c: c.dict(), games[room].players[username].cards_on_table))},
        room=room
    )
    emit(
        'handcards',
        {'username': username, 'hand': list(map(lambda c: c.dict(), games[room].players[username].hand.cards))},
        room=room
    )



@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('status', {'msg': f"{username} has left the room."}, room=room)


@socketio.on('move')
def on_move(data):
    room = data['room']
    move = data['move']
    # Handle the move in the game logic
    emit('update', {'move': move}, room=room)


if __name__ == '__main__':
    socketio.run(app, debug=True)
