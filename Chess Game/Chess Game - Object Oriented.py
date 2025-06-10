#A continuation of my chess game but using object oriented methods
import tkinter as tk
import pickle
import datetime
import os

####################  Define my pieces  #############################
class Game:
    '''
    A class which contains one instance of a game. 
    '''
    def __init__(self):
        self.gameOver = False
        self.winner = None
        self.wName = '' # Name of white player
        self.bName = '' # Name of black player
        self.winMethod='' # String which holds the way in which player won (e.g. 'checkmate')     
        self.board = [] # A matrix of all the pieces in the board
        self.first = None # The first piece that the player has clicked (on button press)
        self.second = None # The second piece the palyer has clicked
        self.turn = 'White' # The curren turn
        self.saved=False # Records whether the player has chosen to save the game
        # ['r','h','b','q','k','b','h','r'],
        # ['p','p','p','p','p','p','p','p'],
        # ['', '', '', '', '', '', '', '' ],
        # ['', '', '', '', '', '', '', '' ],
        # ['', '', '', '', '', '', '', '' ],
        # ['', '', '', '', '', '', '', '' ],
        # ['P','P','P','P','P','P','P','P'],
        # ['R','H','B','Q','K','B','H','R']]
        pieces = [
                  ['r','','','','k','','','r'],
                  ['p','p','p','p','','p','p','p'],
                  ['','','','','','','',''],
                  ['','','','','','','','q'],
                  ['','','','','','','',''],
                  ['','','','','','q','',''],
                  ['P','p','P','P','P','','','P'],
                  ['R','H','B','Q','K','B','H','R']]
        for i in range(8):
            # Loop through the board and create all the piece objects.
            row = []
            for j in range(8):
                _piece = pieces[i][j]
                if _piece == '':
                    piece = Empty([i,j])   
                elif _piece == 'P':
                    piece = Pawn([i,j], 'Black')
                elif _piece == 'p':
                    piece = Pawn([i,j], 'White')
                elif _piece == 'B':
                    piece = Bishop([i,j], 'Black')
                elif _piece == 'b':
                    piece = Bishop([i,j], 'White')
                elif _piece == 'H':
                    piece = Knight([i,j], 'Black')
                elif _piece == 'h':
                    piece =Knight([i,j], 'White')
                elif _piece == 'R':
                    piece =Rook([i,j], 'Black')
                elif _piece == 'r':
                    piece =Rook([i,j], 'White')
                elif _piece == 'K':
                    piece=King([i,j], 'Black')
                    self.blackKing = piece
                elif _piece == 'k':
                    piece = King([i,j], 'White')
                    self.whiteKing= piece
                elif _piece == 'Q':
                    piece =Queen([i,j], 'Black')
                else:
                    piece =Queen([i,j], 'White')
                row.append(piece)
            self.board.append(row)
        return
    
    def createGameCode(self, wName, bName):
        '''
        Parameters
        ----------
        wName : string
            White player name.
        bName : string
            Black player name.

        Returns
        -------
        None.
        
        Creates a unique game code for a chess game. Used to generate a unique file name.

        '''
        time=datetime.datetime.strftime(datetime.datetime.now(),"%Y_%m_%d_%H_%M_%S")
        self.gameCode= wName+'_'+bName+'_'+time
        return
    
    def checkMove(self):
        '''

        Returns
        -------
        legal : Bool
            Whether or not the move was legal.
        errorString : string
            A string describing the type of error the player has made.

        
        Checks whether the players move is legal. First checks that they are moving their own piece and not taking their own piece. 
        Then checks whether the moved piece can move like that, and whether the move puts the player in check.
        '''
        legal = False
        errorString=''
        if self.first.colour == self.second.colour:#Can't take ones own piece
            errorString="You can't take your own piece"
        elif self.movesIntoCheck():
            errorString='That move puts you in check'
        elif not self.first.checkLegal(self, self.second):#Check if the piece can move that way
            errorString="That piece can't move that way"
        else:
            legal=True
        return legal, errorString
     
    def movesIntoCheck(self):
        '''

        Returns
        -------
        inCheck : Bool
            Whether or not the proposed move puts the player in check.

        Checks whether the move will place the current player in check. Makes the players move, tests whether 
        the player is in check and then undoes the move.
        '''
        first  = self.first
        firstLoc=self.first.loc[:] # Make a value copy, not a reference copy
        second = self.second
        self.first.loc = second.loc[:]#moves first piece to loc of second
        self[second.loc]=self.first 
        self[firstLoc] = Empty(first.loc)#adds an empyty square where the first piece was
        inCheck = self.inCheck()
        self.first.loc=firstLoc[:]
        self[second.loc]=second
        self[first.loc]=first
        return inCheck
    
    def inCheck(self):
        '''

        Returns
        -------
        TYPE Bool
            Checks whether the current player is in check in the current layout.
        '''
        king=self.currKing()
        return king.checkCheck(self)
    
    def switchTurn(self):
        if self.turn =='White':
            self.turn= 'Black'
        else:
            self.turn = 'White' 
        return

    def makeMove(self):
        '''
        

        Returns
        -------
        promotePawn : TYPE
            DESCRIPTION.

        '''
        promotePawn=False
        firstLoc = self.first.loc
        self.savedLoc=firstLoc # Need this saved for GUI.promotePawn() method
        secondLoc = self.second.loc
        self[secondLoc]=self[firstLoc] 
        self.first.changeLoc(secondLoc)
        self[firstLoc] = Empty(firstLoc)#adds an empyty square where the first piece was
        if self.first.__class__.__name__=='King' and abs(firstLoc[1]-secondLoc[1])==2:
            # Check if king is making a castling move. If so, then swap the rook
            if secondLoc[1]==2:
                self[secondLoc[0], 0], self[secondLoc[0], 3] = self[secondLoc[0], 3], self[secondLoc[0], 0]
            else:
                self[secondLoc[0], 7], self[secondLoc[0], 5] = self[secondLoc[0], 5], self[secondLoc[0], 7]     
        elif self.first.__class__.__name__=='Pawn' and self.second.loc[0]==(self.first.homeRow+6*self.first.rowChange):
            promotePawn=True
        return promotePawn
 
    def checkGameOver(self):
        '''
        Returns
        -------
        bool
            Checks whether the game is over. Loops through every piece on the board, and calculates every move the current player can 
            do. If none of the players moves take them out of check, then the game is over.

        '''
        first = self.first
        second = self.second
        for row in self.board:
            for piece in row: # Loop through board
                if piece.colour == self.turn: # Look only at current players pieces
                    self.first = piece
                    for x in piece.possMoves(self): # Look at possible moves by the piece in question
                        self.second = x
                        if self.movesIntoCheck() == False: # Check whether the move puts the current player in check.
                            self.first = first
                            self.second = second
                            return False # If any move does not put the player in check, then return for efficiency.
        self.first = first
        self.second = second
        self.gameOver=True
        self.winMethod='checkmate'
        self.switchTurn()
        self.winner=self.turn
        return True
        
    def __getitem__(self, loc):
        if loc[0]>7 or loc[0]<0 or loc[1]>7 or loc[1]<0:
            return False
        else:
            return self.board[loc[0]][loc[1]]
        
    def __setitem__(self,x, value):
        self.board[x[0]][x[1]]=value
        
  
    def currKing(self):
        if self.turn == 'White':
            return  self.whiteKing
        else:
            return  self.blackKing
    
    def empty(self, loc):
        if self[loc].__class__.__name__ == 'Empty':
            return True
        else:
            return False
 
    def highlightMoves(self, board, selectedPiece):
        possMoves = selectedPiece.possMoves(self)
        for piece in possMoves:
            if  not piece.isEmpty():
                if piece.colour != self.turn:
                    piece.bg = 'pink'
            else:
                piece.bg = 'light yellow'
        selectedPiece.bg = 'light green'
        return

    def deHighlightMoves(self):
        for row in self.board:
            for piece in row:
                piece.bg = 'light blue'
        return
    
    
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
        
    def checkLegal(self, board,  moveTo):#This checks to see if a pawn type move has been legally made
        for move in self.possMoves(board):
            if move.loc==moveTo.loc:
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

class GUI():
    def __init__(self):
        self.savedGames=[]
        self.root = tk.Tk()
        self.root.geometry('600x600')
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.root.destroy())
        self.mainMenu()
    
    def saveGame(self):
        self.game.saved=True
        fName=self.game.gameCode+'.chess'
        with open(fName, 'wb') as f:
            pickle.dump(self.game, f, protocol=pickle.HIGHEST_PROTOCOL)
        self.mainMenu()
        
    def clear(self):
        for child in self.root.winfo_children():
            child.destroy()
        
        for x in self.root.grid_slaves():
            x.destroy()
    
    def getPlayerNames(self, fileName):
        '''
        Parameters
        ----------
        fileName : string
            The name of the game (.chess) file in question.

        Returns
        -------
        wName : string
            White player name, from fileName.
        bName : string
            Black player name, from fileName.

        '''
        n=fileName.find('_')
        wName=fileName[:n]
        n1=fileName.find('_',n+1) 
        bName=fileName[n+1:n1]
        return wName, bName
        
    def savedGamesMenu(self):
        self.clear()
        filePaths = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.chess')]
        numGames = len(filePaths)
        if numGames >0:
            tk.Label(self.root, text='Saved games').grid(row=0, column=0)
            options=[]
            for i in range(numGames):
                fileName=filePaths[i]
                wName, bName=self.getPlayerNames(fileName)
                options.append(str(i)+': '+wName+' vs ' +bName)
                
            variable = tk.StringVar(self.root)
            variable.set(options[0]) # default value
            w = tk.OptionMenu(self.root, variable, *options)
            w.grid(row=1,column=0)
            tk.Button(
                self.root, 
                text='Open game', 
                command=lambda:
                    self.viewSavedGame(filePaths[int(variable.get()[:1])])
                    ).grid(row=2,column=0)
        else:
            tk.Label(self.root, text='No saved games').grid(row=0, column=0)
            tk.Button(self.root, text='Main menu', command=self.mainMenu).grid(row=1, column=0)
            
    def viewSavedGame(self, fileName):
        with open(fileName, "rb") as openfile:
            game=pickle.load(openfile)
            
        if game.gameOver:
            self.viewBoard_inactive(game)
        else:
            self.playGame(game)
            
    def newGame(self):
        x = Game()
        self.getPlayers(x)
        self.mainMenu()
        
    def playGame(self, game):
        self.clear()
        self.buttons = []
        self.game=game
        self.viewBoard()
        return
    
    def viewBoard(self):
        self.clear()
        for i in range(8):
            row = []
            for j in range(8):
                piece=self.game[i,j]
                b=tk.Button(
                        self.root, 
                        text=piece.text,
                        fg=piece.colour,
                        bg=piece.bg,
                        height=2, 
                        width=4, 
                        font='Helvetica 16 bold',
                        command=lambda loc=[i,j]: self.buttonPressed(loc)
                )
                b.grid(row=7-i, column=j)# Flip board to show white at bottom.
                row.append(b)
            self.buttons.append(row)
            
        self.textbox=tk.Text(self.root, height=4, width=30)
        self.textbox.grid(row=8, column=0, columnspan=4, rowspan=2)
        tk.Button(self.root, text='Save Game', height=2, width=16, command=self.saveGame).grid(row=8, column=6, columnspan=2)
        if not self.game.gameOver:
            tk.Button(self.root, text='Resign', height=2, width=16, command=self.resignButton).grid(row=9, column=6, columnspan=2)
        tk.Button(self.root, text='Main Menu', height=2, width=16, command=self.askSave).grid(row=9, column=4, columnspan=2)
        self.root.mainloop()
        return
    
    def askSave(self):
        if not self.game.saved:
            top=tk.Toplevel(self.root)
            tk.Label(top, text='Do you wish to save your game?').grid(row=0,column=0,columnspan=2)
            tk.Button(top, text='Yes',command=self.saveGame).grid(row=1,column=0)
            tk.Button(top, text='No', command=self.mainMenu).grid(row=1,column=1)
            top.mainloop()
        else:
            self.saveGame()
        return
    
    def viewBoard_inactive(self, game):
        self.clear()
        tk.Label(text=game.winner+' won by '+game.winMethod).grid(row=0,column=0, columnspan=8)
        for i in range(8):
            for j in range(8):
                piece=game[i, j]
                b=tk.Label(
                        self.root, 
                        text=piece.text,
                        fg=piece.colour,
                        bg=piece.bg,
                        height=2, 
                        width=4, 
                        font='Helvetica 16 bold',
                        relief='solid',
                        borderwidth=1
                )
                b.grid(row=8-i, column=j)# Flip board to show white at bottom.
        tk.Button(self.root, text='Main Menu', height=2, width=16, command=self.mainMenu).grid(row=9, column=0, columnspan=3)
        tk.Button(self.root, text='Saved Games', height=2, width=16, command=self.savedGamesMenu).grid(row=9, column=3, columnspan=3)
        self.root.mainloop()
        return
        
    def resignButton(self):
        self.game.switchTurn()
        self.game.winner=self.game.turn
        self.game.winMethod='resignation'
        self.game.gameOver=True
        self.gameOverBox()
        
    def updateBoard(self):
        #This funciton will display the board to the user or update it when called.
        for i in range(8):
            for j in range(8):
                p=self.game[i, j]
                self.buttons[i][j].config(
                    text=p.text,
                    bg=p.bg,
                    fg=p.colour
                    )
        self.root.mainloop()
        return
    
    def buttonPressed(self, loc):
        piece=self.game[loc]
        if self.game.first==None:
            # Player is selecting the piece to move
            if piece.__class__.__name__ == 'Empty':
                self.printTxt('Invalid selection')
            elif piece.colour != self.game.turn:
                self.printTxt('Invalid selection')
            else:
                self.game.first = piece
                self.game.highlightMoves(self, piece)
        else:
            # Player is selecting the square to move to
            if piece.loc == self.game.first.loc:
                self.game.first = None
                self.game.second = None
                self.game.deHighlightMoves()
            else:
                self.game.second = piece
                self.checkMove()
                
        self.updateBoard()
        return
    
    def checkMove(self):
        legal, errorString = self.game.checkMove()
        if not legal:
            self.game.first = None
            self.game.second = None
            self.game.deHighlightMoves()
            self.printTxt(errorString)
        else:
            promotePawn=self.game.makeMove() 
            if promotePawn:
                self.promotePawn()
            self.endOfMove()
        return
    
    def promotePawn(self):
        top = tk.Toplevel(self.root)
        tk.Label(top, text='Pawn promotion. Choose your piece').grid(row=0,column=0,columnspan=2)
        tk.Button(top, text='Queen', command=lambda window=top: self.promotionButton(window,'Queen')).grid(row=1,column=0)
        tk.Button(top, text='Knight', command=lambda window=top: self.promotionButton(window,'Knight')).grid(row=1,column=1)
        tk.Button(top, text='Bishop', command=lambda window=top: self.promotionButton(window,'Bishop')).grid(row=2,column=0)
        tk.Button(top, text='Rook', command=lambda window=top: self.promotionButton(window,'Rook')).grid(row=2,column=1)
        top.mainloop()
        return
    
    def promotionButton(self, window, text):
        if text == 'Queen':
            self.game[self.game.second.loc]=Queen(self.game.second.loc, self.game.turn)
        elif text == 'Knight':
            self.game[self.game.second.loc]=Knight(self.game.second.loc, self.game.turn)
        elif text == 'Bishop':
            self.game[self.game.second.loc]=Bishop(self.game.second.loc, self.game.turn)
        else:
            self.game[self.game.second.loc]=Rook(self.game.second.loc, self.game.turn)
        
        self.game[self.game.savedLoc]=Empty(self.game.savedLoc)
        window.destroy()
        self.endOfMove()
        self.updateBoard()
        return
    
    def endOfMove(self):
        self.clearTxt()
        self.game.deHighlightMoves()
        self.game.switchTurn()
        self.game.first=None
        self.game.second=None
        if self.game.inCheck():
            if self.game.checkGameOver():
                self.game.switchTurn()
                self.printTxt(self.game.turn+ ' wins!')
                self.gameOverBox()
            else:
                self.printTxt(self.game.turn+ ' is in check! \n'+self.game.turn+' to move.')
        else:
            self.printTxt(self.game.turn+' to move.')
        return
    
    def gameOverBox(self):
        top =tk.Toplevel(self.root)
        tk.Label(top, text=self.game.turn+' won by ' +self.game.winMethod).pack()
        tk.Button(top,
                  text='Close',
                  command=lambda window=top: self.gameOverButton(window)
                  ).pack()
        top.mainloop()
        return
        
    def gameOverButton(self, window):
        window.destroy()
        self.viewBoard()
        return
    
    def printTxt(self, text):
        self.textbox.configure(state='normal')
        self.textbox.insert('end', text+'\n')
        self.textbox.config(state='disabled')
        return
    
    def clearTxt(self):
        self.textbox.configure(state='normal')
        self.textbox.delete('1.0', 'end')
        self.textbox.config(state='disabled')
       
    def on_closing(self):
        self.root.destroy()
        
    def getPlayers(self, game):
        top=tk.Toplevel(self.root)
        tk.Label(top, text='Enter the player names').grid(row=0,column=0,columnspan=2)
        tk.Label(top, text='Player 1:').grid(row=1,column=0)
        tb1=tk.Text(top, height=1, width=16)
        tb1.grid(row=1,column=1)
        tk.Label(top, text='Player 2:').grid(row=2,column=0)
        tb2=tk.Text(top, height=1,width=16)
        tb2.grid(row=2,column=1)
        tk.Button(top,
                  text='Enter',
                  command=lambda:
                      self.getPlayersButton(top, game, tb1, tb2)
            ).grid(row=3,column=0,columnspan=2)
        top.mainloop()
        return
    
    def getPlayersButton(self, top, game, tb1, tb2):
        wName=tb1.get("1.0","end-1c")
        bName=tb2.get("1.0","end-1c")
        game.createGameCode(wName, bName)
        top.destroy()
        self.playGame(game)
             
    def mainMenu(self):
        self.clear()
        tk.Label(self.root, text="Welcome to Dan Hargreaves's chess game!").grid(row=0,column=0,columnspan=2)
        tk.Button(self.root, text='New Game',height=2, width=10, command=self.newGame).grid(row=1,column=0)
        tk.Button(self.root, text='Saved Games',height=2, width=10, command=self.savedGamesMenu).grid(row=1,column=1)
        self.root.mainloop()
a=GUI()