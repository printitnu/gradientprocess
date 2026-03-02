import obplib as obp

from PreHeatW import SqPreHeat

LengthOfCube = 60_000
LineOffset = 1000
LineOrder = 10
BottomLeftCoordX = [-30_000]
BottomLeftCoordY = [-30_000]
Power = 60
BeamSpeed = 2_500_000
SpotSize = 950

preHeatLines =[]
preHeat = SqPreHeat(LengthOfCube, LineOffset, LineOrder, BottomLeftCoordX[0], BottomLeftCoordY[0], Power, BeamSpeed, SpotSize)
preHeatLines.extend(preHeat.BTRL())
preHeatLines.extend(preHeat.BTRL())


obp.FileHandler.write_obp(preHeatLines, "BSE_RAMP.obp")