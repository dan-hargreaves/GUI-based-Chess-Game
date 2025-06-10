# -*- coding: utf-8 -*-


import pytest, sys, ChessGame, unittest, tkinter as tk
from unittest.mock import MagicMock

#  PAWN
#  Happy path
def test_MovePawnTwoForward_WhenNewGame_CheckMoveReturnTrue():
    MovePiece_WhenNewGame_CheckMoveValid([1, 0], [3, 0], (True, ""))
    
#  Sad path
def test_MovePawnThreeForward_WhenNewGame_CheckMoveReturnFalse():
    MovePiece_WhenNewGame_CheckMoveValid([1, 0], [4, 0],  (False, "That piece can't move that way"))
  
#  ROOK
#  Sad path
def test_MoveRookForward_WhenNewGame_CheckMoveReturnTrue():
    MovePiece_WhenNewGame_CheckMoveValid([0, 2], [1, 3], (False, "You can't take your own piece"))
    
#  KNIGHT
#  Happy path
def test_MoveKnightForwardTwoRight_WhenNewGame_CheckMoveReturnTrue():
    MovePiece_WhenNewGame_CheckMoveValid([0, 1], [2, 2], (True, ""))
    
#  Sad path
def test_MoveKnightForwardThreeRight_WhenNewGame_CheckMoveReturnFalse():
    MovePiece_WhenNewGame_CheckMoveValid([0, 1], [3, 2], (False, "That piece can't move that way"))

#  BISHOP
#  Sad path
def test_MoveBishopForwardRight_WhenNewGame_CheckMoveReturnFalse():
    MovePiece_WhenNewGame_CheckMoveValid([0, 2], [1, 3], (False, "You can't take your own piece"))

#  QUEEN
#  Sad path
def test_MoveQueenForwardRight_WhenNewGame_CheckMoveReturnFalse():
    MovePiece_WhenNewGame_CheckMoveValid([0, 3], [1, 4], (False, "You can't take your own piece"))
    
#  KING
#  Happy path
def test_CastleKingside_WhenNothingBetween_CheckMoveReturnTrue():
    pieces = [  ['r','h','b','' ,'k','' ,'' ,'r'],
                ['p','p','p','p','p','p','p','p'],
                ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                ['P','P','P','P','P','P','P','P'],
                ['R','H','B','Q','K','B','H','R']]
    MovePiece_WhenNewGame_CheckMoveValid([0, 4], [0, 6], (True, ""), pieces)

#  Sad path
def test_CastleKingside_KingInCheck_CheckMoveReturnTrue():
    # arrange 
    pieces = [  ['r','h','b','' ,'k','' ,'' ,'r'],
                ['p','p','p','p','Q','p','p','p'],
                ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                ['P','P','P','P','P','P','P','P'],
                ['R','H','B','Q','K','B','H','R']]
    
    GUI = ChessGame.GUI()
    GUI.game = ChessGame.Game(pieces)

    #act 
    
    # assert
    assert [0, 6] not in GUI.game[[0, 4]].possMoves(GUI.game)
    
def test_MoveKingForwardLeft_WhenNewGame_CheckMoveReturnFalse():
    MovePiece_WhenNewGame_CheckMoveValid([0, 4], [1, 3], (False, "You can't take your own piece"))
    
    
def MovePiece_WhenNewGame_CheckMoveValid(first, second, result, pieces=None):
    # arrange 
    GUI = ChessGame.GUI()
    if pieces == None:
        GUI.game = ChessGame.Game()
    else:
        GUI.game = ChessGame.Game(pieces)

    #act 
    GUI.game.first = GUI.game[first]
    GUI.game.second = GUI.game[second]
    
    # assert
    assert GUI.game.checkMove() == result
    
    #  Sad path
def test_MoveBlackPiece_WhenNewGame_CheckSelectionReturnFalse():
    MovePiece_WhenNewGame_CheckSelectionValid([6,0], (False, "You must select your own piece"))
    
    #  Sad path
def test_MoveEmpty_WhenNewGame_CheckSelectionReturnFalse():
    MovePiece_WhenNewGame_CheckSelectionValid([4,0], (False, "Invalid selection"))
    
def MovePiece_WhenNewGame_CheckSelectionValid(first, result):
    # arrange 
    GUI = ChessGame.GUI()
    GUI.game = ChessGame.Game()

    #act 
    GUI.game.first = GUI.game[first]
    
    # assert
    assert GUI.game.checkSelection(GUI.game.first) == result
    
# Happy path
def test_loadGame_WhenCheckmatePosition_CheckCheckmateTrue():
    # arrange 
    pieces = [  ['r','h','b','' ,'k','' ,'' ,'r'],
                ['p','p','p','p','Q','p','p','p'],
                ['' ,'' ,'' ,'' ,'Q','' ,'' ,'' ],
                ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                ['P','P','P','P','P','P','P','P'],
                ['R','H','B','Q','K','B','H','R']]
    GUI = ChessGame.GUI()
    GUI.game = ChessGame.Game(pieces)
    GUI.buttons = []

def test_WhenNewGame_CheckBoardColours():
    # arrange 
    pieces = [  ['r','h','b','' ,'k','' ,'' ,'r'],
                ['' ,'p','p','p','p','p','p','p'],
                ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
                ['P','P','P','P','P','P','P','P'],
                ['R','H','B','Q','K','B','H','R']]
    GUI = ChessGame.GUI()
    GUI.game = ChessGame.Game(pieces)

    #act 
    GUI.game.highlightMoves(GUI.game, GUI.game[[0,0]])
    GUI.updateButtons()
    
    # assert
    assert GUI.buttons[0][0].cget('bg') == "light green"
    assert GUI.buttons[0][2].cget('bg') == "royal blue"
    assert GUI.buttons[0][1].cget('bg') == "wheat1"
    assert GUI.buttons[1][0].cget('bg') == "gold"
    assert GUI.buttons[6][0].cget('bg') == "pink"
    
test_WhenNewGame_CheckBoardColours()