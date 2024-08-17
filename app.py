# app.py
import time
from typing import Dict

import eventlet
from flask import Flask, render_template, request  # Import request here
from flask_socketio import SocketIO, emit, join_room, leave_room

from game import CardGame, Player, CARD_PLACEHOLDER_PATH, Card

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')

# Game state
games: Dict[str, CardGame] = {}


@app.route('/')
def index():
    return render_template('index.html', timestamp=time.time())


# noinspection PyPackageRequirements
@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']

    # Create a new game room if it doesn't exist
    if room not in games:
        games[room] = CardGame()

    game = games[room]
    while len(username) == 0 or username in game.players:
        username = username + "-2"

    game.deal_cards(username, session_id=request.sid)

    join_room(room, sid=request.sid, namespace=room)

    if len(game.players) == 2:
        game_update(game=game, played_card=None, player=None, room=room)
        emit('restore-playcard-placeholders', {'placeholder_path': CARD_PLACEHOLDER_PATH}, room=room)
    else:
        msg = f"You have entered the room {room}, waiting for another player to join."
        emit('status', {'msg': msg}, room=room)


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('status', {'msg': f"{username} has left the room."}, room=room)


# TODO next
@socketio.on('hand-card-click')
def on_hand_card_click(data):
    room = data.get('room')
    handcard_index = data['handcard_index']
    game = games[room]
    player = game.get_active_player()
    if game.active_card is None:
        emit('restore-playcard-placeholders', {'placeholder_path': CARD_PLACEHOLDER_PATH}, room=room)
    played_card = game.play_handcard(handcard_index=handcard_index)
    game_update(game=game, played_card=played_card, player=player, room=room)


@socketio.on('table-card-click')
def on_table_card_click(data):
    room = data.get('room')
    stack_index = data['stack_index']
    game = games[room]
    player = game.get_active_player()
    if game.active_card is None:
        emit('restore-playcard-placeholders', {'placeholder_path': CARD_PLACEHOLDER_PATH}, room=room)
    played_card = game.play_tablecard(stack_index=stack_index)
    game_update(game=game, played_card=played_card, player=player, room=room)


def game_update(game: CardGame, played_card: Card | None, player: Player | None, room: str | None):
    """ Function called once a player has played """
    player1, player2 = game.players.values()
    for current_player in [player1, player2]:
        opponent: Player = player2 if current_player.username == player1.username else player1
        emit('player-update', {'username': current_player.username, 'player': current_player.dict()},
             room=current_player.session_id)
        emit('opponent-setup', {'opponent': opponent.dict()}, room=current_player.session_id)
        msg = (f"You have {current_player.game_score} points (with {current_player.game_n_oudler} oudlers), "
               f"your opponent has {opponent.game_score} points (with {opponent.game_n_oudler} oudlers)")
        emit('status', {'msg': msg}, room=current_player.session_id)
        if played_card is not None:
            if current_player.username == player.username:
                emit('playcard-update', {'card': played_card.dict(), 'current': True}, room=current_player.session_id)
                emit('playcard-update', {'card': played_card.dict(), 'current': False}, room=opponent.session_id)
            else:
                emit('playcard-update', {'card': played_card.dict(), 'current': False}, room=current_player.session_id)
                emit('playcard-update', {'card': played_card.dict(), 'current': True}, room=opponent.session_id)
    if player1.n_cards == 0:
        time.sleep(5)
        game_reset(game=game, room=room)


def game_reset(game: CardGame, room: str):
    game.new_game()
    for username in game.player_usernames:
        player = game.players[username]
        game.deal_cards(username, session_id=player.session_id)
    game_update(game=game, played_card=None, player=None, room=room)
    emit('restore-playcard-placeholders', {'placeholder_path': CARD_PLACEHOLDER_PATH}, room=room)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
