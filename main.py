import sys
import numpy as np
from hashlib import md5
from copy import deepcopy

class Node():
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action

# Depth search
class StackFrontier():
    # Initialize the class with empty frontier
    def __init__(self):
        self.frontier = []
    # Adds a node to the end of the frontier list
    def add(self, node):
        self.frontier.append(node)
    # Checks if a target state has been met
    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)
    # Returns whether the frontier is empty
    def empty(self):
        return len(self.frontier) == 0
    # Removes the last node from the frontier. Also returns that node to be processed
    def remove(self):
        if self.empty():
            raise Exception("Empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node

# Breadth search (Extends the StackFrontier)
class QueueFrontier(StackFrontier):
    # Override the remove function of the StackFrontier with first in first out method
    def remove(self):
        if self.empty():
            raise Exception("Empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node


# Game to be solved
class Sudoku():
    def __init__(self, filename):
        # Initialize useful variables
        self.entryPoints = []
        # Read sudoku file
        with open(filename) as f:
            contents = f.read()

        # No validation

        # Determine height and width of sudoku board
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        # Create a grid (Row, Column)
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    row.append(contents[i][j])
                    if contents[i][j] == " ":
                        self.entryPoints.append((i,j))
                except IndexError:
                    row.append(0)
            self.board.append(row)

        # No solutions yet
        self.solutions = None

    def getMD5(self, plaintext):
        m = md5()
        m.update(plaintext.encode('utf-8'))
        hash = str(m.hexdigest())
        return hash
    # Print out the board
    def print(self, board):
        for i in range(self.height):
            print(board[i])

    # neighbors
    def neighbors(self, grid):
        # Convert board to numpy array
        board = np.array(grid)

        # candidates list
        candidates = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        # Find next space
        row = None
        col = None
        for r in range(self.height):
            done = False
            for c in range(self.width):
                if grid[r][c] == " ":
                    row = r
                    col = c
                    done = True
                    break
            if done:
                break
        # Loop through candidates
        if row == None or col == None:
            return []
        result = []
        for action in candidates:
            # Rules
            possible = True
            # Check rows
            if action in board[row, :]:
                possible = False
            # Check column
            if action in board[:, col]:
                possible = False
            # If not in quadrant
            startRow = row - (row%3)
            startCol = col - (col%3)
            for i in range(3):
                for j in range(3):
                    if board[i + startRow][j + startCol] == action:
                        possible = False
            # Append if possible
            if possible:
                result.append((action, (row, col)))
        # Return result
        return result

    # Check validation
    def validate(self, grid):
        board = np.array(grid)
        errors = 0
        possible = True
        for row in range(self.height):
            for col in range(self.width):
                action = grid[row][col]
                if action != " ":
                    board[row][col] = " "
                    # Check rows
                    if action in board[row, :]:
                        possible = False
                        errors += 1
                    # Check column
                    if action in board[:, col]:
                        possible = False
                        errors += 1
                    # If not in quadrant
                    startRow = row - (row%3)
                    startCol = col - (col%3)
                    for i in range(3):
                        for j in range(3):
                            if board[i + startRow][j + startCol] == action:
                                possible = False
                                errors += 1
                    board[row][col] = action
                else:
                    pass
        return possible

    # Solving the puzzle
    def solve(self):
        # Keep track of number of explored states
        self.num_explored = 0

        # Initialize frontier
        frontierType = int(input("1) StackFrontier 2) QueueFrontier | Enter type: "))
        if frontierType == 1:
            frontier = StackFrontier()
        elif frontierType == 2:
            frontier = QueueFrontier()
        else:
            exit()

        frontier.add(Node(state = self.board, parent = None, action = None))

        # Keep track of explored Nodes
        self.explored = []

        # While loop until solution is found
        while True:
            # Progress report
            if (self.num_explored%100) == 0:
                print("Number explored: " + str(self.num_explored))
            # Exception if no solutions
            if frontier.empty():
                print("Number explored: " + str(self.num_explored))
                raise Exception("No solutions")

            # Get node from frontier
            node = frontier.remove()
            grid = node.state

            # Check goal
            complete = True
            for row in range(self.height):
                for col in range(self.width):
                    if grid[row][col] == " ":
                        complete = False
                        break
                if complete == False:
                    break
            if complete:
                if self.validate(grid):
                    print("Solved: ")
                    self.print(grid)
                    return
            else:
                # Add to explored
                self.num_explored += 1

            # New node
            new_state = grid
            for action in self.neighbors(grid):
                row, col = action[1][0], action[1][1]
                num = action[0]
                new_state[row][col] = num
                if self.validate(new_state):
                    new_node = Node(state = deepcopy(new_state), parent = node.state, action = None)
                    frontier.add(new_node)
                    self.explored.append(self.getMD5(str(new_state)))
                else:
                    print("Invalid")
        else:
            print("Already explored")
            print(self.getMD5(str(grid)))
            print(self.explored)

# Main
#Check if arguments are met
if len(sys.argv) != 2:
    sys.exit("Usage: python3 main.py sudoku.txt")

# Run game
filename = sys.argv[1]
game = Sudoku(filename)
game.solve()
print("Iterations used:" + str(game.num_explored))
