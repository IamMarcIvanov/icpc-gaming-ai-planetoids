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
    # if get_angle_to_object(object_position, ship_position, ship_rotation) < 30:
        # return get_angle_to_object(object_position, ship_position, ship_rotation), get_dist(object_position, ship_position)
    replicated_positions = get_position_through_void(object_position)
    distances = [get_dist(pos, ship_position) for pos in replicated_positions]
    min_dist = min(distances)
    min_dist_index = distances.index(min_dist)
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
    
def get_avg_vel():
    del_x, del_y = [], []
    for i, pos in enumerate(prev_ship_positions[:-1]):
        del_x.append(prev_ship_positions[i+1][0] - pos[0])
        del_y.append(prev_ship_positions[i+1][1] - pos[1])

    n = len(del_x)
    if n > 0:
        return [sum(del_x) / n, sum(del_y) / n]
    else:
        return [0, 0]

def get_velocity_orientation_angle(angle):
    vel_dir = get_avg_vel()
    speed = (vel_dir[0] ** 2 + vel_dir[1] ** 2) ** 0.5
    if speed < speed_threshold:
        return 0

    angle_of_velocity = degrees(atan2(vel_dir[1], vel_dir[0]))
    angle_of_velocity = angle_of_velocity if angle_of_velocity >= 0 else angle_of_velocity + 360

    # logging.debug('{:<50}{:<50}'.format('angle_of_velocity', str(angle_of_velocity)))
    # logging.debug('{:<50}{:<50}'.format('velocity_orientation_angle', str(abs(angle_of_velocity - angle))))
    # logging.debug('{:<50}{:<50}'.format('ship_rotation', str(angle)))
    return abs(angle_of_velocity - angle)


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

def should_jump(ship_position, threat_positions, threat_sizes):
    for pos, size in zip(threat_positions, threat_sizes):
        if get_dist(pos, ship_position) <= ship_radius + size + jump_proximity_threshold:
            return True
    return False

frame = 0
time_of_last_jump = -100
curr_time = 0
ship_radius = 32
asteroid_radii = {'0': 50, '1': 100, '2': 200}
prev_ship_positions = []
jump_cooldown = 5

# hyperparams:
artifact_distance_threshold = 4000
artifact_angle_threshold = 5
velocity_orientation_threshold = 10
jump_distance_threshold = 2000
prev_ship_pos_considered = 10
speed_threshold = 10
jump_proximity_threshold = 50
skip_thrust_n = 4
no_thrust_speed_threshold = 8
no_thrust_distance_threshold = 1000
no_thrust_angle_threshold = 30
hyperspace_jump_angle_threshold = 20

logging.debug('{:<50}{:<50}\n'.format('entering while loop', 'import and all done'))
while True:
    threat_positions, threat_sizes = [], []
    frame += 1
    raw_data = sys.stdin.readline()
    if not raw_data:
        break

    data = json.loads(raw_data)
    if "gameOver" in data and data["gameOver"]:
        break
    
    thrust, clockwise_rotation, counterclockwise_rotation, bullet, hyperspace, change_state = True, False, False, True, False, True
    artifact_position = data['artfPos']
    ship_position = data['shipPos']
    logging.debug('{:<50}{:<50}'.format('ship position', str(ship_position)))
    
    prev_ship_positions.append(ship_position)
    ship_rotation = data['shipR']
    
    curr_time = data['currentTime']
    asteroid_positions = data['astPos']
    
    asteroid_sizes = [asteroid_radii[chr(size)] for size in data['astSizes']]
    
    angle_to_artifact, min_dist = worm_hole(artifact_position, ship_position, ship_rotation)
    
    # orient for artifact
    if angle_to_artifact > artifact_angle_threshold:
        if 0 < angle_to_artifact <= 180:
            logging.debug('{:<50}{:<50}'.format('turning counterclockwise', str(ship_rotation)))
            counterclockwise_rotation = True
            clockwise_rotation = False
        else:
            logging.debug('{:<50}{:<50}'.format('turning clockwise', str(ship_rotation)))
            clockwise_rotation = True
            counterclockwise_rotation = False
    # thrust
    velocity_orientation_angle = get_velocity_orientation_angle(ship_rotation)
    if (min_dist < artifact_distance_threshold and angle_to_artifact > artifact_angle_threshold) or velocity_orientation_angle > velocity_orientation_threshold:
        if frame % skip_thrust_n != 0:
            logging.debug('{:<50}{:<50}'.format('skip thrust to turn', data['currentScore']))
            thrust = False
    
    # finding speed for slowing down before collecting artifact
    curr_speed = no_thrust_speed_threshold
    if len(prev_ship_positions) >= 2:
        del_x = prev_ship_positions[-1][0] - prev_ship_positions[-2][0]
        del_y = prev_ship_positions[-1][1] - prev_ship_positions[-2][1]
        curr_speed = (del_x ** 2 + del_y ** 2) ** 0.5
    logging.debug('{:<50}{:<50}'.format('current_speed', str(curr_speed)))
    
    # slowing down before collecting artifact
    if min_dist < no_thrust_distance_threshold and angle_to_artifact < no_thrust_angle_threshold and velocity_orientation_angle < no_thrust_angle_threshold and curr_speed >= no_thrust_speed_threshold:
        logging.debug('{:<50}{:<50}'.format('slowing down before artifact', min_dist))
        thrust = False
    
    # hyperspce jump
    if curr_time >= time_of_last_jump + jump_cooldown and should_jump(ship_position, asteroid_positions, asteroid_sizes) and min_dist > jump_distance_threshold and angle_to_artifact > hyperspace_jump_angle_threshold:
        hyperspace = True
        logging.debug('{:<50}{:<50}'.format('hyperspace jump', curr_time))
        time_of_last_jump = curr_time
    
    # write to stdout
    sys.stdout.write(generate_command(thrust, clockwise_rotation, counterclockwise_rotation, bullet, hyperspace, change_state) + "\n")
    sys.stdout.flush()
    
    prev_ship_positions = prev_ship_positions[-prev_ship_pos_considered:]
    logging.debug('{:<50}{:<50}\n'.format('current frame', frame))