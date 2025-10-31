import random as rd
import numpy as np
import math

class Experiment:
    def __init__(self, temperature, n):
        self.temperature = temperature
        self.n = n
        self.current_state = [] # (row, col, fitness)
        self.schedule = [1000 - i for i in range(1000)]  #! Simple linear schedule test
    
    def set_initial_random_state(self):
        i = 0
        while i < self.n:
            # da valutare se metere solo 1 per colonna come requisito iniziale
            row = rd.randint(0, self.n - 1)
            # col = rd.randint(0, self.n - 1)
            if (row, i, 0) not in self.current_state:
                self.current_state.append((row, i, 0))  # (row, col, fitness)
                i += 1

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
                if col_q == col_j:
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
        print("Generating neighbor for state: ", neighbor_state)
        queen = rd.randint(0, self.n - 1)
        new_row = rd.randint(0, self.n - 1)
        neighbor_state[queen] = (new_row, queen, 0)  # Move queen to new row
        for i in range(self.n):
            row, col, _ = neighbor_state[i]
            neighbor_state[i] = (row, col, 0)  # Reset fitness
        return neighbor_state

    def simulated_annealing (self , initial ) :
        current = initial
        current_score , current = self.fitness_function(current)
        for T in self.schedule:
            print("Temperature: ", T)
            if T ==0:
                print("Final state: ", current)
                return current
        
            if current_score == 0: #! se 0 allora significa che nessuna regina si attacca = soluzione trovata
                print("Solution found: ", current)
                return current

            next = self.neighbor( current ) # choice a neighbor state
            next_score , next = self.fitness_function( next )

            print("Current state: ", current)
            print("Next state: ", next)
            
            de = next_score - current_score
            
            print("Delta E: ", de)
            if de < 0:
                current, current_score = next , next_score
            else :
                if rd.random() < math.exp( - de / T ) :
                    current, current_score = next , next_score
        
        print("Final state: ", current)
        return current

# for i in range(1000):
exp = Experiment(temperature=100, n=4)
exp.set_initial_random_state()
result = exp.simulated_annealing(exp.current_state)
print(result)