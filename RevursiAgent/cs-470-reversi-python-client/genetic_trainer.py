import random
import numpy as np
from reversi_bot import ReversiBot
from reversi import ReversiGameState
import copy
import json
import os
import time

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
        bot1_timer = 60
        bot2_timer = 60
        
        def print_board_and_stats(state, bot1_timer, bot2_timer):
            """Helper function to print board and statistics"""
            # Clear screen (works on most terminals)
            print("\033[H\033[J")
            
            # Print board
            print("\n  0 1 2 3 4 5 6 7")
            for i in range(8):
                row = [str(i)]
                for j in range(8):
                    if state.board[i][j] == 0:
                        row.append('.')
                    elif state.board[i][j] == 1:
                        row.append('●')
                    else:
                        row.append('○')
                print(' '.join(row))
            
            # Print statistics
            print("\n=== Game Statistics ===")
            print(f"Black (●) Time: {bot1_timer:.2f}s")
            print(f"White (○) Time: {bot2_timer:.2f}s")
            player1_pieces = np.count_nonzero(state.board == 1)
            player2_pieces = np.count_nonzero(state.board == 2)
            print(f"Black pieces: {player1_pieces}")
            print(f"White pieces: {player2_pieces}")
            print("===================")
        
        for game in range(self.games_per_match):
            print(f"\nStarting Game {game + 1}")
            
            # Create new game state with initial Reversi board setup
            initial_board = np.zeros((8, 8), dtype=int)
            initial_board[3][3] = 1
            initial_board[3][4] = 2
            initial_board[4][3] = 2
            initial_board[4][4] = 1
            
            try:
                state = ReversiGameState(initial_board, 1, 0, 0, 0, 0, 0, 0)
                bot1 = ReversiBot(0, bot1_max_depth, *bot1_weights)
                bot2 = ReversiBot(0, bot2_max_depth, *bot2_weights)
                
                current_player = 1
                no_valid_moves_count = 0
                move_count = 0
                
                while True:
                    valid_moves = state.get_valid_moves()
                    
                    if not valid_moves:
                        no_valid_moves_count += 1
                        if no_valid_moves_count >= 2:
                            break
                    else:
                        no_valid_moves_count = 0
                        current_bot = bot1 if state.turn == 1 else bot2
                        current_timer = bot1_timer if state.turn == 1 else bot2_timer
                        
                        start_time = time.time()
                        
                        try:
                            move = current_bot.make_move(state)
                            time_taken = time.time() - start_time
                            
                            if state.turn == 1:
                                bot1_timer -= time_taken
                                if bot1_timer <= 0:
                                    print("Bot 1 ran out of time!")
                                    return 0
                                else:
                                    bot2_timer -= time_taken
                                    if bot2_timer <= 0:
                                        print("Bot 2 ran out of time!")
                                        return 1
                            
                            if move:
                                move_count += 1
                                state.simulate_move(move)
                                print_board_and_stats(state, bot1_timer, bot2_timer)
                                time.sleep(0.1)  # Small delay to make the game visible
                            
                        except Exception as e:
                            print(f"Error during move: {e}")
                            return 0 if state.turn == 1 else 1
                    
                    state.turn = 3 - state.turn
                
                # Count pieces to determine winner
                player1_pieces = np.count_nonzero(state.board == 1)
                player2_pieces = np.count_nonzero(state.board == 2)
                
                print(f"\nGame {game + 1} finished!")
                print(f"Final score - Black: {player1_pieces}, White: {player2_pieces}")
                
                if player1_pieces > player2_pieces:
                    print("Black wins!")
                    bot1_wins += 1
                elif player1_pieces == player2_pieces:
                    print("It's a draw!")
                    bot1_wins += 0.5
                else:
                    print("White wins!")
                
                time.sleep(1)  # Pause to show final result
                
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