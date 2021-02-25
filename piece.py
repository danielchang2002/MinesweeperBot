
class Piece:
    def __init__(self, row, col):
        self.clicked = False
        self.numAround = -1
        self.flagged = False
        self.row, self.col = row, col

    def setNeighbors(self, neighbors):
        self.neighbors = neighbors

    def getNumFlaggedAround(self):
        num = 0
        for n in self.neighbors:
            num += 1 if n.flagged else 0
        return num
    
    def getNumUnclickedAround(self):
        num = 0
        for n in self.neighbors:
            num += 0 if n.clicked else 1
        return num
    
    def hasClickedNeighbor(self):
        for n in self.neighbors:
            if n.clicked:
                return True
        return False