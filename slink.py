import matplotlib.pyplot as plt
from os import system

#remove the previous run
system("rm step*")

class slinky(object):

    #constants
    #Number of turns in the slinky
    __N = 20
    __l1 = 1.0
    #Spring constant
    __k = 1.0
    #grav constant
    __g = 1.0
    #turn mass element
    __m = 1.0
    #dimless COP
    __tornado = 1.0
    #describes the y positions of all turns which aren't fully collapsed
    __slin = []
    #describes the distances between collapsed turns
    __collapsed = []
    __topcolT = 0
    __bottomcolT = 0
    __yrange = []
    __comy0 = 0.0
    __hl = 3.0
    __hw = 0.025
    __scale = 1.0
    
    def __init__(self, _N, _l1, _k, _g, _m):
        #set constants
        self.__N = _N
        self.__l1 = _l1
        self.__k = _k
        self.__g = _g
        self.__m = _m
        self.__tornado = _k/(_m*_g)
        #start at the bottom, as it works down the slinky will find the correct value. Describes the turn below which all turns are collapsed from t = 0
        self.__bottomcolT = _N

        #start the top turn at y = 0.0
        self.__slin.append(0.0)
        for i in range(1,self.__N):
            #impose balanced forces at each turn to initialise turn positions
            dy = float(self.__N - i)/float(self.__tornado)
            #if the extension required to balance gravity is gt the minimum extension use that
            if dy > self.__l1:
                nt = self.__slin[-1] - dy
                self.__collapsed.append(False)
            #otherwise set the turn as collapsed
            else:
                nt = False
                self.__collapsed.append(self.__l1)
                if (i-1) < self.__bottomcolT:
                    self.__bottomcolT = (i-1)
            self.__slin.append(nt)
    
        #calculate the graph yrange and the initial com position
        self.__yrange = [self.gety(self.__N-1)*1.2,self.gety(self.__N-1)*-0.1]
        self.__comy0 = self.com()

    #method to return the correct y position of any turn, collapsed or not
    def gety(self,i):
        y = False
        #if it is not collapsed above and below its position is dictated by the slinky array
        if(i >= self.__topcolT) and (i <= self.__bottomcolT):
            y = self.__slin[i]
        #if the turn is in the top collapsed section, work backwards from the first independantly know y position through the collapsed array
        elif(i < self.__topcolT):
            y = self.__slin[self.__topcolT]
            ctr = self.__topcolT
            while (ctr > i):
                ctr -= 1
                y += self.__collapsed[ctr]
        #if it is in the bottom collapsed section work down from the last independantly known y position
        elif(i > self.__bottomcolT):
            y = self.__slin[self.__bottomcolT]
            ctr = self.__bottomcolT
            #print "bottom",i, y, ctr
            while (ctr < i):
                y -= self.__collapsed[ctr]
                ctr += 1
        return y
        
    #build and return an array containing the y positions of each turn
    def yarray(self):
        ya = []
        for i in range(self.__N):
            ya.append(self.gety(i))
        return ya

    #get the overall tension working on a given turn
    def ten(self,i):
        ten = 0.0
        #ten from turn above
        if(i != 0) and (self.__collapsed[i-1] == False):
            ten += (self.__k/self.__m)*(self.gety(i-1) - self.gety(i))
        #ten from turn below
        if(i != (self.__N - 1)) and (self.__collapsed[i] == False):
            ten += (self.__k/self.__m)*(self.gety(i+1) - self.gety(i))
        return ten
    
    #get the overall acceleration on a turn, actually the
    def accel(self,i):
        f = self.ten(i)
        a = 0.0
        #if the turn isn't collapsed above and isn't collapsed below(
        if(self.__collapsed[i-1] == False) and ( (i == len(self.__collapsed)) or (self.__collapsed[i] == False) ):
            f -= self.__m*self.__g
            a = f/self.__m
        #if the turn is the reference turn for the top collapsed section, include mg and inertial mass for all turns above
        elif(i == self.__topcolT):
            f -= self.__m*self.__g*(self.__topcolT + 1)
            a = f/(self.__m*(self.__topcolT + 1))
        #if the turn is the reference turn for the bottom collapsed section, include mg and inertial mass for all turns below
        elif(i == self.__bottomcolT):
            f -= self.__m*self.__g*(self.__N - self.__bottomcolT)
            a = f/((self.__N -1 - self.__bottomcolT)*self.__m)
        return a

    #central difference integrator
    def adv(self, ylast, dt):
        ynext = []
        #current y positions
        old = self.yarray()
        
        #integrate to get prospective new turn positions
        for i in range(self.__N):
            next = 2.0*self.gety(i) - ylast[i] + dt*dt*self.accel(i)
            ynext.append(next)
        
        #ensure momentum conservation and assign positions
        for i in range(self.__N - 1):
            #only need to handle turns that were not in the collapsed section before this step
            if( i >= self.__topcolT ) and ( i < self.__bottomcolT ):
                #if this step collapses a ring then ensure that momentum is conserved
                if((ynext[i] - ynext[i+1]) < self.__l1):
                
                    #if this is not the last turn to collapse(top and bottom collapsed sections meet)
                    if(i+1 != self.__bottomcolT):
                        mmtBefore = 0.0
                        #the collapse will always happen on the current reference turn, add the momenta of all the turns up to the reference turn
                        for j in range(self.__topcolT + 2):
                            mmtBefore += (ynext[j] - old[j])/dt
                        #ensure that the position of the new reference turn is such that when the momentum of the top section including the new reference turn there has been no momentum change over the 'collision'
                        ynext[i+1] = mmtBefore*dt/(i+2) + old[i+1]
                    else:
                    #if this is the last turn to collapse ensure that the new reference turn for the whole slinky is in a position such that the momentum of the whole slinky is conserved
                        mmtBefore = 0.0
                        for j in range(self.__N):
                            mmtBefore += (ynext[j] - old[j])/dt
                        ynext[i+1] = mmtBefore*dt/(self.__N) + old[i+1]
                
                    #add the new collapsed distance to the collapsed array
                    #TODO:Could make it so that all collapses go to l1 and include the distance change in the momentum conservation
                    self.__collapsed[i] = (ynext[i] - ynext[i+1])
                    #increament the top collapsed section reference turn
                    self.__topcolT = (i+1)
                    #set the old references turn's independant y position to false
                    self.__slin[i] = False
                
                    
                else:
                #if it is just an uncollapsed turn that is still uncollapsed set it's new position
                    self.__slin[i] = ynext[i]
            elif(i == self.__bottomcolT):
                #the reference turn for the bottom collapsed section can just 
                self.__slin[self.__bottomcolT] = ynext[self.__bottomcolT]
        
        #return the old position array to use in the next step
        return old

    #calculate momentum of the system, mainly for debugging
    def mmt(self, ylast,dt):
        tm = 0.0
        yc = self.yarray()
        for i in range(self.__N):
            tm += self.__m*(yc[i] - ylast[i])/dt
        return tm

    #get the center of mass of the slinky system
    def com(self):
        sum = 0.0
        for i in range(self.__N):
            sum += self.__m*self.gety(i)
        return (sum/(self.__m*self.__N))

    #plot out the current position of each turn 
    def printSlinky(self, name, t):
        ypos = []
        for i in range(self.__N):
            ypos.append(self.gety(i))
            if(i%1 == 0) and (i < self.__bottomcolT) and ( i >= self.__topcolT):
                self.drawForce(i)
        plt.plot([1.0]*len(ypos), ypos, 'b_')
        plt.plot([1.0], self.com(), 'r+')
        plt.plot([1.0,2.0], [-1.0*self.__g*t*t/2.0 + self.__comy0]*2, 'g-')
        plt.plot([2.0], [-1.0*self.__g*t*t/2.0 + self.__comy0], 'g+')
        if(self.__topcolT != (self.__bottomcolT)):
            plt.text(0.5,self.gety(self.__topcolT),"GravF")
            plt.text(0.79, self.__yrange[1]*0.4 + self.gety(self.__topcolT), "TenF")
            plt.text(1.25,+ self.gety(self.__topcolT),"TotalF")
        plt.text(2.1, -1.0*self.__g*t*t/2.0 + self.__comy0 ,"Ref. Part.")
        plt.ylim(self.__yrange)
        plt.xlim([0,3.0])
        plt.savefig(name)
        plt.close()
        
    #draw force arrows
    def drawForce(self, i):
        plt.arrow(0.8,self.gety(i),0,-1.0*self.__m*self.__g*self.__scale,shape='full', lw=1, length_includes_head=True, head_width=self.__hw,head_length=self.__hl)
        if(self.accel(i) != 0.0):
            plt.arrow(1.2,self.gety(i),0,self.accel(i)*self.__m*self.__scale,shape='full', lw=1, length_includes_head=True, head_width=self.__hw,head_length=self.__hl, color='red')
        if(self.ten(i) != 0.0):
            plt.arrow(0.9,self.gety(i),0,self.ten(i)*self.__scale,shape='full', lw=1, length_includes_head=True, head_width=self.__hw,head_length=self.__hl,color='green')
        

N = 20
l1 = 1
dt = 0.001
endt = 20.0
imgs = 200
m = 1.0
k = 1.0
g = 5.0
t = dt
imgEvery = (endt/(dt*imgs))
ctr = 0
imgctr = 1000


sl = slinky(N, l1,k,g,m)
last = sl.yarray()

while t < endt :
    #take a step
    last = sl.adv(last,dt)
    
    if (ctr%imgEvery) == 0:
        print "img at t = ", t
        sl.printSlinky('step'+str(imgctr)+'.gif',t)
        imgctr += 1
    ctr += 1
    t += dt


exit()

