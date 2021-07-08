#!/usr/bin/env python3
# ^^^ Important - tells kattis this is python3 vs python2

import sys
import json
import logging


logging.basicConfig(filename=r"D:\LibraryOfBabel\Projects\ICPCPlanetoids\MyAdditions\newfile.log", 
                    level=logging.DEBUG,
                    filemode='w',
                    format='%(message)s')


from math import degrees, atan2, tan
def generate_command(thrust=True,
                     cw_rotation=False,
                     ccw_rotation=False,
                     bullet=True,
                     hyperspace=True,
                     change_state=True):
    command = ''
    command += '1' if thrust else '0'
    command += '1' if cw_rotation else '0'
    command += '1' if ccw_rotation else '0'
    command += '1' if bullet else '0'
    command += '1' if hyperspace else '0'
    command += '1' if change_state else '0'
    return command

def get_angle_to_object(object_position, ship_position, ship_rotation):
    angle_to_object = degrees(atan2(object_position[1] - ship_position[1], object_position[0] - ship_position[0]))
    angle_to_object = angle_to_object if angle_to_object >= 0 else angle_to_object + 360
    return angle_to_object - ship_rotation if angle_to_object >= ship_rotation else angle_to_object - ship_rotation + 360
    
def get_dist(artifact_position, ship_position):
    del_x = artifact_position[0] - ship_position[0]
    del_y = artifact_position[1] - ship_position[1]
    return (del_x ** 2 + del_y ** 2) ** 0.5

def dot(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1]
    
def get_colliding_asteroids(ship_position, ship_rotation):
    if frame == 0:
        for id in asteroid_position_current_frame.keys():
            asteroid_position_last_frame[id] = asteroid_position_current_frame[id]
        return {}
    else:
        asteroid_intersections = {}
        ship_m = tan(ship_rotation)
        ship_c = ship_position[1] - ship_m * ship_position[0]
        for id in asteroid_position_current_frame.keys():
            if id in asteroid_position_last_frame:
                del_x = asteroid_position_current_frame[id][0] - asteroid_position_last_frame[id][0]
                del_y = asteroid_position_current_frame[id][1] - asteroid_position_last_frame[id][1]
                asteroid_m = del_y / del_x
                asteroid_c = asteroid_position_current_frame[id][1] - asteroid_m * asteroid_position_current_frame[id][0]
                if ship_m == asteroid_m and ship_c != asteroid_c:
                    continue
                elif ship_m == asteroid_m:
                    asteroid_intersections.append([(asteroid_position_current_frame[id][0] - ship_position[0]) / 2, (asteroid_position_current_frame[id][1] - ship_position[1]) / 2])
                else:
                    x = (asteroid_c - ship_c) / (ship_m - asteroid_m)
                    y = (ship_m * asteroid_c - asteroid_m * ship_c) / (ship_m - asteroid_m)
                    asteroid_intersections[id] = [x, y]
        asteroids_of_concern = []
        for id in asteroid_intersections.keys():
            if get_dist(asteroid_position_current_frame[id], ship_position) < asteroid_distance_threshold:
                del_x1 = asteroid_intersections[id][0] - ship_pos[0]
                del_y1 = asteroid_intersections[id][1] - ship_pos[1]
                del_x2 = asteroid_intersections[id][0] - asteroid_position_current_frame[id][0]
                del_y2 = asteroid_intersections[id][1] - asteroid_position_current_frame[id][1]
                if dot([del_x1, del_y1], [del_x2, del_y2]) < 0:
                    asteroids_of_concern.append(id)
        # [id if get_dist(asteroid_position_current_frame[id], ship_position) < asteroid_distance_threshold and dot([asteroid_intersections[id][0] - ship_pos[0], asteroid_intersections[id][1] - ship_pos[1]], [asteroid_intersections[id][0] - asteroid_position_current_frame[id][0], asteroid_intersections[id][1] - asteroid_position_current_frame[id][1]]) < 0 for id in asteroid_intersections.keys()]
        asteroid_angle_to_ship = {id: get_angle_to_object(asteroid_position_current_frame[id], ship_position, ship_rotation) for id in asteroid_position_current_frame.keys()}
        hittable_asteroids = {id: asteroid_angle_to_ship[id] for id in asteroid_position_current_frame.keys() if asteroid_angle_to_ship[id] < asteroid_angle_threshold}
        return hittable_asteroids

counter = 0
frame = 0
asteroid_position_last_frame = {}
asteroid_position_current_frame = {}
asteroid_radii = {'0': 50, '1': 100, '2': 200}
asteroid_distance_threshold = 4000
asteroid_angle_threshold = 30
while True:
    frame += 1
    # raw_data = sys.stdin.readline()
    raw_data = """{
    "artfPos": [
        -3286.76806640625,
        -284.64599609375
    ],
    "astIds": [
        3
    ],
    "astNum": 1,
    "astPos": [
        [
            2936.709716796875,
            -1737.310546875
        ]
    ],
    "astSizes": [
        49
    ],
    "bulIds": [
        5
    ],
    "bulNum": 1,
    "bulPos": [
        [
            2.0,
            0.0
        ]
    ],
    "bulSrc": [
        48
    ],
    "currentRound": 1,
    "currentScore": 0,
    "currentTime": 4.182635307312012,
    "gameOver": false,
    "lives": 3,
    "shipPos": [
        -2344.286376953125,
        -122.93001556396484
    ],
    "shipR": 183.00173950195312,
    "ufoIds": [
        4
    ],
    "ufoNum": 1,
    "ufoPos": [
        [
            0.0,
            0.0
        ]
    ],
    "ufoSizes": [
        49
    ]
}"""
    if not raw_data:
        break
    
    data = json.loads(raw_data)
    if "gameOver" in data and data["gameOver"]:
        break
    
    thrust, clockwise_rotation, counterclockwise_rotation, bullet, hyperspace, change_state = True, False, False, True, False, True
    ########################################
    artifact_position = data['artfPos']
    ship_position = data['shipPos']
    ship_rotation = data['shipR']
    current_time = data['currentTime']
    asteroid_ids = data['astIds']
    asteroid_positions = data['astPos']
    asteroid_sizes = [asteroid_radii[chr(size)] for size in data['astSizes']]
    for index, id in enumerate(asteroid_ids):
        asteroid_position_current_frame[id] = asteroid_positions[index]
    # asteroid_position_current_frame = {id: asteroid_positions[index] for index, id in enumerate(asteroid_ids)}
    distance_threshold = 5000
    
    angle_to_artifact = get_angle_to_object(artifact_position, ship_position, ship_rotation)
    

    if 0 < angle_to_artifact <= 180:
        counterclockwise_rotation = True
        clockwise_rotation = False
    elif 180 < angle_to_artifact < 360:
        clockwise_rotation = True
        counterclockwise_rotation = False
    if get_dist(artifact_position, ship_position) < distance_threshold and counter < angle_to_artifact // 1.5 and angle_to_artifact > 30:
        logging.debug(str(angle_to_artifact))
        thrust = False
        counter += 1
    else:
        counter = 0

    colliding_asteroids_angle = get_colliding_asteroids(ship_position, ship_rotation)
    
    closest_asteroid_id = -1
    closest_asteroid_distance = 1000000
    for id in colliding_asteroids_angle:
        if id in asteroid_position_current_frame:
            if get_dist(asteroid_position_current_frame[id], ship_position) < closest_asteroid_distance:
                closest_asteroid_distance = asteroid_position_current_frame[id]
                closest_asteroid_id = id
    
    if closest_asteroid_id != -1:
        if 0 < colliding_asteroids_angle[closest_asteroid_id] <= 180:
            counterclockwise_rotation = True
            clockwise_rotation = False
        elif 180 < colliding_asteroids_angle[closest_asteroid_id] < 360:
            clockwise_rotation = True
            counterclockwise_rotation = False
        if counter == 0 and len(colliding_asteroids_angle) > 0:
            thrust = True

    # logging.debug(str(data))
    # logging.debug(str(type(artifact_position)))
    # logging.debug(generate_command(thrust, clockwise_rotation, counterclockwise_rotation, bullet, hyperspace, change_state) + "\n")
    ########################################
    
    sys.stdout.write(generate_command(thrust, clockwise_rotation, counterclockwise_rotation, bullet, hyperspace, change_state) + "\n")
    sys.stdout.flush()
