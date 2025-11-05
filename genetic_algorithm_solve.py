import random as rd
import numpy as np
from numpy.random import choice

class Experiment:
    def __init__(self, population_size, table_size, seed=None):
        self.population_size = population_size
        self.table_size = table_size

        self.population = np.full((population_size, table_size), -1, dtype=int)
        self.population_probabilities = np.zeros(population_size, dtype=float) # probabilities for selection
        self.fitness_values = np.zeros(population_size, dtype=int)
        self.initial_population() # fill initial population

        # permetti di settare un seed per la riproducibilità
        self.seed = seed
        if seed is not None:
            rd.seed(seed)

    def initial_population(self):
        for i in range(self.population_size):
            current_table = self.population[i] 
            j = 0
            while j < self.table_size:
                row = rd.randint(0, self.table_size - 1)
                if row not in current_table:
                    current_table[j] = row # modifica anche population grazie al view
                    j += 1
        

    # encoding of the state just a list of integers where the index represents the column and the value at that index represents the row
    def selection(self):

        #! test
        total_fitness = sum(self.fitness_values)
        for i in range(self.population_size):
            self.population_probabilities[i] = self.fitness_values[i] / total_fitness  #!! da rivedere -1

        selected = choice(list(range(0, self.population_size)), p=self.population_probabilities, size=self.population_size)
        print("Selected individuals indices: ", selected)
        return selected

    def crossover(self, parent1, parent2):
        pass

    def mutation(self, individual):
        pass

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

            # remaining = individual[:q] + individual[q+1:]
            
            # i = 0
            # for row_j in remaining:
            #     if i == q:
            #         i += 1
            #     if row_q == row_j:
            #         total_q += 1
            #     # if q == col_j:
            #     #     total_q += 1
            #     if abs(row_q - row_j) == abs(q - i):
            #         total_q += 1

            #     i += 1
            
            total += total_q

        return total 

    # pass a starting population
    def genetic_solve(self):
        for i, individual in enumerate(self.population):
            fitness = self.fitness_function(individual)
            self.fitness_values[i] = fitness
        

exp = Experiment(population_size=10, table_size=8, seed=42)
exp.genetic_solve()
print("Population:\n", exp.selection())