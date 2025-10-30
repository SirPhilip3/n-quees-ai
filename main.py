import random as rd
import numpy as np
import math

class experiment:
    def __init__(self, temperature, n):
        self.temperature = temperature
        self.n = n
        self.current_state = []
        self.schedule = [100 - i for i in range(100)]  #! Simple linear schedule test
    
    def set_initial_random_state(self):
        i = 0
        while i < self.n:
            # da valutare se metere solo 1 per colonna come requisito iniziale
            row = rd.randint(0, self.n - 1)
            # col = rd.randint(0, self.n - 1)
            if (i, row, 0) not in self.current_state:
                self.current_state.append((i,row,0))  # (row, col, fitness)
                i += 1

    def fitness_function(self, state): 
        # somma delle volte che ogni regina si attacca
        total = 0 
        for q in range(self.n):

            row_conf = 0 
            col_conf = 0
            diag_main = 0
            diag_anti = 0 

            row_q, col_q, fitness_q = state[q]
            remaining = state[:q] + state[q+1:]

            for row_j, col_j, fitness_j in remaining:
                if row_q == row_j:
                    row_conf += 1
                if col_q == col_j:
                    col_conf += 1
                if abs(row_q - row_j) == abs(col_q - col_j):

                    if (row_q - col_q) == (row_j - col_j):
                        diag_main += 1
                    else:
                        diag_anti += 1
            
            total_q = row_conf + col_conf + diag_main + diag_anti
            total += total_q

            state[q] = (row_q, col_q, total_q)

        # print("State with fitness: ", state)
        return total
    
    def run(self):
        self.set_initial_random_state()
        current_fitness = self.fitness_function()

        print("Initial state: ", self.current_state)
        print("Initial fitness: ", current_fitness)

    def neighbor(self, state):
        # Generate neighboring states by moving each queen to a different row in its column
        neighbor_state = state.copy()
        print("Generating neighbor for state: ", state)
        queen = rd.randint(0, self.n - 1)
        new_row = rd.randint(0, self.n - 1)
        neighbor_state[queen] = (new_row, queen, 0)  # Move queen to new row
        for i in range(self.n):
            row, col, fit = neighbor_state[i]
            neighbor_state[i] = (row, col, 0)  # Reset fitness
        return neighbor_state

    def simulated_annealing (self , initial ) :
        current = initial
        for T in self.schedule:
            if T ==0:
                return current
            next = self.neighbor( current ) # choice a neighbor state
            print("Current state: ", current)
            print("Next state: ", next)
            de = self.fitness_function( next ) - self.fitness_function( current )
            print("Delta E: ", de)
            if de < 0:
                current = next
            else :
                if rd.random() < math.exp( - de / T ) :
                    current = next

# for i in range(1000):
exp = experiment(temperature=100, n=4)
exp.set_initial_random_state()
result = exp.simulated_annealing(exp.current_state)
print(result)