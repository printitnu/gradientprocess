import obplib as obp
import random

## Welcome, this code generated a gradient point and spot melting in 4 cubes. Please consider that the code is written by a guy with materials background and not coding :)

## PARAMETERS SUPPORT LAYERS
numberOfSupportLayers = 20
supportLineOffset = 3000
supportPower = 1200
supportBeamSpeed = 150_000
supportSpotSize = 280


## PARAMETERS INITIAL LAYERS
numberOfInitialLayers = 20 # 42 ~3mm at 0.7um layers
initialLayersPower = 1200
initialSpotSize = 280
initialBeamSpeed = 150_000


##Contour parameters (currently only one line-melt contour)
contourBeamPower = 1200
contourBeamSpeed = 160_000
contourSpotSize = 280
contourBeam = obp.Beamparameters(contourSpotSize, contourBeamPower)

LengthOfCube = 15_000
LineOffset = 150 #updated to 150 on 20240830
BottomLeftCoordX = [-17_500, -17_500, 2_500, 2_500]
BottomLeftCoordY = [2_500,  -17_500, 2_500, -17_500]

##LINE parameters
Powers = [1000, 1200, 1400] # the powers that will be tested in Z-direction
repeatSamePower = 60 #Number of layers with same power. Note this is only exactly true if equally dividable with NumberOfRotations, otherwise the actual number is lower (closest one equally dividable with NumberOfRotations)
BeamSpeed = [200_000, 100_000]#ramp from (0) to (1) --- #[0, 0, 125_000 , 100_000]
SpotSize = 280


##Spot parameters
SpotSizeSpot = 280
spotMelt = [True, False, True, False] #NOT IN USE IN THE GRADIENT SCRIPT
dwellTime = [3_500_000, 4_500_000] #Ramp from (0) to (1) ,[2_500_000, 3_000_000, 0 , 0] #Nanoseconds (=100_000 = 100us)
numberOfPoints = 50 #points per line
distanceBetweenPoints = LengthOfCube/(numberOfPoints-1)
print("Pixel size: ", distanceBetweenPoints), " um"
bp = []
for u in range(len(Powers)):    
    bp.append(obp.Beamparameters(SpotSizeSpot, Powers[u]))


NumberOfCubes = len(BottomLeftCoordX)
NumberOfRotations = 4 #melt rotation and in this case number of obp files to repeat
NumberOfLines = int(LengthOfCube/LineOffset)

NestedMeltList = []
NestedMeltListSupport = []

#Multiplication factors and beam speed list
BeamSpeedList = []
IncreasePerLine = (BeamSpeed[0]-BeamSpeed[1])/(NumberOfLines)
for u in range(NumberOfLines):    
    BeamSpeedList.append(int(BeamSpeed[0]-(IncreasePerLine*u)))
BeamSpeedList.append(BeamSpeed[1])

dwellTimeListXCoord = []
dwellIncreasePerLine = (dwellTime[0]-dwellTime[1])/(numberOfPoints) #This looks wrong but is right, check how the dwells are appended further down! Should be decrease but infact is used as an increase which makes the code operating correctly.
for u in range(numberOfPoints):  ## DUBBELKOLLA  
    dwellTimeListXCoord.append(int(dwellTime[0]-(dwellIncreasePerLine*u))) 
dwellTimeListXCoord.append(dwellTime[1])

class MeltCube:
    def __init__(self, LengthOfCube, LineOffset, BottomLeftCoordX, BottomLeftCoordY, Power, BeamSpeed1, BeamSpeed2, SpotSize):
        self.LengthOfCube = LengthOfCube
        self.LineOffset = LineOffset # LineOffset in um
        self.BottomLeftCoordX = BottomLeftCoordX #
        self.BottomLeftCoordY = BottomLeftCoordY
        self.Power = Power #Power in watt int
        self.BeamSpeed1 = BeamSpeed1
        self.BeamSpeed2 = BeamSpeed2
        self.SpotSize = SpotSize  #Spot size in um int

        self.A = obp.Point(self.BottomLeftCoordX, self.BottomLeftCoordY);
        self.B = obp.Point(self.LengthOfCube, self.BottomLeftCoordY);
        self.C = obp.Point(self.LengthOfCube, self.LengthOfCube);
        self.D = obp.Point(self.BottomLeftCoordX, self.LengthOfCube);
        self.Beam = obp.Beamparameters(self.SpotSize, self.Power);

        self.NumberOfLines = int(self.LengthOfCube/self.LineOffset);
        self.MeltLines = [];   

    def LRTB(self):
        '''Creates a cube of lines from left to right and top to bottom'''
        for i in range(0,self.NumberOfLines):
            LeftCoord = obp.Point(self.BottomLeftCoordX, self.BottomLeftCoordY + self.LengthOfCube-i*self.LineOffset);
            RightCoord = obp.Point(self.BottomLeftCoordX + self.LengthOfCube, self.BottomLeftCoordY + self.LengthOfCube-i*self.LineOffset);
            self.MeltLines.append(obp.AcceleratingLine(LeftCoord, RightCoord, self.BeamSpeed1, self.BeamSpeed2, self.Beam))
        return self.MeltLines
    


    def LRBT(self):
        '''Creates a cube of lines from left to right and bottom to top'''
        self.LRTB()
        self.MeltLines.reverse()
        return self.MeltLines


    def RLTB(self):
        '''Creates a cube of lines from right to left and top to bottom'''
        for i in range(0,self.NumberOfLines+1):
            LeftCoord = obp.Point(self.BottomLeftCoordX, self.BottomLeftCoordY + self.LengthOfCube-i*self.LineOffset)
            RightCoord = obp.Point(self.BottomLeftCoordX + self.LengthOfCube, self.BottomLeftCoordY + self.LengthOfCube-i*self.LineOffset)
            self.MeltLines.append(obp.AcceleratingLine(RightCoord, LeftCoord, self.BeamSpeed1, self.BeamSpeed2, self.Beam))
        return self.MeltLines

    def RLBT(self):
        '''Creates a cube of lines from right to left and bottom to top'''
        self.RLTB()
        self.MeltLines.reverse()
        return self.MeltLines

    def TBLR(self):
        '''Creates a cube of lines from Top to bottom and left to right'''
        for i in range(0,self.NumberOfLines+1):
            TopCoord = obp.Point(self.BottomLeftCoordX+i*self.LineOffset, self.BottomLeftCoordY + self.LineOffset*self.NumberOfLines)
            BottomCoord = obp.Point(self.BottomLeftCoordX+i*self.LineOffset, self.BottomLeftCoordY)
            self.MeltLines.append(obp.AcceleratingLine(TopCoord, BottomCoord, self.BeamSpeed1, self.BeamSpeed2, self.Beam))
        return self.MeltLines

    def TBRL(self):
         '''Creates a cube of lines from top to bottom and right to left'''
         self.TBLR()
         self.MeltLines.reverse()
         return self.MeltLines

    def BTLR(self):
        '''Creates a cube of lines from bottom to top and left to right'''
        for i in range(0,self.NumberOfLines+1):
            TopCoord = obp.Point(self.BottomLeftCoordX+i*self.LineOffset, self.BottomLeftCoordY + self.LineOffset*self.NumberOfLines)
            BottomCoord = obp.Point(self.BottomLeftCoordX+i*self.LineOffset, self.BottomLeftCoordY)
            self.MeltLines.append(obp.AcceleratingLine(BottomCoord, TopCoord,  self.BeamSpeed1, self.BeamSpeed2, self.Beam))
        return self.MeltLines

    def BTRL(self):
         '''Creates a cube of lines from top to bottom and right to left'''
         self.BTLR()
         self.MeltLines.reverse()
         return self.MeltLines
    
class MeltCubeVarioSpeed:
    def __init__(self, LengthOfCube, LineOffset, BottomLeftCoordX, BottomLeftCoordY, Power, BeamSpeedList, SpotSize):
        self.LengthOfCube = LengthOfCube
        self.LineOffset = LineOffset # LineOffset in um
        self.BottomLeftCoordX = BottomLeftCoordX #
        self.BottomLeftCoordY = BottomLeftCoordY
        self.Power = Power #Power in watt int
        self.BeamSpeedList = BeamSpeedList #a list!!
        self.SpotSize = SpotSize  #Spot size in um int

        self.A = obp.Point(self.BottomLeftCoordX, self.BottomLeftCoordY);
        self.B = obp.Point(self.LengthOfCube, self.BottomLeftCoordY);
        self.C = obp.Point(self.LengthOfCube, self.LengthOfCube);
        self.D = obp.Point(self.BottomLeftCoordX, self.LengthOfCube);
        self.Beam = obp.Beamparameters(self.SpotSize, self.Power);

        self.NumberOfLines = int(self.LengthOfCube/self.LineOffset);
        self.MeltLines = [];   

    def LRTB(self):
        '''Creates a cube of lines from left to right and top to bottom'''
        for i in range(0,self.NumberOfLines):
            LeftCoord = obp.Point(self.BottomLeftCoordX, self.BottomLeftCoordY + self.LengthOfCube-i*self.LineOffset);
            RightCoord = obp.Point(self.BottomLeftCoordX + self.LengthOfCube, self.BottomLeftCoordY + self.LengthOfCube-i*self.LineOffset);
            self.MeltLines.append(obp.Line(LeftCoord, RightCoord, self.BeamSpeedList, self.Beam))
        return self.MeltLines
    


    def LRBT(self):
        '''Creates a cube of lines from left to right and bottom to top'''
        self.LRTB()
        self.MeltLines.reverse()
        return self.MeltLines


    def RLTB(self):
        '''Creates a cube of lines from right to left and top to bottom'''
        for i in range(0,self.NumberOfLines+1):
            LeftCoord = obp.Point(self.BottomLeftCoordX, self.BottomLeftCoordY + self.LengthOfCube-i*self.LineOffset)
            RightCoord = obp.Point(self.BottomLeftCoordX + self.LengthOfCube, self.BottomLeftCoordY + self.LengthOfCube-i*self.LineOffset)
            self.MeltLines.append(obp.Line(RightCoord, LeftCoord, self.BeamSpeedList, self.Beam))
        return self.MeltLines

    def RLBT(self):
        '''Creates a cube of lines from right to left and bottom to top'''
        self.RLTB()
        self.MeltLines.reverse()
        return self.MeltLines

    def TBLR(self):
        '''Creates a cube of lines from Top to bottom and left to right'''
        for i in range(0,self.NumberOfLines+1):
            TopCoord = obp.Point(self.BottomLeftCoordX+i*self.LineOffset, self.BottomLeftCoordY + self.LineOffset*self.NumberOfLines)
            BottomCoord = obp.Point(self.BottomLeftCoordX+i*self.LineOffset, self.BottomLeftCoordY)
            #print(BeamSpeedList[i])
            self.MeltLines.append(obp.Line(TopCoord, BottomCoord, self.BeamSpeedList[i], self.Beam))
        
        return self.MeltLines
        

    def TBRL(self):
         '''Creates a cube of lines from top to bottom and right to left'''
         self.TBLR()
         self.MeltLines.reverse()
         return self.MeltLines

    def BTLR(self):
        '''Creates a cube of lines from bottom to top and left to right'''
        for i in range(0,self.NumberOfLines+1):
            TopCoord = obp.Point(self.BottomLeftCoordX+i*self.LineOffset, self.BottomLeftCoordY + self.LineOffset*self.NumberOfLines)
            BottomCoord = obp.Point(self.BottomLeftCoordX+i*self.LineOffset, self.BottomLeftCoordY)
            self.MeltLines.append(obp.Line(BottomCoord, TopCoord,  self.BeamSpeedList[i], self.Beam))
        return self.MeltLines

    def BTRL(self):
         '''Creates a cube of lines from top to bottom and right to left'''
         self.BTLR()
         self.MeltLines.reverse()
         
         return self.MeltLines




##SUPPORT CLASS
class SupportCube:
    def __init__(self, LengthOfCube, LineOffset, BottomLeftCoordX, BottomLeftCoordY, Power, BeamSpeed1, SpotSize):
        self.LengthOfCube = LengthOfCube
        self.LineOffset = LineOffset # LineOffset in um
        self.BottomLeftCoordX = BottomLeftCoordX #
        self.BottomLeftCoordY = BottomLeftCoordY
        self.Power = Power #Power in watt int
        self.BeamSpeed1 = BeamSpeed1
        self.SpotSize = SpotSize  #Spot size in um int

        self.A = obp.Point(self.BottomLeftCoordX, self.BottomLeftCoordY);
        self.B = obp.Point(self.LengthOfCube, self.BottomLeftCoordY);
        self.C = obp.Point(self.LengthOfCube, self.LengthOfCube);
        self.D = obp.Point(self.BottomLeftCoordX, self.LengthOfCube);
        self.Beam = obp.Beamparameters(self.SpotSize, self.Power);

        self.NumberOfLines = int(self.LengthOfCube/self.LineOffset);
        self.MeltLines = [];   

    def LRTB(self):
        '''Creates a cube of lines from left to right and top to bottom'''
        for i in range(0,self.NumberOfLines+1):
            LeftCoord = obp.Point(self.BottomLeftCoordX, self.BottomLeftCoordY + self.LengthOfCube-i*self.LineOffset);
            RightCoord = obp.Point(self.BottomLeftCoordX + self.LengthOfCube, self.BottomLeftCoordY + self.LengthOfCube-i*self.LineOffset);
            self.MeltLines.append(obp.Line(LeftCoord, RightCoord, self.BeamSpeed1, self.Beam))
        return self.MeltLines
    


    def LRBT(self):
        '''Creates a cube of lines from left to right and bottom to top'''
        self.LRTB()
        self.MeltLines.reverse()
        return self.MeltLines


    def RLTB(self):
        '''Creates a cube of lines from right to left and top to bottom'''
        for i in range(0,self.NumberOfLines+1):
            LeftCoord = obp.Point(self.BottomLeftCoordX, self.BottomLeftCoordY + self.LengthOfCube-i*self.LineOffset)
            RightCoord = obp.Point(self.BottomLeftCoordX + self.LengthOfCube, self.BottomLeftCoordY + self.LengthOfCube-i*self.LineOffset)
            self.MeltLines.append(obp.Line(RightCoord, LeftCoord, self.BeamSpeed1, self.Beam))
        return self.MeltLines

    def RLBT(self):
        '''Creates a cube of lines from right to left and bottom to top'''
        self.RLTB()
        self.MeltLines.reverse()
        return self.MeltLines

    def TBLR(self):
        '''Creates a cube of lines from Top to bottom and left to right'''
        for i in range(0,self.NumberOfLines+1):
            TopCoord = obp.Point(self.BottomLeftCoordX+i*self.LineOffset, self.BottomLeftCoordY + self.LineOffset*self.NumberOfLines)
            BottomCoord = obp.Point(self.BottomLeftCoordX+i*self.LineOffset, self.BottomLeftCoordY)
            self.MeltLines.append(obp.Line(TopCoord, BottomCoord, self.BeamSpeed1, self.Beam))
        return self.MeltLines

    def TBRL(self):
         '''Creates a cube of lines from top to bottom and right to left'''
         self.TBLR()
         self.MeltLines.reverse()
         return self.MeltLines

    def BTLR(self):
        '''Creates a cube of lines from bottom to top and left to right'''
        for i in range(0,self.NumberOfLines+1):
            TopCoord = obp.Point(self.BottomLeftCoordX+i*self.LineOffset, self.BottomLeftCoordY + self.LineOffset*self.NumberOfLines)
            BottomCoord = obp.Point(self.BottomLeftCoordX+i*self.LineOffset, self.BottomLeftCoordY)
            self.MeltLines.append(obp.Line(BottomCoord, TopCoord,  self.BeamSpeed1, self.Beam))
        return self.MeltLines

    def BTRL(self):
         '''Creates a cube of lines from top to bottom and right to left'''
         self.BTLR()
         self.MeltLines.reverse()
         return self.MeltLines
##END SUPPORT CLASS


#INITIAL LAYERS AND SUPPORT
## start support
BolHolder = True
for i in range(numberOfSupportLayers):
    Cubes = []
    for n in range (NumberOfCubes):
        #INSERT RAMP HERE
        if n==0:
            spotsizeRAMP = 980
            bpRAMP = obp.Beamparameters(spotsizeRAMP, supportPower);
            numberOfPointsRAMP = 64 #points per line
            dwellTimeRAMP = 100_000 # NAMNOSECONDS
            lineStartCoordRAMP = [-20_000 , -20_000] # Contains
            lineLengthRAMP = 40_000
            distanceBetweenPointsRAMP = lineLengthRAMP/(numberOfPointsRAMP-1)
            pointsRAMP = [] #Clustered [x][y] coordinates of pointCoordinates
            for f in range(numberOfPointsRAMP): #X-coordinates !!
                X = lineStartCoordRAMP[0]+f*distanceBetweenPointsRAMP
                coordinateRAMP = [X , lineStartCoordRAMP[1]]
                pointRAMP = obp.Point(coordinateRAMP[0],coordinateRAMP[1])                                                                   
                pointsRAMP.append(pointRAMP)
                for d in range(numberOfPointsRAMP): #Y-coordinates !!
                    coordinateRAMP = [X , lineStartCoordRAMP[1] + d*distanceBetweenPointsRAMP]
                    pointRAMP = obp.Point(coordinateRAMP[0],coordinateRAMP[1])                                                                   
                    pointsRAMP.append(pointRAMP)
            dwellTimesRAMP = [dwellTimeRAMP]*len(pointsRAMP)
            random.shuffle(pointsRAMP)
            tPoint = obp.TimedPoints(pointsRAMP, dwellTimesRAMP, bpRAMP)
            Cubes.append(tPoint)
            Cubes.append(tPoint)
        #END OF RAMP

        Cube = SupportCube(LengthOfCube, supportLineOffset, BottomLeftCoordX[n], BottomLeftCoordY[n], supportPower, supportBeamSpeed, supportSpotSize)
        if BolHolder == True:
            Cubes.append(Cube.LRTB())
            Cubes.append(Cube.BTRL())
            Bolholder = False
        else:
            Cubes.append(Cube.TBRL())
            Cubes.append(Cube.LRBT())
            Bolholder = True                                                                       
    NestedMeltListSupport.append(Cubes)

name=0
for index,Layer in enumerate(NestedMeltListSupport):
    LayerLines = []
    for cube_number,Cube in enumerate(Layer):
        if type(Cube) is list:
            LayerLines.extend(Cube)
            # print(len(LayerLines), type(LayerLines))
            # obp.FileHandler.write_obp(Cube, f"WMeltLayer{index}Cube{cube_number}.obp")
        else:
            LayerLines.append(Cube)
            # print(len(LayerLines), type(LayerLines))
            # print(type(Cube), type(index), index)
            # obp.FileHandler.write_obp([Cube], f"WSpotLayer{index}Cube{cube_number}.obp")
        # print(type(Cube))
        # print(type(Cube), len(Cube))    
    obp.FileHandler.write_obp(LayerLines, f"WLayer{name}.obp")
    name=name+1
    #print(name)
## END SUPPORT

##START initial layers

NestedMeltListInitial = []
for i in range(numberOfInitialLayers):
    Cubes = []
    for n in range (NumberOfCubes):
        Cube = SupportCube(LengthOfCube, 150, BottomLeftCoordX[n], BottomLeftCoordY[n], initialLayersPower, initialBeamSpeed, supportSpotSize)
        
        #INSERT RAMP HERE
        if n==0:
            spotsizeRAMP = 980
            bpRAMP = obp.Beamparameters(spotsizeRAMP, initialLayersPower);
            numberOfPointsRAMP = 64 #points per line
            dwellTimeRAMP = 100_000 # NAMNOSECONDS
            lineStartCoordRAMP = [-20_000 , -20_000] # Contains
            lineLengthRAMP = 40_000
            distanceBetweenPointsRAMP = lineLengthRAMP/(numberOfPointsRAMP-1)
            pointsRAMP = [] #Clustered [x][y] coordinates of pointCoordinates
            for f in range(numberOfPointsRAMP): #X-coordinates !!
                X = lineStartCoordRAMP[0]+f*distanceBetweenPointsRAMP
                coordinateRAMP = [X , lineStartCoordRAMP[1]]
                pointRAMP = obp.Point(coordinateRAMP[0],coordinateRAMP[1])                                                                   
                pointsRAMP.append(pointRAMP)
                for d in range(numberOfPointsRAMP): #Y-coordinates !!
                    coordinateRAMP = [X , lineStartCoordRAMP[1] + d*distanceBetweenPointsRAMP]
                    pointRAMP = obp.Point(coordinateRAMP[0],coordinateRAMP[1])                                                                   
                    pointsRAMP.append(pointRAMP)
            dwellTimesRAMP = [dwellTimeRAMP]*len(pointsRAMP)
            random.shuffle(pointsRAMP)
            tPoint = obp.TimedPoints(pointsRAMP, dwellTimesRAMP, bpRAMP)
            Cubes.append(tPoint)
            Cubes.append(tPoint)
        #END OF RAMP
        ##CONTOURS
        #CONTOUR INSERT LOOP
        C1 = obp.Line(obp.Point(BottomLeftCoordX[n], BottomLeftCoordY[n]), obp.Point(BottomLeftCoordX[n]+LengthOfCube, BottomLeftCoordY[n]),  contourBeamSpeed, contourBeam)
        C2 = obp.Line(obp.Point(BottomLeftCoordX[n]+LengthOfCube, BottomLeftCoordY[n]), obp.Point(BottomLeftCoordX[n]+LengthOfCube, BottomLeftCoordY[n]+LengthOfCube),  contourBeamSpeed, contourBeam)
        C3 = obp.Line(obp.Point(BottomLeftCoordX[n]+LengthOfCube, BottomLeftCoordY[n]+LengthOfCube), obp.Point(BottomLeftCoordX[n], BottomLeftCoordY[n]+LengthOfCube),  contourBeamSpeed, contourBeam)
        C4 = obp.Line(obp.Point(BottomLeftCoordX[n], BottomLeftCoordY[n]+LengthOfCube), obp.Point(BottomLeftCoordX[n], BottomLeftCoordY[n]),  contourBeamSpeed, contourBeam)
        Cubes.append(C1)
        Cubes.append(C2)
        Cubes.append(C3)
        Cubes.append(C4)
        ##END OF CONTOURS
        if i == 0:
            Cubes.append(Cube.LRTB())
        elif i == 1:
            Cubes.append(Cube.TBRL())
        elif i == 2:
            Cubes.append(Cube.RLBT())
        else:
            Cubes.append(Cube.BTLR())                                                                        
    NestedMeltListInitial.append(Cubes)

#name=0
for index,Layer in enumerate(NestedMeltListInitial):
    LayerLines = []
    for cube_number,Cube in enumerate(Layer):
        if type(Cube) is list:
            LayerLines.extend(Cube)
        else:
            LayerLines.append(Cube) 
    obp.FileHandler.write_obp(LayerLines, f"WLayer{name}.obp")
    name=name+1

#END initial layers



#END INITIAL LAYERS AND SUPPORT









for r in range(len(Powers)):
    #print(len(NestedMeltList))
    


    for o in range(int(repeatSamePower/NumberOfRotations)): # note that this is a fix so that the rotations always aligns with power change
        counter = 0
        
        for i in range(NumberOfRotations):
            if (i % 2) == 0: # checks if i is even
                offsetter = False
            else:
                offsetter = True
            Cubes = []
            counter = 0 #includes ramp in every layer
            #INSERT CONTOUR RAMP HERE
            spotsizeRAMP = 980
            bpRAMP = obp.Beamparameters(spotsizeRAMP, contourBeamPower)
            numberOfPointsRAMP = 64 #points per line
            dwellTimeRAMP = 100_000 # NAMNOSECONDS
            lineStartCoordRAMP = [-20_000 , -20_000] # Contains
            lineLengthRAMP = 40_000
            distanceBetweenPointsRAMP = lineLengthRAMP/(numberOfPointsRAMP-1)
            pointsRAMP = [] #Clustered [x][y] coordinates of pointCoordinates
            for f in range(numberOfPointsRAMP): #X-coordinates !!
                X = lineStartCoordRAMP[0]+f*distanceBetweenPointsRAMP
                coordinateRAMP = [X , lineStartCoordRAMP[1]]
                pointRAMP = obp.Point(coordinateRAMP[0],coordinateRAMP[1])                                                                   
                pointsRAMP.append(pointRAMP)
                for d in range(numberOfPointsRAMP): #Y-coordinates !!
                    coordinateRAMP = [X , lineStartCoordRAMP[1] + d*distanceBetweenPointsRAMP]
                    pointRAMP = obp.Point(coordinateRAMP[0],coordinateRAMP[1])                                                                   
                    pointsRAMP.append(pointRAMP)
            dwellTimesRAMP = [dwellTimeRAMP]*len(pointsRAMP)
            random.shuffle(pointsRAMP)
            tPoint = obp.TimedPoints(pointsRAMP, dwellTimesRAMP, bpRAMP)
            Cubes.append(tPoint)
            Cubes.append(tPoint)
            #END OF RAMP
            ##CONTOURS
            for a in range(NumberOfCubes): #CONTOUR INSERT LOOP
                if a ==1 or a==3:
                    C1 = obp.Line(obp.Point(BottomLeftCoordX[a], BottomLeftCoordY[a]), obp.Point(BottomLeftCoordX[a]+LengthOfCube, BottomLeftCoordY[a]),  contourBeamSpeed, contourBeam)
                    C2 = obp.Line(obp.Point(BottomLeftCoordX[a]+LengthOfCube, BottomLeftCoordY[a]), obp.Point(BottomLeftCoordX[a]+LengthOfCube, BottomLeftCoordY[a]+LengthOfCube),  contourBeamSpeed, contourBeam)
                    C3 = obp.Line(obp.Point(BottomLeftCoordX[a]+LengthOfCube, BottomLeftCoordY[a]+LengthOfCube), obp.Point(BottomLeftCoordX[a], BottomLeftCoordY[a]+LengthOfCube),  contourBeamSpeed, contourBeam)
                    C4 = obp.Line(obp.Point(BottomLeftCoordX[a], BottomLeftCoordY[a]+LengthOfCube), obp.Point(BottomLeftCoordX[a], BottomLeftCoordY[a]),  contourBeamSpeed, contourBeam)
                    Cubes.append(C1)
                    Cubes.append(C2)
                    Cubes.append(C3)
                    Cubes.append(C4)
                else:
                    print("contours disabled on spotmelt")
            ##END OF CONTOURS
            for n in range (NumberOfCubes):
                dwellTimeList = []
                ##CONTOURS
                #C1 = obp.Line(obp.Point(BottomLeftCoordX[n], BottomLeftCoordY[n]), obp.Point(BottomLeftCoordX[n]+LengthOfCube, BottomLeftCoordY[n]),  contourBeamSpeed, contourBeam)
                #C2 = obp.Line(obp.Point(BottomLeftCoordX[n]+LengthOfCube, BottomLeftCoordY[n]), obp.Point(BottomLeftCoordX[n]+LengthOfCube, BottomLeftCoordY[n]+LengthOfCube),  contourBeamSpeed, contourBeam)
                #C3 = obp.Line(obp.Point(BottomLeftCoordX[n]+LengthOfCube, BottomLeftCoordY[n]+LengthOfCube), obp.Point(BottomLeftCoordX[n], BottomLeftCoordY[n]+LengthOfCube),  contourBeamSpeed, contourBeam)
                #C4 = obp.Line(obp.Point(BottomLeftCoordX[n], BottomLeftCoordY[n]+LengthOfCube), obp.Point(BottomLeftCoordX[n], BottomLeftCoordY[n]),  contourBeamSpeed, contourBeam)
                #Cubes.append(C1)
                #Cubes.append(C2)
                #Cubes.append(C3)
                #Cubes.append(C4)
                ##END OF CONTOURS
                if counter == 0: #This inputs the ramping before the first melt (except contours) in each layer
                    #INSERT RAMP HERE
                    spotsizeRAMP = 980
                    bpRAMP = obp.Beamparameters(spotsizeRAMP, Powers[r]);
                    numberOfPointsRAMP = 64 #points per line
                    dwellTimeRAMP = 100_000 # NAMNOSECONDS
                    lineStartCoordRAMP = [-20_000 , -20_000] # Contains
                    lineLengthRAMP = 40_000
                    distanceBetweenPointsRAMP = lineLengthRAMP/(numberOfPointsRAMP-1)
                    pointsRAMP = [] #Clustered [x][y] coordinates of pointCoordinates
                    for f in range(numberOfPointsRAMP): #X-coordinates !!
                        X = lineStartCoordRAMP[0]+f*distanceBetweenPointsRAMP
                        coordinateRAMP = [X , lineStartCoordRAMP[1]]
                        pointRAMP = obp.Point(coordinateRAMP[0],coordinateRAMP[1])                                                                   
                        pointsRAMP.append(pointRAMP)
                        for d in range(numberOfPointsRAMP): #Y-coordinates !!
                            coordinateRAMP = [X , lineStartCoordRAMP[1] + d*distanceBetweenPointsRAMP]
                            pointRAMP = obp.Point(coordinateRAMP[0],coordinateRAMP[1])                                                                   
                            pointsRAMP.append(pointRAMP)
                    dwellTimesRAMP = [dwellTimeRAMP]*len(pointsRAMP)
                    random.shuffle(pointsRAMP)
                    counter = counter+1
                    tPoint = obp.TimedPoints(pointsRAMP, dwellTimesRAMP, bpRAMP)
                    Cubes.append(tPoint)
                    Cubes.append(tPoint)
                    #NestedMeltList.append([tPoint])
                    #END OF RAMP

                
                if n == 0: #This is what will be melted in cube 1 (except contours)
                    #print("Cube 1 killed")
                    points = [] #Clustered [x][y] coordinates of pointCoordinates
                    for k in range(numberOfPoints): #X-coordinates !!
                        X = BottomLeftCoordX[n]+k*distanceBetweenPoints
                        if offsetter == False:
                            coordinate = [X , BottomLeftCoordY[n]]
                            point = obp.Point(coordinate[0],coordinate[1])                                                                   
                            points.append(point)
                            dwellTimeList.append(dwellTimeListXCoord[k])
                            for j in range(numberOfPoints): #Y-coordinates !!
                                coordinate = [X , BottomLeftCoordY[n] + j*distanceBetweenPoints]
                                point = obp.Point(coordinate[0],coordinate[1])                                                                   
                                points.append(point)
                                dwellTimeList.append(dwellTimeListXCoord[k])
                            #print(offsetter)
                        else: # HERE IS OFFSETED POINTS BY 1/2 distancebetween points for every second layer
                            coordinate = [X+(distanceBetweenPoints/2) , BottomLeftCoordY[n]+(distanceBetweenPoints/2)]
                            point = obp.Point(coordinate[0],coordinate[1])                                                                   
                            points.append(point)
                            dwellTimeList.append(dwellTimeListXCoord[k])
                            for j in range(numberOfPoints): #Y-coordinates !!
                                coordinate = [X+(distanceBetweenPoints/2) , BottomLeftCoordY[n] + j*distanceBetweenPoints+(distanceBetweenPoints/2)]
                                point = obp.Point(coordinate[0],coordinate[1])                                                                   
                                points.append(point)
                                dwellTimeList.append(dwellTimeListXCoord[k])
                            #print(offsetter)


                    #dwellTimes = [dwellTime[n]]*len(points)
                    #print(len(points), len(dwellTimeList))

                    randShuffleZIP = list(zip(dwellTimeList, points))            
                    random.shuffle(randShuffleZIP)
                    dwellTimeList, points = zip(*randShuffleZIP)
                    #print(len(points), len(dwellTimeList))
                    tPoint = obp.TimedPoints(points, dwellTimeList, bp[r])
                    Cubes.append(tPoint)
                
                elif n == 1: #This is what will be melted in cube 2 (except contours)
                    #print("cube 2 killed")
                    if i == 0:
                        Cube = MeltCube(LengthOfCube, LineOffset, BottomLeftCoordX[n], BottomLeftCoordY[n], Powers[r], BeamSpeed[0], BeamSpeed[1], SpotSize)
                        Cubes.append(Cube.LRTB())
                    elif i == 1:
                        Cube = MeltCubeVarioSpeed(LengthOfCube, LineOffset, BottomLeftCoordX[n], BottomLeftCoordY[n], Powers[r], BeamSpeedList, SpotSize)
                        Cubes.append(Cube.TBRL())
                    elif i == 2:
                        Cube = MeltCube(LengthOfCube, LineOffset, BottomLeftCoordX[n], BottomLeftCoordY[n], Powers[r], BeamSpeed[1], BeamSpeed[0], SpotSize)
                        Cubes.append(Cube.RLBT())
                    else:
                        Cube = MeltCubeVarioSpeed(LengthOfCube, LineOffset, BottomLeftCoordX[n], BottomLeftCoordY[n], Powers[r], BeamSpeedList, SpotSize)
                        Cubes.append(Cube.BTLR())

                elif n == 2: #This is what will be melted in cube 3 (except contours)
                    #print("cube 3 killed")
                    
                    #USED TO MAKE TWO LINES 241125 Cube = MeltCube(LengthOfCube, 5000, BottomLeftCoordX[n], BottomLeftCoordY[n], Powers[r], BeamSpeed[0], BeamSpeed[1], SpotSize)
                    #Cubes.append(Cube.LRTB())

                    
                    #INSERT RAMP HERE
                    spotsizeRAMP = 980
                    bpRAMP = obp.Beamparameters(spotsizeRAMP, list(reversed(Powers))[r]);
                    numberOfPointsRAMP = 64 #points per line
                    dwellTimeRAMP = 100_000 # NAMNOSECONDS
                    lineStartCoordRAMP = [-20_000 , -20_000] # Contains
                    lineLengthRAMP = 40_000
                    distanceBetweenPointsRAMP = lineLengthRAMP/(numberOfPointsRAMP-1)
                    pointsRAMP = [] #Clustered [x][y] coordinates of pointCoordinates
                    for f in range(numberOfPointsRAMP): #X-coordinates !!
                        X = lineStartCoordRAMP[0]+f*distanceBetweenPointsRAMP
                        coordinateRAMP = [X , lineStartCoordRAMP[1]]
                        pointRAMP = obp.Point(coordinateRAMP[0],coordinateRAMP[1])                                                                   
                        pointsRAMP.append(pointRAMP)
                        for d in range(numberOfPointsRAMP): #Y-coordinates !!
                            coordinateRAMP = [X , lineStartCoordRAMP[1] + d*distanceBetweenPointsRAMP]
                            pointRAMP = obp.Point(coordinateRAMP[0],coordinateRAMP[1])                                                                   
                            pointsRAMP.append(pointRAMP)
                    dwellTimesRAMP = [dwellTimeRAMP]*len(pointsRAMP)
                    random.shuffle(pointsRAMP)
                    counter = counter+1
                    tPoint = obp.TimedPoints(pointsRAMP, dwellTimesRAMP, bpRAMP)
                    Cubes.append(tPoint)
                    Cubes.append(tPoint)
                    #NestedMeltList.append([tPoint])
                    #END OF RAMP
                    
                    
                    points = [] #Clustered [x][y] coordinates of pointCoordinates
                    for k in range(numberOfPoints): #X-coordinates !!
                        X = BottomLeftCoordX[n]+k*distanceBetweenPoints
                        if offsetter == False:
                            coordinate = [X , BottomLeftCoordY[n]]
                            point = obp.Point(coordinate[0],coordinate[1])                                                                   
                            points.append(point)
                            dwellTimeList.append(list(reversed(dwellTimeListXCoord))[k])
                            for j in range(numberOfPoints): #Y-coordinates !!
                                coordinate = [X , BottomLeftCoordY[n] + j*distanceBetweenPoints]
                                point = obp.Point(coordinate[0],coordinate[1])                                                                   
                                points.append(point)
                                dwellTimeList.append(list(reversed(dwellTimeListXCoord))[k])
                        else: # offset every second layer
                            coordinate = [X , BottomLeftCoordY[n]]
                            point = obp.Point(coordinate[0]+(distanceBetweenPoints/2),coordinate[1]+(distanceBetweenPoints/2))                                                                   
                            points.append(point)
                            dwellTimeList.append(list(reversed(dwellTimeListXCoord))[k])
                            for j in range(numberOfPoints): #Y-coordinates !!
                                coordinate = [X+(distanceBetweenPoints/2) , BottomLeftCoordY[n] + j*distanceBetweenPoints+(distanceBetweenPoints/2)]
                                point = obp.Point(coordinate[0],coordinate[1])                                                                   
                                points.append(point)
                                dwellTimeList.append(list(reversed(dwellTimeListXCoord))[k])
                    #dwellTimes = [dwellTime[n]]*len(points)
                    #print(len(points), len(dwellTimeList))

                    randShuffleZIP = list(zip(dwellTimeList, points))            
                    random.shuffle(randShuffleZIP)
                    dwellTimeList, points = zip(*randShuffleZIP)
                    #print(len(points), len(dwellTimeList))
                    tPoint = obp.TimedPoints(points, dwellTimeList, list(reversed(bp))[r])
                    Cubes.append(tPoint)
                    
                    

                else: #n == 3: #This is what will be melted in cube 4 (except contours)
                    
                    if i == 0:
                        Cube = MeltCube(LengthOfCube, LineOffset, BottomLeftCoordX[n], BottomLeftCoordY[n], list(reversed(Powers))[r], BeamSpeed[1], BeamSpeed[0], SpotSize)
                        Cubes.append(Cube.LRTB())
                    elif i == 1:
                        Cube = MeltCubeVarioSpeed(LengthOfCube, LineOffset, BottomLeftCoordX[n], BottomLeftCoordY[n], list(reversed(Powers))[r], list(reversed(BeamSpeedList)), SpotSize)
                        Cubes.append(Cube.TBRL())
                    elif i == 2:
                        Cube = MeltCube(LengthOfCube, LineOffset, BottomLeftCoordX[n], BottomLeftCoordY[n], list(reversed(Powers))[r], BeamSpeed[0], BeamSpeed[1], SpotSize)
                        Cubes.append(Cube.RLBT())
                    else:
                        Cube = MeltCubeVarioSpeed(LengthOfCube, LineOffset, BottomLeftCoordX[n], BottomLeftCoordY[n], list(reversed(Powers))[r], list(reversed(BeamSpeedList)), SpotSize)
                        Cubes.append(Cube.BTLR())
                        

                                                                                         
            print("Last Generated Layer (excl initial and support):", len(NestedMeltList))
            NestedMeltList.append(Cubes)
    

# print(len(NestedMeltList))




print("length NestedMeltList[0]:", len(NestedMeltList[0]))
for index,Layer in enumerate(NestedMeltList):
    LayerLines = []
    for cube_number,Cube in enumerate(Layer):
        if type(Cube) is list:
            LayerLines.extend(Cube)
            # print(len(LayerLines), type(LayerLines))
            # obp.FileHandler.write_obp(Cube, f"WMeltLayer{index}Cube{cube_number}.obp")
        else:
            LayerLines.append(Cube)
            # print(len(LayerLines), type(LayerLines))
            # print(type(Cube), type(index), index)
            # obp.FileHandler.write_obp([Cube], f"WSpotLayer{index}Cube{cube_number}.obp")
        # print(type(Cube))
        # print(type(Cube), len(Cube))    
    obp.FileHandler.write_obp(LayerLines, f"WLayer{name}.obp")
    name=name+1
    #print(name)
print("Number of layers:", name)
print(" ")
print("Cube 1 (2nd quadrant) check: ")
print("Dwelltime will ramp between ", dwellTime[0], " and ", dwellTime[1], " in ", len(dwellTimeListXCoord) , " steps, with a step size of ", dwellIncreasePerLine, " Nanoseconds")
print("Dwell times check: ", dwellTimeListXCoord)

print(" ")
print("Cube 2 (3rd quadrant) check: ")
print("Beam speed will ramp between ", BeamSpeed[0], " and ", BeamSpeed[1], " in ", len(BeamSpeedList) , " steps with a step size of ", IncreasePerLine, " units")
print("Beam speed check: ", BeamSpeedList) ## EJ KLAR

print(" ")
print("Cube 3 (4th quadrant) check: ")
print("Dwelltime will ramp between ", dwellTime[1], " and ", dwellTime[0], " in ", len(dwellTimeListXCoord) , " steps, with a step size of ", -dwellIncreasePerLine, " Nanoseconds")
print("Dwell times check: ", list(reversed(dwellTimeListXCoord)))

print(" ")
print("Cube 4 (1st quadrant) check: ")
print("Beam speed will ramp between ", BeamSpeed[1], " and ", BeamSpeed[0], " in ", len(BeamSpeedList) , " steps with a step size of ", -IncreasePerLine, " units")
print("Beam speed check: ", list(reversed(BeamSpeedList)))

print("Generation of build was successful!")