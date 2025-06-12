# -*- coding: utf-8 -*-


import pytest, sys, ChessGame, unittest, tkinter as tk
from unittest.mock import MagicMock

class MovePiecesTestCase(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        cls.game = ChessGame.Game()
        cls.GUI = ChessGame.GUI()
        cls.GUI.game = cls.game
        
    def MovePiece_WhenNewGame_CheckMoveValid(self, first, second, result, pieces=None):
        # arrange 
        if pieces != None:
            self.game = ChessGame.Game(pieces)
        
        #act 
        self.game.first = self.game[first]
        self.game.second = self.game[second]
        
        # assert
        self.assertEqual(self.game.checkMove(), result)
        
    def MovePiece_WhenNewGame_CheckSelectionValid(self, first, result):
        # arrange 
    
        #act 
        self.GUI.game.first = self.GUI.game[first]
        
        # assert
        self.assertEqual(self.GUI.game.checkSelection(self.GUI.game.first), result)
        
    #  PAWN
    #  Happy path
    def test_MovePawnTwoForward_WhenNewGame_CheckMoveReturnTrue(self):
        self.MovePiece_WhenNewGame_CheckMoveValid([1, 0], [3, 0], (True, ""))
        
    #  Sad path
    def test_MovePawnThreeForward_WhenNewGame_CheckMoveReturnFalse(self):
        self.MovePiece_WhenNewGame_CheckMoveValid([1, 0], [4, 0],  (False, "That piece can't move that way"))
      
     #  ROOK
     #  Sad path
    def test_MoveRookForward_WhenNewGame_CheckMoveReturnTrue(self):
        self.MovePiece_WhenNewGame_CheckMoveValid([0, 2], [1, 3], (False, "You can't take your own piece"))
     
     #  KNIGHT
     #  Happy path
    def test_MoveKnightForwardTwoRight_WhenNewGame_CheckMoveReturnTrue(self):
        self.MovePiece_WhenNewGame_CheckMoveValid([0, 1], [2, 2], (True, ""))
     
     #  Sad path
    def test_MoveKnightForwardThreeRight_WhenNewGame_CheckMoveReturnFalse(self):
        self.MovePiece_WhenNewGame_CheckMoveValid([0, 1], [3, 2], (False, "That piece can't move that way"))
    
     #  BISHOP
     #  Sad path
    def test_MoveBishopForwardRight_WhenNewGame_CheckMoveReturnFalse(self):
        self.MovePiece_WhenNewGame_CheckMoveValid([0, 2], [1, 3], (False, "You can't take your own piece"))
    
     #  QUEEN
     #  Sad path
    def test_MoveQueenForwardRight_WhenNewGame_CheckMoveReturnFalse(self):
        self.MovePiece_WhenNewGame_CheckMoveValid([0, 3], [1, 4], (False, "You can't take your own piece"))
     
     #  KING
     #  Happy path
    def test_CastleKingside_WhenNothingBetween_CheckMoveReturnTrue(self):
        pieces = [  ['r','h','b','' ,'k','' ,'' ,'r'],
                    ['p','p','p','p','p','p','p','p'],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['P','P','P','P','P','P','P','P'],
                    ['R','H','B','Q','K','B','H','R']]
        self.MovePiece_WhenNewGame_CheckMoveValid([0, 4], [0, 6], (True, ""), pieces)
    
      #  Sad path
    def test_CastleKingside_KingInCheck_CheckMoveReturnTrue(self):
        # arrange 
        pieces = [  ['r','h','b','' ,'k','' ,'' ,'r'],
                    ['p','p','p','p','Q','p','p','p'],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['P','P','P','P','P','P','P','P'],
                    ['R','H','B','Q','K','B','H','R']]
    
        game = ChessGame.Game(pieces)
    
        #act 
         
        # assert
        self.assertNotIn([0, 6], game[[0, 4]].possMoves(game))
     
    def test_MoveKingForwardLeft_WhenNewGame_CheckMoveReturnFalse(self):
        self.MovePiece_WhenNewGame_CheckMoveValid([0, 4], [1, 4], (False, "You can't take your own piece"))
    
        #  Sad path
    def test_MoveBlackPiece_WhenNewGame_CheckSelectionReturnFalse(self):
        self.MovePiece_WhenNewGame_CheckSelectionValid([6,0], (False, "You must select your own piece"))
        
        #  Sad path
    def test_MoveEmpty_WhenNewGame_CheckSelectionReturnFalse(self):
        self.MovePiece_WhenNewGame_CheckSelectionValid([4,0], (False, "Invalid selection"))
        
    
    # Happy path
    def test_loadGame_WhenCheckmatePosition_CheckCheckmateTrue(self):
        # arrange 
        pieces = [  ['r','h','b','' ,'k','' ,'' ,'r'],
                    ['p','p','p','p','Q','p','p','p'],
                    ['' ,'' ,'' ,'' ,'Q','' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['P','P','P','P','P','P','P','P'],
                    ['R','H','B','Q','K','B','H','R']]
        game = ChessGame.Game(pieces)
        self.assertEqual(game.checkGameOver(), True)#
        
    def test_WhenPromotePawnToQueen_CheckPromotionSuccessful(self):
        # arrange 
        pieces = [  ['r','h','b','' ,'k','' ,'' ,'r'],
                    ['' ,'p','p','p','p','p','p','p'],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['P','P','P','P','P','P','p','P'],
                    ['R','H','B','Q','K','B','H','R']]

        game = ChessGame.Game(pieces)

        #act 
        game.first = game[[6, 6]]
        game.second = game[[7, 7]]
        game.makeMove()
        game.promotePawn('Queen')
        
        # assert
        self.assertIsInstance(game[[7, 7]], ChessGame.Pieces.Queen)
        self.assertIsInstance(game[[6, 6]], ChessGame.Pieces.Empty)
        
    def test_WhenWhiteResigns_CheckBlackWon(self):
        # arrange 

        #act 
        self.game.resign()
        
        # assert
        self.assertEqual(self.game.gameOver, True)
        self.assertEqual(self.game.winner, 'Black')
        self.assertEqual(self.game.winMethod, 'resignation')

        
class GUITestCase(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        cls.game = ChessGame.Game()
        cls.GUI = ChessGame.GUI()
        cls.GUI.game = cls.game    
        
    def test_WhenNewGame_CheckBoardColours(self):
        # arrange 
        pieces = [  ['r','h','b','' ,'k','' ,'' ,'r'],
                    ['' ,'p','p','p','p','p','p','p'],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['P','P','P','P','P','P','P','P'],
                    ['R','H','B','Q','K','B','H','R']]

        self.GUI.game = ChessGame.Game(pieces)

        #act 
        self.GUI.game.highlightMoves(self.GUI.game, self.GUI.game[[0,0]]) #Select rook
        self.GUI.updateButtons()
        
        # assert
        self.assertEqual(self.GUI.buttons[0][0].cget('bg'), "light green")
        self.assertEqual(self.GUI.buttons[0][2].cget('bg'), "royal blue")
        self.assertEqual(self.GUI.buttons[0][1].cget('bg'), "wheat1")
        self.assertEqual(self.GUI.buttons[1][0].cget('bg'), "gold")
        self.assertEqual(self.GUI.buttons[6][0].cget('bg'), "pink")
    

