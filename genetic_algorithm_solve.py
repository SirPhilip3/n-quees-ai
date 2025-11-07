import random as rd
import numpy as np
from numpy.random import choice

class Experiment:
    def __init__(self, population_size, table_size, seed=None, iterations=1000, crossover_rate=0.7, mutation_rate=0.01):
        self.population_size = population_size
        self.table_size = table_size
        self.iterations = iterations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate

        # permetti di settare un seed per la riproducibilità
        self.seed = seed
        if seed is not None:
            rd.seed(seed)
            np.random.seed(seed)
        
        self.population = np.full((population_size, table_size), -1, dtype=int) # initialize at -1 , it will be overwritten by initial_population
        self.population_probabilities = np.zeros(population_size, dtype=float) # probabilities for selection
        self.fitness_values = np.zeros(population_size, dtype=int)
        self.initial_population() # fill initial population


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

        # print(np.sum(self.population_probabilities))

        selected = choice(list(range(0, self.population_size)), p=self.population_probabilities, size=self.population_size)
        #print("Selected individuals indices: ", selected)
        return selected

    def crossover(self, parents):
        if rd.random() < self.crossover_rate:
            #print("Crossover between parents: ", parents)
            parent1 = self.population[parents[0]]
            parent2 = self.population[parents[1]]

            #print("Parents selected: ", parent1, parent2)

            crossover_point = rd.randint(1, self.table_size - 2)
            #print("Crossover point: ", crossover_point)        

            child1 = np.concatenate((parent1[:crossover_point], parent2[crossover_point:]))
            child2 = np.concatenate((parent2[:crossover_point], parent1[crossover_point:]))

            #print("Children generated: ", child1, child2)
            # replace parents with children in population
            self.population[parents[0]] = child1
            self.population[parents[1]] = child2


    def mutation(self):
        for index in range(self.population_size):
            if rd.random() < self.mutation_rate:
                #print("Mutation in individual: ", index)
                individual = self.population[index]
                
                mutation_point_index = rd.randint(0, self.table_size - 1)
                mutation_point1 = rd.randint(0, self.table_size - 1)

                #print(f"Mutating at index {mutation_point_index} from {individual[mutation_point_index]} to {mutation_point1}")

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

    def check_solution(self):
        for index, fitness in enumerate(self.fitness_values):
            if fitness == 0:
                print("Solution found!")
                return True , index
        return False, None

    # pass a starting population
    def genetic_solve(self):
        
        for iteration in range(self.iterations):

            # print("current population ", iteration, ":\n", self.population)

            for i, individual in enumerate(self.population):
                fitness = self.fitness_function(individual)
                self.fitness_values[i] = fitness

            # print("current fitness values ", iteration, ":\n", self.fitness_values)

            ret , sol_indx = self.check_solution()
            if ret:
                # print("Solution: ", self.population[sol_indx])
                # print("current fitness values ", iteration, ":\n", self.fitness_values)
                # print("current population ", iteration, ":\n", self.population)
                return True ,self.population[sol_indx] , self.fitness_values[sol_indx] , iteration
            
            mating_indices = self.selection()

            # print("current probabilities ", iteration, ":\n", self.population_probabilities)
            
            # possiamo fare anche con un'altra variabile mating_pool
            self.population = self.population[mating_indices]

            #? se dispari uno va a vanti e basta ???
            # per ora consideriamo che la popolazione sia sempre pari
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

            # print(f"Generation {iteration}")

        # print("No solution found within the given iterations.")
        # print("current fitness values ", iteration, ":\n", self.fitness_values)
        # print("current population ", iteration, ":\n", self.population)
        return False , self.population , self.fitness_values , self.iterations

solutions = []
for i in range(500):
    print(f"--- Run {i+1} ---")
    exp = Experiment(population_size=250, table_size=8, iterations=500, mutation_rate=0.15)
    # in generale più iterazioni passano più la soluzione raggiunge un minimo locale e quindi più improbabile che trova
    # una soluzione se sono passate tante iterazioni
    res , sol , fitness , it = exp.genetic_solve()
    solutions.append((res,sol,it))
    if res:
        print(f"Run {i+1}: Solution found in {it} iterations with fitness {fitness}: {sol}")
    else:
        print(f"Run {i+1}: No solution found in {it} iterations. , Best fitness: {min(fitness)}, average fitness: {np.mean(fitness)}, best Solution: {sol[np.argmin(fitness)]}")

iterations = []
chess_arr = []
for res, sol, it in solutions:
    if res:
        iterations.append(it)
        chess_arr.append(np.asarray(sol))

num_runs = len(solutions)
num_solutions = len(iterations)

print(f"percentage of solutions found  {num_solutions/num_runs:.2f}")

if num_solutions == 0:
    print("average iterations for solutions: N/A (no solutions)")
    print("number of unique solutions: 0")
else:
    print("average iterations for solutions " + str(np.average(iterations)))
    stacked = np.vstack(chess_arr)            # shape: (num_solutions, table_size)
    unique_rows = np.unique(stacked, axis=0)  # unique rows
    print("number of unique solutions: " + str(len(unique_rows)))
    print("unique solutions:")
    for row in unique_rows:
        print(row.tolist())