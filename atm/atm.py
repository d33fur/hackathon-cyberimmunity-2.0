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

##
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('TkAgg')
# import PyQt5
# mpl.use('Qt5Agg')
#mpl.use('Agg')
import random
import time
import matplotlib.patches as mpatches
import matplotlib.animation as animation



host_name = "0.0.0.0"
port = 6064

app = Flask(__name__)  # create an app instance


CONTENT_HEADER = {"Content-Type": "application/json"}
FPS_ENDPOINT_URI = "http://fps:6065/atm_input"
DRONE_ENDPOINT_URI = "http://drone:6066/set_command"
DRONE_EMERGENCY_ENDPOINT_URI = "http://drone:6066/emergency"
drones = []
area = []

###
ax = ''
items_z = [0] * 5
plot_x= [0] * 5 
plot_y = [0] * 5 

###


class Drone:
    battery_charge = 100 
    #emergency_stop = threading.Event()
    token = ""
    drone_status = "Stopped"
    task_status = ""
    task_points = []

    def __init__(self, coordinate, name, port, index):
        self.coordinate = coordinate
        self.name = name
        self.endpoint = "http://drone" + str(index) +":" + str(port) + "/set_command"
        self.emergency = "http://drone" + str(index) +":" + str(port) + "/emergency"
        
#def draw_points(index, name, coordinate):
def draw_points(i):
    
    global drones, ax, items_z, plot_x, plot_y


    ###
    
    data = open('/storage/coordinates', 'r').read()
    #lines = data.split('\n')
     
    coordinate = [0,0,0]
    #for line in lines:
    index,name,coordinate[0],coordinate[1],coordinate[2] = data.split(',')
    index = int(index)
    coordinate[0] = int(coordinate[0])
    coordinate[1] = int(coordinate[1])
    coordinate[2] = int(coordinate[2])
    print(index,name,coordinate)
    ###
    
    # x = random.randint(0, 100)
    # y = random.randint(0, 20)
    # z = str(random.randint(0, 20))
    # name = names[random.randint(0,4)]
    
    items_z[index] = coordinate[2]
    plot_x[index] = coordinate[0]
    plot_y[index] = coordinate[1]
    
    colors = ["red","green","black","orange","purple","yellow","blue","grey"]
    patch = [''] * 5
    for i in range(len(drones)):
        patch[i] = mpatches.Patch(color=colors[i], label = name + ': ' + str(items_z[i]))
    for i in range(len(drones), 5 - len(drones) + 1):
        patch[i] = mpatches.Patch(color=colors[i], label = '')
    
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
    
    #return ax

#получение данных на вход
@app.route("/data_in", methods=['POST'])
def data_in():
    content = request.json

    #print(f'[ATM_DEBUG] received {content}')  
    global drones, ax, area
    try:
        drone = list(filter(lambda i: content['name'] == i.name, drones)) #was "in" istead of ""==""
        if len(drone) > 1:
            print(f'[ATM_NEW_TASK] incorrect name: {content["name"]}')
            return "BAD NAME", 404

        drone = drone[0]
        drone.coordinate = content['coordinate']
        print(f"[ATM_DATA_IN] дрон {content['name']} находится по координатам {content['coordinate']}")

        index = drones.index(drone)
        x = int(content['coordinate'][0])
        y = int(content['coordinate'][1])
        with open("/storage/coordinates", "w") as f:
            f.write(str(index) + ',' + str(content['name']) + ',' + str(x )+ ',' + str(y) + ',' + str(content['coordinate'][2]))

        if x < area[0] or x > area [2] or y < area [1] or y > area[3]:
            print(f"[ATM_DATA_IN] дрон {content['name']} находится outside of area!")
            data = {
                    "name": drone.name,
                    "token": drone.token
                }
            requests.post(
                    drone.emergency,
                    data=json.dumps(data),
                    headers=CONTENT_HEADER,
                )


        #draw_points(1)
        #draw()

        #draw_points(index, content['name'], content['coordinate'])
        ###
        # index = drones.index(drone)
        # fig = plt.figure()
        # ax = fig.add_subplot(1,1,1)
        # print(f'[ATM_DEBUG] 9')
        # ani = animation.FuncAnimation(fig, draw_points(index, content['name'], content['coordinate']), interval=1000, save_count=100)
        # print(f'[ATM_DEBUG] 10')
        # plt.show()
        # print(f'[ATM_DEBUG] 11')
        # writer = animation.PillowWriter(fps=15,
        #                         metadata=dict(artist='Me'),
        #                         bitrate=1800)
        # ani.save('scatter.gif', writer=writer)

        
    
        
        
        ### POC
        # import matplot
        # matplot.show()
        ###


        
    except Exception as e:
        print(e)
        error_message = f"malformed request {request.data}"
        return error_message, 400
    return jsonify({"operation": "data_in", "status": True})

@app.route("/set_area", methods=['POST'])
def set_area():
    content = request.json
    print(f'[ATM_DEBUG] received {content}')
    global area
    try:
        area = content['area']
        print(f"[ATM_SET_AREA] area coordinates from: ({area[0]};{area[1]}) to ({area[2]};{area[3]})")
    except Exception as _:
        error_message = f"malformed request {request.data}"
        return error_message, 500
    return jsonify({"operation": "sign_up", "status": True})


@app.route("/sign_up", methods=['POST'])
def sign_up():
    content = request.json
    print(f'[ATM_DEBUG] received {content}')
    global drones
    try:
        tmp = Drone(content['coordinate'], content['name'], content['port'], content['index'])
        drones.append(tmp)
        print(f"[ATM_SIGN_UP] зарегестрирован дрон: {content['name']} в точке {content['coordinate']} at port {content['port']}")
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
                drone.emergency,
                data=json.dumps(data),
                headers=CONTENT_HEADER,
            )

        #print(f'[ATM_DEBUG] activated')

        #token = random.randint(1000,9999)
        tmp = ""
        for i in content["points"]:
            tmp.join(str(i))
        token = hashlib.md5()
        token.update(tmp.encode('utf-8'))
        drone.token = token.hexdigest()
        
        #print(f'[ATM_DEBUG] token generated')

        data = {
            "name": content['name'],
            "command": "task_status_change",
            "task_status": "Accepted",
            "token": drone.token
        }
        requests.post(
            drone.endpoint,
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
        
        
        #print(f'[ATM_DEBUG] fps accepted')
        # else:
        #     print(f'[ATM_NEW_TASK] something went wrong during creating new task for drone {content["name"]}') 

    except Exception as _:
        error_message = f"malformed request {request.data}"
        return error_message, 400
    return jsonify({"operation": "new_task", "status": True})


def draw2():
    try:
        fig = plt.figure()

        ax = ['']*5
        plot_x = ['']*5
        plot_y = ['']*5
        for i in range(5):
            ax[i] = fig.add_subplot(2,3,i+1)
            plot_x[i] = []
            plot_y[i] = []
        items_z = [''] *5
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
            for i in range(len(drones)):
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
    except Exception as e:
        print(e)
        print('AAA')

def draw():
    global ax
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    names = [''] * 5
    
    def draw_points(i):        
        global drones, ax, items_z, plot_x, plot_y

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
        patch = [''] * 5
        for i in range(len(drones), 5):
            patch[i] = mpatches.Patch(color=colors[i], label = ' ')
       
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
        


    #threading.Thread(target = lambda: animation.FuncAnimation(fig, draw_points, interval=1000, save_count=100)).start()
    ani = animation.FuncAnimation(fig, draw_points, interval=1000, save_count=10000)
    plt.show()
    writer = animation.PillowWriter(fps=15,
                            metadata=dict(artist='Me'),
                            bitrate=1800)
    ani.save('scatter.gif', writer=writer)
    

if __name__ == "__main__":
    threading.Thread(
                    target=lambda:  draw()).start()
    threading.Thread(
                    target=lambda:  draw2()).start()
    
    app.run(port=port, host=host_name)
