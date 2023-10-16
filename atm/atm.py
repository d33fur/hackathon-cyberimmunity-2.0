import base64
import hashlib
import json
import os
import random
import subprocess
import time
from urllib.request import urlopen
import requests
from flask import Flask, request, jsonify
from uuid import uuid4
import threading

###
# import matplotlib.pyplot as plt
# #import matplotlib as mpl
# # import PyQt5
# # mpl.use('Qt5Agg')
# #mpl.use('Agg')
# import random
# import time
# import matplotlib.patches as mpatches
# import matplotlib.animation as animation



host_name = "0.0.0.0"
port = 6064

app = Flask(__name__)  # create an app instance


CONTENT_HEADER = {"Content-Type": "application/json"}
FPS_ENDPOINT_URI = "http://fps:6065/atm_input"
DRONE_ENDPOINT_URI = "http://drone:6066/set_command"
DRONE_EMERGENCY_ENDPOINT_URI = "http://drone:6066/emergency"
drones = []

###
ax = ''
items_z = []
plot_x= [] 
plot_y = [] 

###


class Drone:
    v_x = 0
    v_y = 0
    v_z = 0
    battery_charge = 100 
    #emergency_stop = threading.Event()
    token = ""
    drone_status = "Stopped"
    task_status = ""
    task_points = []

    def __init__(self, coordinate, name):
        self.coordinate = coordinate
        self.name = name
        
def draw_points(index, name, coordinate):
    global drones, ax, items_z, plot_x, plot_y
    # x = random.randint(0, 100)
    # y = random.randint(0, 20)
    # z = str(random.randint(0, 20))
    # name = names[random.randint(0,4)]
    items_z[index] = coordinate[0]
    plot_x[index] = coordinate[1]
    plot_y[index] = coordinate[2]

    colors = ["red","green","black","orange","purple","yellow","blue","grey"]
    patch = []
    for i in drones:
        patch[i] = mpatches.Patch(color=colors[i], label= name)
    ax.clear()
    for i in len(patch):
        if plot_x[i]!=0.1 and plot_y[i]!=0.1:
            ax.scatter(plot_x[i],plot_y[i], c=colors[i], s = abs(int(items_z[i]))*2)
    ax.legend(handles=patch, loc='upper right')
    plt.axhline(y=0, color='b', linestyle='-')
    plt.axvline(x=0, color='b', linestyle='-')
    plt.xlim(-2*max(abs(min(plot_x)), max(plot_x)), 2*max(abs(min(plot_x)), max(plot_x)))
    plt.ylim(-2*max(abs(min(plot_y)), max(plot_y)), 2*max(abs(min(plot_y)), max(plot_y)))
    plt.yscale("linear")
    plt.xscale("linear")
    plt.grid()

#получение данных на вход
@app.route("/data_in", methods=['POST'])
def data_in():
    content = request.json

    #print(f'[ATM_DEBUG] received {content}')  
    global drones, ax
    try:
        drone = list(filter(lambda i: content['name'] == i.name, drones)) #was "in" istead of ""==""
        if len(drone) > 1:
            print(f'[ATM_NEW_TASK] incorrect name: {content["name"]}')
            return "BAD NAME", 404

        drone = drone[0]
        drone.coordinate = content['coordinate']
        print(f"[ATM_DATA_IN] дрон {content['name']} находится по координатам {content['coordinate']}")

        ###
        # index = drones.index(drone)
        # fig = plt.figure()
        # ax = fig.add_subplot(1,1,1)
        # ani = animation.FuncAnimation(fig, draw_points(index, content['name'], content['coordinate']), interval=1000)
        # plt.show()
        #exec(open('matplot.py').read())
        
        import matplot
        matplot.show()
        ###


        
    except Exception as e:
        print(e)
        error_message = f"malformed request {request.data}"
        return error_message, 400
    return jsonify({"operation": "data_in", "status": True})


@app.route("/sign_up", methods=['POST'])
def sign_up():
    content = request.json
    print(f'[ATM_DEBUG] received {content}')
    global drones
    try:
        tmp = Drone(content['coordinate'], content['name'])
        drones.append(tmp)
        print(f"[ATM_SIGN_UP] зарегестрирован дрон: {content['name']} в точке {content['coordinate']}")
    except Exception as _:
        error_message = f"malformed request {request.data}"
        return error_message, 500
    return jsonify({"operation": "sign_up", "status": True})

@app.route("/sign_out", methods=['POST'])
def sign_out():
    content = request.json
    global drones
    try:
        drone = list(filter(lambda i: content['name'] == i.name, drones)) #was "in" istead of ""==""
        if len(drone) > 1:
            print(f'[ATM_NEW_TASK] incorrect name: {content["name"]}')
            return "BAD NAME", 404

        drone = drone[0]
        drones.remove(drone)
        print(f"[ATM_SIGN_OUT] удален дрон: {content['name']}")
    except Exception as _:
        error_message = f"malformed request {request.data}"
        return error_message, 500
    return jsonify({"operation": "sign_out", "status": True})

@app.route("/new_task", methods=['POST'])
def new_task():
    content = request.json
 
    global drones
    try:
        print(f'[ATM_DEBUG] received {content}')
        drone = list(filter(lambda i: content['name'] == i.name, drones)) #was "in" istead of ""==""
        if len(drone) > 1:
            print(f'[ATM_NEW_TASK] incorrect name: {content["name"]}')
            return "BAD NAME", 404

        drone = drone[0]
        if drone.drone_status != "Active":
            drone.drone_status = "Active" 
        else: 
            data = {
                "name": content['name'],
                "token": drone.token
            }
            requests.post(
                DRONE_EMERGENCY_ENDPOINT_URI,
                data=json.dumps(data),
                headers=CONTENT_HEADER,
            )

        print(f'[ATM_DEBUG] activated')

        #token = random.randint(1000,9999)
        tmp = ""
        for i in content["points"]:
            tmp.join(str(i))
        token = hashlib.md5()
        token.update(tmp.encode('utf-8'))
        drone.token = token.hexdigest()
        
        print(f'[ATM_DEBUG] token generated')

        data = {
            "name": content['name'],
            "command": "task_status_change",
            "task_status": "Accepted",
            "token": drone.token
        }
        requests.post(
            DRONE_ENDPOINT_URI,
            data=json.dumps(data),
            headers=CONTENT_HEADER,
        )
        print(f'[ATM_NEW_TASK] successfully created new task for drone {content["name"]}')
        
        time.sleep(2)

        data = {
            "name": content['name'],
            "points": content['points'],
            "task_status": "Accepted"
        }
        requests.post(
            FPS_ENDPOINT_URI,
            data=json.dumps(data),
            headers=CONTENT_HEADER,
        )
        
        
        print(f'[ATM_DEBUG] fps accepted')
        # else:
        #     print(f'[ATM_NEW_TASK] something went wrong during creating new task for drone {content["name"]}') 

    except Exception as _:
        error_message = f"malformed request {request.data}"
        return error_message, 400
    return jsonify({"operation": "new_task", "status": True})



if __name__ == "__main__":
    app.run(port=port, host=host_name)
    