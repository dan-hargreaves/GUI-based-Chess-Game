# -*- coding: utf-8 -*-
import tkinter as tk
from ChessGame import Game, Player
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
        self.root.geometry('900x700')
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.root.destroy())
        self.whitePlayer_display_name = ""
        self.blackPlayer_display_name = ""
    
    def saveGame(self):
        self.game.saved = True
        fName = self.game.gameCode + '.chess'
        with open(fName, 'wb') as f:
            pickle.dump(self.game, f, protocol = pickle.HIGHEST_PROTOCOL)
        self.UI_mainMenu()
        
    def clear(self):
        for child in self.root.winfo_children():
            child.destroy()
        for x in self.root.grid_slaves():
            x.destroy()
    
    def getPlayerNames(self, fileName):
        n = fileName.find('_')
        wName = fileName[ : n]
        n1 = fileName.find('_', n + 1) 
        bName = fileName[n + 1 : n1]
        return wName, bName
            
    def viewSavedGame(self, fileName):
        with open(fileName, "rb") as openfile:
            game = pickle.load(openfile)
        if game.gameOver:
            self.UI_chessBoard_inactive(game)
        else:
            self.playGame(game)
        
    def playGame(self, game):
        self.clear()
        self.game = game  
        self.buttons = []
        self.viewBoard()
      
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
    
    def resignButton(self):
        self.game.resign()
        self.UI_gameOver()
        
    def flipOrientation(self):
        if self.flipBoardEachTurn.get() == True and self.game.turn == 'Black':
            return True
        else:
            return False
                
    def transformPieceLocation(self, loc):
        if self.flipOrientation():
            return [7-loc[0], 7-loc[1]]
        else:
            return loc
                
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
                self.UI_promotePawn()
            self.endOfMove()
    
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
            self.UI_gameOver()
        else:
            self.game.first = None
            self.game.second = None
            self.displayTurn()
            if self.game.inCheck() == True:
                self.printTxt(self.game.turn + ' is in check!')
            else:
                self.displayMoveNumber()
      
    def gameOverButton(self, window):
        window.destroy()
        self.UI_chessBoard_inactive(self.game)
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
        
    def set_player_setup_error(self, error_text=""):
        """Set the error message in the player setup dialog"""
        self.player_setup_error_box.config(text=error_text)
        self.player_setup_error_box.grid()
        
    def getPlayersButton(self, assignColoursRandomly=None):
        """Handle player setup with validation and game creation"""
        name1 = self.white_name_entry.get().strip()
        name2 = self.black_name_entry.get().strip()
        player_type1 = self.white_player_type.get()
        player_type2 = self.black_player_type.get()
        
        # Validation with visual feedback
        valid = True
        if name1 == '':
            self.white_name_entry.config(bg='pink')
            valid = False
        else:
            self.white_name_entry.config(bg='white')
            
        if name2 == '':
            self.black_name_entry.config(bg='pink')
            valid = False
        else:
            self.black_name_entry.config(bg='white')
        
        if name1 == name2:
            self.set_player_setup_error("Player names cannot be the same")
            valid = False
        
        if player_type1 == player_type2 == 'computer':
            self.set_player_setup_error("Both players cannot be computer")
            valid = False
            
        if not valid:
            return
    
        player1 = Player.Player(name1, player_type1)
        player2 = Player.Player(name2, player_type2)
        
        # Random color assignment
        if assignColoursRandomly:
            players = [player1, player2]
            random.shuffle(players)
            player1, player2 = players[0], players[1]
        
        # Create and configure game
        game = Game.Game()
        game.whitePlayer = player1
        game.blackPlayer = player2
        
        game.createGameCode()
        self.playGame(game)   
        
    def updateBoard(self):
        ranks = "87654321"
        files = "abcdefgh"
        if self.flipOrientation():
            top_player_text = self.game.whitePlayer.display_name
            bottom_player_text = self.game.blackPlayer.display_name
            ranks = list(reversed(ranks))
            files = list(reversed(files))
            buttons_temp = list(reversed([list(reversed(row)) for row in self.buttons]))
        else:
            top_player_text = self.game.blackPlayer.display_name
            bottom_player_text = self.game.whitePlayer.display_name
            buttons_temp = self.buttons
            
        self.player_textbox_top.config(text=top_player_text)
        self.player_textbox_bottom.config(text=bottom_player_text)     
        for i in range(8):
            # row = calcRowNumber(i)
            self.rank_labels[i].config(text=ranks[i])
            self.file_labels[i].config(text=files[i])
            for j in range(8):
                piece = self.game[i, j]
                buttons_temp[i][j].config(
                    text = piece.display_text,
                    bg = self.backgroundColour(piece),
                    fg = piece.colour
                    )

    def UI_gameOver(self):
        top = tk.Toplevel(self.root)
        top.title("Game Over")
        top.resizable(False, False)
        top.grab_set()
        top.geometry("600x380")
        top.transient(self.root)
        top.configure(bg='#f0f0f0')
        
        # Main container
        main_frame = tk.Frame(top, bg='#f0f0f0', padx=30, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Trophy/Crown icon based on winner
        if self.game.turn.lower() == 'white':
            icon = "👑"
            winner_color = "#ecf0f1"
            accent_color = "#34495e"
        else:
            icon = "♚"
            winner_color = "#2c3e50"
            accent_color = "#ecf0f1"
        
        # Icon display
        icon_label = tk.Label(main_frame,
                             text=icon,
                             font=('Arial', 64),
                             bg='#f0f0f0')
        icon_label.pack(pady=(10, 0))
        
        # Game Over title
        title_label = tk.Label(main_frame,
                              text="Game Over!",
                              font=('Arial', 20, 'bold'),
                              bg='#f0f0f0',
                              fg='#2c3e50')
        title_label.pack(pady=(10, 5))
        
        # Winner announcement with colored background
        winner_frame = tk.Frame(main_frame, bg=winner_color, relief='solid', borderwidth=2)
        winner_frame.pack(fill='x', pady=(10, 5))
        
        winner_label = tk.Label(winner_frame,
                               text=f"{self.game.turn.upper()} Wins!",
                               font=('Arial', 16, 'bold'),
                               bg=winner_color,
                               fg=accent_color,
                               pady=10)
        winner_label.pack()
        
        # Win method details
        method_frame = tk.Frame(main_frame, bg='white', relief='solid', borderwidth=1)
        method_frame.pack(fill='x', pady=(5, 20))
        
        method_label = tk.Label(method_frame,
                               text=f"Victory by {self.game.winMethod}",
                               font=('Arial', 11),
                               bg='white',
                               fg='#7f8c8d',
                               pady=8)
        method_label.pack()
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=(10, 0))
        
        # Close button
        close_btn = tk.Button(button_frame,
                             text='Close',
                             font=('Arial', 12, 'bold'),
                             height=2,
                             width=12,
                             bg='#3498db',
                             fg='white',
                             activebackground='#2980b9',
                             activeforeground='white',
                             relief='raised',
                             borderwidth=2,
                             cursor='hand2',
                             command=lambda window=top: self.gameOverButton(window))
        close_btn.pack()
        
        # Hover effect
        def on_enter(e):
            close_btn.config(bg='#2980b9')
        
        def on_leave(e):
            close_btn.config(bg='#3498db')
        
        close_btn.bind("<Enter>", on_enter)
        close_btn.bind("<Leave>", on_leave)
        
        # Keyboard shortcuts
        top.bind('<Return>', lambda e: self.gameOverButton(top))
        top.bind('<Escape>', lambda e: self.gameOverButton(top))
        top.protocol("WM_DELETE_WINDOW", lambda: self.gameOverButton(top))
        
        # Center the window on screen
        top.update_idletasks()
        width = top.winfo_width()
        height = top.winfo_height()
        x = (top.winfo_screenwidth() // 2) - (width // 2)
        y = (top.winfo_screenheight() // 2) - (height // 2)
        top.geometry(f'{width}x{height}+{x}+{y}')
        
        top.mainloop() 
                   
    def UI_saveGame(self):
        if not self.game.saved:
            # --- Create modal dialog ---
            top = tk.Toplevel(self.root)
            top.title("Save Game?")
            top.configure(bg="#f7f7f7", padx=25, pady=20)
            top.resizable(False, False)
            top.geometry("500x200")
    
            # --- Make modal (block main window) ---
            top.transient(self.root)
            top.grab_set()
    
            # --- Title label ---
            label = tk.Label(
                top,
                text="Do you wish to save your current game?",
                font=("Arial", 12, "bold"),
                bg="#f7f7f7",
                fg="#2c3e50",
                wraplength=280,
                justify="center",
                pady=10
            )
            label.pack(pady=(10, 20))
    
            # --- Button container ---
            button_frame = tk.Frame(top, bg="#f7f7f7")
            button_frame.pack(pady=(0, 10))
                    
            # --- Buttons ---
            yes_btn = tk.Button(
                button_frame,
                text="💾 Save",
                command=lambda: (top.destroy(), self.saveGame()),
                bg="#27ae60",
                fg="white",
                font=("Arial", 11, "bold"),
                activebackground="#219150",
                activeforeground="white",
                relief="flat",
                padx=10,
                pady=8,
                cursor="hand2"
            )
            yes_btn.grid(row=0, column=0, padx=10)
    
            no_btn = tk.Button(
                button_frame,
                text="❌ Don't Save",
                command=lambda: self.UI_mainMenu(),
                bg="#e74c3c",
                fg="white",
                font=("Arial", 11, "bold"),
                activebackground="#c0392b",
                activeforeground="white",
                relief="flat",
                padx=10,
                pady=8,
                cursor="hand2"
            )
            no_btn.grid(row=0, column=1, padx=10)
    
            return_btn = tk.Button(
                button_frame,
                text="Cancel",
                command=lambda: top.destroy(),
                bg="light blue",
                fg="white",
                font=("Arial", 11, "bold"),
                activeforeground="white",
                relief="flat",
                padx=10,
                pady=8,
                cursor="hand2"
            )
            return_btn.grid(row=0, column=2, padx=10)
    
            # --- Keyboard shortcuts ---
            top.bind("<Return>", lambda e: (top.destroy(), self.saveGame()))
            top.bind("<Escape>", lambda e: top.destroy())
    
            # --- Keep focus on the popup ---
            yes_btn.focus_set()
        else:
            # If already saved, just save immediately
            self.saveGame()
        
    def UI_chessBoard(self):
        # --- Main container frame (holds board + side panel) ---
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack()
        
        # --- Left player frame ---
        player_frame = tk.Frame(main_frame, padx=10, pady=10)
        player_frame.grid(row=0, column=0, sticky="n")

        top_label = tk.Label(player_frame, text=self.game.blackPlayer.display_name, font=("Arial", 11, "bold"))
        top_label.pack(pady=(10, 5))
        self.player_textbox_top = top_label
    
        # --- Board frame ---
        board_frame = tk.Frame(player_frame, bd=2, relief="sunken", padx=10, pady=10)
        board_frame.pack(pady=(10, 5))
    
        # --- Right: Controls frame ---
        control_frame = tk.Frame(main_frame, padx=15, pady=5)
        control_frame.grid(row=0, column=1, sticky="n")
    
        # --- Chessboard buttons ---
        self.buttons = []
        self.rank_labels = []
        self.file_labels = []
    
        for i in range(8):
            label = tk.Label(board_frame, font=("Arial", 9))
            label.grid(row=9, column=i+1)
            self.file_labels.append(label)

            label = tk.Label(board_frame, font=("Arial", 9)) #Rank text is handled by updateBoard()
            label.grid(row=i+1, column=0)
            self.rank_labels.append(label)
    
        for i in range(8):
            row_buttons = []
            for j in range(8):
                piece = self.game[i, j]
                b = tk.Button( #Chess piece text is handled by updateBoard()
                    board_frame,
                    height=2,
                    width=4,
                    font=("Helvetica", 16, "bold"),
                    command=lambda loc=[i, j]: self.buttonPressed(loc)
                )
                b.grid(row=8-i, column=j+1)  # show white at bottom
                row_buttons.append(b)
            self.buttons.append(row_buttons)
            
        self.board_frame = board_frame
        
        # --- Side controls ---
        self.textbox_move = tk.Text(control_frame, height=2, width=15)
        self.textbox_move.grid(row=0, column=0, padx=5, pady=3)
    
        self.textbox_turn = tk.Text(control_frame, height=2, width=15)
        self.textbox_turn.grid(row=0, column=1, padx=5, pady=3)
    
        tk.Button(control_frame, text="Main Menu", width=16, height=2, command=self.UI_saveGame).grid(row=1, column=0, padx=5, pady=3)
        tk.Button(control_frame, text="Save Game", width=16, height=2, command=self.saveGame).grid(row=1, column=1, padx=5, pady=3)
    
        if not self.game.gameOver:
            tk.Button(control_frame, text="Resign", width=16, height=2, command=self.resignButton).grid(row=2, column=0, padx=5, pady=3)
    
        self.textbox = tk.Text(control_frame, height=4, width=30)
        self.textbox.grid(row=3, column=0, columnspan=2, pady=(10, 5))
    
        self.flipBoardToggle = tk.Checkbutton(
            control_frame,
            text="Flip Board",
            variable=self.flipBoardEachTurn,
            onvalue=True,
            offvalue=False,
            command=self.updateBoard
        )
        self.flipBoardToggle.grid(row=4, column=0, sticky="w", pady=(5, 0))
    
        # --- Bottom player label ---
        bottom_label = tk.Label(player_frame, text=self.game.whitePlayer.display_name, font=("Arial", 11, "bold"))
        bottom_label.pack(pady=(5, 10))
        self.player_textbox_bottom = bottom_label
        
        # --- Update the board initially ---
        self.updateBoard()   
            
    def viewBoard(self):
        self.clear()      
        self.UI_chessBoard()
        self.displayTurn()
        self.displayMoveNumber()
        self.root.mainloop()
        
    def UI_promotePawn(self):
        top = tk.Toplevel(self.root)
        tk.Label(top, text='Pawn promotion. Choose your piece').grid(row=0,column=0,columnspan=2)
        tk.Button(top, text='Queen', command=lambda window=top: self.promotionButton(window,'Queen')).grid(row=1, column=0)
        tk.Button(top, text='Knight', command=lambda window=top: self.promotionButton(window,'Knight')).grid(row=1, column=1)
        tk.Button(top, text='Bishop', command=lambda window=top: self.promotionButton(window,'Bishop')).grid(row=2, column=0)
        tk.Button(top, text='Rook', command=lambda window=top: self.promotionButton(window,'Rook')).grid(row=2, column=1)
        top.mainloop()
           
    def UI_chessBoard_inactive(self, game):
        self.clear()
        
        # Configure root window
        self.root.configure(bg='#f0f0f0')
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.grid(row=0, column=0)
        
        # Winner announcement banner
        winner_text = f"{game.winner} won by {game.winMethod}"
        
        # Determine banner color based on winner
        if game.winner.lower() == 'white':
            banner_bg = '#ecf0f1'
            banner_fg = '#2c3e50'
            icon = '👑'
        else:
            banner_bg = '#2c3e50'
            banner_fg = '#ecf0f1'
            icon = '♚'
        
        banner_frame = tk.Frame(main_frame, bg=banner_bg, relief='solid', borderwidth=2)
        banner_frame.grid(row=0, column=0, columnspan=10, sticky='ew', pady=(0, 15))
        
        # Icon and text in banner
        banner_content = tk.Frame(banner_frame, bg=banner_bg)
        banner_content.pack(pady=10)
        
        tk.Label(banner_content, 
                text=icon, 
                font=('Arial', 20),
                bg=banner_bg,
                fg=banner_fg).pack(side='left', padx=(0, 10))
        
        tk.Label(banner_content,
                text=winner_text,
                font=('Arial', 14, 'bold'),
                bg=banner_bg,
                fg=banner_fg).pack(side='left')
        
        # Board title
        board_title = tk.Label(main_frame,
                              text="Final Position",
                              font=('Arial', 12, 'bold'),
                              bg='#f0f0f0',
                              fg='#34495e')
        board_title.grid(row=1, column=0, columnspan=10, pady=(0, 10))
        
        # Chess board frame with border
        board_frame = tk.Frame(main_frame, bg='#34495e', relief='solid', borderwidth=3)
        board_frame.grid(row=2, column=1, columnspan=8, rowspan=8, padx=5, pady=5)
        
        # Render chess pieces
        for i in range(8):
            for j in range(8):
                piece = game[i, j]
                b = tk.Label(
                        board_frame, 
                        text=piece.display_text,
                        fg=piece.colour,
                        bg=self.backgroundColour(piece),
                        height=2, 
                        width=4, 
                        font='Helvetica 16 bold',
                        relief='flat',
                        borderwidth=0
                )
                b.grid(row=7-i, column=j, sticky='nsew')  # Flip board to show white at bottom
        
        # File labels (a-h) at bottom
        files = "abcdefgh"
        for col in range(8):
            tk.Label(main_frame, 
                    text=files[col], 
                    font=("Arial", 10, 'bold'),
                    bg='#f0f0f0',
                    fg='#7f8c8d').grid(row=10, column=col+1)
        
        # Rank labels (1-8) on left side
        ranks = "12345678"
        for row in range(8):
            tk.Label(main_frame, 
                    text=ranks[7-row], 
                    font=("Arial", 10, 'bold'),
                    bg='#f0f0f0',
                    fg='#7f8c8d').grid(row=row+2, column=0, padx=(0, 5))
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.grid(row=11, column=0, columnspan=10, pady=(20, 0))
        
        # Main Menu button
        main_menu_btn = tk.Button(button_frame,
                                 text='Main Menu',
                                 font=('Arial', 11, 'bold'),
                                 height=2,
                                 width=16,
                                 bg='#3498db',
                                 fg='white',
                                 activebackground='#2980b9',
                                 activeforeground='white',
                                 relief='raised',
                                 borderwidth=2,
                                 cursor='hand2',
                                 command=self.UI_mainMenu)
        main_menu_btn.grid(row=0, column=0, padx=5)
        
        # Saved Games button
        saved_games_btn = tk.Button(button_frame,
                                   text='Saved Games',
                                   font=('Arial', 11, 'bold'),
                                   height=2,
                                   width=16,
                                   bg='#9b59b6',
                                   fg='white',
                                   activebackground='#8e44ad',
                                   activeforeground='white',
                                   relief='raised',
                                   borderwidth=2,
                                   cursor='hand2',
                                   command=self.UI_savedGamesMenu)
        saved_games_btn.grid(row=0, column=1, padx=5)
        
        # Hover effects
        def on_enter_main_menu(e):
            main_menu_btn.config(bg='#2980b9')
        
        def on_leave_main_menu(e):
            main_menu_btn.config(bg='#3498db')
        
        def on_enter_saved_games(e):
            saved_games_btn.config(bg='#8e44ad')
        
        def on_leave_saved_games(e):
            saved_games_btn.config(bg='#9b59b6')
        
        main_menu_btn.bind("<Enter>", on_enter_main_menu)
        main_menu_btn.bind("<Leave>", on_leave_main_menu)
        saved_games_btn.bind("<Enter>", on_enter_saved_games)
        saved_games_btn.bind("<Leave>", on_leave_saved_games)
        self.root.mainloop()
                  
    def UI_savedGamesMenu(self):
       self.clear()
       
       # Configure the root window
       self.root.configure(bg='#f0f0f0')
       
       # Main container frame
       main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=40, pady=30)
       main_frame.grid(row=0, column=0, sticky='nsew')
       
       # Configure grid weights for centering
       self.root.grid_rowconfigure(0, weight=1)
       self.root.grid_columnconfigure(0, weight=1)
       
       # Title
       title_label = tk.Label(main_frame, 
                             text="Saved Games", 
                             font=('Arial', 18, 'bold'),
                             bg='#f0f0f0',
                             fg='#2c3e50')
       title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
       
       # Get saved game files
       filePaths = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.chess')]
       numGames = len(filePaths)
       
       if numGames > 0:
           # Content frame for saved games list
           content_frame = tk.Frame(main_frame, bg='white', relief='solid', borderwidth=1)
           content_frame.grid(row=1, column=0, columnspan=2, pady=(0, 20), sticky='ew')
           
           # Instructions
           instruction_label = tk.Label(content_frame,
                                       text="Select a game to continue:",
                                       font=('Arial', 10),
                                       bg='white',
                                       fg='#34495e',
                                       anchor='w')
           instruction_label.pack(fill='x', padx=15, pady=(15, 10))
           
           # Build options list
           options = []
           for i in range(numGames):
               fileName = filePaths[i]
               wName, bName = self.getPlayerNames(fileName)
               options.append(f"{i}: {wName} vs {bName}")
           
           # Dropdown menu with enhanced styling
           variable = tk.StringVar(self.root)
           variable.set(options[0])  # default value
           
           dropdown_frame = tk.Frame(content_frame, bg='white')
           dropdown_frame.pack(fill='x', padx=15, pady=(0, 15))
           
           w = tk.OptionMenu(dropdown_frame, variable, *options)
           w.config(font=('Arial', 11),
                   bg='white',
                   fg='#2c3e50',
                   activebackground='#ecf0f1',
                   relief='solid',
                   borderwidth=1,
                   width=30,
                   anchor='w',
                   cursor='hand2')
           w['menu'].config(font=('Arial', 10),
                           bg='white',
                           fg='#2c3e50',
                           activebackground='#3498db',
                           activeforeground='white')
           w.pack(fill='x')
           
           # Buttons frame
           button_frame = tk.Frame(main_frame, bg='#f0f0f0')
           button_frame.grid(row=2, column=0, columnspan=2, pady=10)
           
           # Open Game button
           open_btn = tk.Button(button_frame,
                              text='Open Game',
                              font=('Arial', 12, 'bold'),
                              height=2,
                              width=15,
                              bg='#27ae60',
                              fg='white',
                              activebackground='#229954',
                              activeforeground='white',
                              relief='raised',
                              borderwidth=2,
                              cursor='hand2',
                              command=lambda: self.viewSavedGame(filePaths[int(variable.get().split(':')[0])]))
           open_btn.grid(row=0, column=0, padx=10)
           
           # Main Menu button
           main_menu_btn = tk.Button(button_frame,
                                    text='Main Menu',
                                    font=('Arial', 12, 'bold'),
                                    height=2,
                                    width=15,
                                    bg='#95a5a6',
                                    fg='white',
                                    activebackground='#7f8c8d',
                                    activeforeground='white',
                                    relief='raised',
                                    borderwidth=2,
                                    cursor='hand2',
                                    command=self.UI_mainMenu)
           main_menu_btn.grid(row=0, column=1, padx=10)
           
           # Hover effects
           def on_enter_open(e):
               open_btn.config(bg='#229954')
           
           def on_leave_open(e):
               open_btn.config(bg='#27ae60')
           
           def on_enter_main_menu(e):
               main_menu_btn.config(bg='#7f8c8d')
           
           def on_leave_main_menu(e):
               main_menu_btn.config(bg='#95a5a6')
           
           open_btn.bind("<Enter>", on_enter_open)
           open_btn.bind("<Leave>", on_leave_open)
           main_menu_btn.bind("<Enter>", on_enter_main_menu)
           main_menu_btn.bind("<Leave>", on_leave_main_menu)
           
           # Info footer
           info_label = tk.Label(main_frame,
                               text=f"Found {numGames} saved game{'s' if numGames != 1 else ''}",
                               font=('Arial', 9),
                               bg='#f0f0f0',
                               fg='#7f8c8d')
           info_label.grid(row=3, column=0, columnspan=2, pady=(20, 0))
           
       else:
           # No saved games - empty state
           empty_frame = tk.Frame(main_frame, bg='white', relief='solid', borderwidth=1)
           empty_frame.grid(row=1, column=0, columnspan=2, pady=(0, 20), sticky='ew')
           
           # Empty state icon (using Unicode)
           icon_label = tk.Label(empty_frame,
                               text="📁",
                               font=('Arial', 48),
                               bg='white',
                               fg='#bdc3c7')
           icon_label.pack(pady=(30, 10))
           
           # No saved games message
           message_label = tk.Label(empty_frame,
                                  text="No Saved Games Found",
                                  font=('Arial', 14, 'bold'),
                                  bg='white',
                                  fg='#7f8c8d')
           message_label.pack(pady=(0, 10))
           
           # Helpful text
           help_label = tk.Label(empty_frame,
                               text="Start a new game to create your first saved game!",
                               font=('Arial', 10),
                               bg='white',
                               fg='#95a5a6')
           help_label.pack(pady=(0, 30))
           
           # Main Menu button (centered for empty state)
           button_frame = tk.Frame(main_frame, bg='#f0f0f0')
           button_frame.grid(row=2, column=0, columnspan=2, pady=10)
           
           main_menu_btn = tk.Button(button_frame,
                                    text='Main Menu',
                                    font=('Arial', 12, 'bold'),
                                    height=2,
                                    width=15,
                                    bg='#3498db',
                                    fg='white',
                                    activebackground='#2980b9',
                                    activeforeground='white',
                                    relief='raised',
                                    borderwidth=2,
                                    cursor='hand2',
                                    command=self.UI_mainMenu)
           main_menu_btn.pack()
           
           # Hover effect
           def on_enter_main_menu(e):
               main_menu_btn.config(bg='#2980b9')
           
           def on_leave_main_menu(e):
               main_menu_btn.config(bg='#3498db')
           
           main_menu_btn.bind("<Enter>", on_enter_main_menu)
           main_menu_btn.bind("<Leave>", on_leave_main_menu)      
        
    def UI_getPlayers(self):
        self.clear()
        self.root.title("Player Setup")
        
        # --- Main Container ---
        container = tk.Frame(self.root, padx=20, pady=20, bg="#f7f7f7")
        container.grid(row=0, column=0, sticky="nsew")
        self.root.configure(bg="#f7f7f7")
        
        # --- Title ---
        title_label = tk.Label(
            container,
            text="Enter Player Details",
            font=("Arial", 14, "bold"),
            bg="#f7f7f7"
        )
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # --- White Player Section ---
        tk.Label(container, text="White:", font=("Arial", 10, "bold"), bg="#f7f7f7").grid(
            row=1, column=0, sticky="e", padx=(10, 5)
        )
        
        self.white_name_entry = tk.Entry(container, width=18, font=("Arial", 10))
        self.white_name_entry.grid(row=1, column=1, padx=5)
        self.white_name_entry.insert(0, "Player 1")
        
        white_frame = tk.Frame(container, bg="#f7f7f7")
        white_frame.grid(row=1, column=2, columnspan=2, sticky="w", padx=(10, 0))
        
        self.white_player_type = tk.StringVar(value="human")
        for text, val in [("Human", "human"), ("Computer", "computer")]:
            tk.Radiobutton(
                white_frame,
                text=text,
                variable=self.white_player_type,
                value=val,
                font=("Arial", 9),
                bg="#f7f7f7",
                activebackground="#f7f7f7",
            ).pack(side="left", padx=(0, 10))
        
        # --- Black Player Section ---
        tk.Label(container, text="Black:", font=("Arial", 10, "bold"), bg="#f7f7f7").grid(
            row=2, column=0, sticky="e", padx=(10, 5), pady=(10, 0)
        )
        
        self.black_name_entry = tk.Entry(container, width=18, font=("Arial", 10))
        self.black_name_entry.grid(row=2, column=1, padx=5, pady=(10, 0))
        self.black_name_entry.insert(0, "Player 2")
        
        black_frame = tk.Frame(container, bg="#f7f7f7")
        black_frame.grid(row=2, column=2, columnspan=2, sticky="w", padx=(10, 0), pady=(10, 0))
        
        self.black_player_type = tk.StringVar(value="human")
        for text, val in [("Human", "human"), ("Computer", "computer")]:
            tk.Radiobutton(
                black_frame,
                text=text,
                variable=self.black_player_type,
                value=val,
                font=("Arial", 9),
                bg="#f7f7f7",
                activebackground="#f7f7f7",
            ).pack(side="left", padx=(0, 10))
        
        # --- Buttons Section ---
        button_frame = tk.Frame(container, bg="#f7f7f7")
        button_frame.grid(row=3, column=0, columnspan=4, pady=(25, 10))
        
        def styled_btn(parent, text, command, bg, hover_bg):
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                bg=bg,
                fg="white",
                font=("Arial", 10, "bold"),
                padx=20,
                pady=6,
                relief="flat",
                activebackground=hover_bg,
                activeforeground="white",
                cursor="hand2",
            )
            btn.pack(side="left", padx=7)
            return btn
        
        styled_btn(button_frame, "Start Game", lambda: self.getPlayersButton(False), "#4CAF50", "#45a049")
        styled_btn(button_frame, "Random Colors", lambda: self.getPlayersButton(True), "#2196F3", "#1e88e5")
        styled_btn(button_frame, "Cancel", self.UI_mainMenu, "#f44336", "#e53935")
        
        # --- Error Box ---
        self.player_setup_error_box = tk.Label(
            container,
            text="",
            font=("Arial", 9),
            fg="red",
            bg="#ffeeee",
            relief="sunken",
            borderwidth=1,
            wraplength=380,
            justify="left",
            anchor="w",
            height=2
        )
        self.player_setup_error_box.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        self.player_setup_error_box.grid_remove()
        
        # --- Initial focus & shortcuts ---
        self.white_name_entry.focus()
        self.white_name_entry.select_range(0, tk.END)
        
        self.root.bind("<Return>", lambda e: self.getPlayersButton(False))
        self.root.bind("<Escape>", lambda e: self.root.destroy())    
            
    def UI_mainMenu(self):
        self.clear()
        
        # Main container frame for better layout control
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=40, pady=30)
        main_frame.grid(row=0, column=0, sticky='nsew')
        
        # Configure grid weights for centering#
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Welcome title with enhanced styling
        title_label = tk.Label(main_frame, 
                              text="Welcome to Dan Hargreaves's\nChess Game!", 
                              font=('Arial', 18, 'bold'),
                              bg='#f0f0f0',
                              fg='#2c3e50',
                              justify='center')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        # Chess piece decorative element (optional - uses Unicode chess symbols)
        decoration_label = tk.Label(main_frame,
                                   text="♔ ♕ ♖ ♗ ♘ ♙",
                                   font=('Arial', 16),
                                   bg='#f0f0f0',
                                   fg='#34495e')
        decoration_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Button frame for consistent spacing
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        # New Game button with enhanced styling
        new_game_btn = tk.Button(button_frame,
                                text='New Game',
                                font=('Arial', 12, 'bold'),
                                height=3,
                                width=15,
                                bg='#27ae60',
                                fg='white',
                                activebackground='#229954',
                                activeforeground='white',
                                relief='raised',
                                borderwidth=2,
                                cursor='hand2',
                                command=self.UI_getPlayers)
        new_game_btn.grid(row=0, column=0, padx=10)
        
        # Saved Games button with enhanced styling
        saved_games_btn = tk.Button(button_frame,
                                   text='Saved Games',
                                   font=('Arial', 12, 'bold'),
                                   height=3,
                                   width=15,
                                   bg='#3498db',
                                   fg='white',
                                   activebackground='#2980b9',
                                   activeforeground='white',
                                   relief='raised',
                                   borderwidth=2,
                                   cursor='hand2',
                                   command=self.UI_savedGamesMenu)
        saved_games_btn.grid(row=0, column=1, padx=10)
        self.root.mainloop()