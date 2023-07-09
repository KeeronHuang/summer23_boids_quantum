import random
import math
import cmath
import numpy as np
import matplotlib.pyplot as plt
#import pyglet as pg
from matplotlib.animation import FuncAnimation

width = 400
height = 400
numBoids =100
visualRange_bird = 75
visualRange_eagle = 70
touchRange_bird = 20
zero = 0
boids={}
ax = complex(1,1)
ay = complex(1,1)
omiga = 6 #add the part for initial random phase
gamma = 270/360 * 2 * math.pi #add the part for angle of vision
alpha = 6 #add arctan for the angle of speed
beta = 6 #add arctan for the angle between two individuals
global eagle
eagle=[]
x=0
y=1
dx=2
dy=3
history =4
boidx=[]
boidy=[] #if want to show the track of the bird
Acc=0.1

global scatter_boid
count = 0

fig = plt.figure(figsize=(8, 8))
figax = fig.add_axes([0, 0, 1, 1], frameon=True)
figax.set_xlim(-50, 450), figax.set_xticks([])
figax.set_ylim(-50, 450), figax.set_yticks([])

def initBoids():
    for i in range (0,numBoids):
        boids[i] = {
            x : random.random() * width,
            y : random.random() * height,
            dx : random.random()*10-5,
            dy : random.random()*10-5, # Ranging from [-5,5)
            ax : complex(random.random()*10,random.random()*10),
            ay : complex(random.random()*10,random.random()*10), # Ranging from [0,10+10i)
            omiga : random.random()*2*math.pi, # Ranging from [0,2*pi)
            history :[]}
    
        boid = boids[i]
        if boid[dy] == zero and boid[dx] > zero:
            boid[alpha] = 0
        elif boid[dy] == zero and boid[dx] < zero:
            boid[alpha] = math.pi
        elif boid[dx] == zero and boid[dy] > zero:
            boid[alpha] = math.pi / 2
        elif boid[dx] == zero and boid[dy] < zero:
            boid[alpha] = 3 * math.pi / 2
        elif boid[dx] == zero and boid[dy] == zero:
            boid[alpha] = np.random.uniform(0,2*math.pi)
        elif boid[dy] > zero:
            boid[alpha] = math.atan(boid[dy]/boid[dx])
        else:
            boid[alpha] = math.atan(boid[dy]/boid[dx])+ math.pi
    # Ranging from [0,2pi)

    for boid in boids:
        boidx.append(boids[boid][x])
        boidy.append(boids[boid][y])
    return

def distance(boid1, boid2):
    return math.sqrt( (boid1[x] - boid2[x]) * (boid1[x] - boid2[x]) +(boid1[y] - boid2[y]) * (boid1[y] - boid2[y]))
def distanceX(boid1,boid2):
    return (boid1[x]-boid2[x])
def distanceY(boid1,boid2):
    return (boid1[y]-boid2[y])

def TransToComplex(x,theta,boid):
    phi = theta / 360 * 2 * math.pi + boid[omiga]
    y = complex(x*math.cos(phi),-x*math.sin(phi))
    return y

def acceleration(boid):
    BoidsInRange = 1
    wave = 20/340
    axTotal = complex(0,0)
    ayTotal = complex(0,0)
    for i in range(0,numBoids):
        if distance(boid,boids[i])<touchRange_bird:
            if visionrange(boid,i):
                dx = distanceX(boid,boids[i])
                dy = distanceY(boid,boids[i])
                axTotal += TransToComplex(Acc,dx/wave,boid)
                ayTotal += TransToComplex(Acc,dy/wave,boid) # modified equation for theta
                BoidsInRange += 1

    boid[ax] = axTotal/BoidsInRange
    boid[ay] = ayTotal/BoidsInRange
    return

def keepWithinBounds(boid):
    margin=0
    turnFactor = 5
    if boid[x] < margin :
      boid[dx] += turnFactor
    if boid[x] > width - margin :
      boid[dx] -= turnFactor
    if boid[y] < margin: 
      boid[dy] += turnFactor
    if boid[y] > height - margin :
      boid[dy] -= turnFactor
    
    return

def flyTowardsCenter(boid):
    centeringFactor = 0.005
    centerX=0
    centerY=0
    numNeighbors = 0
    for  i in boids:
        if boids[i] != boid: #"neighbor 包括了他自己"
            if distance(boid,boids[i]) < visualRange_bird:
                if visionrange(boid,i):
                    centerX += boids[i][x]
                    centerY += boids[i][y]
                    numNeighbors += 1
    if numNeighbors:
        centerX = centerX / numNeighbors
        centerY = centerY / numNeighbors

        boid[dx] += (centerX - boid[x]) * centeringFactor
        boid[dy] += (centerY - boid[y]) * centeringFactor

def avoidOthers(boid):
    minDistance = 20
    avoidFactor = 0.2
    moveX = 0
    moveY = 0
    for  i in boids:
        if boids[i] != boid:
            if distance(boid,boids[i])< minDistance:
                if visionrange(boid,i):
                    moveX += boid[x] - boids[i][x]
                    moveY += boid[y] - boids[i][y]
    boid[dx] += moveX * avoidFactor
    boid[dy] += moveY * avoidFactor
    return

def matchVelocity(boid):
    matchingFactor = 0.05
    avgDX=0
    avgDY=0
    numNeighbors=0
    for i in boids:
        if distance(boid,boids[i])< visualRange_bird:
            if visionrange(boid,i):
                avgDX += boids[i][dx]
                avgDY += boids[i][dy]
                numNeighbors+=1
    if numNeighbors :
        avgDX = avgDX/ numNeighbors
        avgDY = avgDY/ numNeighbors
        boid[dx]+=(avgDX-boid[dx])*matchingFactor
        boid[dy]+=(avgDY-boid[dy])*matchingFactor
    return

def limitSpeed(boid):
    speedLimit=15
    speed = math.sqrt(boid[dx]*boid[dx]+boid[dy]*boid[dy])
    if speed > speedLimit:
        boid[dx]=(boid[dx]/speed)*speedLimit
        boid[dy]=(boid[dy]/speed)*speedLimit
    return      
  
initBoids()

scatter_boid = figax.scatter(boidx,boidy)

def update(frame):
    global boidp
    boidp=[]
    #boidp.append([x_target,y_target])
    for i in boids:
        boid=boids[i]
        flyTowardsCenter(boid)
        avoidOthers(boid)
        matchVelocity(boid)
        limitSpeed(boid)
        keepWithinBounds(boid)
        acceleration(boid)
        boid[x] += boid[dx]
        boid[y] += boid[dy]
        boid[dx] += boid[ax].real
        boid[dy] += boid[ay].real
        boidx=[]
        boidx.append(boid[x])
        boidy=[]
        boidy.append(boid[y])
        boidp.append([boid[x],boid[y]])
    return boidp,boidx,boidy
    
def animate(frame):
    update(frame)
    scatter_boid.set_offsets(boidp)
    return

# check if the individual is in the vision range.
def visionrange(boid,i):
    # Calculating beta for each bird.
    #beta = math.atan((boids[i][y]-boid[y])/(boids[i][x]-boid[x]))
    zero = 0
    diffy = boids[i][y]-boid[y]
    diffx = boids[i][x]-boid[x]
    if diffy == zero and diffx > zero:
        beta = 0
    elif diffy == zero and diffx < zero:
        beta = math.pi
    elif diffx == zero and diffy > zero:
        beta = math.pi / 2
    elif diffx == zero and diffy < zero:
        beta = 3 * math.pi / 2
    elif diffx == zero and diffy == zero:
        beta = np.random.uniform(0,2*math.pi)
    elif diffx > zero:
        beta = math.atan(diffy/diffx)
    else:
        beta = math.atan(diffy/diffx)+ math.pi
    # Judging if beta is in the range of vision. 
    if (beta <= (boid[alpha]+gamma/2) % 2*math.pi) or (beta >= (boid[alpha]-gamma/2+2*math.pi) % 2*math.pi):
        return True


animation = FuncAnimation(fig, animate, interval=20)


plt.show()

# first initialize w and make it as a random phi [0,2*math.pi]
# the relative difference would stay the same, but the difference would influce the accleration calculation(equation for theta)

# Initialize the w
# w : random.uniform(0,2*math.pi)

# Modification of the equation for theta
# theta = dx/wave + boid[w]

# 最好还是可以想出一个法则让相对的boid[w]发生一些变化
# key: in the process of operations under all principles, the relative difference between boid[w] would change according to some factors,
# our job is to find out the factors related to quantum dynamics and figure out its algorithm.

# Another job, figure out elimination for more efficient algorithm.