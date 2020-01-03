"""Module that provides planning tools to predict the drone flight path"""
import functools
from numpy import array, pi, sin, cos, arctan2
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D, proj3d
from matplotlib import animation
from matplotlib.patches import FancyArrowPatch

def rotate(angle, x, y):
    """Rotate the vector (x,y) by angle (radians)"""
    s = sin(angle)
    c = cos(angle)
    x2 = x * c - y * s
    y2 = x * s + y * c
    return x2, y2

def update_path(func):
    """Decorator for updating the Planner's path history"""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        self.update_path()
    return wrapper

class Planner:
    """Parses the commands that are sent to it, constructs a flight path,
and then displays it"""
    def __init__(self):
        self.command_history = []

        self.direction = array((0, 1, 0), dtype=float)
        self.position = array((0, 0, 0), dtype=float)
        self.directions = []
        self.positions = []
        self.update_path()

        self.commands = {
            'takeoff': self.takeoff,
            'up': self.up,
            'down': self.down,
            'left': self.left,
            'right': self.right,
            'forward': self.forward,
            'back': self.back,
            'cw': self.cw,
            'ccw': self.ccw,
            'go': self.go,
        }
                               

    def close(self):
        """Dummy interface for Network class"""
        pass

    def send(self, command):
        """Adds command to the history"""
        self.command_history.append(command)

    def recv(self):
        """Dummy interface for Network class"""
        pass

    def sendrecv(self, command):
        self.send(command)
        self.recv()

    def stop(self):
        """Fakes interface for Video class, but actually computes the path and
displays the results

        """
        self.compute_path()
        self.display_path()

    def compute_path(self):
        """Parse each of the commands in the history"""
        for command in self.command_history:
            self.parse_command(command)

    def parse_command(self, command):
        """Parse each command by dispatching to the correct function"""
        command, *args = command.split()
        args = [int(arg) for arg in args]
        if command in self.commands:
            self.commands[command](*args)

    @update_path
    def takeoff(self):
        self.up(50)

    @update_path
    def up(self, distance):
        self.position[2] += distance

    @update_path
    def down(self, distance):
        self.position[2] -= distance

    @update_path
    def left(self, distance):
        i, j = rotate(pi/2, self.direction[0], self.direction[1])
        self.position += distance * array((i, j, 0))

    @update_path
    def right(self, distance):
        i, j = rotate(-pi/2, self.direction[0], self.direction[1])
        self.position += distance * array((i, j, 0))

    @update_path
    def forward(self, distance):
        self.position += distance * self.direction

    @update_path
    def back(self, distance):
        self.position -= distance * self.direction

    @update_path
    def cw(self, angle):
        radians = pi*angle/180
        i, j = rotate(-radians, self.direction[0], self.direction[1])
        self.direction[0], self.direction[1] = i, j
        
    @update_path
    def ccw(self, angle):
        radians = pi*angle/180
        i, j = rotate(radians, self.direction[0], self.direction[1])
        self.direction[0], self.direction[1] = i, j

    @update_path
    def go(self, x, y, z, speed):
        angle = arctan2(-self.direction[0], self.direction[1])
        i, j = rotate(angle, x, y)
        self.position += array((i, j, z))

    def display_path(self):
        fig = plt.figure()
        ax = Axes3D(fig)
        xs, ys, zs = zip(*self.positions)
        line, = ax.plot(xs, ys, zs)
        x, y, z = self.positions[-1]
        arrow_length = 50
        arrow_width = 2
        arrow_head_size = 15
        i, j, k = self.direction * arrow_length
        arrow = Arrow3D((x, x+i), (y, y+j), (z, z+k),
                        lw=arrow_width, mutation_scale=arrow_head_size,
                        arrowstyle='-|>', color='r')
        ax.add_artist(arrow)

        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')

        # plot on equal axes
        p = array(self.positions).flatten()
        m = 1.2*max(-p.min(), p.max())
        ax.set_xlim(-m, m)
        ax.set_ylim(-m, m)
        ax.set_zlim(0, 2*m)

        plt.show()
        
    def update_path(self):
        self.directions.append(self.direction.copy())
        self.positions.append(self.position.copy())
                


class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0,0), (0,0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
        FancyArrowPatch.draw(self, renderer)
