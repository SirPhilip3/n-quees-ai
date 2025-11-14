import numpy as np
import random as rd

class ConstraintExperiment:
    def __init__(self, n, seed=None):
        self.n = n
        self.matrix = np.zeros((n, n), dtype=int) # ogni cella il numero di volte che è stata bloccata dalla regina , regina = -1
        self.tried_positions = np.full((n, n), False, dtype=bool) # salva le posizioni già provate della prima regina nella prima colonna 
        
        #stats
        self.iteration = 0
        self.backtracking_count = 0

        # permetti di settare un seed per la riproducibilità
        self.seed = seed
        if seed is not None:
            rd.seed(seed)

    def add_blocked_pos(self, row, col):
        
        self.matrix[:,col] += 1 # tutta la colonna vietata
        self.matrix[row,:] += 1 # tutta la riga vietata

        idx = np.arange(self.n)
        j_main = idx - (row - col)
        valid_main = (j_main >= 0) & (j_main < self.n)
        self.matrix[idx[valid_main], j_main[valid_main]] += 1

        j_anti = (row + col) - idx
        valid_anti = (j_anti >= 0) & (j_anti < self.n)
        self.matrix[idx[valid_anti], j_anti[valid_anti]] += 1

        # ensure the queen position itself is marked as occupied (not blocked)
        self.matrix[row, col] = -1

    def do_backtracking(self, row, col):

        self.matrix[:,col] -= 1 
        self.matrix[row,:] -= 1 

        idx = np.arange(self.n)
        j_main = idx - (row - col)
        valid_main = (j_main >= 0) & (j_main < self.n)
        self.matrix[idx[valid_main], j_main[valid_main]] -= 1

        j_anti = (row + col) - idx
        valid_anti = (j_anti >= 0) & (j_anti < self.n)
        self.matrix[idx[valid_anti], j_anti[valid_anti]] -= 1

        self.matrix[row, col] = 0
    
    def select_position(self, possibilities):
        if not possibilities:
            return None
        return rd.choice(possibilities)
     
    # seleziona una posizione a caso tra quelle possibili che non sono state già provate
    def find_possibilities(self, col):
        current_col = self.matrix[:, col]
        current_col_tried = self.tried_positions[:, col]

        possibilities = []
        for j in range(self.n):
            if current_col[j] == 0 and not current_col_tried[j]:
                possibilities.append(j)
        return possibilities
    
    def find_previous_queen_row(self, col):
        for i in range(self.n):
            if self.matrix[i, col] == -1:
                return i

    def matrix_to_array(self):
        result = []
        for col in range(self.n):
            for row in range(self.n):
                if self.matrix[row, col] == -1:
                    result.append(row)
                    break
        return result


    def constrain_backtracking_solve(self): 
        col = 0
        sol = True
        while col < self.n:
            self.iteration += 1
            
            if col == -1:
                sol = False
                break

            possibilities = self.find_possibilities(col)

            if not possibilities:
                self.backtracking_count += 1

                col -= 1
                if col < 0:
                    sol = False
                    break
                q_row = self.find_previous_queen_row(col)
                self.do_backtracking(q_row, col)
                self.tried_positions[:, col + 1] = False 
                
            else:
                selected_row = self.select_position(possibilities)
                self.tried_positions[selected_row, col] = True
                self.add_blocked_pos(selected_row, col)
                col += 1
            
        solution_array = self.matrix_to_array() if sol else []
        return (solution_array ,self.iteration, self.backtracking_count, sol)
