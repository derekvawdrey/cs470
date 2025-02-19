import math
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
        self.file_name = "training_progress_TEST_" + str(random.randint(1, 1000000)) + ".json"        
        
    def initialize_population(self):
        """Initialize random population of bots with different weights"""
        rng = np.random.default_rng()
        for _ in range(self.population_size):
            weights = [rng.uniform(0, 1) for _ in range(7)]
            # The 6th weight is the random weight, which is a number between 1 and 100 so I dont want it to be huge
            weights[5] = rng.uniform(0, 0.4)
            # Stability being the 4th weight, if it is active (greater than 0.2) I want to cap the max_depth at 5
            if weights[3] > 0.2:
                max_depth = random.randint(1, 5)
            else:
                max_depth = random.randint(1, 8)
            self.population.append({
                'weights': weights,
                'max_depth': max_depth,
                'fitness': 0
            })
    
    def evaluate_fitness(self, bot1_weights, bot2_weights, bot1_max_depth, bot2_max_depth):
        """Play multiple games between two bots and return win ratio for bot1"""
        bot1_wins = 0
        bot1_timer = 180
        bot2_timer = 180
        
        def print_board_and_stats(state, bot1_timer, bot2_timer):
            """Helper function to print board and statistics"""
            # Clear screen
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
            
            print("\n=== Game Statistics ===")
            print(f"Black (●) Time: {bot1_timer:.2f}s")
            print(f"White (○) Time: {bot2_timer:.2f}s")
            player1_pieces = np.count_nonzero(state.board == 1)
            player2_pieces = np.count_nonzero(state.board == 2)
            print(f"Black pieces: {player1_pieces}")
            print(f"White pieces: {player2_pieces}")
            print(f"Black max_depth: {bot1_max_depth}")
            print(f"White max_depth: {bot2_max_depth}")
            print(f"Black weights: ")
            print(f"    Coin parity: {bot1_weights[0]}")
            print(f"    Mobility: {bot1_weights[1]}")
            print(f"    Corners Captured: {bot1_weights[2]}")
            print(f"    Stability: {bot1_weights[3]}")
            print(f"    Positional Weight: {bot1_weights[4]}")
            print(f"    Random: {bot1_weights[5]}")
            print(f"    Frontier Discs: {bot1_weights[6]}")
            print(f"White weights:")
            print(f"    Coin parity: {bot2_weights[0]}")
            print(f"    Mobility: {bot2_weights[1]}")
            print(f"    Corners Captured: {bot2_weights[2]}")
            print(f"    Stability: {bot2_weights[3]}")
            print(f"    Positional Weight: {bot2_weights[4]}")
            print(f"    Random: {bot2_weights[5]}")
            print(f"    Frontier Discs: {bot2_weights[6]}")
            print("===================")
        
        for game in range(self.games_per_match):
            print(f"\nStarting Game {game + 1}")
            
            initial_board = np.zeros((8, 8), dtype=int)
            initial_board[3][3] = 1
            initial_board[3][4] = 2
            initial_board[4][3] = 2
            initial_board[4][4] = 1
            
            try:
                state = ReversiGameState(initial_board, 1, 0, 0, 0, 0, 0, 0, 0)
                bot1 = ReversiBot(0, bot1_max_depth, *bot1_weights)
                bot2 = ReversiBot(0, bot2_max_depth, *bot2_weights)
                
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
                        start_time = time.time()
                        
                        try:
                            move = current_bot.make_move(state)
                            time_taken = time.time() - start_time
                            
                            if state.turn == 1:
                                bot1_timer -= time_taken
                                if bot1_timer <= 0:
                                    print("Bot 1 (Black) ran out of time!")
                                    return 0
                            else:
                                bot2_timer -= time_taken
                                if bot2_timer <= 0:
                                    print("Bot 2 (White) ran out of time!")
                                    return 1
                            
                            if move:
                                move_count += 1
                                state.simulate_move(move)
                                print_board_and_stats(state, bot1_timer, bot2_timer)
                                time.sleep(0.1)
                            
                        except Exception as e:
                            print(f"Error during move: {e}")
                            return 0 if state.turn == 1 else 1
                    
                    state.turn = 3 - state.turn
                
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
                
                time.sleep(1)
                
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
        """Create child by combining parents' weights and max_depth"""
        child_weights = []
        for w1, w2 in zip(parent1['weights'], parent2['weights']):
            if random.random() < 0.5:
                child_weights.append(w1)
            else:
                child_weights.append(w2)
        
        # Inherit max_depth from one of the parents
        max_depth = parent1['max_depth'] if random.random() < 0.5 else parent2['max_depth']
        
        return {
            'weights': child_weights,
            'max_depth': max_depth,
            'fitness': 0
        }
    
    def mutate(self, individual, mutation_rate=0.1, mutation_range=0.2):
        """Randomly mutate weights and possibly max_depth"""
        new_weights = []
        for weight in individual['weights']:
            if random.random() < mutation_rate:
                mutation = random.uniform(-mutation_range, mutation_range)
                new_weights.append(weight + mutation)
            else:
                new_weights.append(weight)
        
        max_depth = individual['max_depth']
        if random.random() < mutation_rate:
            max_depth += math.floor(random.uniform(-1, 1))
        
        return {
            'weights': new_weights,
            'max_depth': max_depth,
            'fitness': 0
        }
    
    def save_progress(self, generation, best_weights, best_fitness, best_max_depth):
        """Save the training progress to a file"""
        progress = {
            'generation': generation,
            'best_weights': best_weights,
            'best_fitness': best_fitness,
            'best_max_depth': best_max_depth,
            'weights_history': []
        }
        
        try:
            with open(self.file_name, 'r') as f:
                old_progress = json.load(f)
                progress['weights_history'] = old_progress.get('weights_history', [])
        except FileNotFoundError:
            pass
        
        # Add current generation to history
        progress['weights_history'].append({
            'generation': generation,
            'weights': best_weights,
            'fitness': best_fitness,
            'max_depth': best_max_depth
        })
        
        with open(self.file_name, 'w') as f:
            json.dump(progress, f)
    
    def load_progress(self):
        """Load previous training progress if it exists"""
        if os.path.exists(self.file_name):
            with open(self.file_name, 'r') as f:
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
            if generation % 1 == 0:
                self.save_progress(generation, self.population[0]['weights'], self.population[0]['fitness'], self.population[0]['max_depth'])
            
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
    trainer = GeneticTrainer(population_size=6, games_per_match=1)
    trainer.evolve(generations=10) 