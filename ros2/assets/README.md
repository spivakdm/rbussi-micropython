# RBussi simulator artwork

`rbussi-top.svg` is an editable, simplified top view, front upwards. Its 90 × 200 body proportions and chamfered outline are based on the instructor's `Rbussi-design/top.dxf`; the body uses a plain plywood colour with a dark outline and a white outer edge for contrast against the map. A dark arrow marks the front. Printed bus artwork has been removed. Wheel locations are illustrative, not a verified assembly drawing. No generative image model was used.

The Docker build renders it to a transparent 45 × 45 PNG and replaces every bundled turtlesim turtle PNG. Replacing all variants avoids the simulator randomly selecting a different turtle on reset/spawn. The 45-pixel canvas height preserves the stock coordinate scale; the drawing does not change physics, sensors or controls. Turtlesim rotates its front-up image 90 degrees at theta=0, so the bus correctly points right initially.

Upstream sources: https://github.com/ros/ros_tutorials/tree/jazzy/turtlesim . Existing turtlesim package licenses remain installed. The supplied original mechanical/artwork files are preserved separately and are not modified by this build.

## Riihimäki map

`riihimaki-map.png` is rendered from the supplied vector PDF, cropped to its print trim box. The 640 × 480 simulator window matches the map's approximately 4:3 proportions. The artwork is displayed without stretching. Clear/reset preserve the background. This is a visual map: roads have no collision rules and the stock color sensor does not read the map layer.

**Copyright Robotx Oy. All rights reserved. Use of this map requires prior permission from Robotx Oy.** See [the map notice](RIIHIMAKI-MAP-NOTICE.txt). Software licenses do not grant rights to this artwork.
