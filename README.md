- Need to know how to highlight allowed moves
- Need to understand the command.

```shell
conda activate tarot 
gunicorn eventlet flask flask_socketio numpy pydantic

gunicorn -k eventlet -w 1 app:app

# kill
lsof -i tcp:8000
kill -9 $PID
```