# -*- coding: utf-8 -*-
import tkinter as tk
from ChessGame import Game, Player
from ChessGame import APIs
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
        self.root.geometry('900x900')
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.root.destroy())
        self.whitePlayer_display_name = ""
        self.blackPlayer_display_name = ""
        self.resign_btn = None
        self.flipBoardToggle = None
    
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
            self.game = pickle.load(openfile)

        if self.game.gameOver:
            self.viewBoard()
        else:
            self.playGame()
        
    def playGame(self):
        self.clear()
        self.buttons = []
        if self.game.whitePlayer.type == 'computer' or self.game.blackPlayer.type == 'computer':
            self.computer = APIs.StockfishClient()
        self.viewBoard()
      
    def backgroundColour(self, piece):
        selected_piece_colour = "#f6f669"      # Bright yellow for selected piece
        black_square_colour = "#769656"          # Green-brown for dark squares
        white_square_colour = "#eeeed2"         # Cream for light squares
        possible_move_colour = "#baca44"        # Yellow-green for possible moves (on light squares)
        possible_capture_colour = "#f56c6c"     # Red for possible captures (on light squares)
       
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
        if self.game.blackPlayer.type == 'computer':
            flip = False
        elif self.game.whitePlayer.type == 'computer':
            flip = True
        else:
            if self.flipBoardEachTurn.get() == True and self.game.turn == 'Black':
                flip = True
            else:
                flip = False
        return flip
                
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
    
    def checkGameOver(self):
        self.game.checkGameOver()
        if self.game.gameOver == True:
            self.game.deHighlightMoves()
            self.UI_gameOver()
            
    def endOfMove(self):
        self.clearText()
        self.game.deHighlightMoves()
        self.checkGameOver()
        self.game.first = None
        self.game.second = None
        self.displayTurn()
        if self.game.inCheck() == True:
            self.printTxt(self.game.turn + ' is in check!')
        else:
            self.displayMoveNumber()
        
        if self.game.turn == 'White' and self.game.whitePlayer.type == 'computer' or self.game.turn == 'Black' and self.game.blackPlayer.type == 'computer':
            self.playComputerMove()
                
    
    def playComputerMove(self):
        self.updateBoard()
        self.root.update_idletasks()
        fen_str = self.game.FEN_string()
        (result, APIError, NetworkError, ValueError) = self.computer.getStockfishMove(fen_str)
        if result.success:
            self.game.first = self.game[result.best_move[0:2]]
            self.game.second = self.game[result.best_move[2:4]]
            try:
                promotePawn = self.game.makeMove()
            except:
                self.printTxt(result.best_move)
        else:
            self.printTxt("Error connecting to chess engine")
        
        self.updateBoard()
        self.root.update_idletasks()
        self.checkGameOver()

    def gameOverButton(self, window):
        window.destroy()
        self.updateBoard()
    
    def printTxt(self, text):
        self.textbox.configure(state = 'normal')
        self.textbox.delete('1.0', 'end')
        self.textbox.insert('end', text + '\n')
        self.textbox.config(state = 'disabled')
    
    def displayTurn(self):
        self.textbox_turn.configure(state = 'normal')
        self.textbox_turn.delete('1.0', 'end')
        self.textbox_turn.insert('end', self.game.turn + ' to move.')
        self.textbox_turn.config(state = 'disabled')
        
    def displayWinner(self):
        self.textbox_turn.configure(state = 'normal')
        self.textbox_turn.delete('1.0', 'end')
        self.textbox_turn.insert('end', f"{self.game.winner} won by {self.game.winMethod}")
        self.textbox_turn.config(state = 'disabled') 
        
    def displayMoveNumber(self):
        self.textbox_move.configure(state = 'normal')
        self.textbox_move.delete('1.0', 'end')
        self.textbox_move.insert('end', 'Move ' + str(self.game.moveNumber))
        self.textbox_move.config(state = 'disabled')
    
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
        self.game = Game.Game()
        self.game.whitePlayer = player1
        self.game.blackPlayer = player2
        
        self.game.createGameCode()
        self.playGame()   
                
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
        button_state = 'disabled' if self.game.gameOver else 'normal'
        button_cursor = 'arrow' if self.game.gameOver else 'hand2'
        for i in range(8):
            # row = calcRowNumber(i)
            self.rank_labels[i].config(text=ranks[i])
            self.file_labels[i].config(text=files[i])
            for j in range(8):
                piece = self.game[i, j]
                buttons_temp[i][j].config(
                    text = piece.display_text,
                    bg = self.backgroundColour(piece),
                    fg = piece.colour,
                    disabledforeground= piece.colour,
                    cursor=button_cursor,
                    state=button_state,
                    )
        if self.game.gameOver:
            if self.resign_btn != None:
                self.resign_btn.grid_remove()
                self.resign_btn = None
            if self.flipBoardToggle != None:
                self.flipBoardToggle.pack_forget()
                self.flipBoardToggle = None

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
        # Configure root window
        self.root.configure(bg='#f0f0f0')
        
        # --- Main container frame (holds board + side panel) ---
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack()
        
        # --- Left: Board section (with player names) ---
        board_section = tk.Frame(main_frame, bg='#f0f0f0', padx=10, pady=10)
        board_section.grid(row=0, column=0, sticky="n")
        
        # --- Top player frame (Black) ---
        top_player_frame = tk.Frame(board_section, bg='#2c3e50', relief='solid', borderwidth=2, padx=15, pady=8)
        top_player_frame.pack(pady=(0, 10))
        
        top_label = tk.Label(top_player_frame, 
                            text=self.game.blackPlayer.display_name, 
                            font=("Arial", 12, "bold"),
                            bg='#2c3e50',
                            fg='white')
        top_label.pack()
        self.player_textbox_top = top_label
        
        # --- Board frame with enhanced border ---
        board_outer_frame = tk.Frame(board_section, bg='#34495e', relief='solid', borderwidth=4, padx=2, pady=2)
        board_outer_frame.pack()
        
        board_frame = tk.Frame(board_outer_frame, bg='#34495e', padx=3, pady=3)
        board_frame.pack()
        
        # --- Chessboard buttons ---
        self.buttons = []
        self.rank_labels = []
        self.file_labels = []
        
        # File labels (a-h) at bottom
        for i in range(8):
            label = tk.Label(board_frame, 
                            font=("Arial", 10, "bold"),
                            bg='#34495e',
                            fg='#ecf0f1',
                            width=2)
            label.grid(row=9, column=i+1)
            self.file_labels.append(label)
        
        # Rank labels (1-8) on left
        for i in range(8):
            label = tk.Label(board_frame, 
                            font=("Arial", 10, "bold"),
                            bg='#34495e',
                            fg='#ecf0f1',
                            width=2)
            label.grid(row=i+1, column=0)
            self.rank_labels.append(label)
        
        # Chess piece buttons
        button_state = 'disabled' if self.game.gameOver else 'normal'
        button_cursor = 'arrow' if self.game.gameOver else 'hand2'
        for i in range(8):
            row_buttons = []
            for j in range(8):
                b = tk.Button(
                    board_frame,
                    height=2,
                    width=4,
                    font=("Helvetica", 18, "bold"),
                    relief='flat',
                    borderwidth=0,
                    cursor=button_cursor,
                    state=button_state,
                    command=lambda loc=[i, j]: self.buttonPressed(loc)
                )
                b.grid(row=8-i, column=j+1, padx=0, pady=0)
                row_buttons.append(b)
            self.buttons.append(row_buttons)
            
        self.board_frame = board_frame
        
        # --- Bottom player frame (White) ---
        bottom_player_frame = tk.Frame(board_section, bg='#ecf0f1', relief='solid', borderwidth=2, padx=15, pady=8)
        bottom_player_frame.pack(pady=(10, 0))
        
        bottom_label = tk.Label(bottom_player_frame, 
                               text=self.game.whitePlayer.display_name, 
                               font=("Arial", 12, "bold"),
                               bg='#ecf0f1',
                               fg='#2c3e50')
        bottom_label.pack()
        self.player_textbox_bottom = bottom_label
        
        # --- Right: Controls frame ---
        control_frame = tk.Frame(main_frame, bg='#f0f0f0', padx=15, pady=5)
        control_frame.grid(row=0, column=1, sticky="n")
        
        # Game info section
        info_frame = tk.Frame(control_frame, bg='white', relief='solid', borderwidth=1, padx=10, pady=10)
        info_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        # Move info
        move_label = tk.Label(info_frame, text="Current Move:", font=("Arial", 9, "bold"), bg='white', fg='#7f8c8d')
        move_label.grid(row=0, column=0, sticky='w', pady=(0, 3))
        
        self.textbox_move = tk.Text(info_frame, 
                                   height=2, 
                                   width=30,
                                   font=("Arial", 10),
                                   relief='flat',
                                   bg='#f8f9fa',
                                   borderwidth=0,
                                   padx=5,
                                   pady=5)
        self.textbox_move.grid(row=1, column=0, pady=(0, 8))
        
        # Turn info
        turn_label = tk.Label(info_frame, text="Turn:", font=("Arial", 9, "bold"), bg='white', fg='#7f8c8d')
        turn_label.grid(row=2, column=0, sticky='w', pady=(0, 3))
        
        self.textbox_turn = tk.Text(info_frame, 
                                   height=2, 
                                   width=30,
                                   font=("Arial", 10),
                                   relief='flat',
                                   bg='#f8f9fa',
                                   borderwidth=0,
                                   padx=5,
                                   pady=5)
        self.textbox_turn.grid(row=3, column=0)
        
        # Action buttons
        button_frame = tk.Frame(control_frame, bg='#f0f0f0')
        button_frame.grid(row=1, column=0, columnspan=2, pady=(5, 0))
        
        main_menu_btn = tk.Button(button_frame, 
                                 text="Main Menu", 
                                 width=16, 
                                 height=2,
                                 font=("Arial", 10, "bold"),
                                 bg='#95a5a6',
                                 fg='white',
                                 activebackground='#7f8c8d',
                                 relief='raised',
                                 borderwidth=2,
                                 cursor='hand2',
                                 command=self.UI_saveGame)
        main_menu_btn.grid(row=0, column=0, padx=3, pady=3)
        
        save_btn = tk.Button(button_frame, 
                            text="Save Game", 
                            width=16, 
                            height=2,
                            font=("Arial", 10, "bold"),
                            bg='#3498db',
                            fg='white',
                            activebackground='#2980b9',
                            relief='raised',
                            borderwidth=2,
                            cursor='hand2',
                            command=self.saveGame)
        save_btn.grid(row=1, column=0, padx=3, pady=3)
        
        # Hover effects
        def on_enter_menu(e):
            main_menu_btn.config(bg='#7f8c8d')
        def on_leave_menu(e):
            main_menu_btn.config(bg='#95a5a6')
        def on_enter_save(e):
            save_btn.config(bg='#2980b9')
        def on_leave_save(e):
            save_btn.config(bg='#3498db')
        
        main_menu_btn.bind("<Enter>", on_enter_menu)
        main_menu_btn.bind("<Leave>", on_leave_menu)
        save_btn.bind("<Enter>", on_enter_save)
        save_btn.bind("<Leave>", on_leave_save)
        
        # Resign button (if game not over)
        if not self.game.gameOver:
            self.resign_btn = tk.Button(button_frame, 
                                  text="Resign", 
                                  width=16, 
                                  height=2,
                                  font=("Arial", 10, "bold"),
                                  bg='#e74c3c',
                                  fg='white',
                                  activebackground='#c0392b',
                                  relief='raised',
                                  borderwidth=2,
                                  cursor='hand2',
                                  command=self.resignButton)
            self.resign_btn.grid(row=2, column=0, padx=3, pady=3)
            
            def on_enter_resign(e):
                self.resign_btn.config(bg='#c0392b')
            def on_leave_resign(e):
                self.resign_btn.config(bg='#e74c3c')
            
            self.resign_btn.bind("<Enter>", on_enter_resign)
            self.resign_btn.bind("<Leave>", on_leave_resign)
        
        # Move history / messages section
        message_frame = tk.Frame(control_frame, bg='white', relief='solid', borderwidth=1, padx=5, pady=5)
        message_frame.grid(row=2, column=0, columnspan=2, pady=(10, 5), sticky='ew')
        
        message_label = tk.Label(message_frame, 
                                text="Messages:", 
                                font=("Arial", 9, "bold"), 
                                bg='white', 
                                fg='#7f8c8d')
        message_label.pack(anchor='w', pady=(0, 3))
        
        self.textbox = tk.Text(message_frame, 
                              height=4, 
                              width=30,
                              font=("Arial", 9),
                              relief='flat',
                              bg='#f8f9fa',
                              wrap='word',
                              padx=5,
                              pady=5)
        self.textbox.pack(fill='both', expand=True)
        
        # Options section
        options_frame = tk.Frame(control_frame, bg='#f0f0f0')
        options_frame.grid(row=3, column=0, columnspan=2, pady=(5, 0), sticky='w')
        
        if not self.game.gameOver:
            self.flipBoardToggle = tk.Checkbutton(
                options_frame,
                text="Flip Board Each Turn",
                variable=self.flipBoardEachTurn,
                onvalue=True,
                offvalue=False,
                font=("Arial", 9),
                bg='#f0f0f0',
                activebackground='#f0f0f0',
                cursor='hand2',
                command=self.updateBoard
            )
            self.flipBoardToggle.pack(anchor='w')
        
        # --- Update the board initially ---
        self.updateBoard()        
            
    def viewBoard(self):
        self.clear()      
        self.UI_chessBoard()
        if self.game.gameOver:
            self.displayWinner()
        else:
            self.displayTurn()
        self.displayMoveNumber()
        if self.game.turn == 'White' and self.game.whitePlayer.type == 'computer' or self.game.turn == 'Black' and self.game.blackPlayer.type == 'computer':
            # self.updateBoard()
            self.playComputerMove()
        self.root.mainloop()
        
    def UI_promotePawn(self):
        top = tk.Toplevel(self.root)
        tk.Label(top, text='Pawn promotion. Choose your piece').grid(row=0,column=0,columnspan=2)
        tk.Button(top, text='Queen', command=lambda window=top: self.promotionButton(window,'Queen')).grid(row=1, column=0)
        tk.Button(top, text='Knight', command=lambda window=top: self.promotionButton(window,'Knight')).grid(row=1, column=1)
        tk.Button(top, text='Bishop', command=lambda window=top: self.promotionButton(window,'Bishop')).grid(row=2, column=0)
        tk.Button(top, text='Rook', command=lambda window=top: self.promotionButton(window,'Rook')).grid(row=2, column=1)
        top.mainloop()
        
                  
    def UI_savedGamesMenu(self):
       self.clear()
       
       # Configure the root window
       self.root.configure(bg='#f0f0f0')
       
       # Main container frame
       main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=40, pady=30)
       main_frame.pack()
       
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
               options.append(f"{i+1}: {wName} vs {bName}")
           
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
                              command=lambda: self.viewSavedGame(filePaths[int(variable.get().split(':')[0])-1]))
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
        container.pack()
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
                                   font=('Arial', 32),
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