# Keeron,Huang Lia,Li
# 26' ZJU-UIUC CompE
import random
from openpyxl import load_workbook
import math
import cmath
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

for Num in range(3,7):

    width = 700
    height = 700
    numBoids =100
    visualRange_bird = 75
    visualRange_eagle = 140
    touchRange_bird = 30
    catchrange = 10
    numberofcatch = 5
    maxspeed_eagle = 20
    minspeed_eagle = 10
    Acc=0

    boids={}
    ax = complex(1,1)
    ay = complex(1,1)
    global eagle
    eagle=[]
    x=0
    y=1
    dx=2
    dy=3
    history =4
    life = 10
    phi = 5 # phase for the wave function

    m = 0.398
    g = 9.81
    b = 0.549
    S = 0.0369
    p = 1.29
    omega = 1.08*(m**(1/3)*g**(1/2)*b**(-1)*S**(-1/4)*p**(-1/3))*2*math.pi # frequency of the wave function

    boidx=[]
    boidy=[] #if want to show the track of the bird
    eaglex=[]
    eagley=[]
    
    

    global scatter_boid,scatter_eagle
    count = 0
    global score
    score = 0
    point = 0
    loop_time = 0
    v = 0

    #initial plot
    fig = plt.figure(figsize=(8, 8))
    figax = fig.add_axes([0, 0, 1, 1], frameon=True)
    figax.set_xlim(-50, 1150), figax.set_xticks([])
    figax.set_ylim(-50, 1150), figax.set_yticks([])
    xtext_ani = plt.text(-40,1120,'',fontsize=12)

    def initBoids():
        for i in range (0,numBoids):
            boids[i] = {
                x : random.random() * (width-50)+50,
                y : random.random() * height,
                dx : random.random()*10-5,
                dy : random.random()*10-5,
                ax : complex(0,random.random()*10),
                ay : complex(0,random.random()*10),
                phi : random.random()*math.pi*2, # ranging from [0, pi*2)
                life : 10,
                history:[]}
        for boid in boids:
            boidx.append(boids[boid][x])
            boidy.append(boids[boid][y])
        return
    #Initialize Eagle structure
    def initEagle():
        eagle={ x:random.choice([0]), y:random.choice(range(25,height-25)), dx:random.random()*5 , dy:random.random()*5,
            history:[]}
        eaglex.append(eagle[x])
        eagley.append(eagle[y])
        return eagle

    def distance(boid1, boid2):
        return math.sqrt( (boid1[x] - boid2[x]) * (boid1[x] - boid2[x]) +(boid1[y] - boid2[y]) * (boid1[y] - boid2[y]))
    def distanceX(boid1,boid2):
        return (boid1[x]-boid2[x])
    def distanceY(boid1,boid2):
        return (boid1[y]-boid2[y])
    
    def TransToComplex(theta):
                    x = 1
                    y = complex(x*math.cos(theta),-x*math.sin(theta))
                    return y

                #Define the action function of interference behavior
    def acceleration(boid):
                    BoidsInRange = 0
                    wavelength = 340/20
                    boid[ax] = complex(0,0)
                    boid[ay] = complex(0,0)
                    phasechange(boid)
                    for i in range(0,numBoids):
                        if distance(boid,boids[i])<touchRange_bird:
                            cal_accleration(boid,i,wavelength)
                            BoidsInRange += 1

                    boid[ax] = (boid[ax]/BoidsInRange+TransToComplex(boid[phi]))/2
                    boid[ay] = (boid[ay]/BoidsInRange+TransToComplex(boid[phi]))/2
                    return

    def phasechange(boid):
            boid[phi] += omega
            boid[phi] = boid[phi] % 2 * math.pi
            return
        
    def cal_accleration(boid,i,wavelength):
                    # Calculating alpha between two birds.
                    diffy = boids[i][y]-boid[y]
                    diffx = boids[i][x]-boid[x]
                    zero = 0
                    delta = TransToComplex(((distance(boid,boids[i])/wavelength)*2*math.pi + boids[i][phi])% 2 * math.pi)
                    if diffy == zero and diffx > zero:
                        boid[ax] += -delta * coefficient(distance(boid,boids[i]))
                    elif diffy == zero and diffx < zero:
                        boid[ax] += +delta * coefficient(distance(boid,boids[i]))
                    elif diffx == zero and diffy > zero:
                        boid[ay] += -delta * coefficient(distance(boid,boids[i]))
                    elif diffx == zero and diffy < zero:
                        boid[ay] += +delta * coefficient(distance(boid,boids[i]))
                    elif diffx == zero and diffy == zero:
                        return
                    else:
                        alpha = math.atan(abs(diffy)/abs(diffx))
                        deltax = delta * math.cos(alpha)
                        deltay = delta * math.sin(alpha)
                        boid[ax] += coefficient(distance(boid,boids[i])) * deltax * (-abs(diffx)/diffx)
                        boid[ay] += coefficient(distance(boid,boids[i])) * deltay * (-abs(diffy)/diffy)
                    return
    
    def coefficient(r):
        #equation for exponential damping: e^(-t/torque)
        relative_dis = touchRange_bird
        coeffi = -(r-10)/relative_dis
        return (math.e**coeffi)**Acc

    #Defining the predation behavior of eagles
    def catchbird(eagle):
        catchFactor = 0.05
        min_dis_eagle = 0
        min_boid = 0
        for i in range(0,numBoids):
                if i==0:
                    min_dis_eagle = distance(boids[i],eagle)
                else:
                    if distance(boids[i],eagle)<min_dis_eagle:
                        min_dis_eagle = distance(boids[i],eagle)
                        min_boid = i
        interval = (maxspeed_eagle-minspeed_eagle)/(visualRange_eagle-catchrange)
        chasingcheck(boids[min_boid],eagle,maxspeed_eagle,catchrange,interval,catchFactor)
        return
    

    def chasingcheck(creature,eagle,speedlimit,min_dis,delta_change,factor):
            zero = 0
            v = 0
            global point
            diffy = creature[y]-eagle[y]
            diffx = creature[x]-eagle[x]
            if distance(creature,eagle) <= visualRange_eagle:
                v = (speedlimit - (distance(creature,eagle)- min_dis) * delta_change)
                if point == 0:
                    point = 1
            else:
                v = 10
                alpha = math.atan(abs(eagle[dx])/abs(eagle[dy]))
                deltax = v * math.cos(alpha)
                deltay = v * math.sin(alpha)
                eagle[dx] = deltax * (abs(eagle[dx])/eagle[dx])
                eagle[dy] = deltay * (abs(eagle[dy])/eagle[dy])
                return
            if v > speedlimit:
                v = speedlimit
            if diffy == zero and diffx > zero:
                eagle[dx] = v
                eagle[dy] = 0
            elif diffy == zero and diffx < zero:
                eagle[dx] = -v
                eagle[dy] = 0
            elif diffx == zero and diffy > zero:
                eagle[dy] = v
                eagle[dx] = 0
            elif diffx == zero and diffy < zero:
                eagle[dy] = -v
                eagle[dx] = 0
            elif diffx == zero and diffy == zero:
                return
            else:
                alpha = math.atan(abs(diffy)/abs(diffx))
                deltax = v * math.cos(alpha)
                deltay = v * math.sin(alpha)
                eagle[dx] = deltax * (abs(diffx)/diffx)
                eagle[dy] = deltay * (abs(diffy)/diffy)
            return
        

    def catchscore(eagle,boids):
        global catchrange
        flag = 0
        catchrange = 10
        for boid in boids:
            if distance(eagle,boids[boid]) < catchrange:
                boids[boid][life] -= 1
                if boids[boid][life] <= 0:
                    flag = 1
                    boids[boid][x] = -9999
                    boids[boid][y] = -9999
                    boids[boid][dx] = 0
                    boids[boid][dy] = 0
                    return flag
        return flag

    def keepWithinBounds(boid,turnFactor):
        margin=0
        if boid[x] < margin :
            boid[dx] += turnFactor
        if boid[x] > width - margin :
            boid[dx] -= turnFactor
        if boid[y] < margin: 
            boid[dy] += turnFactor  
        if boid[y] > height - margin :
            boid[dy] -= turnFactor
        return
    
    def avoideagle(boid,eagle):
        avoideagle_F = 0.2
        if distance(boid,eagle)<visualRange_bird:
            boid[dx] -= (eagle[x]-boid[x]) * avoideagle_F
            boid[dy] -= (eagle[y]-boid[y]) * avoideagle_F
        return

    def flyTowardsCenter(boid):
        centeringFactor = 0.005
        centerX=0
        centerY=0
        numNeighbors = 0
        for  i in boids:
            if boids[i] != boid: #"neighbor includes itself"
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

    def limitSpeed(boid,speedLimit):
        speed = math.sqrt(boid[dx]*boid[dx]+boid[dy]*boid[dy])
        if speed > speedLimit:
            boid[dx]=(boid[dx]/speed)*speedLimit
            boid[dy]=(boid[dy]/speed)*speedLimit
        return      
    
    initBoids()
    eagle = initEagle()

    scatter_boid = figax.scatter(boidx,boidy)  
    scatter_eagle = figax.scatter(eaglex,eagley,c='red') 



    def update(frame):
        global loop_time
        if point:
            loop_time += 1
        global count
        global boidp
        global boidq
        global score
        boidp=[]
        boidq=[]
        for i in range (0,numBoids):
            boid=boids[i]
            flyTowardsCenter(boid)
            avoidOthers(boid)
            matchVelocity(boid)
            avoideagle(boid,eagle)
            limitSpeed(boid,15)
            keepWithinBounds(boid,7)
            acceleration(boid)
            boid[x] += boid[dx]
            boid[y] += boid[dy]
            boid[dx] += Acc*abs(boid[ax])*abs(boid[ax])*math.ceil(Acc)
            boid[dy] += Acc*abs(boid[ay])*abs(boid[ay])*math.ceil(Acc)
            boidx=[]
            boidx.append(boid[x])
            boidy=[]
            boidy.append(boid[y])
            boidp.append([boid[x],boid[y]])
        catchbird(eagle)
        limitSpeed(eagle,maxspeed_eagle)
        keepWithinBounds(eagle,12)
        eagle[x] += eagle[dx]
        eagle[y] += eagle[dy]
        eaglex=[]
        eaglex.append(eagle[x])
        eagley=[]
        eagley.append(eagle[y])
        boidq.append([eagle[x],eagle[y]])

        xtext_ani.set_text('score={:}'.format(loop_time))
        count += catchscore(eagle,boids)
        if count == numberofcatch:
            plt.close()
        return boidp,boidx,boidy,boidq
        
    def animate(frame):
        update(frame)
        scatter_boid.set_offsets(boidp)
        scatter_eagle.set_offsets(boidq)
        return

    animation = FuncAnimation(fig, animate, interval=1)


    plt.show()