#!/usr/bin/env python

import hashlib
import os
from random import randrange
from flask import Flask, request, jsonify
import Drone

CONTENT_HEADER = {"Content-Type": "application/json"}
ATM_ENDPOINT_URI = "http://atm:6064/data_in"
ATM_SIGN_UP_URI = "http://atm:6064/sign_up"
ATM_SIGN_OUT_URI = "http://atm:6064/sign_out"
FPS_ENDPOINT_URI = "http://fps:6065/data_in"
DELIVERY_INTERVAL_SEC = 1
drones = []

host_name = "0.0.0.0"
port = os.environ['DRONE_PORT']#6066
app = Flask(__name__)             # create an app instance




@app.route("/set_command", methods=['POST'])
def set_command():
    global drones
    try:
        content = request.json
        print(f'[DRONE_DEBUG] received {content}')
        if content['command'] == 'initiate':
            print(port)
            tmp = Drone.Drone(content['coordinate'], content['name'], content['psswd'])
            drones.append(tmp)
            print (f"Added in point {tmp.coordinate}")
        else:
            
            drone = list(filter(lambda i: content['name'] == i.name, drones))
            
            if len(drone) > 1:
                print(f'incorrect name: {content["name"]}')
                return "BAD NAME", 404
            drone = drone[0] 
            if content['command'] == 'task_status_change':
                    drone.token = content['token']
                    drone.task_status = content['task_status']
                    print(f'[DRONE_DEBUG] token added: {drone.token}')
            elif drone.psswd == content['psswd']:
                if content['command'] == 'start':
                    print(f'[DRONE_DEBUG] points: {drone.task_points}')
                    drone.start(content["speed"])
                if content['command'] == 'stop':
                    drone.stop()
                if content['command'] == 'sign_out':
                    drone.sign_out()
                if content['command'] == 'clear_flag':
                    drone.clear_emergency_flag()
                if content['command'] == 'move_to':
                    drone.stop() 
                    drone.clear_emergency_flag()
                    drone.move_to(content['coordinate'][0], content['coordinate'][1], content['coordinate'][2], content["speed"])
                if content['command'] == 'set_task':
                    tmp = ""
                    for i in content["points"]:
                        tmp.join(str(i))
                    tmp_token = hashlib.md5()
                    tmp_token.update(tmp.encode('utf-8'))
                    tmp_token = tmp_token.hexdigest()
                    print(f'[DRONE_DEBUG] token: {drone.token}')
                    print(f'[DRONE_DEBUG] new token: {tmp_token}')
                    if drone.token == tmp_token:
                        print(f'[DRONE_DEBUG] points added')
                        drone.task_points = content["points"]
                if content['command'] == 'registrate':
                    drone.registrate()
                
    except Exception as e:
        print(f'exception raised: {e}')
        return "MALFORMED REQUEST", 400
    return jsonify({"status": True})

@app.route("/emergency", methods=['POST'])
def emergency():
    global drones
    try:
        content = request.json
        drone = list(filter(lambda i: content['name'] == i.name, drones)) #was "in" istead of ""==""
        if len(drone) > 1:
            print(f'incorrect name: {content["name"]}')
            return "BAD NAME", 404
        else:
            if content['token'] == drone[0].token:
                drone[0].status = "Blocked"
                drone[0].emergency() 
                print(f"[ATTENTION] Дрон экстренно остановлен: {content['name']}")

    except Exception as e:
        print(f'exception raised: {e}')
        return "MALFORMED REQUEST", 400
    return jsonify({"status": True})




if __name__ == "__main__":
    # threading.Thread(
    #             target=lambda: temperature_pushing()).start()
    app.run(port = port, host=host_name)
    
   