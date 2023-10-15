import matplotlib.pyplot as plt
import matplotlib as mpl
import random
import time
import matplotlib.patches as mpatches
import matplotlib.animation as animation

fig = plt.figure()
ax0 = fig.add_subplot(2,3,1)
ax1 = fig.add_subplot(2,3,2)
ax2 = fig.add_subplot(2,3,3)
ax3 = fig.add_subplot(2,3,4)
ax4 = fig.add_subplot(2,3,5)
items_z = ['']*5
names = []
plot_x0 = []
plot_x1 = []
plot_x2 = []
plot_x3 = []
plot_x4 = []
plot_y0 = []
plot_y1 = []
plot_y2 = []
plot_y3 = []
plot_y4 = []
for i in range(5):
    names.append('item' + str(i))

def animate(i):
    x = random.randint(0, 100)
    y = random.randint(0, 20)
    z = str(random.randint(0, 20))
    item_name = names[random.randint(0,4)]
    items_z[int(item_name[-1])] = z
    colors = ["red","green","black","orange","purple"]
    ax0.axhline(y=0, color='b', linestyle='-')
    ax0.axvline(x=0, color='b', linestyle='-')
    ax1.axhline(y=0, color='b', linestyle='-')
    ax1.axvline(x=0, color='b', linestyle='-')
    ax2.axhline(y=0, color='b', linestyle='-')
    ax2.axvline(x=0, color='b', linestyle='-')
    ax3.axhline(y=0, color='b', linestyle='-')
    ax3.axvline(x=0, color='b', linestyle='-')
    ax4.axhline(y=0, color='b', linestyle='-')
    ax4.axvline(x=0, color='b', linestyle='-')
    if item_name[-1]=='0':
        patch_0 = mpatches.Patch(color=colors[0], label='item0: ' + items_z[0])
        ax0.legend(handles=[patch_0], loc="upper right")
        ax0.scatter(x,y, c=colors[int(item_name[-1])], s = abs(int(z)))
        plot_x0.append(x)
        plot_y0.append(y)
    elif item_name[-1]=='1':
        patch_1 = mpatches.Patch(color=colors[1], label='item1: ' + items_z[1])
        ax1.legend(handles=[patch_1], loc="upper right")
        ax1.scatter(x,y, c=colors[int(item_name[-1])], s = abs(int(z)))
        plot_x1.append(x)
        plot_y1.append(y)
    elif item_name[-1]=='2':
        patch_2 = mpatches.Patch(color=colors[2], label='item2: ' + items_z[2])
        ax2.legend(handles=[patch_2], loc="upper right")
        ax2.scatter(x,y, c=colors[int(item_name[-1])], s = abs(int(z)))
        plot_x2.append(x)
        plot_y2.append(y)
    elif item_name[-1]=='3':
        patch_3 = mpatches.Patch(color=colors[3], label='item3: ' + items_z[3])
        ax3.legend(handles=[patch_3], loc="upper right")
        ax3.scatter(x,y, c=colors[int(item_name[-1])], s = abs(int(z)))
        plot_x3.append(x)
        plot_y3.append(y)
    elif item_name[-1]=='4':
        patch_4 = mpatches.Patch(color=colors[4], label='item4: ' + items_z[4])
        ax4.legend(handles=[patch_4], loc="upper right")
        ax4.scatter(x,y, c=colors[int(item_name[-1])], s = abs(int(z)))
        plot_x4.append(x)
        plot_y4.append(y)
    ax0.set_title("item0")
    ax1.set_title("item1")
    ax2.set_title("item2")
    ax3.set_title("item3")
    ax4.set_title("item4")
    ax0.plot(plot_x0, plot_y0, color = colors[0])
    ax1.plot(plot_x1, plot_y1, color = colors[1])
    ax2.plot(plot_x2, plot_y2, color = colors[2])
    ax3.plot(plot_x3, plot_y3, color = colors[3])
    ax4.plot(plot_x4, plot_y4, color = colors[4])
    plt.tight_layout(h_pad=2)

ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()
