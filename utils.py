import math
import numpy as np


def curve_length(points):
    total = 0.0
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        total += math.dist((x1, y1), (x2, y2))
    return float(total)


def curvature(points):
    angles = []
    for i in range(1, len(points) - 1):
        p1 = np.array(points[i - 1])
        p2 = np.array(points[i])
        p3 = np.array(points[i + 1])

        v1 = p1 - p2
        v2 = p3 - p2

        denom = np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6
        cos_angle = np.dot(v1, v2) / denom
        cos_angle = np.clip(cos_angle, -1, 1)

        angle = np.arccos(cos_angle)
        angles.append(angle)

    if len(angles) == 0:
        return 0.0

    return float(np.mean(angles))


def max_curvature(points):
    angles = []
    for i in range(1, len(points) - 1):
        p1 = np.array(points[i - 1])
        p2 = np.array(points[i])
        p3 = np.array(points[i + 1])

        v1 = p1 - p2
        v2 = p3 - p2

        denom = np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6
        cos_angle = np.dot(v1, v2) / denom
        cos_angle = np.clip(cos_angle, -1, 1)

        angle = np.arccos(cos_angle)
        angles.append(angle)

    if len(angles) == 0:
        return 0.0

    return float(np.max(angles))


def line_angle(points):
    x1, y1 = points[0]
    x2, y2 = points[-1]
    return float(math.degrees(math.atan2(y2 - y1, x2 - x1)))


def bbox_size(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    width = max(xs) - min(xs)
    height = max(ys) - min(ys)
    return float(width), float(height)


def average_x(points):
    xs = [p[0] for p in points]
    return float(np.mean(xs))


def average_y(points):
    ys = [p[1] for p in points]
    return float(np.mean(ys))


def ccw(A, B, C):
    return (
        (C[1] - A[1]) * (B[0] - A[0])
        >
        (B[1] - A[1]) * (C[0] - A[0])
    )


def intersect(A, B, C, D):
    return (
        ccw(A, C, D) != ccw(B, C, D)
    ) and (
        ccw(A, B, C) != ccw(A, B, D)
    )


def count_intersections(line1, line2):
    count = 0
    for i in range(len(line1) - 1):
        A = line1[i]
        B = line1[i + 1]
        for j in range(len(line2) - 1):
            C = line2[j]
            D = line2[j + 1]
            if intersect(A, B, C, D):
                count += 1
    return int(count)


def palm_width(life_points, head_points, heart_points):
    xs = []
    for p in life_points + head_points + heart_points:
        xs.append(p[0])
    return float(max(xs) - min(xs))


def palm_height(life_points, head_points, heart_points):
    ys = []
    for p in life_points + head_points + heart_points:
        ys.append(p[1])
    return float(max(ys) - min(ys))


def palm_size(life_points, head_points, heart_points):
    width = palm_width(life_points, head_points, heart_points)
    height = palm_height(life_points, head_points, heart_points)
    return width, height


def normalized_ratio(value, reference):
    if reference == 0:
        return 0.0
    return float(value / reference)


def angle_difference(angle1, angle2):
    return float(abs(angle1 - angle2))