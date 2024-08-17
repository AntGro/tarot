- Need to add a button to start a new game.
- Need to add an exit room
- Need to add placeholders for stacks
- Need to center the card playground

```shell
conda create -n tarot python=1.12
conda activate tarot 

python app.py
gunicorn -k eventlet -w 1 app:app

# kill
lsof -i tcp:8000
kill -9 $PID
```

ngrok http 5001