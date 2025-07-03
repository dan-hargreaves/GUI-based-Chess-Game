import ChessGame
# arrange 
pieces = [  ['' ,'' ,'' ,'' ,'k','' ,'' ,'' ],
            ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
            ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
            ['p','' ,'' ,'' ,'' ,'' ,'' ,'' ],
            ['P','' ,'' ,'' ,'q','' ,'' ,'' ],
            ['' ,'' ,'' ,'' ,'' ,'q','' ,'' ],
            ['' ,'' ,'' ,'' ,'' ,'q','R','' ],
            ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'K']]

game = ChessGame.Game(pieces)
GUI = ChessGame.GUI()
GUI.game = game
GUI.game.turn = 'White'
# GUI.game.checkGameOver()
GUI.viewBoard()

# #act 
# game[[4,3]].doubleJumpedLastMove = True #Black queen pawn jumped 2 last move
# game[[4,5]].doubleJumpedLastMove = False #Black king-side bishop pawn did not jump 2 last move
# # assert
# for i in game[[4, 4]].possMoves(game):
#     print(i.loc)



