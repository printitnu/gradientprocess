import obplib as obp
import random

#BeamParameters
spotsize = 1100
power = 2500
bp = obp.Beamparameters(spotsize, power);


#Initial spot parameters
numberOfPoints = 64 #points per line
dwellTime = 100_000 # NAMNOSECONDS


lineStartCoord = [-32_000 , -32_000] # Contains
lineLength = 64_000
# endCoord = [lineStartCoord[0] , lineStartCoord[1]+lineLength]
distanceBetweenPoints = lineLength/(numberOfPoints-1)


points = [] #Clustered [x][y] coordinates of pointCoordinates
for i in range(numberOfPoints): #X-coordinates !!
    X = lineStartCoord[0]+i*distanceBetweenPoints
    coordinate = [X , lineStartCoord[1]]
    point = obp.Point(coordinate[0],coordinate[1])                                                                   
    points.append(point)
    for n in range(numberOfPoints): #Y-coordinates !!
        coordinate = [X , lineStartCoord[1] + n*distanceBetweenPoints]
        point = obp.Point(coordinate[0],coordinate[1])                                                                   
        points.append(point)

print(len(points), type(points))

dwellTimes = [dwellTime]*len(points)

random.shuffle(points)
tPoint = obp.TimedPoints(points, dwellTimes, bp)



print(type(tPoint))
#shuffle before this
obp.FileHandler.write_obp([tPoint], "WPlateHeat.obp")











