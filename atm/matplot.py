import matplotlib.pyplot as plt
#import matplotlib as mpl
#mpl.use('TkAgg')
#mpl.use('Agg')
# import PyQt5
# mpl.use('Qt5Agg')
import random
import matplotlib.patches as mpatches
import matplotlib.animation as animation

def show():
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    items_z = [""] * 5
    plot_x = [0.1]*5
    plot_y = [0.1]*5
    names = []


    for i in range(5):
        names.append('item' + str(i))

    def animate(i):
        x = random.randint(0, 100)
        y = random.randint(0, 20)
        z = str(random.randint(0, 20))
        item_names = names[random.randint(0,4)]
        items_z[int(item_names[-1])] = z
        plot_x[int(item_names[-1])] = x
        plot_y[int(item_names[-1])] = y
        colors = ["red","green","black","orange","purple"]
        patch_0 = mpatches.Patch(color=colors[0], label='item0: ' + items_z[0])
        patch_1 = mpatches.Patch(color=colors[1], label='item1: ' + items_z[1])
        patch_2 = mpatches.Patch(color=colors[2], label='item2: ' + items_z[2])
        patch_3 = mpatches.Patch(color=colors[3], label='item3: ' + items_z[3])
        patch_4 = mpatches.Patch(color=colors[4], label='item4: ' + items_z[4])
        ax.clear()
        if plot_x[0]!=0.1 and plot_y[0]!=0.1:
            ax.scatter(plot_x[0],plot_y[0], c=colors[0], s = abs(int(items_z[0]))*2)
        if plot_x[1]!=0.1 and plot_y[1]!=0.1:
            ax.scatter(plot_x[1],plot_y[1], c=colors[1], s = abs(int(items_z[1]))*2)
        if plot_x[2]!=0.1 and plot_y[2]!=0.1:
            ax.scatter(plot_x[2],plot_y[2], c=colors[2], s = abs(int(items_z[2]))*2)
        if plot_x[3]!=0.1 and plot_y[3]!=0.1:
            ax.scatter(plot_x[3],plot_y[3], c=colors[3], s = abs(int(items_z[3])*2))
        if plot_x[4]!=0.1 and plot_y[4]!=0.1:
            ax.scatter(plot_x[4],plot_y[4], c=colors[4], s = abs(int(items_z[4]))*2)
        ax.legend(handles=[patch_0, patch_1, patch_2, patch_3, patch_4], loc='upper right')
        plt.axhline(y=0, color='b', linestyle='-')
        plt.axvline(x=0, color='b', linestyle='-')
        plt.xlim(-2*max(abs(min(plot_x)), max(plot_x)), 2*max(abs(min(plot_x)), max(plot_x)))
        plt.ylim(-2*max(abs(min(plot_y)), max(plot_y)), 2*max(abs(min(plot_y)), max(plot_y)))
        plt.yscale("linear")
        plt.xscale("linear")
        plt.grid()


    ani = animation.FuncAnimation(fig, animate, interval=1000, save_count=100)
    plt.show()
