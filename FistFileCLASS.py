import obplib as obp

class MeltCube:
    def __init__(self, LengthOfCube, LineOffset, BottomLeftCoordX, BottomLeftCoordY, Power, BeamSpeed, SpotSize):
        self.LengthOfCube = LengthOfCube
        self.LineOffset = LineOffset # LineOffset in um
        self.BottomLeftCoordX = BottomLeftCoordX #
        self.BottomLeftCoordY = BottomLeftCoordY
        self.Power = Power #Power in watt int
        self.BeamSpeed = BeamSpeed
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
            self.MeltLines.append(obp.Line(LeftCoord, RightCoord, self.BeamSpeed, self.Beam))
        return self.MeltLines
    
    def LRBT(self):
        '''Creates a cube of lines from left to right and bottom to top'''
        self.LRTB()
        self.MeltLines.reverse()
        return self.MeltLines


    def RLTB(self):
        '''Creates a cube of lines from right to left and top to bottom'''
        for i in range(0,self.NumberOfLines+1):
            LeftCoord = obp.Point(self.BottomLeftCoordX, self.BottomLeftCoordY + self.LengthOfCube-i*self.LineOffset);
            RightCoord = obp.Point(self.BottomLeftCoordX + self.LengthOfCube, self.BottomLeftCoordY + self.LengthOfCube-i*self.LineOffset);
            self.MeltLines.append(obp.Line(RightCoord, LeftCoord, self.BeamSpeed, self.Beam))
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
            self.MeltLines.append(obp.Line(TopCoord, BottomCoord, self.BeamSpeed, self.Beam))
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
            self.MeltLines.append(obp.Line(BottomCoord, TopCoord,  self.BeamSpeed, self.Beam))
        return self.MeltLines

    def BTRL(self):
         '''Creates a cube of lines from top to bottom and right to left'''
         self.BTLR()
         self.MeltLines.reverse()
         return self.MeltLines




