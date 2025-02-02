import os
import sys

positions = []
input_lst = sys.argv[1]
output_dir = sys.argv[2]

try: 
    with open(input_lst, 'r') as file:
        for line in file:
            X,Y = line.strip().split(',')
            positions.append((int(X), int(Y)))
except IOError:
    print('File with coordinates does not exist')
positions.sort()


from matplotlib import pyplot as plt, patches
plt.rcParams["figure.figsize"] = [12, 10]
plt.rcParams["figure.autolayout"] = True
fig = plt.figure()
ax = fig.add_subplot(111)
rect = patches.Rectangle((0, 0), max(list(map(lambda x: x[0], positions)))+4,4+ max(list(map(lambda x: x[1], positions))), color='yellow')
ax.add_patch(rect)
#step = 0

for position in positions:
    #text = str(position[0] + position[1]+step) #CHECK
    #ax.text(position[0]+2, position[1]+2, text, ha="center", va="center", zorder=2, fontsize=6)
    circle = patches.Circle((position[0]+2, position[1]+2), radius=0.5, color='red')
    ax.add_patch(circle)
    #step += 1


plt.axis('equal')
ax.set_title(os.path.basename(input_lst).replace('.lst', ''))
plt.show()

fig.savefig(os.path.join(output_dir, os.path.basename(input_lst).replace('.lst', '.svg')))