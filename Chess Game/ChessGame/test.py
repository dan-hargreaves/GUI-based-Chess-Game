import ChessGame
# arrange 
pieces = [  ['r','h','b','' ,'k','' ,'' ,'r'],
            ['p','p','p','p','' ,'p','p','p'],
            ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
            ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
            ['' ,'' ,'' ,'P','p','P','' ,'' ],
            ['' ,'' ,'' ,'' ,'' ,'' ,'' ,'' ],
            ['P','P','P','' ,'P','' ,'P','P'],
            ['R','H','B','Q','K','B','H','R']]

game = ChessGame.Game(pieces)

#act 
game[[4,3]].doubleJumpedLastMove = True #Black queen pawn jumped 2 last move
game[[4,5]].doubleJumpedLastMove = False #Black king-side bishop pawn did not jump 2 last move
# assert
for i in game[[4, 4]].possMoves(game):
    print(i.loc)
