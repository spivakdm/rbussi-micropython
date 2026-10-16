"""Geometry for the teaching track; independent of ROS and window size."""
import math

PIXELS_PER_UNIT = 45.0
LINE_WIDTH = 6.0
SENSOR_FORWARD = 0.46
SENSOR_HALF_SPACING = 0.15
# Road centres in the supplied 1575 x 1181 map raster, including west of Hyria.
MAP_WAYPOINTS = [
    (800, 165), (1010, 225), (1170, 300), (1235, 410), (1250, 565),
    (1235, 665), (1160, 755), (1145, 850), (1120, 930), (1030, 1005),
    (940, 1050), (790, 1095), (630, 1090), (500, 1040), (420, 945),
    (330, 845), (200, 750), (105, 665), (90, 500), (95, 365),
    (170, 300), (400, 255), (600, 210),
]
# Match the renderer's aspect-preserving fit into the logical 640 x 480 scene.
MAP_SCALE = 640 / 1575
MAP_TOP = (480 - 1181 * MAP_SCALE) / 2
WAYPOINTS = [(x * MAP_SCALE, y * MAP_SCALE + MAP_TOP) for x, y in MAP_WAYPOINTS]



def make_track():
    points = []
    for i in range(len(WAYPOINTS)):
        p0, p1, p2, p3 = [WAYPOINTS[j % len(WAYPOINTS)]
                           for j in (i-1, i, i+1, i+2)]
        for step in range(16):
            t = step / 16
            point = []
            for axis in (0, 1):
                a, b, c, d = [p[axis] for p in (p0, p1, p2, p3)]
                point.append(0.5 * (2*b + (-a+c)*t +
                    (2*a-5*b+4*c-d)*t*t + (-a+3*b-3*c+d)*t*t*t))
            points.append(point)
    return points


TRACK = make_track()


def pixel(x, y):
    return [x * PIXELS_PER_UNIT, 479 - y * PIXELS_PER_UNIT]


def distance_to_track(px, py):
    nearest = float('inf')
    for i, (ax, ay) in enumerate(TRACK):
        bx, by = TRACK[(i+1) % len(TRACK)]
        dx, dy = bx-ax, by-ay
        fraction = max(0, min(1, ((px-ax)*dx + (py-ay)*dy) / (dx*dx+dy*dy)))
        nearest = min(nearest, math.hypot(px-ax-fraction*dx, py-ay-fraction*dy))
    return nearest


def sensors(x, y, theta):
    result = []
    for side in (1, -1):  # Left, then right, relative to the robot's front.
        sx = x + SENSOR_FORWARD*math.cos(theta) - side*SENSOR_HALF_SPACING*math.sin(theta)
        sy = y + SENSOR_FORWARD*math.sin(theta) + side*SENSOR_HALF_SPACING*math.cos(theta)
        px, py = pixel(sx, sy)
        black = int(distance_to_track(px, py) <= LINE_WIDTH/2)
        result.append([px, py, black])
    return result


def start_pose():
    x, y = TRACK[0]
    nx, ny = TRACK[1]
    return x/45, (479-y)/45, math.atan2(y-ny, nx-x)
