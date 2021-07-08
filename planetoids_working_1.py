#!/usr/bin/env python3

import sys
import json
import logging
from math import degrees, atan2, tan


logging.basicConfig(filename=r"D:\LibraryOfBabel\Projects\ICPCPlanetoids\MyAdditions\planetoids1.log", 
                    level=logging.DEBUG,
                    filemode='w',
                    format='%(message)s')

def get_position_through_void(object_position):
    x, y = object_position[0], object_position[1]
    return [[x, y], [x+7600, y], [x-7600, y], [x, y+4200], [x, y-4200]]

def get_angle_to_object(object_position, ship_position, ship_rotation):    
    angle_to_object = degrees(atan2(object_position[1] - ship_position[1], object_position[0] - ship_position[0]))
    angle_to_object = angle_to_object if angle_to_object >= 0 else angle_to_object + 360
    return angle_to_object - ship_rotation if angle_to_object >= ship_rotation else angle_to_object - ship_rotation + 360

def worm_hole(object_position, ship_position, ship_rotation):
    replicated_positions = get_position_through_void(object_position)
    distances = [get_dist(pos, ship_position) for pos in replicated_positions]
    min_dist = min(distances)
    min_dist_index = distances.index(min_dist)
    # angles_to_min = [get_angle_to_object(pos, ship_position, ship_rotation) for i, pos in enumerate(replicated_positions) if 0.8 * min_dist <= distances[i] <= 1.2 * min_dist]
    angles_to_min = [get_angle_to_object(pos, ship_position, ship_rotation) for i, pos in enumerate(replicated_positions) if distances[i] == min_dist]
    sorted_angles = sorted(angles_to_min, key=lambda x: min(x, 360-x))
    return sorted_angles[0], min_dist

def get_dist(artifact_position, ship_position):
    del_x = artifact_position[0] - ship_position[0]
    del_y = artifact_position[1] - ship_position[1]
    return (del_x ** 2 + del_y ** 2) ** 0.5

def get_new_artifact_position(object_position, ship_position, ship_rotation):
    possible_pos = get_position_through_void(object_position)
    distances = [get_dist(pos, ship_position) for pos in possible_pos]
    min_dist = min(distances)
    min_dist_index = distances.index(min_dist)
    return possible_pos[min_dist_index]

def generate_command(thrust,
                     cw_rotation,
                     ccw_rotation,
                     bullet,
                     hyperspace,
                     change_state):
    if cw_rotation and ccw_rotation:
        logging.debug('both clockwise and counterclockwise rotations are enabled')
    command = ''
    command += '1' if thrust else '0'
    command += '1' if cw_rotation else '0'
    command += '1' if ccw_rotation else '0'
    command += '1' if bullet else '0'
    command += '1' if hyperspace else '0'
    command += '1' if change_state else '0'
    return command
    
    
while True:
    raw_data = sys.stdin.readline()
    if not raw_data:
        break

    data = json.loads(raw_data)
    if "gameOver" in data and data["gameOver"]:
        break
    
    thrust, clockwise_rotation, counterclockwise_rotation, bullet, hyperspace, change_state = True, False, False, True, False, True
    artifact_position = data['artfPos']
    ship_position = data['shipPos']
    ship_rotation = data['shipR']
    
    # new_artifact_position = get_new_artifact_position(artifact_position, ship_position, ship_rotation)
    # angle_to_artifact = get_angle_to_object(new_artifact_position, ship_position, ship_rotation)
    angle_to_artifact, min_dist = worm_hole(artifact_position, ship_position, ship_rotation)
    if angle_to_artifact > 5:
        if 0 < angle_to_artifact <= 180:
            counterclockwise_rotation = True
            clockwise_rotation = False
        else:
            clockwise_rotation = True
            counterclockwise_rotation = False

    artifact_distance_threshold = 3000
    artifact_angle_threshold = 3
    # if get_dist(new_artifact_position, ship_position) < artifact_distance_threshold and angle_to_artifact > artifact_angle_threshold:
    if min_dist < artifact_distance_threshold and angle_to_artifact > artifact_angle_threshold:
        thrust = False
    
    sys.stdout.write(generate_command(thrust, clockwise_rotation, counterclockwise_rotation, bullet, hyperspace, change_state) + "\n")
    sys.stdout.flush()