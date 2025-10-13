# -*- coding: utf-8 -*-

class Player():
    def __init__(self, player_name, player_type):
        self.name = player_name
        self.type = player_type
        if player_type == 'computer':
            self.display_name = f"{self.name} ({self.type})"
        else:
            self.display_name = self.name
