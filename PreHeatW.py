import obplib as obp





class SqPreHeat:
    def __init__(self, LengthOfCube, LineOffset, LineOrder, BottomLeftCoordX, BottomLeftCoordY, Power, BeamSpeed, SpotSize):
        self.LengthOfCube = LengthOfCube
        self.LineOffset = LineOffset # LineOffset in mm
        self.LineOrder = LineOrder
        self.BottomLeftCoordX = BottomLeftCoordX #
        self.BottomLeftCoordY = BottomLeftCoordY
        self.Power = Power #Power in watt int
        self.BeamSpeed = BeamSpeed
        self.SpotSize = SpotSize  #Spot size in um int

        self.A = obp.Point(self.BottomLeftCoordX, self.BottomLeftCoordY)
        self.B = obp.Point(self.LengthOfCube, self.BottomLeftCoordY)
        self.C = obp.Point(self.LengthOfCube, self.LengthOfCube)
        self.D = obp.Point(self.BottomLeftCoordX, self.LengthOfCube)
        self.Beam = obp.Beamparameters(self.SpotSize, self.Power)

        self.NumberOfLines = int(self.LengthOfCube / self.LineOffset)
        self.heatLines = [];
        self.heatLinesLineOrder = self.heatLines 


    def LRTB(self):
        '''Creates a cube of lines from left to right and top to bottom'''
        for i in range(0,self.NumberOfLines):
            LeftCoord = obp.Point(self.BottomLeftCoordX, self.BottomLeftCoordY + self.LengthOfCube-i*self.LineOffset);
            RightCoord = obp.Point(self.BottomLeftCoordX + self.LengthOfCube, self.BottomLeftCoordY + self.LengthOfCube-i*self.LineOffset);
            self.heatLines.append(obp.Line(LeftCoord, RightCoord, self.BeamSpeed, self.Beam))
        # return self.heatLines
    
    def LRBT(self):
        '''Creates a cube of lines from left to right and bottom to top'''
        self.LRTB()
        self.heatLines.reverse()
        # return self.heatLines


    def RLTB(self):
        '''Creates a cube of lines from right to left and top to bottom'''
        for i in range(0,self.NumberOfLines):
            LeftCoord = obp.Point(self.BottomLeftCoordX, self.BottomLeftCoordY + self.LengthOfCube-i*self.LineOffset);
            RightCoord = obp.Point(self.BottomLeftCoordX + self.LengthOfCube, self.BottomLeftCoordY + self.LengthOfCube-i*self.LineOffset);
            self.heatLines.append(obp.Line(RightCoord, LeftCoord, self.BeamSpeed, self.Beam))
        # return self.heatLines

    def RLBT(self):
        '''Creates a cube of lines from right to left and bottom to top'''
        self.RLTB()
        self.heatLines.reverse()
        # return self.heatLines

    def TBLR(self):
        '''Creates a cube of lines from Top to bottom and left to right'''
        for i in range(0,self.NumberOfLines):
            TopCoord = obp.Point(self.BottomLeftCoordX+i*self.LineOffset, self.BottomLeftCoordY + self.LineOffset*self.NumberOfLines)
            BottomCoord = obp.Point(self.BottomLeftCoordX+i*self.LineOffset, self.BottomLeftCoordY)
            self.heatLines.append(obp.Line(TopCoord, BottomCoord, self.BeamSpeed, self.Beam))
        # return self.heatLines

    def TBRL(self):
         '''Creates a cube of lines from top to bottom and right to left'''
         self.TBLR()
         self.heatLines.reverse()
        #  return self.heatLines

    def BTLR(self):
        '''Creates a cube of lines from bottom to top and left to right'''
        for i in range(0,self.NumberOfLines):
            TopCoord = obp.Point(self.BottomLeftCoordX+i*self.LineOffset, self.BottomLeftCoordY + self.LineOffset*self.NumberOfLines)
            BottomCoord = obp.Point(self.BottomLeftCoordX+i*self.LineOffset, self.BottomLeftCoordY)
            self.heatLines.append(obp.Line(BottomCoord, TopCoord,  self.BeamSpeed, self.Beam))
        # return self.heatLines

    def BTRL(self):
         '''Creates a cube of lines from top to bottom and right to left'''
         self.BTLR()
         self.heatLines.reverse()
         if self.LineOrder == 1:
             return self.heatLines
         else:
             Lines = self.LineOrderShuffle()
             return Lines
        

    
    def LineOrderShuffle(self):

        orderList = self.heatLines
        order = self.LineOrder

        newlist=[]
        for i in range(order):
            for j in range(len(orderList)):
                if i+j*order < len(orderList):
                    newlist.append(orderList[i+j*order])

        return newlist
        




