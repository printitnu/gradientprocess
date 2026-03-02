import obplib as obp

from FistFileCLASS import MeltCube
from PreHeatW import SqPreHeat

LengthOfCube = 78_000 #input correct side of scan in microns
BottomLeftCoordX = [-39_000] #offset to (0,0) = center of the cube
BottomLeftCoordY = [-39_000]
Power = 60
beamSpeed = 20_000_000 #10000_000
samplingFreq = 250_000 #250_000 Hz is preset in Freemelt data logger
spotDistanceX = beamSpeed/samplingFreq
LineOffset = spotDistanceX
print("Pixel size and line offset = ", spotDistanceX)
SpotSize = 320

NumberOfCubes = len(BottomLeftCoordX)
NumberOfLayers = 1 #in this case number of obp files to repeat


NestedMeltList = []

for i in range(NumberOfLayers):
    Cubes = []
    for n in range (NumberOfCubes):
        Cube = MeltCube(LengthOfCube, LineOffset, BottomLeftCoordX[n], BottomLeftCoordY[n], Power, beamSpeed, SpotSize)
        if i == 0:
            Cubes.append(Cube.LRTB())
        elif i == 1:
            Cubes.append(Cube.RLTB())
        elif i == 2:
            Cubes.append(Cube.TBLR())
        elif i == 3:
            Cubes.append(Cube.BTLR())
        elif i == 4:
            Cubes.append(Cube.RLBT())
        elif i == 5:
            Cubes.append(Cube.LRBT())
        elif i == 6:
            Cubes.append(Cube.BTRL())
        else:
            Cubes.append(Cube.TBRL())                                                                        
    NestedMeltList.append(Cubes)
    

#print(len(NestedMeltList), len(Cubes), len(Cubes[0]))



def wrap_with_syncpoint(pattern: list) -> list:
    
    bse_gain = obp.SyncPoint("BSEGain", False, 0)
    bse_true = obp.SyncPoint("BseImage", True, 0)

    wrapped_pattern = [bse_gain, bse_true]

    bse_false = obp.SyncPoint("BseImage", False, 0)
    
    wrapped_pattern.extend(pattern)
    wrapped_pattern.append(bse_false)
    
    return wrapped_pattern    
 


LayerLines = []
##RAMP STARTS HERE
#preHeat = SqPreHeat(LengthOfCube, 1000, 10, BottomLeftCoordX[0], BottomLeftCoordY[0], Power, 2_500_000, 100)
#preHeatLines = preHeat.BTRL()
#LayerLines.extend(preHeatLines)
#LayerLines.extend(preHeatLines)
#LayerLines.extend(preHeatLines)
#LayerLines.extend(preHeatLines)
##RAMP ENDS HERE
for i,Layer in enumerate(NestedMeltList):
    for Cube in Layer:
        #print(type(Cube), len(Cube))
        LayerLines.extend(Cube)
        LinesWidthSyncPoints = wrap_with_syncpoint(LayerLines)
    obp.FileHandler.write_obp(LinesWidthSyncPoints, "BSEScan.obp")

