#!/usr/bin/tmux source-file

echo "----------------"
running pylog485/start.sh
(tmux ls) || (tmux new-session -d; tmux split-window -d -t 0 -h; tmux send-keys -t 0 'sudo python /home/pi/pylog485/manage.py runserver 0.0.0.0:9001' enter C-l)
echo "----------------"