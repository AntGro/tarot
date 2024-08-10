# app.py
import time
from typing import Dict

from flask import Flask, render_template, request  # Import request here
from flask_socketio import SocketIO, emit, join_room, leave_room
import eventlet

eventlet.monkey_patch()

from game import CardGame, BACK_CARD_PATH

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

    # Create a new game room if it doesn't exist
    if room not in games:
        games[room] = CardGame()

    games[room].deal_cards(username, session_id=request.sid)

    join_room(room, sid=request.sid, namespace=room)

    player = games[room].players[username].dict()
    emit('game-setup', {'username': username, 'player': player}, room=request.sid)

    if len(games[room].players) == 2:
        msg = "You're opponent is already here, the game can start!"
        player1, player2 = games[room].players.values()
        emit('opponent-setup', {'opponent': player1.dict()}, room=player2.session_id)
        emit('opponent-setup', {'opponent': player2.dict()}, room=player1.session_id)
    else:
        msg = f"You have entered the room {room}, waiting for another player to join."
    emit('status', {'msg': msg}, room=room)

    # emit(
    #     'tablecards',
    #     {'username': username,
    #      'tablecards': list(map(lambda c: c.dict(), games[room].players[username].cards_on_table))},
    #     room=room
    # )
    #
    # emit(
    #     'card-hands',
    #     {'username': username, 'hand': list(map(lambda c: c.dict(), games[room].players[username]))},
    #     room=room
    # )


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
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
