import random as rand

class MiniMaxNode:
    def __init__(self, state, parent: 'MiniMaxNode', move: tuple, max_depth: int, alpha, beta):
        self.state = state
        self.parent = parent
        self.move = move
        self.alpha = alpha
        self.beta = beta
        self.children = []
        self.max_depth = max_depth
        self.cost = 0

    def expand(self, maximizing_player):
        '''
            Expand the node boiiiii
        '''
        if self.max_depth == 0:
            return self.state.get_score(self.state.turn)
        
        if maximizing_player:
            value = float("-inf")
        else:
            value = float("inf")

        valid_moves = self.state.get_valid_moves()
        if not valid_moves:
            return self.state.get_score(self.state.turn)
    
        for move in valid_moves:
            new_state = self.state.clone_state()
            new_state.simulate_move(move)

            child_node = MiniMaxNode(new_state, self, move, self.max_depth - 1, self.alpha, self.beta)
            self.children.append(child_node)

            if maximizing_player:
                value = max(value, child_node.expand(False))
                self.alpha = max(self.alpha, value)
                if value >= self.beta:
                    break
            else:
                value = min(value, child_node.expand(True))
                self.beta = min(self.beta, value)
                if value <= self.alpha:
                    break
        return value

class ReversiBot:
    def __init__(self, move_num, max_depth, w_1, w_2, w_3, w_4, w_5, w_6):
        self.move_num = move_num
        self.max_depth = max_depth
        self.w_1 = float(w_1) 
        self.w_2 = float(w_2)
        self.w_3 = float(w_3)
        self.w_4 = float(w_4)
        self.w_5 = float(w_5)
        self.w_6 = float(w_6)
        
    def make_move(self, state):
        '''
        This is the only function that needs to be implemented for the lab!
        The bot should take a game state and return a move.

        The parameter "state" is of type ReversiGameState and has two useful
        member variables. The first is "board", which is an 8x8 numpy array
        of 0s, 1s, and 2s. If a spot has a 0 that means it is unoccupied. If
        there is a 1 that means the spot has one of player 1's stones. If
        there is a 2 on the spot that means that spot has one of player 2's
        stones. The other useful member variable is "turn", which is 1 if it's
        player 1's turn and 2 if it's player 2's turn.

        ReversiGameState objects have a nice method called get_valid_moves.
        When you invoke it on a ReversiGameState object a list of valid
        moves for that state is returned in the form of a list of tuples.

        Move should be a tuple (row, col) of the move you want the bot to make.
        '''
        initial_beta = float("inf")
        initial_alpha = float("-inf")
        root_node = MiniMaxNode(state, None, None, 4, initial_alpha, initial_beta)
        root_node.state.w_1 = self.w_1
        root_node.state.w_2 = self.w_2
        root_node.state.w_3 = self.w_3
        root_node.state.w_4 = self.w_4
        root_node.state.w_5 = self.w_5
        root_node.state.w_6 = self.w_6

        best_score = float("-inf")
        best_move = None
        
        # find a move that maximizes the cost for initial alpha

        for move in root_node.state.get_valid_moves():
            new_state = root_node.state.clone_state()
            new_state.simulate_move(move)
            child_node = MiniMaxNode(new_state, root_node, move, self.max_depth - 1, root_node.alpha, root_node.beta)
            score = child_node.expand(True)
            if score > best_score:
                best_score = score
                best_move = move

        return best_move
