# -*- coding: utf-8 -*-
import tkinter as tk
from ChessGame.Game import *
import pickle
import datetime
import os

class GUI():
    def __init__(self):
        self.savedGames=[]
        self.buttons = []
        self.root = tk.Tk()
        self.root.geometry('600x600')
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.root.destroy())
    
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
        
    def playGame(self, game):
        self.clear()
        self.buttons = []
        self.game=game
        self.viewBoard()
        return
    
    def updateButtons(self):
        for i in range(8):
            row = []
            for j in range(8):
                piece=self.game[i,j]
                b=tk.Button(
                        self.root, 
                        text=piece.text,
                        fg=piece.colour,
                        bg=self.backgroundColour(piece),
                        height=2, 
                        width=4, 
                        font='Helvetica 16 bold',
                        command=lambda loc=[i,j]: self.buttonPressed(loc)
                )
                b.grid(row=7-i, column=j)# Flip board to show white at bottom.
                row.append(b)
            self.buttons.append(row)
            
    def backgroundColour(self, piece):
        selected_piece_colour = "light green"
        black_square_colour = "royal blue"
        white_square_colour = "wheat1"
        possible_move_colour = "gold"
        possible_capture_colour = "pink"
        if piece.bg == 0:
            if (piece.loc[0]+piece.loc[1]) % 2 == 0:
                colour = black_square_colour
            else:
                colour = white_square_colour
        elif piece.bg == 1:
            colour = selected_piece_colour
        elif piece.bg == 2:
            colour = possible_move_colour
        elif piece.bg == 3:
            colour = possible_capture_colour
        return colour
    
    def viewBoard(self):
        self.clear()
        self.updateButtons()
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
                        bg=self.backgroundColour(piece),
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
                piece = self.game[i, j]
                self.buttons[i][j].config(
                    text=piece.text,
                    bg=self.backgroundColour(piece),
                    fg=piece.colour
                    )
        self.root.mainloop()
        return
    
    def buttonPressed(self, loc):
        piece = self.game[loc]
        if self.game.first==None:
            # Player is selecting the piece to move
            legal, errorString = self.game.checkSelection(piece)
            if legal == True:
                self.game.first = piece
                self.game.highlightMoves(self, piece)
                self.updateBoard()
            else:
                self.printTxt(errorString)
        else:
            # Player is selecting the square to move to
            if piece.loc == self.game.first.loc:
                self.game.first = None
                self.game.second = None
                self.game.deHighlightMoves()
                self.updateBoard()
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
    
    def getPlayersButton(self, top, tb1, tb2):
        game = Game()
        wName = tb1.get("1.0","end-1c")
        bName = tb2.get("1.0","end-1c")
        game.createGameCode(wName, bName)
        top.destroy()
        self.playGame(game)
        
    def newGameMenu(self):
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
                      self.getPlayersButton(top, tb1, tb2)
            ).grid(row=3,column=0,columnspan=2)
        top.mainloop()
             
    def mainMenu(self):
        self.clear()
        tk.Label(self.root, text="Welcome to Dan Hargreaves's chess game!").grid(row=0,column=0,columnspan=2)
        tk.Button(self.root, text='New Game',height=2, width=10, command=self.newGameMenu).grid(row=1,column=0)
        tk.Button(self.root, text='Saved Games',height=2, width=10, command=self.savedGamesMenu).grid(row=1,column=1)
        self.root.mainloop()