#!/usr/bin/tmux source-file

echo ""
echo ""
echo "-------WELCOME-TO-PYLOG485-------"
echo "this software was developed by omar gammoh (omar.gammoh@gmail.com)"
echo ""
echo "-> making sure the server is running in a tmux session"
session_name=pylog485
if (tmux has-session -t $session_name 2> /dev/null); then
	echo "  -> session already exists"
	echo "  ->" $(tmux ls)
else
	echo  "  -> session does not exist, starting new session"
	if [ "$TMUX" != "" ]; then
		echo "Error: cannot start session from within tmux."
		exit
	fi
	tmux new-session -d -s $session_name
	tmux split-window -d -t $session_name -h
	tmux send-keys -t $session_name 'sudo python /home/pi/pylog485/manage.py runserver 0.0.0.0:9001' enter C-l
    echo "  -> sudo python /home/pi/pylog485/manage.py runserver 0.0.0.0:9001"
    echo "  -> session started sucessfully"
fi

echo ""
echo "some info for you:"
echo "  to attach the session: tmux a -t $session_name"
echo "  to detach the session type: ctrl-b then d"
echo "  to kill the session: tmux kill-session -t $session_name"
echo "  to run the session: . /home/pi/pylog485/start.sh"
echo "  to find out all the tmux shortcuts: ctrl-b ? when in a tmux session"
echo "---------------ENJOY--------------"
