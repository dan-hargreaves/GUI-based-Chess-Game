# -*- coding: utf-8 -*-

import ChessGame
import unittest, tkinter as tk
from unittest.mock import MagicMock, patch

class PieceTestCases(unittest.TestCase):
    def CheckAlgebraicLocation_WhenA1H8Rook_CheckAlebraicLocCorrect(self):
        # arrange 
        piece = ChessGame.Pieces.Rook([0, 0], 'White')
        piece2 = ChessGame.Pieces.Queen([7, 7], 'White')
        
        #act
        
        # assert
        self.assertEqual(piece.algebraicLoc(), 'a1')
        self.assertEqual(piece2.algebraicLoc(), 'h8')
