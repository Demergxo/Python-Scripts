# -*- coding: utf-8 -*-

# see write-up at www.ttested.com/coding-up-christmas/ for more detail

from random import uniform

import matplotlib.animation as ani
import matplotlib.colors as col
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

fig = plt.figure(figsize=(8, 12))
ax = Axes3D(fig, elev=-10, azim=0)
ax.set_axis_off()
ax.set_facecolor('black')

t = np.arange(0, 200, .6)

params = {
    'cl': [1, .45, 1, .45],  # base colour
    'ps': [15, 15, 5, 5],  # point size
    'sg': [-1, 1, 1, -1],  # sign - starting point of curve
    'hf': [1, 1, 4, 4],  # hue frequency
    'dp': [0, 0, .2, .2],  # drop - offset points in negative z direction
    'fg': [True, True, False, False]  # flag - add second curve if true
}

# map frame and parameter to scalar
m = np.vectorize(lambda t_, f_: t_ ** .6 - f_)


def generate_frame_data(fr=0):
    """Generate the locations, point sizes, and colours for a given frame.
    Returns five numpy arrays giving the x, y, z coordinates of each point
    as well as their size and colour. The arrays are sorted so that the points
    closest to the 'camera' are first in the array."""
    x = []
    y = []
    z = []
    s = []
    c = []

    for cl, ps, sg, hf, dp, fg in zip(*list(params.values())):
        sv = m(t, fr)
        base_x = -sg * sv * np.sin(sv)
        base_y = sg * sv * np.cos(sv)
        base_z = -(dp + sv)
        x.append(base_x)
        y.append(base_y)
        z.append(base_z)
        s.append(np.repeat(ps, len(t)))
        c.append(col.hsv_to_rgb([(h, 1, v) for h, v in
                                 zip(cl * (1 + np.sin(.02 * t)) / 2,
                                     .3 + sg * .3 * np.sin(hf * sv))]))
        if fg:
            x_off = []
            y_off = []
            z_off = []
            # matrix for rotating theta degrees about a 3D vector
            # see: computergraphics.stackexchange.com/questions/2399/
            for v in sv:
                C = np.array([
                    [0, 0, np.sin(v)],
                    [0, 0, np.cos(v)],
                    [-np.sin(v), -np.cos(v), 0]
                ])
                R = np.identity(3) + C * np.sin(20 * v) + np.matmul(C, C) * (
                            1 - np.cos(20 * v))
                T = np.matmul(R,np.transpose(np.array([np.sin(v), np.cos(v), 0])))
                x_off.append(T[0])
                y_off.append(T[1])
                z_off.append(T[2])
            x.append(base_x + .5 * np.array(x_off))
            y.append(base_y + .5 * np.array(y_off))
            z.append(base_z + .5 * np.array(z_off))
            s.append(np.array([uniform(0, ps) for __ in range(len(t))]))
            c.append(col.hsv_to_rgb([(h, 1, v) for h, v in
                                     zip(cl * (1 + np.sin(.1 * t)) / 2,
                                         .6 + sg * .4 * np.sin(hf * sv))]))

    x = np.concatenate(x)
    y = np.concatenate(y)
    z = np.concatenate(z)
    s = np.concatenate(s)
    c = np.concatenate(c)

    in_range = (-20 < x) & (x < 20) & (-20 < y) & (y < 20) & (-20 < z) & (z < 0)

    x = x[in_range]
    y = y[in_range]
    z = z[in_range]
    s = s[in_range]
    c = c[in_range]

    y = y[np.argsort(-x)]
    z = z[np.argsort(-x)]
    s = s[np.argsort(-x)]
    c = c[np.argsort(-x)]
    x = x[np.argsort(-x)]

    return x, y, z, s, c


# initial plot layout
x, y, z, s, c = generate_frame_data()
scat = ax.scatter(x, y, z, s=s, c=c, depthshade=False)

def animate(frame_num):
    """Update the figure with a new frame."""
    fr = frame_num / 250

    x, y, z, s, c = generate_frame_data(fr)

    # update plot
    scat._offsets3d = (x, y, z)
    scat._facecolor3d = c
    scat._edgecolor3d = c
    scat.set_sizes(s)


# animation driver
anim = ani.FuncAnimation(fig, animate, interval=1000/30, frames=1000)
#plt.show()
# output animation
#Writer = ani.writers['ffmpeg']
#writer = Writer(fps=60, metadata=dict(artist='Mer'), bitrate=6000)

#anim.save('christmas_tree.mp4', writer=writer)
anim.save('xmas_tree.gif', writer='Pillow')