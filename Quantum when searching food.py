import random
from openpyxl import load_workbook
import math
import cmath
import numpy as np
import matplotlib.pyplot as plt
#import pyglet as pg
from matplotlib.animation import FuncAnimation

for Num in range(2,52):

    width = 400
    height = 400
    numBoids =100
    visualRange_bird = 75
    touchRange_bird = 20
    Char = "A"
    boids={}
    ax = complex(0,1)
    ay = complex(0,1)
    x=0
    y=1
    dx=2
    dy=3
    history =4
    phix = 5 # phase for the wave function
    phiy = 6
    m = 0.398
    g = 9.81
    b = 0.549
    S = 0.0369
    p = 1.29
    omega = 1.08*(m**(1/3)*g**(1/2)*b**(-1)*S**(-1/4)*p**(-1/3))*2*math.pi # frequency of the wave function
    boidx=[]
    boidy=[] #if want to show the track of the bird
    Acc=0.05

    X_target = -200
    Y_target = -200

    global scatter_boid
    count = 0

    loop_time = 0
    totaltime = 0

    workbook = load_workbook(filename="Modified Quantum(1).xlsx")
    sheet = workbook.active

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
                ax : complex(0,random.random()*10),
                ay : complex(0,random.random()*10),
                phix : random.random()*math.pi*2, # ranging from [0, pi*2)
                phiy : random.random()*math.pi*2, # ranging from [0, pi*2)
                history:[]}
        for boid in boids:
            boidx.append(boids[boid][x])
            boidy.append(boids[boid][y])
        return
    #Define Euclidean distance
    def distance(boid1, boid2):
        return math.sqrt( (boid1[x] - boid2[x]) * (boid1[x] - boid2[x]) +(boid1[y] - boid2[y]) * (boid1[y] - boid2[y]))
    def distanceX(boid1,boid2):
        return (boid2[x]-boid1[x])
    def distanceY(boid1,boid2):
        return (boid2[y]-boid1[y])

    def TransToComplex(x,theta):
        y = complex(x*np.cos(theta),-x*np.sin(theta))
        return y

    #Define the action function of interference behavior
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
        cofact = 0.8 # reduce the influency of other birds on phi
        boid[phix] += omega*0.035 + cofact*((distanceX(boid,boids[i])/wave)*2*math.pi + boids[i][phix])
        boid[phiy] += omega*0.035 + cofact*((distanceX(boid,boids[i])/wave)*2*math.pi + boids[i][phiy])
        boid[phix] = boid[phix] % 2 * math.pi
        boid[phiy] = boid[phiy] % 2 * math.pi
        return

    #Keep the Boids inside the window
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
        centeringFactor = 0.01
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
        avoidFactor = 0.05
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
    #Defining the foraging behavior of boids
    def attraction(boid,x_target,y_target):
        attractingfactor = 0.05
        a=[x_target,y_target]
        moveX = 0
        moveY = 0
        if distance(boid,a)<visualRange_bird: #attract
            moveX += -boid[x] + a[x]
            moveY += -boid[y] + a[y]
        boid[dx] += moveX * attractingfactor
        boid[dy] += moveY * attractingfactor 

    def limitSpeed(boid):
        speedLimit=15
        speed = math.sqrt(boid[dx]*boid[dx]+boid[dy]*boid[dy])
        if speed > speedLimit:
            boid[dx]=(boid[dx]/speed)*speedLimit
            boid[dy]=(boid[dy]/speed)*speedLimit
        return      

    def numNearFood(boids):
        flag = 0
        num = 0
        global X_target
        global Y_target
        for i in range(0,numBoids):
            distance = math.sqrt( (boids[i][x] - X_target) * (boids[i][x] - X_target) +(boids[i][y] - Y_target) * (boids[i][y] - Y_target))
            if distance <= 25:
                num += 1
                if num >= 10:
                    flag = 1
                    break
        return flag
    
    initBoids()
    global scatter
    scatter_boid = figax.scatter(boidx,boidy)
    flag = 0

    def update(frame):
        global boidp
        global loop_time
        global flag
        global point
        global totaltime
        if point:
            loop_time += 1
        else:
            totaltime += 0.035
            if totaltime >= 5:
                mouse_move()
        boidp=[]
        boidp.append([X_target,Y_target])
        for i in boids:
            boid=boids[i]
            flyTowardsCenter(boid)
            avoidOthers(boid)
            matchVelocity(boid)
            limitSpeed(boid)
            keepWithinBounds(boid)
            attraction(boid,X_target,Y_target)
            acceleration(boid)
            boid[x] += boid[dx]
            boid[y] += boid[dy]
            boid[dx] += Acc*abs(boid[ax])*abs(boid[ax])
            boid[dy] += Acc*abs(boid[ay])*abs(boid[ay])
            boidx=[]
            boidx.append(boid[x])
            boidy=[]
            boidy.append(boid[y])
            boidp.append([boid[x],boid[y]])

        flag += numNearFood(boids)
        if flag == 1 :
            #print(loop_time)
            sheet[Char+str(Num)] = loop_time
            workbook.save(filename="Modified Quantum(1).xlsx")
            plt.close()

        return boidp,boidx,boidy
        
    def animate(frame):
        update(frame)
        scatter_boid.set_offsets(boidp)
        return

    point = 0
    #def mouse_move(ev):
        #global X_target
        #global Y_target
        #global point
        #X_target = ev.xdata
        #Y_target = ev.ydata
        #point = 1

    def mouse_move():
        global X_target
        global Y_target
        global point
        X_target = 200
        Y_target = 200
        point = 1

        figax.scatter(X_target,Y_target,c='pink')
        # scatter_target
        
    #def plotFood(ev):
        #timer = fig.canvas.new_timer(interval=2000)
        #timer.add_callback(mouse_move)
        #fig.canvas.mpl_disconnect(cid)

    # Create a new timer object. Set the interval to 2000 milliseconds
    # (1000 is default) and tell the timer what function should be called.

    #fig.canvas.mpl_disconnect(fig.canvas.mpl_connect('draw_event', mouse_move))

    #timer = fig.canvas.new_timer(interval=0)
    #timer.add_callback(mouse_move)

    #def timing():
        #if point == 0:
            #global totaltime
            #totaltime += 0.035
            #if totaltime == 5:
                #mouse_move()
        #timer = threading.Timer(2000, mouse_move)
        #timer.add_callback(fig.canvas.mpl_connect('draw_event', mouse_move))
        #cid = fig.canvas.mpl_connect('draw_event', mouse_move)

    animation = FuncAnimation(fig, animate, interval=35)





    plt.show()