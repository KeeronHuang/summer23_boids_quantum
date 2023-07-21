import random
from openpyxl import load_workbook
import math
#import cmath
#import numpy as np
#import matplotlib.pyplot as plt
#import pyglet as pg
#from matplotlib.animation import FuncAnimation


for Acc in [0,0.01,0.02,0.03,0.04]:
    for Char in ["A","B","C"]:
        Char = chr(ord(Char) + int((round(Acc / 0.01)) * 3))
        for Num in range(3,23):

            foodrange = 30
            foodtime = 600
            attractingfactor = 0.1

            width = 500
            height = 500
            numBoids =100
            visualRange_bird = 75
            touchRange_bird = 30
            boids={}
            #a = complex(0,1)
            ax = complex(0,1)
            ay = complex(0,1)
            x=0
            y=1
            dx=2
            dy=3
            history =4
            phi = 5 # phase for the wave function
            m = 0.398
            g = 9.81
            b = 0.549
            S = 0.0369
            p = 1.29
            omega = 1.08*(m**(1/3)*g**(1/2)*b**(-1)*S**(-1/4)*p**(-1/3))*2*math.pi # frequency of the wave function
            boidx=[]
            boidy=[] #if want to show the track of the bird

            X_target = -200
            Y_target = -200

            global scatter_boid
            count = 0

            loop_time = 0
            totaltime = 0
            alpha = 0
            counter = 0
            #num_max = 0
            num = 0

            check = 0
            frame = 0

            workbook = load_workbook(filename="searching_food_new.xlsx")
            sheet = workbook.active

            #fig = plt.figure(figsize=(8, 8))
            #figax = fig.add_axes([0, 0, 1, 1], frameon=True)
            #figax.set_xlim(-50, 550), figax.set_xticks([])
            #figax.set_ylim(-50, 550), figax.set_yticks([])

            def initBoids():
                for i in range (0,numBoids):
                    boids[i] = {
                        x : random.random() * width,
                        y : random.random() * height,
                        dx : random.random()*10-5,
                        dy : random.random()*10-5,
                        #a : complex(0,random.random()*10),
                        ax : complex(0,random.random()*10),
                        ay : complex(0,random.random()*10),
                        phi : random.random()*math.pi*2, # ranging from [0, pi*2)
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

            def TransToComplex(theta):
                y = complex(math.cos(theta),-math.sin(theta))
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
                    boid[ax] += coefficient(distance(boid,boids[i]))*deltax * (-abs(diffx)/diffx)
                    boid[ay] += coefficient(distance(boid,boids[i]))*deltay * (-abs(diffy)/diffy)
                return
            
            def coefficient(r):
                #equation for exponential damping: e^(-t/torque)
                relative_dis = touchRange_bird
                coeffi = -(r-relative_dis/2)/relative_dis
                return (math.e**coeffi)**Acc

            #Keep the Boids inside the window
            def keepWithinBounds(boid):
                margin=0
                turnFactor = 7
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
                #flag = 0
                #num = 0
                global X_target
                global Y_target
                global point
                #global num_max
                global flag
                global num
                for i in range(0,numBoids):
                    distance = math.sqrt( (boids[i][x] - X_target) * (boids[i][x] - X_target) +(boids[i][y] - Y_target) * (boids[i][y] - Y_target))
                    if distance <= foodrange:
                        num += 1
                        if num == 1:
                            point = 1
                        #if num >= 6:
                            #flag = 1
                            #return flag
                if num > foodtime:
                    flag = 1
                return flag
            
            initBoids()
            global scatter
            #scatter_boid = figax.scatter(boidx,boidy)
            flag = 0

            def update(frame):
                global boidp
                global loop_time
                global flag
                global point
                global totaltime
                global counter
                global check
                if point:
                    loop_time += 1
                    #counter += 0.001
                    #if counter > 3 and counter < 3.04:
                        #flag = 1
                else:
                    totaltime += 0.001
                    if totaltime > 0.150 and totaltime < 0.151:
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
                    print(Char+str(Num))
                    sheet[Char+str(Num)] = loop_time
                    workbook.save(filename="searching_food_new.xlsx")
                    workbook.close()
                    check = 1
                    #plt.close()

                return boidp,boidx,boidy
                
            def animate(frame):
                update(frame)
                #scatter_boid.set_offsets(boidp)
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
                #global point
                X_target = random.choice(range(int(width/2-50),int(width/2+50)))
                Y_target = random.choice(range(int(height/2-50),int(height/2+50)))
                #point = 1

                #figax.scatter(X_target,Y_target,c='pink')
                # scatter_target


            while check != 1:
                animate(frame)
            #animation = FuncAnimation(fig,animate, interval=1)
            if check == 1:
                continue

            #plt.show()