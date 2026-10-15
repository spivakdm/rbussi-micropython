# Turtlesim background extension

Vendored from https://github.com/ros/ros_tutorials/tree/c83136eb8d0d3ed52eb0906183dd86ca309a4ed2/turtlesim (Jazzy). Original BSD 3-clause notices are retained in each source/header; see LICENSE.

Changes: fixed 640 × 480 field; optional startup-only `background_image` ROS parameter; aspect-preserving cached map drawn below trails. The local CMakeLists builds against the installed Jazzy turtlesim interfaces. Topic, service and motion implementations are unchanged. The stock color sensor reads trails, not the map.

The separate map artwork is owned by Robotx Oy and is not covered by this software license; see ../assets/RIIHIMAKI-MAP-NOTICE.txt.
