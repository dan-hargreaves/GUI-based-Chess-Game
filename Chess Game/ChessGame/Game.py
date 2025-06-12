# -*- coding: utf-8 -*-

#A continuation of my chess game but using object oriented methods
# import tkinter as tk
# import pickle
import datetime
from ChessGame.Pieces import *
# import os

####################  Define my pieces  #############################
class Game:
    '''
    A class which contains one instance of a game. 
    '''
    def __init__(self, pieces=None):
        self.gameOver = False
        self.winner = None
        self.wName = '' # Name of white player
        self.bName = '' # Name of black player
        self.winMethod='' # String which holds the way in which player won (e.g. 'checkmate')     
        self.board = [] # A matrix of all the pieces in the board
        self.first = None # The first piece that the player has clicked (on button press)
        self.second = None # The second piece the palyer has clicked
        self.turn = 'White' # The curren turn
        self.saved=False # Records whether the player has chosen to save the game
        
        if pieces == None:
            pieces=[['r','h','b','q','k','b','h','r'],
                    ['p','p','p','p','p','p','p','p'],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['P','P','P','P','P','P','P','P'],
                    ['R','H','B','Q','K','B','H','R']]
        
                    
        for i in range(8):
            # Loop through the board and create all the piece objects.
            row = []
            for j in range(8):
                _piece = pieces[i][j]
                if _piece == '':
                    piece = Empty([i,j])   
                elif _piece == 'P':
                    piece = Pawn([i,j], 'Black')
                elif _piece == 'p':
                    piece = Pawn([i,j], 'White')
                elif _piece == 'B':
                    piece = Bishop([i,j], 'Black')
                elif _piece == 'b':
                    piece = Bishop([i,j], 'White')
                elif _piece == 'H':
                    piece = Knight([i,j], 'Black')
                elif _piece == 'h':
                    piece =Knight([i,j], 'White')
                elif _piece == 'R':
                    piece =Rook([i,j], 'Black')
                elif _piece == 'r':
                    piece =Rook([i,j], 'White')
                elif _piece == 'K':
                    piece=King([i,j], 'Black')
                    self.blackKing = piece
                elif _piece == 'k':
                    piece = King([i,j], 'White')
                    self.whiteKing= piece
                elif _piece == 'Q':
                    piece =Queen([i,j], 'Black')
                else:
                    piece =Queen([i,j], 'White')
                row.append(piece)
            self.board.append(row)
        return
    
    def createGameCode(self, wName, bName):
        '''
        Parameters
        ----------
        wName : string
            White player name.
        bName : string
            Black player name.

        Returns
        -------
        None.
        
        Creates a unique game code for a chess game. Used to generate a unique file name.

        '''
        time=datetime.datetime.strftime(datetime.datetime.now(),"%Y_%m_%d_%H_%M_%S")
        self.gameCode= wName + '_' + bName + '_' + time
        return
    
    def checkMove(self):
        '''

        Returns
        -------
        legal : Bool
            Whether or not the move was legal.
        errorString : string
            A string describing the type of error the player has made.

        
        Checks whether the players move is legal. First checks that they are moving their own piece and not taking their own piece. 
        Then checks whether the moved piece can move like that, and whether the move puts the player in check.
        '''
        legal = False
        errorString=''
        if self.first.colour == self.second.colour:#Can't take ones own piece
            errorString="You can't take your own piece"
        elif self.movesIntoCheck():
            errorString='That move puts you in check'
        elif not self.first.checkLegal(self, self.second):#Check if the piece can move that way
            errorString="That piece can't move that way"
        else:
            legal=True
        return legal, errorString
    
    def checkSelection(self, piece):
        legal = False
        errorString=''
        if piece.__class__.__name__ == 'Empty':
            errorString = 'Invalid selection'
        elif piece.colour != self.turn:
            errorString = 'You must select your own piece'
        else:
            legal=True
        return legal, errorString 
    
    def movesIntoCheck(self):
        '''

        Returns
        -------
        inCheck : Bool
            Whether or not the proposed move puts the player in check.

        Checks whether the move will place the current player in check. Makes the players move, tests whether 
        the player is in check and then undoes the move.
        '''
        first  = self.first
        firstLoc=self.first.loc[:] # Make a value copy, not a reference copy
        second = self.second
        self.first.loc = second.loc[:]#moves first piece to loc of second
        self[second.loc]=self.first 
        self[firstLoc] = Empty(first.loc)#adds an empyty square where the first piece was
        inCheck = self.inCheck()
        self.first.loc=firstLoc[:]
        self[second.loc]=second
        self[first.loc]=first
        return inCheck
    
    def inCheck(self):
        '''

        Returns
        -------
        TYPE Bool
            Checks whether the current player is in check in the current layout.
        '''
        king=self.currKing()
        return king.checkCheck(self)
    
    def switchTurn(self):
        if self.turn =='White':
            self.turn= 'Black'
        else:
            self.turn = 'White' 
        return

    def makeMove(self):
        '''
        

        Returns
        -------
        promotePawn : TYPE
            DESCRIPTION.

        '''
        promotePawn = False
        firstLoc = self.first.loc
        self.savedLoc = firstLoc # Need this saved for GUI.promotePawn() method
        secondLoc = self.second.loc
        self[secondLoc] = self[firstLoc] 
        self.first.changeLoc(secondLoc)
        self[firstLoc] = Empty(firstLoc)#adds an empyty square where the first piece was
        if self.first.__class__.__name__ == 'King' and abs(firstLoc[1] - secondLoc[1]) == 2:
            # Check if king is making a castling move. If so, then swap the rook
            if secondLoc[1]==2:
                self[secondLoc[0], 0], self[secondLoc[0], 3] = self[secondLoc[0], 3], self[secondLoc[0], 0]
            else:
                self[secondLoc[0], 7], self[secondLoc[0], 5] = self[secondLoc[0], 5], self[secondLoc[0], 7]     
        elif self.first.__class__.__name__ == 'Pawn' and self.second.loc[0] == (self.first.homeRow + 6*self.first.rowChange):
            promotePawn = True
            
        return promotePawn
    
    def promotePawn(self, piece_name):
        if piece_name == 'Queen':
            self[self.second.loc] = Queen(self.second.loc, self.turn)
        elif piece_name == 'Knight':
            self[self.second.loc] = Knight(self.second.loc, self.turn)
        elif piece_name == 'Bishop':
            self[self.second.loc] = Bishop(self.second.loc, self.turn)
        else:
            self[self.second.loc] = Rook(self.second.loc, self.turn)
        self[self.savedLoc] = Empty(self.savedLoc)
 
    def checkGameOver(self):
        '''
        Returns
        -------
        bool
            Checks whether the game is over. Loops through every piece on the board, and calculates every move the current player can 
            do. If none of the players moves take them out of check, then the game is over.

        '''
        first = self.first
        second = self.second
        for row in self.board:
            for piece in row: # Loop through board
                if piece.colour == self.turn: # Look only at current players pieces
                    self.first = piece
                    for x in piece.possMoves(self): # Look at possible moves by the piece in question
                        self.second = x
                        if self.movesIntoCheck() == False: # Check whether the move puts the current player in check.
                            self.first = first
                            self.second = second
                            return False # If any move does not put the player in check, then return for efficiency.
        self.first = first
        self.second = second
        self.gameOver=True
        self.winMethod='checkmate'
        self.switchTurn()
        self.winner=self.turn
        return True
    
    def resign(self):
        self.switchTurn()
        self.winner = self.turn
        self.winMethod = 'resignation'
        self.gameOver = True
        
    def __getitem__(self, loc):
        if loc[0]>7 or loc[0]<0 or loc[1]>7 or loc[1]<0:
            return False
        else:
            return self.board[loc[0]][loc[1]]
        
    def __setitem__(self,x, value):
        self.board[x[0]][x[1]]=value
        
  
    def currKing(self):
        if self.turn == 'White':
            return  self.whiteKing
        else:
            return  self.blackKing
    
    def empty(self, loc):
        if self[loc].__class__.__name__ == 'Empty':
            return True
        else:
            return False
 
    def highlightMoves(self, board, selectedPiece):
        possMoves = selectedPiece.possMoves(self)
        for piece in possMoves:
            if  not piece.isEmpty():
                if piece.colour != self.turn:
                    piece.bg = 3
            else:
                piece.bg = 2
        selectedPiece.bg = 1
        return

    def deHighlightMoves(self):
        for row in self.board:
            for piece in row:
                piece.bg = 0
        return