# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 23:03:37 2021

@author: 17264
"""
import random
from openpyxl import load_workbook
import math
import cmath
import numpy as np
import matplotlib.pyplot as plt
#import pyglet as pg
from matplotlib.animation import FuncAnimation

for Num in range(3,33):

    width = 500
    height = 500
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
    history =4
    attract_or_repulse=1  #set the meaning of mouseclick.0 is attract,1 is repulse
    #x_target,y_target=0,0
    boidx=[]
    boidy=[] #if want to show the track of the bird
    eaglex=[]
    eagley=[]
    Char = "J"
    Acc=0.1

    global scatter_boid,scatter_eagle
    global loop_time
    loop_time = 0
    #global count            #表示捕获成功的次数
    count = 0
    global score
    score = 0

    #initial plot
    fig = plt.figure(figsize=(8, 8))
    figax = fig.add_axes([0, 0, 1, 1], frameon=True)
    figax.set_xlim(-50, 550), figax.set_xticks([])
    figax.set_ylim(-50, 550), figax.set_yticks([])
    #显示捕获次数
    xtext_ani = plt.text(-40,520,'',fontsize=12)


    def initBoids():
        for i in range (0,numBoids):
            boids[i] = {
                x : random.random() * width,
                y : random.random() * height,
                dx : random.random()*10-5,
                dy : random.random()*10-5,
                ax : complex(random.random()*10,random.random()*10),
                ay : complex(random.random()*10,random.random()*10),
                history:[]}
        for boid in boids:
            boidx.append(boids[boid][x])
            boidy.append(boids[boid][y])
        return
    #Initialize Eagle structure
    def initEagle():
        eagle={ x:random.choice([0,500]), y:random.choice([0,500]), dx:random.random()*15-5 , dy:random.random()*15-5,
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

    def TransToComplex(x,theta):
        phi = theta / 360 * 2 * math.pi
        y = complex(x*math.cos(phi),x*math.sin(-phi))
        return y

    def acceleration(boid):
        BoidsInRange = 0
        wave = 340/20
        axTotal = complex(0,0)
        ayTotal = complex(0,0)
        for i in range(0,numBoids):
            if distance(boid,boids[i])<touchRange_bird:
                dx = distanceX(boid,boids[i])
                dy = distanceY(boid,boids[i])
                axTotal += TransToComplex(1,dx/wave)
                ayTotal += TransToComplex(1,dy/wave)
                BoidsInRange += 1

        boid[ax] = axTotal/BoidsInRange
        boid[ay] = ayTotal/BoidsInRange
        return
    #Defining the predation behavior of eagles
    def catchbird(eagle):
        catchFactor = 0.3
        min_dis_eagle = 0 
        min_boid = 0
        for i in range(0,numBoids):
            if i==0:
                min_dis_eagle = distance(boids[i],eagle)
            else:
                if distance(boids[i],eagle)<min_dis_eagle:
                    min_dis_eagle = distance(boids[i],eagle)
                    min_boid = i
        eagle[dx] = (boids[min_boid][x] - eagle[x]) * catchFactor
        eagle[dy] = (boids[min_boid][y] - eagle[y]) * catchFactor
        return

    def catchscore(eagle,boids):
        flag = 0                #表示捕捉成功：只要catchrange内有鸟就算成功
        catchrange = 10
        for boid in boids:
            if distance(eagle,boids[boid]) < catchrange:
                flag = 1
                break
        return flag

    def keepWithinBounds(boid):
        margin=0
        turnFactor = 10
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
        matchingFactor = 0.1
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

    def avoideagle(boid,eagle):
        avoideagle_F = 0.1
        if distance(boid,eagle)<visualRange_bird:
            boid[dx] -= (eagle[x]-boid[x]) * avoideagle_F
            boid[dy] -= (eagle[y]-boid[y]) * avoideagle_F

        return

    def limitSpeed(boid):
        speedLimit=15
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
        loop_time += 1
        global count
        global boidp
        global boidq
        global score
        boidp=[]
        boidq=[]
        #boidp.append([x_target,y_target])
        for i in range (0,numBoids):
            boid=boids[i]
            flyTowardsCenter(boid)
            avoidOthers(boid)
            matchVelocity(boid)
            avoideagle(boid,eagle)
            limitSpeed(boid)
            keepWithinBounds(boid)
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
        catchbird(eagle)
        keepWithinBounds(eagle)
        eagle[x] += eagle[dx]
        eagle[y] += eagle[dy]
        eaglex=[]
        eaglex.append(eagle[x])
        eagley=[]
        eagley.append(eagle[y])
        boidq.append([eagle[x],eagle[y]])

        count += catchscore(eagle,boids)
        score = count/loop_time
        xtext_ani.set_text('score={:.2%}'.format(score))
        return boidp,boidx,boidy,boidq
        
    def animate(frame):
        update(frame)
        scatter_boid.set_offsets(boidp)
        scatter_eagle.set_offsets(boidq)
        return

    animation = FuncAnimation(fig, animate, interval=5)


    plt.show()