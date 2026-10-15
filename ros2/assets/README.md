# RBussi simulator artwork

`rbussi-top.svg` is an editable, simplified top view, front upwards. Its 90 × 200 body proportions and chamfered outline are based on the instructor's `Rbussi-design/top.dxf`; colours and bus identity are based on `Rbussi-design/bus-rgb.pdf`. Wheel locations and roof details are illustrative, not a verified assembly drawing. No generative image model was used.

The Docker build renders it to a transparent 45 × 45 PNG and replaces every bundled turtlesim turtle PNG. Replacing all variants avoids the simulator randomly selecting a different turtle on reset/spawn. The 45-pixel canvas height preserves the stock coordinate scale; the drawing does not change physics, sensors or controls. Turtlesim rotates its front-up image 90 degrees at theta=0, so the bus correctly points right initially.

Upstream sources: https://github.com/ros/ros_tutorials/tree/jazzy/turtlesim . Existing turtlesim package licenses remain installed. The supplied original mechanical/artwork files are preserved separately and are not modified by this build.
