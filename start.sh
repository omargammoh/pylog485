#!/usr/bin/tmux source-file

echo "-------WELCOME-TO-PYLOG485-------"
echo "this software was developed by omar gammoh (omar.gammoh@gmail.com)"
echo ""
echo "-> making sure the server is running in a tmux session"

if (tmux has-session -t 0 2> /dev/null); then
	echo "  -> session already exists"
	echo "  ->" $(tmux ls)
else
	echo  "  -> session does not exist, starting new session"
	if [ "$TMUX" != "" ]; then
		echo "Error: cannot start session from within tmux."
		exit
	fi
	tmux new-session -d
	tmux split-window -d -t 0 -h
	tmux send-keys -t 0 'sudo python /home/pi/pylog485/manage.py runserver 0.0.0.0:9001' enter C-l
    echo "  -> sudo python /home/pi/pylog485/manage.py runserver 0.0.0.0:9001"
    echo "  -> session started sucessfully"
fi


#(tmux ls) || (tmux new-session -d; tmux split-window -d -t 0 -h; tmux send-keys -t 0 'sudo python /home/pi/pylog485/manage.py runserver 0.0.0.0:9001' enter C-l)
echo ""
echo "some info for you:"
echo "  to attach the session: tmux a -t 0"
echo "  to detach the session type: ctrl-b then d"
echo "  to kill the session: tmux kill-session -t 0"
echo "  to run the session: . /home/pi/pylog485/start.sh"
echo "---------------ENJOY--------------"





