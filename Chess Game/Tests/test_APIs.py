# # -*- coding: utf-8 -*-
from ChessGame import APIs
import unittest
from unittest.mock import MagicMock, patch

class APITestCases(unittest.TestCase):
    
    def test_client(self):
        
        # arrange 
        client = APIs.StockfishClient(timeout=10, max_retries=2)

        #act
        
        # assert
        
        
        test_cases = [
            # Starting position
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            # Tactical position
            "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 4"
        ]
        
        for i, fen in enumerate(test_cases, 1):
            print(f"\n=== Test Case {i} ===")
            try:
                result = client.analyze_position(fen, depth=10)
                print(f"Success: {result.success}")
                if result.success:
                    print(f"Best move: {result.best_move}")
                    print(f"Evaluation: {result.evaluation}")
                else:
                    print(f"Error: {result.error}")
            except Exception as e:
                print(f"Exception: {e}")
        
        client.close()