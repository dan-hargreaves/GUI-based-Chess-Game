# -*- coding: utf-8 -*-
  
class Piece:
    '''
    A parent class for any piece type
    '''
    def __init__(self, loc, colour, display_text): 
        self.loc = loc
        self.colour = colour
        self.bg = 0
        self.display_text = display_text
        self.moved = False
        self.enPassantSquare = False
        
    def __eq__(self, other):
        try:
            if self.loc == other.loc:
                return True
            else:
                return False
        except:
            return False
        
    def checkLegal(self, game,  moveTo):#This checks to see if a pawn type move has been legally made
        for move in self.possMoves(game):
            if move.loc == moveTo.loc:
                return True
        
        return False
    
    def changeLoc(self, newLoc):
        self.loc = newLoc[:]
        self.moved = True
        return
    
    def algebraicLoc(self):
        return chr(97 + self.loc[1]) + str(self.loc[0] + 1)
    
    def scanAlong(self, board, rowScan, columnScan):
        #This function will scan along the board in a given direction from a start point and return all the pieces along that direction which could be moved to/ taken
        piece = True
        possPieces = []
        startRow = self.loc[0]
        startColumn = self.loc[1]
        i = 1
        while piece != False:
            piece = board[startRow+i*rowScan, startColumn+i*columnScan]
            if piece != False:
                if piece.__class__.__name__ == 'Empty':
                    possPieces.append(piece)
                elif piece.colour != self.colour:
                    possPieces.append(piece)
                    piece = False
                else:
                    piece = False
            i += 1
        return possPieces
    
    def isEmpty(self):
        if self.text =="":
            return True
        else:
            return False
     
class Empty(Piece):
    '''
    A parent class for any piece type
    '''
    def __init__(self,loc):
        Piece.__init__(self, loc, 'red', "")
        self.text = ''
        
class Pawn(Piece):
    def __init__(self, loc, colour):
        Piece.__init__(self, loc, colour, '♙')
        self.doubleJumpedLastMove = False
        if self.colour == 'Black':
            self.text = 'p'
            self.rowChange = -1 
            self.homeRow = 6
        else:
            self.text = 'P'
            self.rowChange = 1
            self.homeRow = 1
            
    def changeLoc(self, newLoc):
        if self.__class__.__name__ == 'Pawn' and abs(newLoc[0] - self.loc[0]) == 2:
            self.doubleJumpedLastMove = True
        else: 
            self.doubleJumpedLastMove = False
        self.loc = newLoc[:]
        self.moved = True
        return

    def possMoves(self, board):
        possMoves = []
        startRow = self.loc[0]
        startColumn = self.loc[1]
        
        #Move 2 forward
        if (not self.moved) and (board.empty([startRow + self.rowChange, startColumn]))and board.empty([startRow + 2*self.rowChange, startColumn]):
            possMoves.append(board[startRow + 2*self.rowChange, startColumn])

        #Move 1 forward
        square_moveTo = board[startRow + self.rowChange, startColumn]
        if square_moveTo.isEmpty():
            possMoves.append(square_moveTo)
            
        #Take forward left    
        square_moveTo = board[startRow + self.rowChange, startColumn - 1]
        if square_moveTo != False:
            if not square_moveTo.isEmpty():
               if square_moveTo.colour != self.colour:
                    possMoves.append(square_moveTo)
                    
        #Take forward right     
        square_moveTo = board[startRow + self.rowChange, startColumn + 1]
        if square_moveTo != False:
            if not square_moveTo.isEmpty():
                if square_moveTo.colour != self.colour:
                    possMoves.append(square_moveTo)
                    
        #En Passant forward left    
        square_moveTo = board[startRow + self.rowChange, startColumn - 1]
        if square_moveTo != False:
            if square_moveTo.isEmpty():
               possibleEnPassantPawn = board[startRow, startColumn - 1]
               if possibleEnPassantPawn.__class__.__name__ == 'Pawn':
                   if possibleEnPassantPawn.colour != self.colour and possibleEnPassantPawn.doubleJumpedLastMove == True:
                       square_moveTo.enPassantSquare = True
                       possMoves.append(square_moveTo)
                                          
         #En Passant forward right    
        square_moveTo = board[startRow + self.rowChange, startColumn + 1]
        if square_moveTo != False:
            if square_moveTo.isEmpty():
               possibleEnPassantPawn = board[startRow, startColumn + 1]
               if possibleEnPassantPawn.__class__.__name__ == 'Pawn':
                   if possibleEnPassantPawn.colour != self.colour and possibleEnPassantPawn.doubleJumpedLastMove == True:
                       square_moveTo.enPassantSquare = True
                       possMoves.append(square_moveTo)
        return possMoves
          
class Bishop(Piece):
    def __init__(self, loc, colour):
        Piece.__init__(self, loc, colour, '♗')
        if self.colour == 'Black':
            self.text = 'b'
        else:
            self.text = 'B'
    def possMoves(self, board):#compiles a list of squares to which a bishop, placed at that loc, can move to
        possMoves = []       
        possMoves += self.scanAlong(board, -1, -1)
        possMoves += self.scanAlong(board, -1, 1)
        possMoves += self.scanAlong(board, 1, -1)
        possMoves += self.scanAlong(board, 1, 1)
        return possMoves
    
class Knight(Piece):
    def __init__(self,  loc, colour):
        Piece.__init__(self, loc, colour, '♘')
        if self.colour == 'Black':
            self.text = 'n'
        else:
            self.text = 'N'
            
    def possMoves(self, board):
        possMoves = []
        startRow = self.loc[0]
        startColumn = self.loc[1]
        for i in [-2,2]:
            for j in [-1,1]:
                square = board[startRow+i, startColumn+j]
                if square != False:
                    if square.__class__.__name__ == 'Empty':
                        possMoves.append(square)
                    elif square.colour != self.colour:
                        possMoves.append(square)
        for i in [-1,1]:
            for j in [-2,2]:
                square = board[startRow+i, startColumn+j]
                if square != False:
                    if square.__class__.__name__ == 'Empty':
                        possMoves.append(square)
                    elif square.colour != self.colour:
                        possMoves.append(square)
        return possMoves

class Rook(Piece):
    def __init__(self, loc, colour):
        Piece.__init__(self, loc, colour, '♖')
        if self.colour == 'Black':
            self.text = 'r'
        else:
            self.text = 'R'
            
    def possMoves(self, board):#compiles a list of squares to which a bishop, placed at that loc, can move to
        possMoves = []       
        possMoves += self.scanAlong(board, 0, -1)
        possMoves += self.scanAlong(board, 0, 1)
        possMoves += self.scanAlong(board, 1, 0)
        possMoves += self.scanAlong(board, -1, 0)
        return possMoves

class King(Piece):
    def __init__(self, loc, colour):
        Piece.__init__(self, loc, colour, '♔')
        if colour == 'White':
            self.text = 'K'
            self.kingDirection = -1
        else:
            self.text = 'k'
            self.kingDirection = 1

    def possMoves(self, board):
        possMoves = []
        startRow = self.loc[0]
        startColumn = self.loc[1]
        for i in range(-1, 2):
            for j in range(-1, 2):
                square = board[startRow + i, startColumn + j]
                if square != False:
                    if square.__class__.__name__ == 'Empty':
                        possMoves.append(square)
                    elif square.colour != self.colour:
                        possMoves.append(square)
        if not self.moved: # Check whether the king can make a castle
            r = board[self.loc[0], 0]
            if self.checkCheck(board) == False:
                if r.__class__.__name__== 'Rook' and r.moved == False:
                    pieces = self.scanAlong(board, 0, -1)
                    if len(pieces) == 3:
                        possMoves.append(board[self.loc[0], 2])
                r = board[self.loc[0], 7]
                if r.__class__.__name__ == 'Rook' and r.moved == False:
                    pieces = self.scanAlong(board, 0, 1)
                    if len(pieces) == 2:
                        possMoves.append(board[self.loc[0], 6])
        return possMoves

    def checkCheck(self, board):
        #check for Bishops, Pawns (and queens)
        moves = getattr(Bishop, 'possMoves')
        possMoves = moves(self, board)
        for piece in possMoves:
            if piece.__class__.__name__ == 'Bishop' and piece.colour != self.colour:
                return True
            if piece.__class__.__name__ == 'Queen' and piece.colour != self.colour:
                return True
            if piece.__class__.__name__ == 'Pawn' and piece.colour!= self.colour and (self.loc[0]-piece.loc[0])==piece.rowChange:
                return True
        #check for rooks ( and queens)
        moves = getattr(Rook, 'possMoves')
        possMoves = moves(self, board)
        for piece in possMoves:
            if piece.__class__.__name__ == 'Rook' and piece.colour != self.colour:
                return True
            if piece.__class__.__name__ == 'Queen' and piece.colour != self.colour:
                return True
        #check for knights
        moves = getattr(Knight, 'possMoves')
        possMoves = moves(self, board)
        for piece in possMoves:
            if piece.__class__.__name__ == 'Knight' and piece.colour != self.colour:
                return True    
        return False

class Queen(Piece):
    def __init__(self, loc, colour):
        Piece.__init__(self, loc, colour, '♕')
        if self.colour == 'Black':
            self.text = 'q'
        else:
            self.text = 'Q'
            
    def possMoves(self, board):#compiles a list of squares to which a bishop, placed at that loc, can move to
        possMoves = []       
        possMovesBishop = getattr(Bishop, 'possMoves')
        possMovesRook = getattr(Rook, 'possMoves')
        possMoves += possMovesBishop(self, board)
        possMoves += possMovesRook(self, board)
        return possMoves