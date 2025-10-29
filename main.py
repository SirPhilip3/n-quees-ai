import numpy as np
import random as rd


class Experiment:
    def __init__(self, n):
        self.n = n
        self.matrix = np.zeros((n, n), dtype=int)
        self.tried_positions = np.full((n, n), False, dtype=bool)
        # ogni cella il numero di volte che è stata bloccata dalla regina
        # regina = -1
        # salva le posizioni già provate della prima regina nella prima colonna 

    def print_matrix(self):
        print(self.matrix)
    
    def print_tried_positions(self):
        print(self.tried_positions)

    def add_blocked_pos(self, row, col):
        
        self.matrix[:,col] += 1 # tutta la colonna vietata
        self.matrix[row,:] += 1 # tutta la riga vietata

        # block both diagonals that pass through (row, col)
        idx = np.arange(self.n)
        # main diagonal (i - j == row - col) -> j = idx - (row - col)
        j_main = idx - (row - col)
        valid_main = (j_main >= 0) & (j_main < self.n)
        self.matrix[idx[valid_main], j_main[valid_main]] += 1

        # anti-diagonal (i + j == row + col) -> j = (row + col) - idx
        j_anti = (row + col) - idx
        valid_anti = (j_anti >= 0) & (j_anti < self.n)
        self.matrix[idx[valid_anti], j_anti[valid_anti]] += 1

        # ensure the queen position itself is marked as occupied (not blocked)
        self.matrix[row, col] = -1

    def do_backtracking(self, row, col):

        self.matrix[:,col] -= 1 # tutta la colonna vietata
        self.matrix[row,:] -= 1 # tutta la riga vietata

        # block both diagonals that pass through (row, col)
        idx = np.arange(self.n)
        # main diagonal (i - j == row - col) -> j = idx - (row - col)
        j_main = idx - (row - col)
        valid_main = (j_main >= 0) & (j_main < self.n)
        self.matrix[idx[valid_main], j_main[valid_main]] -= 1

        # anti-diagonal (i + j == row + col) -> j = (row + col) - idx
        j_anti = (row + col) - idx
        valid_anti = (j_anti >= 0) & (j_anti < self.n)
        self.matrix[idx[valid_anti], j_anti[valid_anti]] -= 1

        # remove queen mark and mark this position as tried
        self.matrix[row, col] = 0
        self.tried_positions[row, col] = True

        print("After backtracking:")
        self.print_matrix()

    # def check_backtracking(self, col):
    #     return np.all(self.matrix[:, col] == -1)
    
    def select_position(self, possibilities):
        if not possibilities:
            return None
        return rd.choice(possibilities) 

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

    def constrain_solve(self):

        # first_col_position = rd.randint(0, self.n - 1)

        # # 1 = regina , 0 = vuoto , -1 = vietato
        # self.matrix[first_col_position][0] = 1
        # self.add_blocked_pos(first_col_position, 0)
        
        # self.print_matrix()
        col  = 0
        while col < self.n:

            if col == -1:
                print("No solution found")
                break

            possibilities = self.find_possibilities(col)

            if not possibilities:
                print("Backtracking needed")
                row = self.find_previous_queen_row(col - 1)
                self.do_backtracking(row, col - 1)

                #!
                possibilities = self.find_possibilities(col) #!!!!  

                if not possibilities:
                    print("Backtracking again")
                    self.tried_positions[:, col] = False
                    col -= 1 #? se va a -1
                    break
                #!
            
            
            else:
                selected_row = self.select_position(possibilities)
                self.tried_positions[selected_row, col] = True
                self.add_blocked_pos(selected_row, col)
                self.print_matrix()
                col += 1
        
            
            print("-----")



            # più semplicemente possiamo prendere la prima posizione valida
            # per il backtracking
        
        self.print_tried_positions()
        print("Solved")

# for i in range(100):
experiment = Experiment(4)
experiment.constrain_solve()
