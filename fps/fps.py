#!/usr/bin/env python

import time
import threading
import requests
import json
from random import randrange
from flask import Flask, request, jsonify


CONTENT_HEADER = {"Content-Type": "application/json"}
DRONE_ENDPOINT_URI = "http://drone:6066/set_command"
ATM_ENDPOINT_URI = "http://atm:6064/new_task"

drones = []

host_name = "0.0.0.0"
port = 6065
app = Flask(__name__)             # create an app instance

class Drone:
    # v_x = 0
    # v_y = 0
    # v_z = 0
    # battery_charge = 100 
    # token = ""
    # drone_status = "stopped"
    # task_status = ""
    # task_points = []

    def __init__(self, coordinate, name, psswd):
        self.coordinate = coordinate
        self.name = name
        self.psswd = psswd

@app.route("/set_command", methods=['POST'])
def set_command():
    content = request.json
    print(f'[FPS_DEBUG] received {content}')
    global drones
    try:
        if content['command'] == 'start':
            data = {
               "name": content['name'],
               "command": content['command'],
               "psswd": content['psswd'],
               "speed": content['speed']
            }
            requests.post( 
                DRONE_ENDPOINT_URI,
                data=json.dumps(data),
                headers=CONTENT_HEADER,
            )
            print(f'[FPS_START] requested start for drone {content["name"]}')
        if content['command'] == 'stop':
            data = {
               "name": content['name'],
               "command": content['command'],
               "psswd": content['psswd']
            }
            requests.post(
                DRONE_ENDPOINT_URI,
                data=json.dumps(data),
                headers=CONTENT_HEADER,
            )
            print(f'[FPS_STOP] requested for drone {content["name"]}')
        if content['command'] == 'sign_out':
            data = {
               "name": content['name'],
               "command": content['command'],
               "psswd": content['psswd']
            }
            requests.post(
                DRONE_ENDPOINT_URI,
                data=json.dumps(data),
                headers=CONTENT_HEADER,
            )
            print(f'[FPS_SIGN_OUT] requested for drone {content["name"]}')
        if content['command'] == 'move_to':
            data = {
               "name": content['name'],
               "command": content['command'],
               "coordinate": content['coordinate'],
               "psswd": content['psswd'],
               "speed": content['speed']
            }
            requests.post(
                DRONE_ENDPOINT_URI,
                data=json.dumps(data),
                headers=CONTENT_HEADER,
            )
            print(f'[FPS_MOVE_TO] requested motion for drone {content["name"]}')
        if content['command'] == 'new_task':
            data = {
               "name": content['name'],
               "points": content['points']
            }
            requests.post(
                ATM_ENDPOINT_URI,
                data=json.dumps(data),
                headers=CONTENT_HEADER,
            )
            print(f'[FPS_NEW_TASK] requested new task for drone {content["name"]}')
        if content['command'] == 'initiate':
            tmp = Drone(content['coordinate'], content['name'], content['psswd'])
            drones.append(tmp)
            data = {
               "name": content['name'],
               "command": "initiate",
               "coordinate": content['coordinate'],
               "psswd": content['psswd']
            }
            requests.post(
                DRONE_ENDPOINT_URI,
                data=json.dumps(data),
                headers=CONTENT_HEADER,
            )
            print(f'[FPS_INITIATE] successfully requested for drone {content["name"]}')
        if content['command'] == 'registrate': 
            data = {
               "name": content['name'],
               "command": "registrate",
               "psswd": content['psswd']
            }
            requests.post(
                DRONE_ENDPOINT_URI,
                data=json.dumps(data),
                headers=CONTENT_HEADER,
            )
            print(f'[FPS_REGISTRARE] successfully requested for drone {content["name"]}')
        if content['command'] == 'clear_flag': 
            data = {
               "name": content['name'],
               "command": "clear_flag",
               "psswd": content['psswd']
            }
            requests.post(
                DRONE_ENDPOINT_URI,
                data=json.dumps(data),
                headers=CONTENT_HEADER,
            )
            print(f'[FPS_CLEAR_FLAG] successfully requested for drone {content["name"]}')
        # else:
        #     print(f'[ATM_NEW_TASK] something went wrong during creating new task for drone {content["name"]}') 

    except Exception as _:
        error_message = f"malformed request {request.data}"
        return error_message, 400
    return jsonify({"operation": "new_task", "status": True})

@app.route("/data_in", methods=['POST'])
def data_in():
    content = request.json

    global drones
    try:
        drone = list(filter(lambda i: content['name'] == i.name, drones)) #was "in" istead of ""==""
        if len(drone) > 1:
            print(f'[FPS_DATA_IN] incorrect name: {content["name"]}')
            return "BAD NAME", 404

        drone = drone[0]
        print(f'[FPS_DATA_IN] successfully received content from drone {content["name"]} : {content["content"]}')

    except Exception as _:
        error_message = f"malformed request {request.data}"
        return error_message, 400
    return jsonify({"operation": "new_task", "status": True})

@app.route("/atm_input", methods=['POST'])
def atm_input():
    content = request.json
    global drones
    try:
        drone = list(filter(lambda i: content['name'] == i.name, drones)) #was "in" istead of ""==""
        if len(drone) > 1:
            print(f'[ATM_NEW_TASK] incorrect name: {content["name"]}')
            return "BAD NAME", 404

        if content['task_status'] == 'Accepted':
            data = {
               "name": content['name'],
               "points": content['points'],
               "command": 'set_task',
               "psswd": drone[0].psswd
            }
            requests.post(
                DRONE_ENDPOINT_URI,
                data=json.dumps(data),
                headers=CONTENT_HEADER,
            )
            print(f'[FPS_NEW_TASK] successfully accepted new task for drone {content["name"]}')
        else:
            print(f'[FPS_NEW_TASK] something went wrong during accepting new task for drone {content["name"]}') 

    except Exception as _:
        error_message = f"malformed request {request.data}"
        return error_message, 400
    return jsonify({"operation": "new_task", "status": True})

if __name__ == "__main__":
    app.run(port = port, host=host_name)
    