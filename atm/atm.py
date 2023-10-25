import hashlib
import json
import random
import time
from urllib.request import urlopen
import requests
from flask import Flask, request, jsonify
from uuid import uuid4
import threading

##
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('TkAgg')
import time
import matplotlib.patches as mpatches
import matplotlib.animation as animation



host_name = "0.0.0.0"
port = 6064

app = Flask(__name__)  # create an app instance


CONTENT_HEADER = {"Content-Type": "application/json"}
FPS_ENDPOINT_URI = "http://fps:6065/atm_input"
# DRONE_ENDPOINT_URI = "http://drone:6066/set_command"
# DRONE_EMERGENCY_ENDPOINT_URI = "http://drone:6066/emergency"
drones = []
area = []

###
# ax = ''
# items_z = [0] * 5
# plot_x= [0] * 5 
# plot_y = [0] * 5 
###


class Drone:
    # battery_charge = 100 
    # token = ""
    # drone_status = "Stopped"
    # task_status = ""
    # task_points = []

    def __init__(self, coordinate, name, port, index):
        self.coordinate = coordinate
        self.name = name
        self.endpoint = "http://drone" + str(index) +":" + str(port) + "/set_command"
        self.emergency = "http://drone" + str(index) +":" + str(port) + "/emergency"
        self.token = ''
        self.drone_status = "Stopped"
        # self.battery_charge = 100
        

def testing_retranslate(content):
    requests.post(
            "http://172.17.0.1:6062/",
            data=json.dumps(content),
            headers=CONTENT_HEADER,
    )


#получение данных на вход
@app.route("/data_in", methods=['POST'])
def data_in():
    content = request.json

    #print(f'[ATM_DEBUG] received {content}')  
    global drones, area#, ax
    try:
        drone = list(filter(lambda i: content['name'] == i.name, drones))
        if len(drone) > 1:
            print('[ATM_DATA_IN_ERROR]')
            print(f'Nonunique name: {content["name"]}')
            return "BAD ITEM NAME", 404

        drone = drone[0]
        drone.coordinate = content['coordinate']
        print(f"[ATM_DATA_IN] {content['name']} located in: {content['coordinate']}")

        index = drones.index(drone)
        x = int(content['coordinate'][0])
        y = int(content['coordinate'][1])
        with open("/storage/coordinates", "w") as f:
            f.write(str(index) + ',' + str(content['name']) + ',' + str(x )+ ',' + str(y) + ',' + str(content['coordinate'][2]))

        if len(area) > 0:
            if x < area[0] or x > area [2] or y < area [1] or y > area[3]:
                print(f"[ATM_LOCATION_ERROR]")
                print(f"{content['name']} is outside of area!")
                data = {
                        "name": drone.name,
                        "token": drone.token
                    }
                requests.post(
                        drone.emergency,
                        data=json.dumps(data),
                        headers=CONTENT_HEADER,
                    )
        testing_retranslate(content)

    except Exception as e:
        print(e)
        error_message = f"malformed request {request.data}"
        return error_message, 500
    return jsonify({"operation": "data_in", "status": True})

@app.route("/set_area", methods=['POST'])
def set_area():
    content = request.json
    # print(f'[ATM_DEBUG] received {content}')
    global area
    try:
        area = content['area']
        print(f"[ATM_SET_AREA]")
        print(f"Area coordinates: from ({area[0]};{area[1]}) to ({area[2]};{area[3]})")
    except Exception as _:
        error_message = f"malformed request {request.data}"
        return error_message, 500
    return jsonify({"operation": "set_area", "status": True})


@app.route("/sign_up", methods=['POST'])
def sign_up():
    content = request.json
    # print(f'[ATM_DEBUG] received {content}')
    global drones
    try:
        drone = Drone(content['coordinate'], content['name'], content['port'], content['index'])
        drones.append(drone)
        
        
        drone.token = random.randint(1000,9999)
        
        #print(f'[ATM_DEBUG] token generated')

        #todo
        data = {
            "name": content['name'],
            "command": "set_token",
            "token": drone.token
        }

        requests.post(
            drone.endpoint,
            data=json.dumps(data),
            headers=CONTENT_HEADER,
        )
        
        print(f"[ATM_SIGN_UP]")
        print(f"Drone signed up: {content['name']} in point {content['coordinate']} at port {content['port']}")

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
            print(f'[ATM_SIGN_OUT_ERROR]')
            print(f'Nonunique name: {content["name"]}')
            return "BAD ITEM NAME", 400

        drone = drone[0]
        drones.remove(drone)
        print(f"[ATM_SIGN_OUT]")
        print(f"Deleted drone: {content['name']}")
    except Exception as _:
        error_message = f"malformed request {request.data}"
        return error_message, 500
    return jsonify({"operation": "sign_out", "status": True})

@app.route("/new_task", methods=['POST'])
def new_task():
    content = request.json
 
    global drones
    try:
        # print(f'[ATM_DEBUG] received {content}')
        drone = list(filter(lambda i: content['name'] == i.name, drones)) #was "in" istead of ""==""
        if len(drone) > 1:
            print(f'[ATM_NEW_TASK_ERROR]')
            print(f'Nonunique name: {content["name"]}')
            return "BAD ITEM NAME", 400

        drone = drone[0]
        if drone.drone_status != "Active":
            drone.drone_status = "Active" 
        else: 
            data = {
                "name": content['name'],
                "token": drone.token
            }
            requests.post(
                drone.emergency,
                data=json.dumps(data),
                headers=CONTENT_HEADER,
            )
        

        tmp = ""
        for i in content["points"]:
            tmp.join(str(i))
        hash = hashlib.md5()
        hash.update(tmp.encode('utf-8'))
        hash = hash.hexdigest()
        data = {
            "name": content['name'],
            "command": "task_status_change",
            "task_status": "Accepted",
            "token": drone.token,
            "hash": hash
        }
        requests.post(
            drone.endpoint,
            data=json.dumps(data),
            headers=CONTENT_HEADER,
        )

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
        

    except Exception as _:
        error_message = f"malformed request {request.data}"
        return error_message, 400
    return jsonify({"operation": "new_task", "status": True})


def draw2():
    fig = plt.figure()

    ax = [''] * 5
    plot_x = [''] * 5
    plot_y = [''] * 5
    for i in range(5):
        ax[i] = fig.add_subplot(2,3,i+1)
        plot_x[i] = []
        plot_y[i] = []
    items_z = [''] * 5
    names = [''] * 5


    def animate(i):
        data = ''
        with open('/storage/coordinates', 'r') as f:
            data = f.readline()

        index,name,x,y,z = data.split(',')
        x = int(x)
        y = int(y)
        z = str(z)
        index = int(index)
        ###
        
        items_z[index] = z
        # plot_x[index] = x
        # plot_y[index] = y
        names[index] = name
        colors = ["red","green","black","orange","purple","yellow","blue","grey"]
        patch = [''] * 5


        for j in range(len(drones)):
            ax[j].axhline(y = 0, color = 'b', linestyle = '-')
            ax[j].axvline(x = 0, color = 'b', linestyle = '-')

        #for i in range(len(drones)):
        for i in range(5):
            patch[i] = mpatches.Patch(color=colors[i], label = ' ')
        patch[index] = mpatches.Patch(color =colors[index], label = names[index] + ': ' + str(items_z[index]))
        ax[index].legend(handles = [patch[index]], loc = "upper right")
        ax[index].scatter(x,y, c = colors[index], s = abs(int(z)))
        plot_x[index].append(x)
        plot_y[index].append(y)

        for j in range(len(drones)):
            ax[j].set_title(names[j])
            ax[j].plot(plot_x[j],plot_y[j], color = colors[j])

    ani = animation.FuncAnimation(fig, animate, interval=1000, save_count=1000)
    plt.show()
    writer = animation.PillowWriter(fps=15,
                            metadata=dict(artist='Me'),
                            bitrate=1800)
    ani.save('scatter.gif', writer=writer)

def draw():
    #global ax
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    names = [''] * 5
    items_z = [0] * 5
    plot_x= [0] * 5 
    plot_y = [0] * 5 
    
    def draw_points(i):
 
        global drones#, ax , items_z, plot_x, plot_y

        data = ''
        with open('/storage/coordinates', 'r') as f:
            data = f.readline()
        
        index,name,x,y,z = data.split(',')
        x = int(x)
        y = int(y)
        z = str(z)
        index = int(index)
        ###
        
        items_z[index] = z
        plot_x[index] = x
        plot_y[index] = y
        names[index] = name
        
        colors = ["red","green","black","orange","purple","yellow","blue","grey"]
        patch = [''] * len(drones)
        # for i in range(len(drones), 5):
        #     patch[i] = mpatches.Patch(color=colors[i], label = ' ')
    
        for i in range(len(drones)):
            patch[i] = mpatches.Patch(color=colors[i], label = names[i] + ': ' + str(items_z[i]))
        
        ax.clear()
        for i in range(len(patch)):
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
        
    ani = animation.FuncAnimation(fig, draw_points, interval=1000, save_count=1000)
    plt.show()
    writer = animation.PillowWriter(fps=15,
                            metadata=dict(artist='Me'),
                            bitrate=1800)
    ani.save('scatter.gif', writer=writer)
    

if __name__ == "__main__":
    # threading.Thread(
    #                 target=lambda:  draw()).start()
    threading.Thread(
                    target=lambda:  draw2()).start()
   
    
    app.run(port=port, host=host_name)
