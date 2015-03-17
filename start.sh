#!/usr/bin/tmux source-file

echo "-------WEILCOME-TO-PYLOG485-------"
echo "->this software was developed by omar gammoh (omar.gammoh@gmail.com)"
echo "->making sure the server is running in a tmuw session: sudo python /home/pi/pylog485/manage.py runserver 0.0.0.0:9001"
(tmux ls) || (tmux new-session -d; tmux split-window -d -t 0 -h; tmux send-keys -t 0 'sudo python /home/pi/pylog485/manage.py runserver 0.0.0.0:9001' enter C-l)
echo "->to attach the session: tmux a -t 0"
echo "->to detach the session type: ctrl-b then d"
echo "->to kill the session: tmux kill-session -t 0"
echo "->to run the session: . /home/pi/pylog485/start.sh"
echo "---------------ENJOY--------------"