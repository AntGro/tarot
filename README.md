- Need to know how to highlight allowed moves
- Need to understand the command.
- Need to store sid of each player
- Need to add score
- Need to add a button to start a new game.
- Need to add an exit room

```shell
conda activate tarot 

gunicorn -k eventlet -w 1 app:app

# kill
lsof -i tcp:8000
kill -9 $PID
```