#!/bin/bash
source /opt/ros/jazzy/setup.bash
cd /course
printf '\nRBussi ROS classroom\n\n'
printf '1. Move the simulated bus:\n   ros2 run turtlesim turtle_teleop_key\n\n'
printf '2. Use arrow keys while this terminal has focus.\n   Ctrl+C ends keyboard control.\n\n'
printf '3. List channels:\n   ros2 topic list\n\n'
printf 'New terminal: F8 or ros-terminal\n'
printf 'Paste: Ctrl+V (Mac: Command+V). Wait for text, then Enter.\n\n'
printf 'Line-following demo: sim-line-demo (Ctrl+C to stop)\n\n'
printf 'Connect to the real robot when needed:\n   robot-connect\n\n'
exec bash -i
