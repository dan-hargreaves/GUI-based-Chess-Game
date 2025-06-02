# -*- coding: utf-8 -*-
  
class Piece:
    '''
    A parent class for any piece type
    '''
    def __init__(self, loc, colour, text): 
        self.loc = loc
        self.colour = colour
        self.bg = 'light blue'
        self.text = text
        self.moved = False
        
    def __eq__(self, other):
        try:
            if self.loc==other.loc:
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
        self.loc=newLoc[:]
        self.moved=True
        return
    
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

class Pawn(Piece):
    def __init__(self, loc, colour):
        Piece.__init__(self, loc, colour, '♙')
        if self.colour == 'Black':
            self.rowChange = -1 
            self.homeRow = 6
        else:
            self.rowChange = 1
            self.homeRow = 1

    def possMoves(self, board):
        possMoves = []
        startRow = self.loc[0]
        startColumn = self.loc[1]
        if (not self.moved) and (board.empty([startRow+self.rowChange, startColumn]))and board.empty([startRow+2*self.rowChange, startColumn]):
            possMoves.append(board[startRow+2*self.rowChange, startColumn])

        x = board[startRow+self.rowChange, startColumn]
        if x.isEmpty():
            possMoves.append(x)
        x = board[startRow+self.rowChange, startColumn-1]
        if x != False:
            if not x.isEmpty():
                if x.colour != self.colour:
                    possMoves.append(x)
        x = board[startRow+self.rowChange, startColumn+1]
        if x != False:
            if not x.isEmpty():
                if x.colour != self.colour:
                    possMoves.append(x)
        return possMoves
          
class Bishop(Piece):
    def __init__(self, loc, colour):
        Piece.__init__(self, loc, colour, '♗')
        
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
        if colour=='White':
            self.kingDirection=-1
        else:
            self.kingDirection=1

    def possMoves(self, board):
        possMoves = []
        startRow = self.loc[0]
        startColumn = self.loc[1]
        for i in range(-1,2):
            for j in range(-1,2):
                square = board[startRow+i,startColumn+j]
                if square != False:
                    if square.__class__.__name__ == 'Empty':
                        possMoves.append(square)
                    elif square.colour != self.colour:
                        possMoves.append(square)
        if not self.moved: # Check whether the king can make a castle
            r=board[self.loc[0], 0]
            if self.checkCheck(board) == False:
                if r.__class__.__name__=='Rook' and r.moved==False:
                    pieces=self.scanAlong(board,0, -1)
                    if len(pieces)==3:
                        possMoves.append(board[self.loc[0], 2])
                r=board[self.loc[0], 7]
                if r.__class__.__name__=='Rook' and r.moved==False:
                    pieces=self.scanAlong(board,0, 1)
                    if len(pieces)==2:
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
        
    def possMoves(self, board):#compiles a list of squares to which a bishop, placed at that loc, can move to
        possMoves = []       
        possMovesBishop = getattr(Bishop, 'possMoves')
        possMovesRook = getattr(Rook, 'possMoves')
        possMoves += possMovesBishop(self, board)
        possMoves += possMovesRook(self, board)
        return possMoves
