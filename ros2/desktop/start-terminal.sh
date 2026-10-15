#!/bin/bash
source /opt/ros/jazzy/setup.bash
cd /course
printf '\nRBussi ROS classroom\n\n'
printf '1. Move the simulated bus:\n   ros2 run turtlesim turtle_teleop_key\n\n'
printf '2. Use arrow keys while this terminal has focus.\n   Ctrl+C ends keyboard control.\n\n'
printf '3. List channels:\n   ros2 topic list\n\n'
printf 'Open another terminal: ros-terminal\n\n'
printf 'Real robot connection is OFF until you run:\n   robot-connect\n\n'
exec bash -i
