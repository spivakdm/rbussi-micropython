"""Geometry for the teaching track; independent of ROS and window size."""
import math

PIXELS_PER_UNIT = 45.0
LINE_WIDTH = 6.0
SENSOR_FORWARD = 0.46
SENSOR_HALF_SPACING = 0.15
# A single smooth loop drawn over the city map, in its logical 640 x 480 frame.
WAYPOINTS = [(343, 128), (391, 100), (470, 130), (492, 206),
             (506, 267), (471, 333), (449, 408), (353, 441),
             (260, 420), (210, 371), (253, 303), (270, 240), (310, 170)]


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
