import random as rd
import numpy as np
from numpy.random import choice
import matplotlib.pyplot as plt

class GeneticExperiment:
    def __init__(self, population_size=150, table_size=8, seed=None, iterations=1000, crossover_rate=0.7, mutation_rate=0.01):
        self.population_size = population_size
        self.table_size = table_size
        self.iterations = iterations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate

        self.history = {
            'generation': [],
            'best_fitness': [],
            'avg_fitness': [],
            'worst_fitness': [],
            'std_fitness': [],
            'diversity': [],  # genetic diversity metric
            'best_individual': []
        }

        # permetti di settare un seed per la riproducibilità
        self.seed = seed
        if seed is not None:
            rd.seed(seed)
            np.random.seed(seed)
        
        self.population = np.full((population_size, table_size), -1, dtype=int) # initialize at -1 , it will be overwritten by initial_population
        self.population_probabilities = np.zeros(population_size, dtype=float) # probabilities for selection
        self.fitness_values = np.zeros(population_size, dtype=int)
        self.initial_population() # fill initial population


    def calculate_diversity(self):
        # diversity as the ratio of unique individuals to total population
        unique_individuals = len(np.unique(self.population, axis=0))
        return unique_individuals / self.population_size

    def record_generation(self, generation):
        self.history['generation'].append(generation)
        self.history['best_fitness'].append(np.min(self.fitness_values))
        self.history['avg_fitness'].append(np.mean(self.fitness_values))
        self.history['worst_fitness'].append(np.max(self.fitness_values))
        self.history['std_fitness'].append(np.std(self.fitness_values))
        self.history['diversity'].append(self.calculate_diversity())
        
        best_idx = np.argmin(self.fitness_values)
        self.history['best_individual'].append(self.population[best_idx].copy())

    def initial_population(self):
        for i in range(self.population_size):
            current_table = self.population[i] 
            j = 0
            while j < self.table_size:
                row = rd.randint(0, self.table_size - 1)
                if row not in current_table:
                    current_table[j] = row # modifica anche population grazie al view
                    j += 1
        
    def set_population_probabilities(self):
        total_fitness = sum(1 / f for f in self.fitness_values if f != 0)
        for i in range(self.population_size):
            self.population_probabilities[i] = (1 / self.fitness_values[i]) / total_fitness


    # encoding of the state just a list of integers where the index represents the column and the value at that index represents the row
    def selection(self):

        self.set_population_probabilities()

        selected = choice(list(range(0, self.population_size)), p=self.population_probabilities, size=self.population_size)
        return selected

    def crossover(self, parents):
        if rd.random() < self.crossover_rate:
            parent1 = self.population[parents[0]]
            parent2 = self.population[parents[1]]

            crossover_point = rd.randint(1, self.table_size - 2)
            child1 = np.concatenate((parent1[:crossover_point], parent2[crossover_point:]))
            child2 = np.concatenate((parent2[:crossover_point], parent1[crossover_point:]))

            # replace parents with children in population
            self.population[parents[0]] = child1
            self.population[parents[1]] = child2


    def mutation(self):
        for index in range(self.population_size):
            if rd.random() < self.mutation_rate:
                individual = self.population[index]
                
                mutation_point_index = rd.randint(0, self.table_size - 1)
                mutation_point1 = rd.randint(0, self.table_size - 1)

                individual[mutation_point_index] = mutation_point1
                
                self.population[index] = individual
        

    def fitness_function(self, individual): # same as in simulated annealing 
        total = 0 
        for q in range(self.table_size):
            total_q = 0
            row_q = individual[q]

            for col_j in range(self.table_size):
                if col_j == q:
                    continue
                row_j = individual[col_j]

                if row_q == row_j:
                    total_q += 1
                if abs(row_q - row_j) == abs(q - col_j):
                    total_q += 1
            
            total += total_q

        return total 

    def check_solution(self):
        for index, fitness in enumerate(self.fitness_values):
            if fitness == 0:
                return True , index
        return False, None

    def genetic_solve(self):
        
        for iteration in range(self.iterations):
            for i, individual in enumerate(self.population):
                self.fitness_values[i] = self.fitness_function(individual)
            
            self.record_generation(iteration)

            ret , sol_indx = self.check_solution() 
            if ret:
                return True ,self.population[sol_indx] , self.fitness_values[sol_indx] , iteration
            
            mating_indices = self.selection()

            self.population = self.population[mating_indices]

            selected_couples = []
            while len(selected_couples) < self.population_size // 2:
                parent1_idx = rd.randint(0, self.population_size - 1)
                parent2_idx = rd.randint(0, self.population_size - 1)
                parents = (parent1_idx, parent2_idx)
                if parent1_idx != parent2_idx:
                    if parents not in selected_couples:
                        selected_couples.append(parents)
            
            for parents in selected_couples:
                self.crossover(parents)

            self.mutation()

        return False , self.population , self.fitness_values , self.iterations

    def visualize_evolution(self, save_path=None):
        """Visualize the evolution of the genetic algorithm"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        generations = self.history['generation']
        
        # 1. Fitness Evolution
        ax1 = axes[0, 0]
        ax1.plot(generations, self.history['best_fitness'], label='Best', linewidth=2, color='green')
        ax1.plot(generations, self.history['avg_fitness'], label='Average', linewidth=2, color='blue')
        ax1.plot(generations, self.history['worst_fitness'], label='Worst', linewidth=2, color='red', alpha=0.5)
        ax1.fill_between(generations, 
                         np.array(self.history['avg_fitness']) - np.array(self.history['std_fitness']),
                         np.array(self.history['avg_fitness']) + np.array(self.history['std_fitness']),
                         alpha=0.2, color='blue')
        ax1.set_xlabel('Generation', fontsize=12)
        ax1.set_ylabel('Fitness (Conflicts)', fontsize=12)
        ax1.set_title('Fitness Evolution', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=0, color='green', linestyle='--', alpha=0.5, label='Optimal')
        
        # 2. Genetic Diversity
        ax2 = axes[0, 1]
        ax2.plot(generations, self.history['diversity'], linewidth=2, color='purple')
        ax2.set_xlabel('Generation', fontsize=12)
        ax2.set_ylabel('Diversity (Unique Individuals Ratio)', fontsize=12)
        ax2.set_title('Population Diversity', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim([0, 1])

        # 3. Fitness Improvement Rate
        ax3 = axes[1, 0]
        if len(self.history['best_fitness']) > 1:
            improvements = [self.history['best_fitness'][i] - self.history['best_fitness'][i+1] 
                          for i in range(len(self.history['best_fitness'])-1)]
            ax3.plot(generations[1:], improvements, linewidth=1, color='orange', alpha=0.7)
            ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            ax3.set_xlabel('Generation', fontsize=12)
            ax3.set_ylabel('Best Fitness Change', fontsize=12)
            ax3.set_title('Fitness Improvement Rate', fontsize=14, fontweight='bold')
            ax3.grid(True, alpha=0.3)
        
        # 4. Final Best Board
        ax4 = axes[1, 1]
        if self.history['best_individual']:
            best_individual = self.history['best_individual'][-1]
            board = np.zeros((self.table_size, self.table_size))
            for col, row in enumerate(best_individual):
                if 0 <= row < self.table_size:
                    board[row, col] = 1
            
            ax4.imshow(board, cmap='RdYlGn', interpolation='nearest')
            ax4.set_title(f'Best Solution (Fitness={self.history["best_fitness"][-1]})', 
                         fontsize=14, fontweight='bold')
            ax4.set_xticks(range(self.table_size))
            ax4.set_yticks(range(self.table_size))
            ax4.grid(False)
            
            # Add queen symbols
            for col, row in enumerate(best_individual):
                if 0 <= row < self.table_size:
                    ax4.text(col, row, '♛', ha='center', va='center', fontsize=20, color='black')
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
        else:
            plt.show()
