import random
import numpy as np
from reversi_bot import ReversiBot
from reversi import ReversiGameState
import copy
import json
import os

class GeneticTrainer:
    def __init__(self, population_size=50, games_per_match=10):
        self.population_size = population_size
        self.games_per_match = games_per_match
        self.population = []
        self.best_weights_history = []
        self.initialize_population()
        
    def initialize_population(self):
        """Initialize random population of bots with different weights"""
        for _ in range(self.population_size):
            # Generate random weights between -1 and 1
            weights = [random.uniform(-1, 1) for _ in range(6)]
            
            self.population.append({
                'weights': weights,
                'max_depth': random.randint(1, 10),
                'fitness': 0
            })
    
    def evaluate_fitness(self, bot1_weights, bot2_weights, bot1_max_depth, bot2_max_depth):
        """Play multiple games between two bots and return win ratio for bot1"""
        bot1_wins = 0
        
        def print_board(board):
            """Helper function to print board in a readable format"""
            print("\n  0 1 2 3 4 5 6 7")
            for i in range(8):
                row = [str(i)]
                for j in range(8):
                    if board[i][j] == 0:
                        row.append('.')
                    elif board[i][j] == 1:
                        row.append('●')
                    else:
                        row.append('○')
                print(' '.join(row))
            print()
        
        for game in range(self.games_per_match):
            print(f"\nStarting Game {game + 1}")
            print(f"Bot 1 weights: {bot1_weights}")
            print(f"Bot 2 weights: {bot2_weights}")
            
            # Create new game state with initial Reversi board setup
            initial_board = np.zeros((8, 8), dtype=int)
            initial_board[3][3] = 1
            initial_board[3][4] = 2
            initial_board[4][3] = 2
            initial_board[4][4] = 1
            
            try:
                state = ReversiGameState(initial_board, 1, 0, 0, 0, 0, 0, 0)
                
                # Create bots with their respective weights
                bot1 = ReversiBot(0, *bot1_weights)
                bot2 = ReversiBot(0, *bot2_weights)
                
                current_player = 1
                no_valid_moves_count = 0
                move_count = 0
                
                while True:
                    valid_moves = state.get_valid_moves()
                    print(f"Valid moves for player {state.turn}: {valid_moves}")
                    
                    if not valid_moves:
                        print(f"Player {state.turn} has no valid moves!")
                        no_valid_moves_count += 1
                        if no_valid_moves_count >= 2:
                            break
                    else:
                        no_valid_moves_count = 0
                        current_bot = bot1 if state.turn == 1 else bot2
                        move = current_bot.make_move(state)
                        print(f"Bot chose move: {move}")
                        
                        if move:
                            move_count += 1
                            state.simulate_move(move)
                            print_board(state.board)
                        
                    state.turn = 3 - state.turn  # Switch between 1 and 2
                
                # Count pieces to determine winner
                player1_pieces = np.count_nonzero(state.board == 1)
                player2_pieces = np.count_nonzero(state.board == 2)
                
                print(f"\nGame {game + 1} finished!")
                print(f"Final score - Player 1: {player1_pieces}, Player 2: {player2_pieces}")
                
                if player1_pieces > player2_pieces:
                    print("Player 1 wins!")
                    bot1_wins += 1
                elif player1_pieces == player2_pieces:
                    print("It's a draw!")
                    bot1_wins += 0.5  # Draw counts as half a win
                else:
                    print("Player 2 wins!")
                
                return bot1_wins / self.games_per_match
            except Exception as e:
                print(f"Error during game: {e}")
                raise e
    
    def tournament(self):
        """Run tournament between all bots to determine fitness"""
        for i in range(len(self.population)):
            total_fitness = 0
            for j in range(len(self.population)):
                if i != j:
                    fitness = self.evaluate_fitness(
                        self.population[i]['weights'],
                        self.population[j]['weights'],
                        self.population[i]['max_depth'],
                        self.population[j]['max_depth']
                    )
                    total_fitness += fitness
            # Average fitness against all opponents
            self.population[i]['fitness'] = total_fitness / (len(self.population) - 1)
    
    def select_parents(self):
        """Select parents using tournament selection"""
        tournament_size = 3
        tournament = random.sample(self.population, tournament_size)
        return max(tournament, key=lambda x: x['fitness'])
    
    def crossover(self, parent1, parent2):
        """Create child by combining parents' weights"""
        child_weights = []
        for w1, w2 in zip(parent1['weights'], parent2['weights']):
            if random.random() < 0.5:
                child_weights.append(w1)
            else:
                child_weights.append(w2)
        return {'weights': child_weights, 'fitness': 0}
    
    def mutate(self, individual, mutation_rate=0.1, mutation_range=0.2):
        """Randomly mutate weights"""
        new_weights = []
        for weight in individual['weights']:
            if random.random() < mutation_rate:
                mutation = random.uniform(-mutation_range, mutation_range)
                new_weights.append(weight + mutation)
            else:
                new_weights.append(weight)
        return {'weights': new_weights, 'fitness': 0}
    
    def save_progress(self, generation):
        """Save the current best weights and training progress"""
        data = {
            'generation': generation,
            'best_weights': self.population[0]['weights'],
            'best_fitness': self.population[0]['fitness'],
            'weights_history': self.best_weights_history
        }
        
        with open('training_progress.json', 'w') as f:
            json.dump(data, f)
    
    def load_progress(self):
        """Load previous training progress if it exists"""
        if os.path.exists('training_progress.json'):
            with open('training_progress.json', 'r') as f:
                data = json.load(f)
                return data
        return None
    
    def evolve(self, generations=100):
        """Run the genetic algorithm for specified generations"""
        # Try to load previous progress
        progress = self.load_progress()
        start_gen = 0
        if progress:
            start_gen = progress['generation']
            self.best_weights_history = progress['weights_history']
            print(f"Resuming from generation {start_gen}")
        
        for generation in range(start_gen, generations):
            print(f"Generation {generation + 1}")
            
            self.tournament()
            self.population.sort(key=lambda x: x['fitness'], reverse=True)
            
            # Save best weights from this generation
            self.best_weights_history.append({
                'generation': generation,
                'weights': self.population[0]['weights'],
                'fitness': self.population[0]['fitness']
            })
            
            print(f"Best fitness: {self.population[0]['fitness']}")
            print(f"Best weights: {self.population[0]['weights']}")
            
            # Save progress every 5 generations
            if generation % 5 == 0:
                self.save_progress(generation)
            
            # Create new population
            new_population = []
            
            # Keep top 3 individuals (elitism)
            new_population.extend(copy.deepcopy(self.population[:3]))
            
            while len(new_population) < self.population_size:
                parent1 = self.select_parents()
                parent2 = self.select_parents()
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                new_population.append(child)
            
            self.population = new_population

if __name__ == "__main__":
    trainer = GeneticTrainer(population_size=2, games_per_match=4)
    trainer.evolve(generations=100) 