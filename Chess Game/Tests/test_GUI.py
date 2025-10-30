# -*- coding: utf-8 -*-

import ChessGame
import unittest, tkinter as tk
from unittest.mock import MagicMock, patch

class GUITestCase(unittest.TestCase):
               
    def setUp(self):
        # Create a real but hidden root window      
        self.patcher = patch("tkinter.Tk.mainloop", return_value = None)
        self.patcher.start()
        self.root = tk.Tk()
        self.root.withdraw()
        self.GUI = ChessGame.GUI(self.root)
        self.GUI.game = ChessGame.Game()
        
    def tearDown(self):
        self.patcher.stop()
        self.root.destroy()
        
    def test_WhenNewGame_CheckBoardColours(self):
        # arrange 
        pieces = [  ['R','H','B','' ,'K','' ,'' ,'R'],
                    ['' ,'' ,'P','P','P','P','P','P'],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'P','p','' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['p','p','' ,'p','p','p','p','p'],
                    ['r','h','b','q','k','b','h','r']]

        self.GUI.game = ChessGame.Game(pieces)

        #act 
        self.GUI.game.highlightMoves(self.GUI.game, self.GUI.game[0, 0]) #Select rook
        self.GUI.UI_chessBoard()

        # assert
        self.assertEqual(self.GUI.buttons[0][0].cget('bg'), "#f6f669")
        self.assertEqual(self.GUI.buttons[0][2].cget('bg'), "#769656")
        self.assertEqual(self.GUI.buttons[0][1].cget('bg'), "#eeeed2")
        self.assertEqual(self.GUI.buttons[1][0].cget('bg'), "#baca44")
        self.assertEqual(self.GUI.buttons[6][0].cget('bg'), "#f56c6c")
        
        # Ensure squares are highlighted pink for en passant
        #act
        self.GUI.game.deHighlightMoves()
        self.GUI.game[4, 2].doubleJumpedLastMove = True #Black advanced pawn double jumped last move
        self.GUI.game.highlightMoves(self.GUI.game, self.GUI.game[4, 1]) #Highlight white advanced pawn
        self.GUI.updateBoard()

        # assert
        self.assertEqual(self.GUI.buttons[5][2].cget('bg'), "#f56c6c")

    def test_WhenSelectTwoWhitePieces_CheckSecondPieceHighlighted(self):
        # arrange 
        self.GUI.UI_chessBoard()
        self.GUI.game.highlightMoves = MagicMock()

        #act 
        self.GUI.buttonPressed([1,1])
        self.GUI.buttonPressed([1,2])

        # assert
        self.assertEqual(self.GUI.game.highlightMoves.call_count, 2)

    def test_WhenNewGame_CheckTurnDisplayed(self):
        # arrange 
        self.GUI.displayTurn = MagicMock()
        self.GUI.viewBoard()

        #act 

        # assert
        self.assertEqual(self.GUI.displayTurn.call_count, 1)
        
    def test_WhenNewGame_CheckMoveNumberDisplayed(self):
        # arrange 
        self.GUI.displayMoveNumber = MagicMock()
        self.GUI.viewBoard()
        
        #act 

        # assert
        self.assertEqual(self.GUI.displayMoveNumber.call_count, 1)

    def test_WhenSwitchTurns_BoardOrientationFlips(self):
        # arrange 
        self.GUI.UI_chessBoard()
        
        # assert
        self.assertEqual(self.GUI.buttons[1][0].cget('fg'), 'White')
        self.assertEqual(self.GUI.rank_labels[0].cget('text'), '8')
        self.assertEqual(self.GUI.file_labels[0].cget('text'), 'a')
        
        #act 
        self.GUI.flipBoardEachTurn.set(True)
        self.GUI.game.turn = 'Black'
        self.GUI.game.highlightMoves(self.GUI.game, self.GUI.game[6, 1])#Highlight black pawn b7
        self.GUI.updateBoard()

        # assert
        self.assertEqual(self.GUI.buttons[1][7].cget('fg'), 'Black')
        self.assertEqual(self.GUI.buttons[2][6].cget('bg'), '#baca44') # Square in front of highlighted pawn
        self.assertEqual(self.GUI.rank_labels[0].cget('text'), '1')
        self.assertEqual(self.GUI.file_labels[0].cget('text'), 'h')

        #act 
        self.GUI.flipBoardEachTurn.set(False)
        self.GUI.game.turn = 'Black'
        self.GUI.updateBoard()
        
        # assert
        self.assertEqual(self.GUI.buttons[1][0].cget('fg'), 'White')
        self.assertEqual(self.GUI.rank_labels[0].cget('text'), '8')
    
    def test_WhenCheckPosition_CheckMessagePrinted(self):
        # arrange 
        pieces = [  ['R','H','B','' ,'K','' ,'' ,'R'],
                    ['P','P','P','P','P','' ,'P','P'],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'q'],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                    ['p','p','p','p','p','p','p','p'],
                    ['r','h','b','q','k','b','h','r']]

        self.GUI = ChessGame.GUI()
        self.GUI.game = ChessGame.Game(pieces)
        self.GUI.printTxt = MagicMock()
        self.GUI.textbox = MagicMock()
        self.GUI.textbox_turn = MagicMock()
        self.GUI.textbox_move = MagicMock()
        self.GUI.game.turn = 'White'
         
        # act 
        self.GUI.endOfMove() 
           
        # assert
        self.GUI.printTxt.assert_called_with('White is in check!')
        
    def test_WhenNewGameVSComputer_CheckPlayComputerCalled(self):
        # arrange 
        self.GUI.game.turn = 'White' 
        self.GUI.game.whitePlayer.type = 'computer'
        self.GUI.playComputerMove = MagicMock()

    
        # act 
        self.GUI.playGame()
           
        # assert
        self.assertEqual(self.GUI.playComputerMove.call_count, 1)