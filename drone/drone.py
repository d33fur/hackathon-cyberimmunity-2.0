#!/usr/bin/env python

import hashlib
import math
import random
import time
import threading
import requests
import json
from random import randrange
from flask import Flask, request, jsonify


CONTENT_HEADER = {"Content-Type": "application/json"}
ATM_ENDPOINT_URI = "http://atm:6064/data_in"
ATM_SIGN_UP_URI = "http://atm:6064/sign_up"
ATM_SIGN_OUT_URI = "http://atm:6064/sign_out"
FPS_ENDPOINT_URI = "http://fps:6065/data_in"
DELIVERY_INTERVAL_SEC = 1
drones = []

host_name = "0.0.0.0"
port = 6066
app = Flask(__name__)             # create an app instance


class Drone:
    v_x = 0
    v_y = 0
    v_z = 0
    battery_charge = 100 
    emergency_stop = threading.Event()
    token = ''
    motion_status = "Stopped"
    task_points = []
    status = 'Active'

    def __init__(self, coordinate, name, psswd):
        self.coordinate = coordinate
        self.name = name
        self.psswd = psswd  

    def get_coordinate(self):
        return self.coordinate

    def move_to(self, x, y, z, speed):
        # global DELIVERY_INTERVAL_SEC
        # dx_target = x - self.coordinate[0]
        # dy_target = y - self.coordinate[1]
        # direction = math.atan2(dy_target, dx_target)
        # distance = math.sqrt(dx_target**2 + dy_target**2)

        # if z != self.coordinate[2]:
        #     threading.Thread(target=lambda: self.flight_level_change(x, y, z, speed)).start()
        # else:
        #     threading.Thread(target=lambda: self.motion(x, y, speed)).start()
        self.motion_status = "Active"
        global DELIVERY_INTERVAL_SEC
        dx_target = x - self.coordinate[0]
        dy_target = y - self.coordinate[1]
        dz_target = z - self.coordinate[2]
        direction = math.atan2(dy_target, dx_target)
        t = math.sqrt(dx_target**2 + dy_target**2)/speed
        time_offset = t%DELIVERY_INTERVAL_SEC

        while not self.emergency_stop.is_set():
            if abs(self.coordinate[2] - z) >= 1:
                time.sleep(1)
                if (self.coordinate[2] - z) >= 0:
                    self.coordinate[2] -= 1
                else: 
                    self.coordinate[2] += 1
                self.send_position()
            else:
                # self.emergency_stop.set()
                # print(f'[REACHED_ECHELONE] {self.coordinate}')
                if time_offset == 0:
                    if (abs(self.coordinate[0] - x) > 1) or (abs(self.coordinate[1] - y) > 1):
                        time.sleep(DELIVERY_INTERVAL_SEC)
                        self.coordinate[0] += math.cos(direction) * speed * DELIVERY_INTERVAL_SEC
                        self.coordinate[1] += math.sin(direction) * speed * DELIVERY_INTERVAL_SEC
                        self.send_position()
                    else:
                        self.emergency_stop.set()
                        self.motion_status = "Stopped"
                        print(f'[REACHED_POINT] {self.coordinate}')
                else:
                    if (abs(self.coordinate[0] - x) > 1) or (abs(self.coordinate[1] - y) > 1):
                        time.sleep(time_offset)
                        self.coordinate[0] += math.cos(direction) * speed * DELIVERY_INTERVAL_SEC
                        self.coordinate[1] += math.sin(direction) * speed * DELIVERY_INTERVAL_SEC
                        self.send_position()
                    else:
                        self.emergency_stop.set()
                        self.motion_status = "Stopped"
                        print(f'[REACHED_POINT] {self.coordinate}')
                    time_offset=0

    def clear_emergency_flag(self):
        if not self.status == "Blocked":
            self.emergency_stop.clear()
    
    # def flight_level_change(self, x,y,z):
    #     while not self.emergency_stop.is_set():
    #         if abs(self.coordinate[2] - z) > 1:
    #             time.sleep(1)
    #             self.coordinate[2] += 1
    #             self.send_position()
    #         else:
    #             self.emergency_stop.set()
    #             print(f'[REACHED_ECHELONE] {self.coordinate}')

    # def motion(self, x, y, speed):
        # global DELIVERY_INTERVAL_SEC
        # dx_target = x - self.coordinate[0]
        # dy_target = y - self.coordinate[1]
        # direction = math.atan2(dy_target, dx_target)
        # while not self.emergency_stop.is_set():
        #     if (abs(self.coordinate[0] - x) > 1) or (abs(self.coordinate[1] - y) > 1):
        #         time.sleep(DELIVERY_INTERVAL_SEC)
        #         self.coordinate[0] += math.cos(direction) * speed * DELIVERY_INTERVAL_SEC
        #         self.coordinate[1] += math.sin(direction) * speed * DELIVERY_INTERVAL_SEC
        #         self.send_position()
        #     else:
        #         self.emergency_stop.set()
        #         print(f'[REACHED_POINT] {self.coordinate}')

    # def move_to(self, x, y, z, speed):
    #     v_x = speed[0]
    #     v_y = speed[1]
    #     v_z = speed[2]
    #     global DELIVERY_INTERVAL_SEC
    #     self.emergency()
    #     self.emergency_stop.clear()

    #     if self.motion_status == "Stopped":
    #         self.motion_status = "Active"
    #         while not self.emergency_stop.is_set() and self.motion_status == "Active":
    #             self.v_x = v_x
    #             self.v_y = v_y
    #             self.v_z = v_z
    #             time.sleep(DELIVERY_INTERVAL_SEC)
    #             self.coordinate[0] = self.coordinate[0] + v_x
    #             self.coordinate[1] = self.coordinate[1] + v_y
    #             self.coordinate[2] = self.coordinate[2] + v_z
    #             self.battery_charge-=1
    #             if self.battery_charge <= 0:
    #                 self.emergency()
    #                 print(f'[ERROR] Battre low')
    #             if (abs(self.coordinate[0] - x) < 3) and (abs(self.coordinate[1] - y) < 3) and (abs(self.coordinate[2] - z) < 3):
    #                 self.motion_status == "Stopped"
    #                 if self.task_points[0] == [x,y,z]:
    #                     self.task_points.pop(0)
    #             else:
    #                 self.send_position()
    #     else:
    #         self.emergency_stop.clear()

    def telemetry(self):
        try:
            data = {
            "name": self.name,
            "content": random.randint(1000,9999)
            }
            response = requests.post(
                FPS_ENDPOINT_URI,
                data=json.dumps(data),
                headers=CONTENT_HEADER,
            )
            #print(f"[info] результат отправки данных: {response}")
        except Exception as e:
            print(f'exception raised: {e}')

    def change_echelon(self, new_echelon):
        self.emergency()
        self.move_to(self.coordinate[0],self.coordinate[1], new_echelon, 1)
        #self.start()

    def start(self, speed):
        self.clear_emergency_flag()
        while not len(self.task_points) == 0: #or not self.emergency_stop.is_set():
            # if self.motion_status == "Stopped":
            x = self.task_points[0][0]
            y = self.task_points[0][1]
            z = self.task_points[0][2]
            if not self.emergency_stop.is_set() and self.motion_status=="Stopped":
                print(f'[DRONE_DEBUG] asked motion to {x,y,z}')
                threading.Thread(
                    target=lambda:  self.move_to(x,y,z,speed)).start()
            else:
                if abs(self.coordinate[0] - x) <= 1 and abs(self.coordinate[1] - y) <= 1 and abs(self.coordinate[2] - z) <= 1:
                    self.task_points.pop(0)
                    self.clear_emergency_flag()
                time.sleep(DELIVERY_INTERVAL_SEC)
            
    def stop(self):
        self.emergency()
        
    def sign_out(self):
        self.emergency()
        data = {
            "name": self.name
            }
        try:
            response = requests.post(
                ATM_SIGN_OUT_URI,
                data=json.dumps(data),
                headers=CONTENT_HEADER,
            )
            #print(f"[info] результат отправки данных: {response}")
        except Exception as e:
            print(f'exception raised: {e}')

    def registrate(self):
        data = {
            "name": self.name,
            "coordinate": self.coordinate,
            "status": "OK"
            }
        try:
            response = requests.post(
                ATM_SIGN_UP_URI,
                data=json.dumps(data),
                headers=CONTENT_HEADER,
            )
            #print(f"[info] результат отправки данных: {response}")
        except Exception as e:
            print(f'exception raised: {e}')

    def send_position(self):
        data = {
            "name": self.name,
            "token": self.token,
            "coordinate": self.coordinate,
            "coordinate_x": self.coordinate[0],
            "coordinate_y": self.coordinate[1],
            "coordinate_z": self.coordinate[2]
            }
        try:
            response = requests.post(
                ATM_ENDPOINT_URI,
                data=json.dumps(data),
                headers=CONTENT_HEADER,
            )
            #print(f"[info] результат отправки данных: {response}")
        except Exception as e:
            print(f'exception raised: {e}')

    def emergency(self):
        self.emergency_stop.set()
        self.motion_status = "Stopped"
        time.sleep(DELIVERY_INTERVAL_SEC)
        self.send_position()


@app.route("/set_command", methods=['POST'])
def set_command():
    global drones
    try:
        content = request.json
        print(f'[DRONE_DEBUG] received {content}')
        if content['command'] == 'initiate':
            tmp = Drone(content['coordinate'], content['name'], content['psswd'])
            drones.append(tmp)
            print (f"Added in point {tmp.coordinate}")
        else:
            
            drone = list(filter(lambda i: content['name'] == i.name, drones)) #was "in" istead of ""==""
            
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
    
   