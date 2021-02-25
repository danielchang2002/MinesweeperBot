import pyautogui
import keyboard
import numpy as np
from termcolor import colored
from piece import Piece
from time import sleep
from math import inf
import copy
import sys

class Board:
    def __init__(self, rows, cols, pieceWidth, pieceHeight, left, top):
        self.rows, self.cols = rows, cols
        self.setBoard()
        # set the matrix of digit colors
        self.colors = np.asarray([
            [189, 189, 189], # 0
            [0, 33, 245], # 1
            [53, 120, 32], # 2
            [234, 50, 35], # 3
            [5, 0, 123], # 4
            [123, 1, 0], # 5
            [255, 255, 255] # white, for the left region of unclicked piece
        ])
        # set the matrix of colors that will not predict zero
        self.colorsNo0 = np.asarray([
            [100000, 100000, 100000], # 0
            [0, 33, 245], # 1
            [53, 120, 32], # 2
            [234, 50, 35], # 3
            [5, 0, 123], # 4
            [123, 1, 0], # 5
            [255, 255, 255] # left of unclicked
        ])
        # set termcolor dictionary
        self.colorWord = {
            '0' : 'grey',
            '1' : 'blue',
            '2' : 'green',
            '3' : 'red',
            '4' : 'blue',
            '5' : 'red',
            '6' : 'white',
            'F' : 'cyan'
        }
        self.pieceWidth = pieceWidth
        self.pieceHeight = pieceHeight
        self.left = left
        self.top = top
        # set a board filled with false for the DFS
        self.falseBoard = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                row.append(False)
            self.falseBoard.append(row)

    def setBoard(self):
        '''
        Adds an instance of Piece to each position of the board. 
        Adds an adjacency list for each piece
        '''
        self.board = []
        # add a piece for each position
        for r in range(self.rows):
            row = [] 
            for c in range(self.cols):
                row.append(Piece(r, c))
            self.board.append(row)
        # add a list of neighbors for each piece, creates an adjacency list
        for r in range(self.rows):
            for c in range(self.cols):
                neighborsList = self.getNeighborsList(r, c)
                self.board[r][c].setNeighbors(neighborsList)
    
    def getNeighborsList(self, row, col):
        '''
        Returns an adjacency list for each position 
        '''
        l = []
        # add neighbor if in bounds and not itself
        for r in range(row - 1, row + 2):
            for c in range(col - 1, col + 2):
                if r < 0 or r >= self.rows or \
                    c < 0 or c >= self.cols or \
                        (r == row and c == col):
                    continue
                l.append(self.board[r][c])
        return l
    
    def updateBoard(self, img):
        '''
        Updates the board with the screenshot pixel colors.
        If flagged, does not update. Prints colored result 
        '''
        print()
        for row in range(self.rows):
            for col in range(self.cols):
                piece = self.board[row][col]
                result = None
                if (piece.flagged):
                    result = 'F'
                else:
                    result = self.getResult(img, row, col)
                    if result != 6:
                        piece.clicked = True
                        piece.numAround = result
                print(colored(result, self.colorWord[str(result)]), end=" ")
            print()
        print()
    
    def getResult(self, img, row, col):
        '''
        Returns the piece that is at row, col. Reads a small region
        of pixels near the center of each position. If the minimum squared error 
        is always for 0, checks if the tile is unclicked by reading the left
        part of the piece and checking if its white. Otherwise, returns the piece that 
        has the color that gives the lowest squared error
        '''
        centerX, centerY = (col * self.pieceWidth + 0.5 * self.pieceWidth, \
            row * self.pieceHeight + 0.50 * self.pieceHeight)
        allZero = True
        result = None
        lowestError = inf
        for y in range(int(centerY - self.pieceHeight * 0.10), int(centerY + self.pieceHeight * 0.10)):
            rgb = np.asarray(img.getpixel((self.left + centerX, self.top + y))[:3])
            err = np.sum(np.square(self.colors - rgb), axis=1, keepdims=True)
            res = np.argmin(err)
            if res != 0:
                allZero = False
            err = np.sum(np.square(self.colorsNo0 - rgb), axis=1, keepdims=True)
            res = np.argmin(err)
            if np.min(err) < lowestError:
                lowestError = np.min(err)
                result = res
        allZero2 = True
        if (allZero):
            result = 0
            for x in range(int(col * self.pieceWidth), int(col * self.pieceWidth + 0.2 * self.pieceWidth)):
                rgb = np.asarray(img.getpixel((self.left + x, self.top + centerY))[:3])
                err = np.sum(np.square(self.colors - rgb), axis=1, keepdims=True)
                res = np.argmin(err)
                if res != 0:
                    result = 6
                    break
        return result
    
    def move(self, img):
        '''
        Iterates through the clicked pieces on the board. 
        If the number of mines around is equal to the number of flagged
        pieces, clicks all unflagged neighbors. If the number of mines
        around is equal to the number of unclicked neighbors, flags
        all unflagged neighbors.
        '''
        didSomething = False
        for row in self.board:
            for piece in row:
                if not (piece.clicked and piece.numAround != 0):
                    continue
                numAround = piece.numAround
                unclicked = piece.getNumUnclickedAround()
                flagged = piece.getNumFlaggedAround()
                if numAround == flagged:
                    if self.clickUnflaggedNeighbors(piece):
                        didSomething = True
                if numAround == unclicked:
                    if self.flagUnflaggedNeighbors(piece):
                        didSomething = True
        if didSomething:
            return True
        return False
                    
    def getNonTrivial(self, img):
        '''
        Performs DFS to grab a list of connected components, where 
        the components are composed of pieces that are unclicked 
        and adjacent to a clicked piece. TODO: Enumerate all possible
        mine arrangements and return the piece with the lowest probability
        of having a bomb
        '''
        components = []
        visited = copy.deepcopy(self.falseBoard)
        partOfComponent = copy.deepcopy(self.falseBoard)
        for row in self.board:
            for piece in row:
                if visited[piece.row][piece.col] or piece.clicked \
                    or (not piece.hasClickedNeighbor()) or piece.flagged:
                    continue 
                component = []
                self.DFS(piece, visited, component, partOfComponent)
                components.append(component)
        for component in components:
            for piece in component:
                print(piece.row, piece.col)
            print()

        print()
        for row in range(self.rows):
            for col in range(self.cols):
                piece = self.board[row][col]
                result = None
                if (piece.flagged):
                    result = 'F'
                else:
                    result = self.getResult(img, row, col)
                    if result != 6:
                        piece.clicked = True
                        piece.numAround = result
                if partOfComponent[row][col]:
                    print(colored(result, self.colorWord[str(result)], 'on_red'), end=" ")
                else:
                    print(colored(result, self.colorWord[str(result)]), end=" ")
            print()
        print()
        shortest = min(components, key=len)

    def DFS(self, piece, visited, component, partOfComponent):
        '''
        DFS utility function 
        '''
        visited[piece.row][piece.col] = True
        if piece.clicked or (not piece.hasClickedNeighbor()) or \
            piece.flagged:
            return
        component.append(piece)
        partOfComponent[piece.row][piece.col] = True
        for p in piece.neighbors:
            if not visited[p.row][p.col]:
                self.DFS(p, visited, component, partOfComponent)

    def firstMove(self):
        '''
        Clicks in the center of the board 
        '''
        self.clickPiece(self.rows // 2, self.cols // 2, flag=False)
    
    def clickUnflaggedNeighbors(self, piece):
        '''
        Iterates through all the neighbors of the piece and clicks on
        the unflagged ones 
        '''
        didSomething = False
        for neighbor in piece.neighbors:
            if (not neighbor.flagged) and (not neighbor.clicked):
                neighbor.clicked = True
                self.clickPiece(neighbor.row, neighbor.col, flag=False)
                didSomething = True
        return didSomething
    
    def flagUnflaggedNeighbors(self, piece):
        '''
        Iterates through all the neighbors of the piece and flags on
        the unflagged unclicked ones 
        '''
        didSomething = False
        for neighbor in piece.neighbors:
            if not neighbor.flagged and (not neighbor.clicked):
                neighbor.flagged = True
                self.clickPiece(neighbor.row, neighbor.col, flag=True)
                didSomething = True
        return didSomething
                

    def clickPiece(self, row, col, flag):
        '''
        Clicks a piece given the row and column. Right clicks if flag 
        '''
        print("flagging: " if flag else "clicking: ", row, col)
        x, y = self.left + (col * self.pieceWidth) + (0.5 * self.pieceWidth), \
            self.top + (row * self.pieceHeight) + (0.5 * self.pieceHeight)
        x /= 2
        y /= 2
        pyautogui.click(x, y, button='right' if flag else 'left')