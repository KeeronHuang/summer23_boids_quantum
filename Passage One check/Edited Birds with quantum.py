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
boids={}
ax = complex(1,1)
ay = complex(1,1)
global eagle
eagle=[]
x=0
y=1
dx=2
dy=3
history = 4
phix = 5 # phase for the wave function
phiy = 6
omega = math.pi # frequency of the wave function
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
            dy : random.random()*10-5,
            ax : complex(random.random()*10,random.random()*10),
            ay : complex(random.random()*10,random.random()*10),
            phix : random.random()*math.pi*2, # ranging from [0, pi*2)
            phiy : random.random()*math.pi*2, # ranging from [0, pi*2)
            history:[]}
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

def TransToComplex(x,phi):
    phi = phi % 2 * math.pi
    y = complex(x*math.cos(phi),-x*math.sin(phi))
    return y

def acceleration(boid):
    BoidsInRange = 0
    wave = 340/20
    axTotal = complex(0,0)
    ayTotal = complex(0,0)
    for i in range(0,numBoids):
        if distance(boid,boids[i])<touchRange_bird:
            phasechange(boid,wave,i)
            axTotal += TransToComplex(Acc,boid[phix])
            ayTotal += TransToComplex(Acc,boid[phiy])
            BoidsInRange += 1

    boid[ax] = axTotal/BoidsInRange
    boid[ay] = ayTotal/BoidsInRange
    return

def phasechange(boid,wave,i):
    cofact = 1 # reduce the influency of other birds on phi
    boid[phix] += omega*0.035 + cofact*((distanceX(boid,boids[i])/wave)*2*math.pi + boids[i][phix])
    boid[phiy] += omega*0.035 + cofact*((distanceX(boid,boids[i])/wave)*2*math.pi + boids[i][phiy])
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

animation = FuncAnimation(fig, animate, interval=35)


plt.show()