import moderngl
import glm
import numpy as np
import stl
import math

def print_help():
    print("File, Depth of Cut, Tool Diameter (all units in mm).")

def deg_to_rad(degrees):
    return (degrees * np.pi) / 180.0

def load_shader(filepath):
    with open(filepath) as shader_file:
        with shader_file as file:
            shader = file.read()

    return shader

def calculate_aspect_ratio(res_tuple):
    gcd = np.gcd(res_tuple[0], res_tuple[1])

    return ((res_tuple[0] / gcd), (res_tuple[1] / gcd))

def get_model_min_max(model):
    x_min = np.min(model.vectors[:,:,0])
    x_max = np.max(model.vectors[:,:,0])
    y_min = np.min(model.vectors[:,:,1])
    y_max = np.max(model.vectors[:,:,1])
    z_min = np.min(model.vectors[:,:,2])
    z_max = np.max(model.vectors[:,:,2])

    return (x_min, x_max, y_min, y_max, z_min, z_max)

def determine_square_ortho(min_max_tuple):
    highest_coords = np.ceil(min_max_tuple[1::2])
    lowest_coords = np.floor(min_max_tuple[::2])

    xy_midpoint = (highest_coords[:4] + lowest_coords[:4]) / 2
    largest_dim = 0
    return xy_midpoint[0] if xy_midpoint[0] > xy_midpoint[1] else xy_midpoint[1]

def bounding_box_circle(center, radius: float, target_res=0.1, margin=0):
    top = (math.floor(center[0]), math.ceil(center[1] + radius + margin))
    bottom = (math.floor(center[0]), math.floor(center[1] - radius - margin))
    left = (math.floor(center[0] - radius - margin), math.floor(center[1]))
    right = (math.ceil(center[0] + radius + margin), math.floor(center[1]))
    
    return (top, bottom, left, right)

def double_circle_bbox(center1, radius1: float, center2, radius2: float):
    '''
    Takes two circles, represented by their center coordinates and
    radii, and calculates a bounding box containing both circles.
    '''
    top_circ1 = math.ceil(center1[1] + radius1)
    bottom_circ1 = math.floor(center1[1] - radius1)
    left_circ1 = math.floor(center1[0] - radius1)
    right_circ1 = math.ceil(center1[0] + radius1)

    top_circ2 = math.ceil(center2[1] + radius2)
    bottom_circ2 = math.floor(center2[1] - radius2)
    left_circ2 = math.floor(center2[0] - radius2)
    right_circ2 = math.ceil(center2[0] + radius2)

    top = top_circ1 if top_circ1 > top_circ2 else top_circ2
    bottom = bottom_circ1 if bottom_circ1 < bottom_circ2 else bottom_circ2
    left = left_circ1 if left_circ1 < left_circ2 else left_circ2
    right = right_circ1 if right_circ1 > right_circ2 else right_circ2

    return (top, bottom, left, right)

def check_point_in_circle(circ_center, radius, pixel_coord):
    pythag = (pixel_coord[0] - circ_center[0])**2 + (pixel_coord[1] - circ_center[1])**2

    return pythag <= radius**2
