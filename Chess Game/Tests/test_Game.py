# -*- coding: utf-8 -*-

import ChessGame
import unittest, tkinter as tk
from unittest.mock import MagicMock, patch

class GameTestCases(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        cls.game = ChessGame.Game()
        
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
        self.game.first = self.game[first]
        
        # assert
        self.assertEqual(self.game.checkSelection(self.game.first), result)
        
    #  PAWN
    #  Happy path
    def test_MovePawnTwoForward_WhenNewGame_CheckMoveReturnTrue(self):
        self.MovePiece_WhenNewGame_CheckMoveValid([1, 0], [3, 0], (True, ""))
        
    def test_CheckEnPassant_WhenInPosition(self):
        # arrange 
        pieces = [ ['R','H','B','' ,'K','' ,'' ,'R'],
                   ['P','P','P','P','' ,'P','P','P'],
                   ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                   ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                   ['' ,'' ,'' ,'p','P','p','' ,'' ],
                   ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                   ['p','p','p','' ,'p','' ,'p','p'],
                   ['r','h','b','q','k','b','h','r']]

        game = ChessGame.Game(pieces)

        #act 
        game[4,3].doubleJumpedLastMove = True #Black queen pawn jumped 2 last move
        game[4,5].doubleJumpedLastMove = False #Black king-side bishop pawn did not jump 2 last move
        # assert
        self.assertIn(game[5, 3], game[4, 4].possMoves(game))
        self.assertNotIn(game[5, 5], game[4, 4].possMoves(game))
        
    def test_CheckPawnRemoved_WhenPawnTakesEnPassant(self):
        # arrange 
        pieces = [ ['R','H','B','' ,'K','' ,'' ,'R'],
                   ['P','P','P','P','' ,'P','P','P'],
                   ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                   ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                   ['' ,'' ,'' ,'p','P','' ,'' ,'' ],
                   ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                   ['p','p','p','' ,'p','' ,'p','p'],
                   ['r','h','b','q','k','b','h','r']]

        game = ChessGame.Game(pieces)
        game[4,3].doubleJumpedLastMove = True #Black queen pawn jumped 2 last move
        self.game = game
        
        #act 
        self.game.first = self.game[4,4]
        self.game.second = self.game[5,3]
        self.game.makeMove()
        
        # assert
        self.assertEqual(self.game[4, 3].__class__.__name__, 'Empty')
        
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
        pieces = [ ['R','H','B','' ,'K','' ,'' ,'R'],
                   ['P','P','P','P','P','P','P','P'],
                   ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                   ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                   ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                   ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                   ['p','p','p','p','p','p','p','p'],
                   ['r','h','b','q','k','b','h','r']]
        self.MovePiece_WhenNewGame_CheckMoveValid([0, 4], [0, 6], (True, ""), pieces)
    
      #  Sad path
    def test_CastleKingside_KingInCheck_CheckMoveReturnTrue(self):
        # arrange 
        pieces = [ ['R','H','B','' ,'K','' ,'' ,'R'],
                   ['P','P','P','P','q','P','P','P'],
                   ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                   ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                   ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                   ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                   ['p','p','p','p','p','p','p','p'],
                   ['r','h','b','q','k','b','h','r']]
    
        game = ChessGame.Game(pieces)
    
        #act 
         
        # assert
        self.assertNotIn(game[0, 6], game[0, 4].possMoves(game))
     
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
        pieces = [  ['R','H','B','' ,'K','' ,'' ,'R'],
                    ['P','P','P','P','q','P','P','P'],
                    ['' ,'' ,'' ,'' ,'q','' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['p','p','p','p','p','p','p','p'],
                    ['r','h','b','q','k','b','h','r']]
        game = ChessGame.Game(pieces)
        
        # Act
        game.checkGameOver()
        
        # Assert
        self.assertEqual(game.gameOver, True)
        self.assertEqual(game.winMethod, 'checkmate')

        
    # Happy path
    def test_loadGame_WhenStalematePosition_CheckStalemateTrue(self):
        # arrange 
        pieces = [  ['' ,'' ,'' ,'' ,'K','' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['P','' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['p','' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'Q','' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'k']]
        game = ChessGame.Game(pieces)
        game.turn = 'Black'
                
        # Act
        game.checkGameOver()
        
        # Assert
        self.assertEqual(game.gameOver, True)
        self.assertEqual(game.winMethod, 'stalemate')

        
        # arrange 

        game = ChessGame.Game(pieces)   
        pieces = [  ['' ,'' ,'' ,'' ,'K','' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['P','' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['p','' ,'' ,'' ,'' ,'Q','' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'Q','' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'Q','r','' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'k']]
        game.turn = 'Black'
                
        # Act
        game.checkGameOver()
        
        # Assert
        self.assertEqual(game.gameOver, True)
        self.assertEqual(game.winMethod, 'stalemate')

        
    # Sad path    
    def test_loadGame_WhenStalematePosition_CheckStalemateFalse(self):
        # arrange 
        pieces = [  ['' ,'' ,'' ,'' ,'K','' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['p','' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'Q','' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'k']]
        game = ChessGame.Game(pieces)
        game.turn = 'Black'
        self.assertEqual(game.gameOver, False)    
        self.assertEqual(game.winMethod, '')

        
    def test_WhenPromotePawnToQueen_CheckPromotionSuccessful(self):
        # arrange 
        pieces = [  ['R','H','B','' ,'K','' ,'' ,'R'],
                    ['' ,'P','P','P','P','P','P','P'],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['p','p','p','p','p','p','P','p'],
                    ['r','h','b','q','k','b','h','r']]


        game = ChessGame.Game(pieces)

        #act 
        game.first = game[6, 6]
        game.second = game[7, 7]
        game.makeMove()
        game.promotePawn('Queen')
        
        # assert
        self.assertIsInstance(game[7, 7], ChessGame.Pieces.Queen)
        self.assertIsInstance(game[6, 6], ChessGame.Pieces.Empty)
        
    def test_WhenWhiteResigns_CheckBlackWon(self):
        # arrange 

        #act 
        self.game.resign()
        
        # assert
        self.assertEqual(self.game.gameOver, True)
        self.assertEqual(self.game.winner, 'Black')
        self.assertEqual(self.game.winMethod, 'resignation')

    def test_WhenChangeTurn_CheckMoveNumberCorrect(self):
        # arrange 
        self.game = ChessGame.Game()
        
        # assert
        self.assertEqual(self.game.moveNumber, 1)
        
        #act 
        self.game.switchTurn()
        
        # assert
        self.assertEqual(self.game.moveNumber, 1)
        
        #act 
        self.game.switchTurn()
        
        # assert
        self.assertEqual(self.game.moveNumber, 2)
        
    def test_CheckFENStringCorrect_WhenNewGame(self):
        # arrange 
        self.game = ChessGame.Game()
        
        # assert
        self.assertEqual(self.game.FEN_string(), 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')       

        # act 
        self.game.first = self.game[1, 4]
        self.game.second = self.game[[3, 4]]
        self.game.makeMove()
        
        # assert
        self.assertEqual(self.game.FEN_string(), 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1')    
        
        # act 
        self.game.first = self.game[6, 2]
        self.game.second = self.game[[4, 2]]
        self.game.makeMove()
        
        # assert
        self.assertEqual(self.game.FEN_string(), 'rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2')       