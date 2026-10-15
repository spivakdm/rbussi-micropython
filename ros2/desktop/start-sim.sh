#!/bin/bash
source /opt/ros/jazzy/setup.bash
exec ros2 run turtlesim turtlesim_node --ros-args -p background_r:=245 -p background_g:=247 -p background_b:=250
