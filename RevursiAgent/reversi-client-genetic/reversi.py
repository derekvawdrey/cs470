import random
import numpy as np
import reversi_bot
import socket
import sys
import time

class ReversiServerConnection:
    def __init__(self, host, bot_move_num):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (host, 3333 + bot_move_num)
        self.sock.connect(server_address)
        self.sock.recv(1024)

    def get_game_state(self):
        server_msg = self.sock.recv(1024).decode('utf-8').split('\n')

        turn = int(server_msg[0])

        # If the game is over
        if turn == -999:
            return ReversiGameState(None, turn,0,0,0,0,0,0,0)

        # Flip is necessary because of the way the server does indexing
        board = np.flip(np.array([int(x) for x in server_msg[4:68]]).reshape(8, 8), 0)

        return ReversiGameState(board, turn,0,0,0,0,0,0,0)

    def send_move(self, move):
        # The 7 - bit is necessary because of the way the server does indexing
        move_str = str(7 - move[0]) + '\n' + str(move[1]) + '\n'
        self.sock.send(move_str.encode('utf-8'))

class ReversiGame:
    def __init__(self, host, bot_move_num, max_depth, w_1, w_2, w_3, w_4, w_5, w_6, w_7):
        self.bot_move_num = bot_move_num
        self.server_conn = ReversiServerConnection(host, bot_move_num)
        self.bot = reversi_bot.ReversiBot(bot_move_num, max_depth, w_1, w_2, w_3, w_4, w_5, w_6, w_7)

    def play(self):
        while True:
            state = self.server_conn.get_game_state()

            # If the game is over
            if state.turn == -999:
                time.sleep(1)
                sys.exit()

            # If it is the bot's turn
            if state.turn == self.bot_move_num:
                move = self.bot.make_move(state)
                self.server_conn.send_move(move)

class ReversiGameState:
    def __init__(self, board, turn, w_1, w_2, w_3, w_4, w_5, w_6, w_7):
        self.board_dim = 8 # Reversi is played on an 8x8 board
        self.board = board
        self.turn = turn # Whose turn is it
        self.simulated_moves = []
        self.w_1 = w_1
        self.w_2 = w_2
        self.w_3 = w_3
        self.w_4 = w_4
        self.w_5 = w_5
        self.w_6 = w_6
        self.w_7 = w_7
        self.position_values = np.array([
            [1.00, 0.20, 0.70, 0.60, 0.60, 0.70, 0.20, 1.00],
            [0.20, 0.10, 0.55, 0.50, 0.50, 0.55, 0.10, 0.20],
            [0.70, 0.55, 0.60, 0.55, 0.55, 0.60, 0.55, 0.70],
            [0.60, 0.50, 0.55, 0.50, 0.50, 0.55, 0.50, 0.60],
            [0.60, 0.50, 0.55, 0.50, 0.50, 0.55, 0.50, 0.60],
            [0.70, 0.55, 0.60, 0.55, 0.55, 0.60, 0.55, 0.70],
            [0.20, 0.10, 0.55, 0.50, 0.50, 0.55, 0.10, 0.20],
            [1.00, 0.20, 0.70, 0.60, 0.60, 0.70, 0.20, 1.00]
        ])

        self.position_values2 = np.array([
            [100, -15, 55, 40, 40, 55, -15, 100],
            [-15, -35, -20, 5, 5, -20, -35, -15],
            [55, -20, 10, 10, 10, 10, -20, 55],
            [40, 5, 10, -15, -15, 10, 5, 40],
            [40, 5, 10, -15, -15, 10, 5, 40],
            [55, -20, 10, 10, 10, 10, -20, 55],
            [-15, -35, -20, 5, 5, -20, -35, -15],
            [100, -15, 55, 40, 40, 55, -15, 100]
        ])

    def clone_state(self):
        return ReversiGameState(self.board, self.turn, self.w_1, self.w_2, self.w_3, self.w_4, self.w_5, self.w_6, self.w_7)

    def capture_will_occur(self, row, col, xdir, ydir, could_capture=0):
        # We shouldn't be able to leave the board
        if not self.space_is_on_board(row, col):
            return False

        # If we're on a space associated with our turn and we have pieces
        # that could be captured return True. If there are no pieces that
        # could be captured that means we have consecutive bot pieces.
        if self.board[row, col] == self.turn:
            return could_capture != 0

        if self.space_is_unoccupied(row, col):
            return False

        return self.capture_will_occur(row + ydir,
                                       col + xdir,
                                       xdir, ydir,
                                       could_capture + 1)

    def simulate_move(self, move):
        board_copy = np.copy(self.board)
        board_copy[move[0], move[1]] = self.turn
        directions = [(dx, dy) for dx in range(-1, 2) for dy in range(-1, 2) if not (dx == 0 and dy == 0)]
        
        row = move[0]
        col = move[1]
        for dx, dy in directions:
            curr_row = row + dy
            curr_col = col + dx
            
            if self.capture_will_occur(curr_row, curr_col, dx, dy):
                while True:
                    if not (0 <= curr_row < self.board_dim and 0 <= curr_col < self.board_dim):
                        break
                    if board_copy[curr_row, curr_col] == 0 or board_copy[curr_row, curr_col] == self.turn:
                        break
                    board_copy[curr_row, curr_col] = self.turn
                    curr_row += dy
                    curr_col += dx
        
        self.board = board_copy
        return self.get_score(self.turn)

    def get_score(self, turn):
        return self.w_1 * self.coin_parity(turn) + \
               self.w_2 * self.mobility(turn) + \
               self.w_3 * self.corners_captured(turn) + \
               self.w_4 * self.get_stability(turn) + \
               self.w_5 * self.get_positional_weight(turn) + \
               self.w_6 * self.get_random_weight() + \
               self.w_7 * self.frontier_discs(turn)

    def get_piece_count(self, player):
        return np.sum(self.board == player)
    
    def coin_parity(self,player):
        if(self.w_1 < 0.2):
            return 0
        return 100 * (self.get_piece_count(player) - self.get_piece_count(3 - player)) / (self.get_piece_count(player) + self.get_piece_count(3 - player))

    def mobility(self,player):
        if(self.w_2 < 0.2):
            return 0
        return 100 * len(self.get_valid_moves()) / (self.board_dim * self.board_dim)

    def corners_captured(self, player):
        if(self.w_3 < 0.2):
            return 0
        return 25 * (self.board[0, 0] == player) + \
               25 * (self.board[0, 7] == player) + \
               25 * (self.board[7, 0] == player) + \
               25 * (self.board[7, 7] == player)
    
    def get_stability(self, player):
        if self.w_4 < 0.2:
            return 0
            
        user_stable = 0
        for i in range(self.board_dim):
            for j in range(self.board_dim):
                if self.board[i, j] == player:
                    user_stable += self.position_values2[i][j]

        enemy_stable = 0
        for i in range(self.board_dim):
            for j in range(self.board_dim):
                if self.board[i, j] == 3 - player:
                    enemy_stable += self.position_values2[i][j]
        
        return (user_stable - enemy_stable) / 10
        
        
        

    def get_positional_weight(self, turn):
        if(self.w_5 < 0.1):
            return 0

        total = 0
        for i in range(self.board_dim):
            for j in range(self.board_dim):
                if self.board[i, j] == turn:
                    total += self.position_values[i][j]
        return total / 100
    
    def get_random_weight(self):
        if(self.w_6 < 0.1):
            return 0
        rng = np.random.default_rng()
        ran_num = rng.uniform(0, 100)
        return ran_num

    def frontier_discs(self, player):
        if self.w_7 < 0.1:
            return 0
        frontier_count = 0
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for row in range(self.board_dim):
            for col in range(self.board_dim):
                if self.board[row, col] == player:
                    for dx, dy in directions:
                        adj_row, adj_col = row + dy, col + dx
                        if self.space_is_on_board(adj_row, adj_col) and self.space_is_unoccupied(adj_row, adj_col):
                            frontier_count += 1
                            break

        return frontier_count * 2
    
    def change_turn(self):
        self.turn = 3 - self.turn
        return self.turn

    def space_is_on_board(self, row, col):
        return 0 <= row < self.board_dim and 0 <= col < self.board_dim

    def space_is_unoccupied(self, row, col):
        return self.board[row, col] == 0

    def space_is_available(self, row, col):
        return self.space_is_on_board(row, col) and \
               self.space_is_unoccupied(row, col)

    def is_valid_move(self, row, col):
        if self.space_is_available(row, col):
            # A valid move results in capture
            for xdir in range(-1, 2):
                for ydir in range(-1, 2):
                    if xdir == ydir == 0:
                        continue
                    if self.capture_will_occur(row + ydir, col + xdir, xdir, ydir):
                        return True

    def get_valid_moves(self):
        valid_moves = []

        # If the middle four squares aren't taken the remaining ones are all
        # that is available
        if 0 in self.board[3:5, 3:5]:
            for row in range(3, 5):
                for col in range(3, 5):
                    if self.board[row, col] == 0:
                        valid_moves.append((row, col))
        else:
            for row in range(self.board_dim):
                for col in range(self.board_dim):
                    if self.is_valid_move(row, col):
                        valid_moves.append((row, col))

        return valid_moves
