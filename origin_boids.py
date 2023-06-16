class boids():
    #Initialize bird flock structure
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

    #Define the action function of aggregation behavior
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

    #Define the action function of separation behavior
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

    #Define the action function of alignment behavior
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

    #Define Euclidean distance
    def distance(boid1, boid2):
        return math.sqrt( (boid1[x] - boid2[x]) * (boid1[x] - boid2[x]) +(boid1[y] - boid2[y]) * (boid1[y] - boid2[y]))
    def distanceX(boid1,boid2):
        return (boid2[x]-boid1[x])
    def distanceY(boid1,boid2):
        return (boid2[y]-boid1[y])

    #Define the action function of interference behavior
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

    #Initialize Eagle structure
    def initEagle():
        eagle={ x:0, y:0, dx:random.random()*15-5 , dy:random.random()*15-5,
            history:[]}
        eaglex.append(eagle[x])
        eagley.append(eagle[y])
        return eagle

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

    #Defining the avoiding eagle behavior of boids
    def avoideagle(boid,eagle):
        avoideagle_F = 0.1
        if distance(boid,eagle)<visualRange_bird:
            boid[dx] -= (eagle[x]-boid[x]) * avoideagle_F
            boid[dy] -= (eagle[y]-boid[y]) * avoideagle_F
        return

    #Updating the location coordinates of boids and eagle
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
        if loop_time == 500:
            print('score={:.2%}'.format(score))
        return boidp,boidx,boidy,boidq