# -*- coding: utf-8 -*-
import tkinter as tk
from ChessGame.Game import *
import pickle
import datetime
import os
import random

class GUI():
    def __init__(self, root = None):
        self.savedGames = []
        self.buttons = []
        if root == None:
            self.root = tk.Tk()
        else:
            self.root = root
        self.flipBoardEachTurn = tk.BooleanVar(value = False)
        self.root.geometry('800x600')
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.root.destroy())
    
    def saveGame(self):
        self.game.saved = True
        fName = self.game.gameCode + '.chess'
        with open(fName, 'wb') as f:
            pickle.dump(self.game, f, protocol = pickle.HIGHEST_PROTOCOL)
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
        n = fileName.find('_')
        wName = fileName[ : n]
        n1 = fileName.find('_', n + 1) 
        bName = fileName[n + 1 : n1]
        return wName, bName
        
    def savedGamesMenu(self):
        self.clear()
        tk.Button(self.root, text = 'Main menu', command = self.mainMenu).grid(row = 1, column = 1)
        filePaths = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.chess')]
        numGames = len(filePaths)
        if numGames > 0:
            tk.Label(self.root, text = 'Saved games').grid(row = 0, column = 0)
            options = []
            for i in range(numGames):
                fileName = filePaths[i]
                wName, bName = self.getPlayerNames(fileName)
                options.append(str(i) + ': ' + wName + ' vs ' + bName)
                
            variable = tk.StringVar(self.root)
            variable.set(options[0]) # default value
            w = tk.OptionMenu(self.root, variable, *options)
            w.grid(row = 1, column = 0)
            tk.Button(
                self.root, 
                text = 'Open game', 
                command = lambda:
                    self.viewSavedGame(filePaths[int(variable.get()[:1])])
                    ).grid(row = 2, column = 0)
        else:
            tk.Label(self.root, text = 'No saved games').grid(row = 0, column = 0)
            
    def viewSavedGame(self, fileName):
        
        with open(fileName, "rb") as openfile:
            game = pickle.load(openfile)
            
        if game.gameOver:
            self.viewBoard_inactive(game)
        else:
            self.playGame(game)
        
    def playGame(self, game):
        self.clear()
        self.buttons = []
        self.game = game
        self.viewBoard()
        return
      
    def backgroundColour(self, piece):
        selected_piece_colour = "light green"
        black_square_colour = "royal blue"
        white_square_colour = "wheat1"
        possible_move_colour = "gold"
        possible_capture_colour = "pink"
        if piece.bg == 0:
            if (piece.loc[0] + piece.loc[1]) % 2 == 0:
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
    
    def askSave(self):
        if not self.game.saved:
            top = tk.Toplevel(self.root)
            tk.Label(top, text = 'Do you wish to save your game?').grid(row = 0, column = 0, columnspan = 2)
            tk.Button(top, text = 'Yes', command = self.saveGame).grid(row = 1, column = 0)
            tk.Button(top, text = 'No', command = self.mainMenu).grid(row = 1, column = 1)
            top.mainloop()
        else:
            self.saveGame()
        return    
    
    def resignButton(self):
        self.game.resign()
        self.gameOverBox()
        
    def updateBoard(self):
        #This funciton will display the board to the user or update it when called.
        if self.flipBoardEachTurn.get() == True and self.game.turn == 'Black':
            calcRowNumber = lambda i : 7 - i
        else:
            calcRowNumber = lambda i : i
        for i in range(8):
            row = calcRowNumber(i)
            for j in range(8):
                piece = self.game[i, j]
                self.buttons[row][j].config(
                    text = piece.text,
                    bg = self.backgroundColour(piece),
                    fg = piece.colour
                    )
                
    def transformPieceLocation(self, loc):
        if self.flipBoardEachTurn.get() == True and self.game.turn == 'Black':
            calcRowNumber = lambda i : 7 - i
        else:
            calcRowNumber = lambda i : i
            
        return [calcRowNumber(loc[0]), loc[1]]
    
    def buttonPressed(self, loc):
        loc = self.transformPieceLocation(loc)
        piece = self.game[loc]
        if self.game.first == None:
            # Player is selecting the first square (piece to move)
            legal, errorString = self.game.checkSelection(piece)
            if legal == True:
                self.game.first = piece
                self.game.highlightMoves(self, piece)
                self.updateBoard()
            else:
                self.printTxt(errorString)
        else:
            # Player is selecting the second square (to move to)
            if piece.loc == self.game.first.loc:
                self.game.first = None
                self.game.second = None
                self.game.deHighlightMoves()
                self.updateBoard()
            elif piece.colour == self.game.turn:
                self.game.deHighlightMoves()
                self.game.first = piece
                self.game.highlightMoves(self, piece)
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
            promotePawn = self.game.makeMove() 
            if promotePawn:
                self.promotePawn()
            self.endOfMove()
        return
    
    def promotePawn(self):
        top = tk.Toplevel(self.root)
        tk.Label(top, text='Pawn promotion. Choose your piece').grid(row=0,column=0,columnspan=2)
        tk.Button(top, text='Queen', command=lambda window=top: self.promotionButton(window,'Queen')).grid(row=1, column=0)
        tk.Button(top, text='Knight', command=lambda window=top: self.promotionButton(window,'Knight')).grid(row=1, column=1)
        tk.Button(top, text='Bishop', command=lambda window=top: self.promotionButton(window,'Bishop')).grid(row=2, column=0)
        tk.Button(top, text='Rook', command=lambda window=top: self.promotionButton(window,'Rook')).grid(row=2, column=1)
        top.mainloop()
        return
    
    def promotionButton(self, window, piece_name):
        self.game.promotePawn(piece_name)
        window.destroy()
        self.endOfMove()
        self.updateBoard()
        return
    
    def endOfMove(self):
        self.clearText()
        self.game.deHighlightMoves()
        self.game.checkGameOver()
        if self.game.gameOver == True:
            self.gameOverBox()
        else:
            self.game.switchTurn()
            self.game.first = None
            self.game.second = None
            self.displayTurn()
            if self.game.inCheck() == True:
                self.printTxt(self.game.turn + ' is in check!')
            else:
                self.displayMoveNumber()
        return
    
    def gameOverBox(self):
        top = tk.Toplevel(self.root)
        tk.Label(top, text = self.game.turn + ' won by ' + self.game.winMethod).pack()
        tk.Button(top,
                  text = 'Close',
                  command = lambda window = top: self.gameOverButton(window)
                  ).pack()
        top.mainloop()
        return
        
    def gameOverButton(self, window):
        window.destroy()
        self.viewBoard_inactive(self.game)
        return
    
    def printTxt(self, text):
        self.textbox.configure(state = 'normal')
        self.textbox.delete('1.0', 'end')
        self.textbox.insert('end', text + '\n')
        self.textbox.config(state = 'disabled')
        return
    
    def displayTurn(self):
        self.textbox_turn.configure(state = 'normal')
        self.textbox_turn.delete('1.0', 'end')
        self.textbox_turn.insert('end', self.game.turn + ' to move.')
        self.textbox_turn.config(state = 'disabled')
        return
    
    def displayMoveNumber(self):
        self.textbox_move.configure(state = 'normal')
        self.textbox_move.delete('1.0', 'end')
        self.textbox_move.insert('end', 'Move ' + str(self.game.moveNumber))
        self.textbox_move.config(state = 'disabled')
        return   
    
    def clearText(self):
        self.textbox.configure(state='normal')
        self.textbox.delete('1.0', 'end')
        self.textbox.config(state='disabled')
       
    def on_closing(self):
        self.root.destroy()
        
    def createButtons(self):
        for i in range(8):
            row = []
            for j in range(8):
                piece = self.game[i, j]
                b = tk.Button(
                        self.root, 
                        text = piece.text,
                        fg = piece.colour,
                        bg = self.backgroundColour(piece),
                        height = 2, 
                        width = 4, 
                        font = 'Helvetica 16 bold',
                        command = lambda loc = [i, j]: self.buttonPressed(loc)
                )
                b.grid(row = 8 - i, column = j)# Flip board to show white at bottom.
                row.append(b)
            self.buttons.append(row)     
            
    def viewBoard(self):
        self.clear()
        tk.Label(self.root, text = self.game.blackPlayerName).grid(row = 0, column = 0)
        tk.Label(self.root, text = self.game.whitePlayerName).grid(row = 9, column = 0)
        self.createButtons()
        self.textbox_move = tk.Text(self.root, height = 2, width = 15)
        self.textbox_move.grid(row = 0, column = 8, columnspan = 2)
        self.textbox_turn = tk.Text(self.root, height = 2, width = 15)
        self.textbox_turn.grid(row = 0, column = 10, columnspan = 2)
        tk.Button(self.root, text = 'Main Menu', height = 2, width = 16, command = self.askSave).grid(row = 1, column = 8, columnspan = 2)
        tk.Button(self.root, text = 'Save Game', height = 2, width = 16, command = self.saveGame).grid(row = 2, column = 10, columnspan = 2)
        if not self.game.gameOver:
            tk.Button(self.root, text = 'Resign', height = 2, width = 16, command = self.resignButton).grid(row = 2, column = 8, columnspan = 2)
        self.textbox = tk.Text(self.root, height = 4, width = 30)
        self.textbox.grid(row = 3, column = 8, columnspan = 4, rowspan = 1)
        self.flipBoardToggle = tk.Checkbutton(
            self.root,
            text = "Flip Board",
            variable = self.flipBoardEachTurn,
            onvalue = True,
            offvalue = False,
            command = self.updateBoard  # Optional: callback when changed
            )
        self.flipBoardToggle.grid(row = 4, column = 8, sticky = "w")
        self.displayTurn()
        self.displayMoveNumber()
        self.root.mainloop()
        return
            
    def viewBoard_inactive(self, game):
        self.clear()
        tk.Label(text = game.winner + ' won by ' + game.winMethod).grid(row = 0, column = 0, columnspan = 8)
        for i in range(8):
            for j in range(8):
                piece = game[i, j]
                b = tk.Label(
                        self.root, 
                        text = piece.text,
                        fg = piece.colour,
                        bg = self.backgroundColour(piece),
                        height = 2, 
                        width = 4, 
                        font = 'Helvetica 16 bold',
                        relief = 'solid',
                        borderwidth = 1
                )
                b.grid(row = 8-i, column = j)# Flip board to show white at bottom.
        tk.Button(self.root, text = 'Main Menu', height = 2, width = 16, command = self.mainMenu).grid(row = 9, column = 0, columnspan = 3)
        tk.Button(self.root, text = 'Saved Games', height = 2, width = 16, command = self.savedGamesMenu).grid(row = 9, column = 3, columnspan = 3)
        self.root.mainloop()
        return  
    
    def getPlayersButton(self, top, tb1, tb2, assignColoursRandomly=None):
        name1 = tb1.get("1.0", "end-1c")
        name2 = tb2.get("1.0", "end-1c")
        if name1 == '':
            tb1.config(bg = 'pink')
        else:
            tb1.config(bg = 'white')
            
        if name2 == '':
            tb2.config(bg = 'pink')
        else:
            tb2.config(bg = 'white')
            
        if name1 != '' and name2 != '':
            if assignColoursRandomly == True:
                names = [name1, name2]
                random.shuffle(names)
                name1, name2 = names[0], names[1]
            game = Game()
            game.whitePlayerName = name1
            game.blackPlayerName = name2
            game.createGameCode()
            top.destroy()
            self.playGame(game)
        
    def getPlayersMenu(self):
        top = tk.Toplevel(self.root)
        tk.Label(top, text = 'Enter the player names').grid(row = 0, column = 0, columnspan = 2)
        tk.Label(top, text = 'White:').grid(row = 1, column = 0)
        tb1 = tk.Text(top, height = 1, width = 16)
        tb1.grid(row = 1, column = 1)
        tb1.insert('1.0', "Player 1")  # Set default text  
        tk.Label(top, text = 'Black:').grid(row = 2, column = 0)
        tb2 = tk.Text(top, height = 1, width = 16)
        tb2.grid(row = 2, column = 1)
        tb2.insert('1.0', "Player 2")  # Set default text  
        tk.Button(top,
                  text = 'Start',
                  command = lambda:
                      self.getPlayersButton(top, tb1, tb2)
            ).grid(row = 3, column = 0)
        tk.Button(top,
                  text = 'Assign Colours (psuedo) Randomly',
                  command = lambda:
                      self.getPlayersButton(top, tb1, tb2, True)
            ).grid(row = 3, column = 1)
        top.mainloop()
             
    def mainMenu(self):
        self.clear()
        tk.Label(self.root, text = "Welcome to Dan Hargreaves's chess game!").grid(row = 0, column = 0, columnspan = 2)
        tk.Button(self.root, text = 'New Game', height = 2, width = 10, command = self.getPlayersMenu).grid(row = 1, column = 0)
        tk.Button(self.root, text = 'Saved Games', height = 2, width = 10, command = self.savedGamesMenu).grid(row = 1, column = 1)
        self.root.mainloop()