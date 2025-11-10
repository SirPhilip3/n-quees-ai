import numpy as np
import random as rd

class ConstraintExperiment:
    def __init__(self, n, seed=None):
        self.n = n
        self.matrix = np.zeros((n, n), dtype=int)
        self.tried_positions = np.full((n, n), False, dtype=bool)
        self.iteration = 0
        # ogni cella il numero di volte che è stata bloccata dalla regina
        # regina = -1
        # salva le posizioni già provate della prima regina nella prima colonna 

        # permetti di settare un seed per la riproducibilità
        self.seed = seed
        if seed is not None:
            rd.seed(seed)

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
            # print(f"Current column: {col}, Iteration: {self.iteration}")
            
            if col == -1:
                # print("No solution found")
                sol = False
                break

            possibilities = self.find_possibilities(col)

            if not possibilities:
                # print("Backtracking needed")

                col -= 1
                if col < 0:
                    # print("No solution found after backtracking")
                    sol = False
                    break
                q_row = self.find_previous_queen_row(col)
                self.do_backtracking(q_row, col)
                self.tried_positions[:, col + 1] = False # test
                
            else:
                selected_row = self.select_position(possibilities)
                self.tried_positions[selected_row, col] = True
                self.add_blocked_pos(selected_row, col)
                col += 1
            
            
            self.print_matrix()
            # print("-----")
            # self.print_tried_positions()
        solution_array = self.matrix_to_array() if sol else []
        return (solution_array ,self.iteration, sol)

# stats = []
# for i in range(4000):
#     experiment = Experiment(8)
#     stats.append(experiment.constrain_backtracking_solve())

# from collections import Counter, defaultdict

# # estrai le soluzioni (escludendo entry con lista vuota)
# solutions = [tuple(s[0]) for s in stats if s[0]]

# # conteggi e unici
# counts = Counter(solutions)
# unique_solutions = list(counts.keys())

# # iterations arrays
# all_iterations = np.array([s[1] for s in stats])
# success_iterations = np.array([s[1] for s in stats if s[2]])  # sol == True
# failed_iterations = np.array([s[1] for s in stats if not s[2]])

# # iterations per unique solution
# iters_per_solution = defaultdict(list)
# for sol, it, solflag in stats:
#     if sol:  # only consider non-empty solution arrays as keys
#         iters_per_solution[tuple(sol)].append(it)

# print("Total runs:", len(stats))
# print("Successful runs:", len(success_iterations), f"({100*len(success_iterations)/len(stats):.1f}%)")
# print("Empty/failed runs:", sum(1 for s in stats if not s[0]))

# # overall iterations stats (all runs)
# print("\nOverall iterations (all runs):")
# print("  min:", int(all_iterations.min()))
# print("  max:", int(all_iterations.max()))
# print("  mean:", float(all_iterations.mean()))
# print("  median:", float(np.median(all_iterations)))
# print("  std:", float(all_iterations.std()))

# # successful runs iterations stats
# if success_iterations.size:
#     print("\nIterations (successful runs):")
#     print("  min:", int(success_iterations.min()))
#     print("  max:", int(success_iterations.max()))
#     print("  mean:", float(success_iterations.mean()))
#     print("  median:", float(np.median(success_iterations)))
#     print("  std:", float(success_iterations.std()))
# else:
#     print("\nNo successful runs to report iterations stats.")

# # failed runs iterations stats (optional)
# if failed_iterations.size:
#     print("\nIterations (failed runs):")
#     print("  min:", int(failed_iterations.min()))
#     print("  max:", int(failed_iterations.max()))
#     print("  mean:", float(failed_iterations.mean()))
#     print("  median:", float(np.median(failed_iterations)))
#     print("  std:", float(failed_iterations.std()))

# print("\nUnique solutions count:", len(unique_solutions))
# print("Frequencies and iteration stats per unique solution:")
# for sol in unique_solutions:
#     iters = np.array(iters_per_solution[sol])
#     print("  Solution:", list(sol), "count:", counts[sol])
#     if iters.size:
#         print("    iters -> min:", int(iters.min()), "mean:", float(iters.mean()), "max:", int(iters.max()), "median:", float(np.median(iters)), "std:", float(iters.std()))
#     else:
#         print("    no iteration data")
