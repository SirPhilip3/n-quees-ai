import random as rd
import numpy as np
import math
import matplotlib.pyplot as plt

class AnnealingExperiment:
    def __init__(self, initial_temperature=100, max_iterations=1000, table_size=8, schedule_type='linear', cooling_rate=1, seed=None):
        self.initial_temperature = initial_temperature
        self.max_iterations = max_iterations
        self.cooling_rate = cooling_rate
        self.n = table_size
        self.current_state = [] # (row, col, fitness)
        self.schedule = []

        self.history = []  # to keep track of the states visited

        self.acceptance_history = []  # to track acceptance decisions

        if schedule_type == 'linear':
            self.linear_schedule()
        elif schedule_type == 'exponential':
            self.exponential_schedule()
        elif schedule_type == 'logarithmic':
            self.logarithmic_schedule()
        else:
            raise ValueError("Invalid schedule type. Choose 'linear', 'exponential', or 'logarithmic'.")
        # self.schedule = [initial_temperature - i for i in range(initial_temperature)]  #! Simple linear schedule test

        # permetti di settare un seed per la riproducibilità
        self.seed = seed
        if seed is not None:
            rd.seed(seed)
        
        self.set_initial_random_state()
    
    def set_initial_random_state(self):
        i = 0
        while i < self.n:
            # da valutare se metere solo 1 per colonna come requisito iniziale
            row = rd.randint(0, self.n - 1)
            # col = rd.randint(0, self.n - 1)
            if (row, i, 0) not in self.current_state:
                self.current_state.append((row, i, 0))  # (row, col, fitness)
                i += 1

    def linear_schedule(self):
        decrement = self.initial_temperature / self.max_iterations
        self.schedule = [self.initial_temperature - (i * decrement) for i in range(self.max_iterations)]  

    def exponential_schedule(self):
        self.schedule = [self.initial_temperature * (self.cooling_rate ** i) for i in range(self.max_iterations)]

    def logarithmic_schedule(self):
        # K = 100 
        self.schedule = [self.initial_temperature / (1 + math.log(1 + i)) for i in range(self.max_iterations)]

    def fitness_function(self, state): 
        # somma delle volte che ogni regina si attacca
        s = [(r, c, 0) for (r, c, _) in state]  # copia pulita
        total = 0 
        for q in range(self.n):
            total_q = 0
            row_q, col_q, _ = state[q]
            remaining = state[:q] + state[q+1:]

            for row_j, col_j, _ in remaining:
                if row_q == row_j:
                    total_q += 1
                if col_q == col_j: # teoricamente inutile perchè mettiamo solo 1 regina per colonna all'inizio
                    total_q += 1
                if abs(row_q - row_j) == abs(col_q - col_j):
                    total_q += 1
            
            total += total_q

            s[q] = (row_q, col_q, total_q)

        # print("State with fitness: ", state)
        return total , s

    def neighbor(self, state):
        # Generate neighboring states by moving each queen to a different row in its column
        neighbor_state = state.copy()
        #print("Generating neighbor for state: ", neighbor_state)
        #! maybe consider a different neighbor selection
        queen = rd.randint(0, self.n - 1) 

        current_row, col, _ = neighbor_state[queen]
        new_row = rd.choice([r for r in range(self.n) if r != current_row])
        neighbor_state[queen] = (new_row, col, 0)

        for i in range(self.n):
            row, col, _ = neighbor_state[i]
            neighbor_state[i] = (row, col, 0)  # Reset fitness
        return neighbor_state
    
    def neighbor_alternative(self, state, n_moves=2):
        neighbor_state = state.copy()
    
        # Select random queens to move
        queens_to_move = rd.sample(range(self.n), min(n_moves, self.n))
        
        for queen in queens_to_move:
            current_row, col, _ = neighbor_state[queen]
            new_row = rd.choice([r for r in range(self.n) if r != current_row])
            neighbor_state[queen] = (new_row, col, 0)
        
        # Reset fitness
        for i in range(self.n):
            row, col, _ = neighbor_state[i]
            neighbor_state[i] = (row, col, 0)
        
        return neighbor_state


    # return current state and score to check if solution found
    def simulated_annealing (self , initial ) :
        current = initial
        current_score , current = self.fitness_function(current)
        # this should be the iterations over the temperature 
        i = 0
        for T in self.schedule:
            i += 1
            self.history.append((T, current_score, current))

            #print("Temperature: ", T)
            
            if current_score == 0: #! se 0 allora significa che nessuna regina si attacca = soluzione trovata
                # print("Solution found: ", current)
                return current, current_score
            
            if T == 0:
                # print("Final state: ", current)
                return current, current_score


            # next = self.neighbor_alternative( current ) # choice a neighbor state
            next = self.neighbor( current ) # choice a neighbor state
            next_score , next = self.fitness_function( next )

            #print("Current state: ", current)
            #print("Next state: ", next)
            
            de = next_score - current_score
            
            #print("Delta E: ", de)
            if de < 0: 
                current, current_score = next , next_score

                self.acceptance_history.append({
                    'iteration': i,
                    'temperature': T,
                    'delta_e': de,
                    'probability': 1.0,
                    'random_value': None,
                    'accepted': True,
                    'reason': 'better'
                })

            else :
                probability = math.exp(-de / T)
                random_value = rd.random()
                accepted = random_value < probability
                
                self.acceptance_history.append({
                    'iteration': i,
                    'temperature': T,
                    'delta_e': de,
                    'probability': probability,
                    'random_value': random_value,
                    'accepted': accepted,
                    'reason': 'worse_accepted' if accepted else 'worse_rejected'
                })
                
                if accepted:
                    current, current_score = next , next_score
                # if rd.random() < math.exp( - de / T ) :
                #     current, current_score = next , next_score
        
        #print("Final state: ", current)
        return current , current_score




    def visualize_history(self, save_path=None):
        """Enhanced visualization showing fitness evolution over iterations"""
        iterations = list(range(len(self.history)))
        temperatures = [record[0] for record in self.history]
        fitness_values = [record[1] for record in self.history]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Plot fitness over iterations
        ax1.plot(iterations, fitness_values, linewidth=2, color='blue', alpha=0.7)
        ax1.set_xlabel('Iteration', fontsize=12)
        ax1.set_ylabel('Fitness (Conflicts)', fontsize=12)
        ax1.set_title('Fitness Evolution Over Iterations', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=0, color='green', linestyle='--', label='Optimal Solution')
        ax1.legend()
        
        # Plot temperature over iterations
        ax2.plot(iterations, temperatures, linewidth=2, color='red', alpha=0.7)
        ax2.set_xlabel('Iteration', fontsize=12)
        ax2.set_ylabel('Temperature', fontsize=12)
        ax2.set_title('Temperature Schedule', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
        else:
            plt.show()
    
    def visualize_comprehensive(self, save_path=None):
        """Comprehensive visualization with multiple subplots"""
        iterations = list(range(len(self.history)))
        temperatures = [record[0] for record in self.history]
        fitness_values = [record[1] for record in self.history]
        
        fig = plt.figure(figsize=(15, 10))
        
        # 1. Fitness over time
        ax1 = plt.subplot(2, 3, 1)
        ax1.plot(iterations, fitness_values, linewidth=2, color='blue')
        ax1.set_xlabel('Iteration')
        ax1.set_ylabel('Fitness (Conflicts)')
        ax1.set_title('Fitness Evolution')
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=0, color='green', linestyle='--', alpha=0.5)
        
        # 2. Temperature over time
        ax2 = plt.subplot(2, 3, 2)
        ax2.plot(iterations, temperatures, linewidth=2, color='red')
        ax2.set_xlabel('Iteration')
        ax2.set_ylabel('Temperature')
        ax2.set_title('Temperature Schedule')
        ax2.grid(True, alpha=0.3)
        
        # 3. Fitness vs Temperature (phase diagram)
        ax3 = plt.subplot(2, 3, 3)
        scatter = ax3.scatter(temperatures, fitness_values, c=iterations, cmap='viridis', alpha=0.6)
        ax3.set_xlabel('Temperature')
        ax3.set_ylabel('Fitness (Conflicts)')
        ax3.set_title('Phase Diagram')
        ax3.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax3, label='Iteration')
        
        # 4. Fitness improvement rate
        ax4 = plt.subplot(2, 3, 4)
        if len(fitness_values) > 1:
            improvements = [fitness_values[i] - fitness_values[i+1] for i in range(len(fitness_values)-1)]
            ax4.plot(iterations[1:], improvements, linewidth=1, color='green', alpha=0.7)
            ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            ax4.set_xlabel('Iteration')
            ax4.set_ylabel('Fitness Change')
            ax4.set_title('Fitness Improvement Rate')
            ax4.grid(True, alpha=0.3)
        
        # 5. Acceptance probability estimation
        ax5 = plt.subplot(2, 3, 5)
        if len(self.acceptance_history) > 1:
            # Count acceptance statistics
            worse_accepted = [d for d in self.acceptance_history if d['reason'] == 'worse_accepted']
            worse_rejected = [d for d in self.acceptance_history if d['reason'] == 'worse_rejected']
            better = [d for d in self.acceptance_history if d['reason'] == 'better']
            
            # Plot acceptance probability over time
            accepted_probs = [d['probability'] for d in self.acceptance_history if d['reason'] == 'worse_accepted']
            accepted_iters = [d['iteration'] for d in self.acceptance_history if d['reason'] == 'worse_accepted']
            
            rejected_probs = [d['probability'] for d in self.acceptance_history if d['reason'] == 'worse_rejected']
            rejected_iters = [d['iteration'] for d in self.acceptance_history if d['reason'] == 'worse_rejected']
            
            # Plot accepted worse moves
            if accepted_iters:
                ax5.scatter(accepted_iters, accepted_probs, color='green', marker='o', 
                           s=30, alpha=0.6, label=f'Accepted Worse ({len(worse_accepted)})')
            
            # Plot rejected worse moves
            if rejected_iters:
                ax5.scatter(rejected_iters, rejected_probs, color='red', marker='x', 
                           s=30, alpha=0.4, label=f'Rejected Worse ({len(worse_rejected)})')
            
            ax5.set_xlabel('Iteration')
            ax5.set_ylabel('Acceptance Probability')
            ax5.set_title(f'Worse Moves: {len(better)} Better, {len(worse_accepted)} Accepted, {len(worse_rejected)} Rejected')
            ax5.legend(fontsize=9)
            ax5.grid(True, alpha=0.3)
            ax5.set_ylim([0, 1.05])
        
        # 6. Final board state
        ax6 = plt.subplot(2, 3, 6)
        if self.history:
            final_state = self.history[-1][2]
            board = np.zeros((self.n, self.n))
            for row, col, _ in final_state:
                board[row, col] = 1
            ax6.imshow(board, cmap='RdYlGn', interpolation='nearest')
            ax6.set_title(f'Final Board (Fitness={self.history[-1][1]})')
            ax6.set_xticks(range(self.n))
            ax6.set_yticks(range(self.n))
            ax6.grid(False)
            
            # Add queen symbols
            for row, col, _ in final_state:
                ax6.text(col, row, '♛', ha='center', va='center', fontsize=20, color='black')
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
        else:
            plt.show()
    
    def visualize_board_evolution(self, save_path=None):
        """Visualize how the board state changes over time"""
        # Select key moments to display
        n_snapshots = min(9, len(self.history))
        snapshot_indices = np.linspace(0, len(self.history)-1, n_snapshots, dtype=int)
        
        fig, axes = plt.subplots(3, 3, figsize=(12, 12))
        axes = axes.flatten()
        
        for idx, snapshot_idx in enumerate(snapshot_indices):
            T, fitness, state = self.history[snapshot_idx]
            
            board = np.zeros((self.n, self.n))
            for row, col, _ in state:
                board[row, col] = 1
            
            axes[idx].imshow(board, cmap='RdYlGn', interpolation='nearest')
            axes[idx].set_title(f'Iter {snapshot_idx}\nT={T:.2f}, F={fitness}')
            axes[idx].set_xticks(range(self.n))
            axes[idx].set_yticks(range(self.n))
            axes[idx].grid(False)
            
            # Add queen symbols
            for row, col, _ in state:
                axes[idx].text(col, row, '♛', ha='center', va='center', fontsize=16, color='black')
        
        # Hide unused subplots
        for idx in range(n_snapshots, 9):
            axes[idx].axis('off')
        
        plt.suptitle('Board Evolution During Simulated Annealing', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
        else:
            plt.show()
        