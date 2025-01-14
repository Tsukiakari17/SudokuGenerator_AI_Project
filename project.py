import numpy as np
import random
import heapq
import math

#randomize seed
random.seed(random.randint(1,2**28))


#function that find candidates/domain for a given cell
def get_candidates(grid,row, col):
  candidates = {1,2,3,4,5,6,7,8,9}

  #remove numbers that are already in row
  candidates -= set(grid[row,:])

  #remove numbers that are already in column
  candidates -= set(grid[:,col])

  #find current subgrid
  subgrid = grid[(row//3)*3:(row//3)*3+3, (col//3)*3:(col//3)*3+3]

  #remove numbers already in subgrid
  candidates -= set(subgrid.flatten())

  return candidates

#get heuristic value for valid candidates.
#heuristic favours numbers that appear in future subgrids along the row
def heuristic_appear_in_future_subgrids(grid,row,col,num):
  score = 0

  #find all next subgrids along the row
  subgrids = [grid[row,6:9]]
  if col < 3:
    subgrids.append(grid[row,0:3])
  elif col < 6:
    subgrids.append(grid[row,3:6])

  #if number appear in future subgrids along the row then
  #greatest priority is placing that number as soon as possible
  for subgrid in subgrids:
    #subgrid are ndarray, 'in' is used for efficiency
    if num in subgrid:
      score -= 1

  return score

#fill in the empty grid with a solved/valid sudoku solution
def fill_grid(grid):
  for row in range(9):
    for col in range(9):
      if grid[row,col] == 0:
        #only consider numbers that do not violate any constraints
        candidates = get_candidates(grid,row,col)
        candidates_heap = []
        for num in candidates:
          heapq.heappush(candidates_heap, (heuristic_appear_in_future_subgrids(grid,row,col,num),random.random(),num))
          #min-heap to favour numbers that cannot be placed further along the row --> some form of forward checking
          #the forward checking reduce the need for backtracking

        while candidates_heap:
          _,_,num = heapq.heappop(candidates_heap)
          grid[row,col] = num
          if fill_grid(grid):
            #returns first solution we find. last call (when solution is found) return True
            #this propagates upwards until the first call stack that called fill_grid() 
            #this initial call stack return True to the calling program then. 
            # fill_grid() returns False when you filled the grid in such a way that for the cell you are now looking other there is no available number/domain is Null
            return True     
          grid[row,col] = 0     #backtracking
        return False
  return True

#print grid in such a way that more human-readable
def pretty_print(grid):
  for i in range(9):
    #new subgrid reach on axis y (new subgrid if you look at the grid up to down)
    if i == 3 or i == 6:
      print("---------------------")

    the_row = grid[i]
    seq = ''
    for j in range(9):
      #new subgrid on axis x (new subgrid if you look at the grid from left to right)
      if j == 2 or j == 5:
        emb = ' | '
      else:
        emb = ' '
      seq += str(the_row[j]) + emb
    print(seq)

#from a non-zero grid, pick a random non-zero cell so that cell is cleared
def pick_random_cell(grid):
  nzcells = np.argwhere(grid!=0)        #return Nx2 ndarray where N is the number od matches 
  #pick an row in the ndarray where each row is a coordinate in the ndarray array
  #cast to tuple for consistency
  return tuple(nzcells[random.randint(0,len(nzcells)-1)])

def estimate_difficulty(iteration_count):
  #from found correlation
  log_iteration = math.log(iteration_count)
  if log_iteration < 3.7:
    return 0 #puzzle way too easy
  if log_iteration <3.83:
    return 1 # is easy
  if log_iteration < 4.44:
    return 2 #medium
  if log_iteration < 5.70:
    return 3 # hard
  return 4 #extreme

#use mrv heurustic to get next best cell
def find_mrv_cell(grid):
  #find cell which has minimum domain, 
  #for efficiency return first cell that has domain 1, that is, only 1 candidate possible
  min_remaining_values = 10
  mrv_cell = None

    #convert ndarray to a list of tuples for consistency
  empty_cells = list(map(tuple, np.argwhere(grid == 0)))

  for cell in empty_cells:
    row,col = cell
    candidates = get_candidates(grid,row,col)
    if len(candidates) == 1:
      return cell
    if len(candidates) < min_remaining_values:
      min_remaining_values = len(candidates)
      mrv_cell = cell

  return mrv_cell

#big solver that's a wrapper for inner solver
def solve(grid):
  iteration_count = 0
  solution_counter = 0
  stop_search = False

  def solver(grid):
    nonlocal solution_counter
    nonlocal iteration_count
    nonlocal stop_search

    if stop_search:
      return False

    iteration_count += 1

    cell = find_mrv_cell(grid)
    if cell is None:
      #if cell is None then the whole grid is filled --> solution was found
      solution_counter += 1
      if solution_counter > 1:
        stop_search = True    #set to True so that solver immediately stops execution (that is do not attempt to find more solution)
        return False #want to perpertuate the false so that backtrack to initial calling program gets done quickly
      return solution_counter ==1  #propagate the true upwards so that it attemps to find a 2nd solution

    row,col = cell

    candidates = get_candidates(grid,row,col)
    for num in candidates:
      grid[row,col] = num
      if solver(grid):
        if solution_counter > 1:
          return False      #solver will then attempt to find 2nd solution
      grid[row,col] = 0         #backtrack

    return False  #backtrack since no values is possible


  solver(grid)
  #print(solution_counter)
  #chck solution counter to return uniqueness or not
  return solution_counter ==1, iteration_count




def generate_sudoku(target_difficulty):
  current_difficulty = 0
  #create empty grid
  grid = np.zeros((9,9), dtype=int)

  fill_grid(grid)
  #pretty_print(grid)
  removed_clues = 0


  while current_difficulty != target_difficulty:

    cell = pick_random_cell(grid)
    row,col = cell

    original_value = grid[row,col]
    grid[row,col] = 0

    grid_copy = grid.copy()


    is_unique, iteration_count = solve(grid_copy)

    current_difficulty = estimate_difficulty(iteration_count)

    if is_unique and current_difficulty == target_difficulty:
      break

    if not is_unique:
      grid[row,col] = original_value
    elif current_difficulty != target_difficulty:
      removed_clues += 1
      if (removed_clues == 64):
        break
      continue

  pretty_print(grid)

def launch():
  print("Select difficulty level:")
  print("1. Easy")
  print("2. Medium")
  print("3. Hard")
  print("4. Expert")
  print()
  difficulty = input("Enter difficulty level (1-4): ")

  generate_sudoku(int(difficulty))

launch()