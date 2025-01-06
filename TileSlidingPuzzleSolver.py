# All starter code (as indicated below) has been provided by the University of Toronto for the course, CSC384H5: Introduction to Artificial Intelligence
# DFS and A* Search algorithms and other helper functions have been implemented to solve a given tile sliding puzzle

#References
#“Hungarian Algorithm.” Wikipedia, 16 Sept. 2024. Wikipedia, https://en.wikipedia.org/w/index.php?title=Hungarian_algorithm&oldid=1246018075.
#“Scipy.optimize.linear_sum_assignment.” Docs.scipy.org, https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html.

# Import statements
import numpy as np
from scipy.optimize import linear_sum_assignment
import heapq
# Below statements from starter code
import argparse
import sys

#====================================================================================

char_single = '2' # From starter code

class Piece: # Class implementation from starter code with minor change
    """
    This represents a piece on the Hua Rong Dao puzzle.
    """

    def __init__(self, is_2_by_2, is_single, coord_x, coord_y, orientation):
        """
        :param is_2_by_2: True if the piece is a 2x2 piece and False otherwise.
        :type is_2_by_2: bool
        :param is_single: True if this piece is a 1x1 piece and False otherwise.
        :type is_single: bool
        :param coord_x: The x coordinate of the top left corner of the piece.
        :type coord_x: int
        :param coord_y: The y coordinate of the top left corner of the piece.
        :type coord_y: int
        :param orientation: The orientation of the piece (one of 'h' or 'v') 
            if the piece is a 1x2 piece. Otherwise, this is None
        :type orientation: str
        """

        self.is_2_by_2 = is_2_by_2
        self.is_single = is_single
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.orientation = orientation

    def set_coords(self, coord_x, coord_y):
        """
        Move the piece to the new coordinates. 

        :param coord: The new coordinates after moving.
        :type coord: int
        """

        self.coord_x = coord_x
        self.coord_y = coord_y

    def __repr__(self):
        return '{} {} {} {} {}'.format(self.is_2_by_2, self.is_single, \
            self.coord_x, self.coord_y, self.orientation)
    
    def copy(self): # Modification of class to create a function that duplicates the current piece instance
        return Piece(self.is_2_by_2, self.is_single, self.coord_x, self.coord_y, self.orientation)

class Board: # Class implementation from starter code
    """
    Board class for setting up the playing board.
    """

    def __init__(self, height, pieces):
        """
        :param pieces: The list of Pieces
        :type pieces: List[Piece]
        """

        self.width = 4
        self.height = height
        self.pieces = pieces

        # self.grid is a 2-d (size * size) array automatically generated
        # using the information on the pieces when a board is being created.
        # A grid contains the symbol for representing the pieces on the board.
        self.grid = []
        self.__construct_grid()

        self.blanks = []

    # customized eq for object comparison.
    def __eq__(self, other):
        if isinstance(other, Board):
            return self.grid == other.grid
        return False


    def __construct_grid(self):
        """
        Called in __init__ to set up a 2-d grid based on the piece location information.

        """

        for i in range(self.height):
            line = []
            for j in range(self.width):
                line.append('.')
            self.grid.append(line)

        for piece in self.pieces:
            if piece.is_2_by_2:
                self.grid[piece.coord_y][piece.coord_x] = '1'
                self.grid[piece.coord_y][piece.coord_x + 1] = '1'
                self.grid[piece.coord_y + 1][piece.coord_x] = '1'
                self.grid[piece.coord_y + 1][piece.coord_x + 1] = '1'
            elif piece.is_single:
                self.grid[piece.coord_y][piece.coord_x] = char_single
            else:
                if piece.orientation == 'h':
                    self.grid[piece.coord_y][piece.coord_x] = '<'
                    self.grid[piece.coord_y][piece.coord_x + 1] = '>'
                elif piece.orientation == 'v':
                    self.grid[piece.coord_y][piece.coord_x] = '^'
                    self.grid[piece.coord_y + 1][piece.coord_x] = 'v'
      
    def display(self):
        """
        Print out the current board.

        """
        for i, line in enumerate(self.grid):
            for ch in line:
                print(ch, end='')
            print()
        

class State: # Class implementation from starter code with minor change
    """
    State class wrapping a Board with some extra current state information.
    Note that State and Board are different. Board has the locations of the pieces. 
    State has a Board and some extra information that is relevant to the search: 
    heuristic function, f value, current depth and parent.
    """

    def __init__(self, board, hfn, f, depth, parent=None):
        """
        :param board: The board of the state.
        :type board: Board
        :param hfn: The heuristic function.
        :type hfn: Optional[Heuristic]
        :param f: The f value of current state.
        :type f: int
        :param depth: The depth of current state in the search tree.
        :type depth: int
        :param parent: The parent of current state.
        :type parent: Optional[State]
        """
        self.board = board
        self.hfn = hfn
        self.f = f
        self.depth = depth
        self.parent = parent
    
    def __lt__(self, other): # Modification of class to create a function that defines the less than operator for state instances
        if self.f == other.f:# based on the f value (sum of the cost to reach the goal state and the estimated cost to the goal state)
            return self.depth < other.depth # and depth of both states (used for A* search algorithm)
        return self.f < other.f


def goal_test(state, goal_state):
    """
    Checks if the given state is the goal state.

    :param state: A given state.
    :type state: State
    :param goal_state: The goal state.
    :type goal_state: State
    """
    # Compare the board of the current state with the goal state's board
    if state.board == goal_state.board:
        return True
    return False

def piece_tracker(state):
    """
    Returns the number of each type of piece in the given state.

    :param state: A given state.
    :type state: State
    """
    tracker = {}
    tracker["two_by_two"] = []  # Tracks 2x2 pieces
    tracker["single"] = []  # Tracks single-cell pieces
    tracker["v"] = []  # Tracks vertically-oriented pieces
    tracker["h"] = []  # Tracks horizontally-oriented pieces

    # Categorize each piece based on its type and orientation
    for piece in state.board.pieces:
        if piece.is_2_by_2:
            tracker["two_by_two"].append(piece)
        elif piece.is_single:
            tracker["single"].append(piece)
        elif piece.orientation == 'v':
            tracker["v"].append(piece)
        else:
            tracker["h"].append(piece)
    return tracker

def manhattan_matrix(curr_piece_type, goal_piece_type):
    """
    Constructs an assignment matrix where each row represents each piece of a specific type in the current state and
    each column represents each piece of this type in the goal state.
    Each entry of the matrix is initialized as the manhattan disance from the corresponding piece in the
    current state to that in the goal state.

    :param curr_piece_type: A list of pieces of a specific type within a given state.
    :type curr_piece_type: List[Piece]
    :param goal_piece_type: A list of pieces of a specific type within the goal state.
    :type goal_piece_type: List[Piece]
    """
    piece_type_dist_matrix = [[] for _ in range(len(curr_piece_type))]
    
    # Compute the Manhattan distance for each piece pair
    for i in range(len(curr_piece_type)):
        for j in range(len(goal_piece_type)):
            dist = abs(curr_piece_type[i].coord_x - goal_piece_type[j].coord_x) + abs(curr_piece_type[i].coord_y - goal_piece_type[j].coord_y)
            piece_type_dist_matrix[i].append(dist)
    return piece_type_dist_matrix

def total_piece_type_dist(matrix):
    """
    Solves a provided assignment matrix that represents the manhattan distance between pieces of the same type with a
    given state and the goal state.
    This is done using the Hungarian algorithm implemented by the linear_sum_assignment function.

    :param matrix: An assignment matrix representing the manhattan distance between pieces of the same type with a
    given state and the goal state.
    :type matrix: List[List[float]]
    """
    matrix = np.array(matrix) # Convert to NumPy array for processing
    optimal_row, optimal_col = linear_sum_assignment(matrix) # Find optimal pairing (“Hungarian Algorithm”; “Scipy.Optimize.Linear_sum_assignment”)
    total = 0
    # Sum the distances for optimal pairings
    for row, col in zip(optimal_row, optimal_col):
        total += matrix[row][col]
    return total

def heuristic(state, goal_state):
    """
    A heuristic function that calculates a heuristic value for a given state.
    The heuristic is calculated by pairing each piece in the current state with
    the corresponding piece of the same type in the goal state.
    The goal is to minimize the total distance between all paired pieces using
    the Hungarian algorithm, and this total distance
    represents the heuristic value of the given state.
    
    :param state: A given state.
    :type state: State
    :param goal_state: The goal state.
    :type goal_state: State
    """
    heuristic_total = 0
    curr_pieces = piece_tracker(state) # Track pieces in the current state
    goal_pieces = piece_tracker(goal_state) # Track pieces in the goal state
    
    # Calculate total distance between all paired pieces
    for piece_type in curr_pieces:
        if curr_pieces[piece_type]:
            matrix = manhattan_matrix(curr_pieces[piece_type], goal_pieces[piece_type])
            if piece_type == 'two_by_two':
                heuristic_total += total_piece_type_dist(matrix)
            if piece_type == 'single':
                heuristic_total += total_piece_type_dist(matrix)
            if piece_type == 'h':
                heuristic_total += total_piece_type_dist(matrix)
            else:
                heuristic_total += total_piece_type_dist(matrix)
    return heuristic_total
    
def check_2_by_2_move(piece, board):
    """
    Generates successor boards by sliding a 2x2 piece in all possible directions for the given board.

    :param piece: A 2x2 piece on the board.
    :type piece: Piece
    :param board: The current board.
    :type board: Board
    :return: List of new boards after performing valid moves.
    :rtype: list[Board]
    """
    successor_boards = []
    # Check move to the right
    if 0 <= piece.coord_x + 2 <= 3:
        new_board = Board(board.height, board.pieces.copy())
        new_board.grid = [row[:] for row in board.grid]
        if board.grid[piece.coord_y][piece.coord_x + 2] == '.' and board.grid[piece.coord_y + 1][piece.coord_x + 2] == '.':
            new_board.grid[piece.coord_y][piece.coord_x + 2] = '1'
            new_board.grid[piece.coord_y + 1][piece.coord_x + 2] = '1'
            new_board.grid[piece.coord_y][piece.coord_x] = '.'
            new_board.grid[piece.coord_y + 1][piece.coord_x] = '.'
            new_piece = piece.copy()
            new_piece.set_coords(piece.coord_x + 1, piece.coord_y)
            index = new_board.pieces.index(piece)
            new_board.pieces[index] = new_piece
            successor_boards.append(new_board)
    # Check move to the left
    if 0 <= piece.coord_x - 1 <= 3:
        new_board = Board(board.height, board.pieces.copy())
        new_board.grid = [row[:] for row in board.grid]
        if board.grid[piece.coord_y][piece.coord_x - 1] == '.' and board.grid[piece.coord_y + 1][piece.coord_x - 1] == '.':
            new_board.grid[piece.coord_y][piece.coord_x - 1] = '1'
            new_board.grid[piece.coord_y + 1][piece.coord_x - 1] = '1'
            new_board.grid[piece.coord_y][piece.coord_x + 1] = '.'
            new_board.grid[piece.coord_y + 1][piece.coord_x + 1] = '.'
            new_piece = piece.copy()
            new_piece.set_coords(piece.coord_x - 1, piece.coord_y)
            index = new_board.pieces.index(piece)
            new_board.pieces[index] = new_piece
            successor_boards.append(new_board)
    # Check move upward
    if 0 <= piece.coord_y - 1 <= board.height - 1:
        new_board = Board(board.height, board.pieces.copy())
        new_board.grid = [row[:] for row in board.grid]
        if board.grid[piece.coord_y - 1][piece.coord_x] == '.' and board.grid[piece.coord_y - 1][piece.coord_x + 1] == '.':
            new_board.grid[piece.coord_y - 1][piece.coord_x] = '1'
            new_board.grid[piece.coord_y - 1][piece.coord_x + 1] = '1'
            new_board.grid[piece.coord_y + 1][piece.coord_x] = '.'
            new_board.grid[piece.coord_y + 1][piece.coord_x + 1] = '.'
            new_piece = piece.copy()
            new_piece.set_coords(piece.coord_x, piece.coord_y - 1)
            index = new_board.pieces.index(piece)
            new_board.pieces[index] = new_piece
            successor_boards.append(new_board)
    # Check move downward
    if 0 <= piece.coord_y + 2 <= board.height - 1:
        new_board = Board(board.height, board.pieces.copy())
        new_board.grid = [row[:] for row in board.grid]
        if board.grid[piece.coord_y + 2][piece.coord_x] == '.' and board.grid[piece.coord_y + 2][piece.coord_x + 1] == '.':
            new_board.grid[piece.coord_y + 2][piece.coord_x] = '1'
            new_board.grid[piece.coord_y + 2][piece.coord_x + 1] = '1'
            new_board.grid[piece.coord_y][piece.coord_x] = '.'
            new_board.grid[piece.coord_y][piece.coord_x + 1] = '.'
            new_piece = piece.copy()
            new_piece.set_coords(piece.coord_x, piece.coord_y + 1)
            index = new_board.pieces.index(piece)
            new_board.pieces[index] = new_piece
            successor_boards.append(new_board)
    return successor_boards

def check_horiz_move(piece, board):
    """
    Generates successor boards by sliding a 1x2 horizontal piece in all possible directions for the given board.

    :param piece: A 1x2 horizontal piece on the board.
    :type piece: Piece
    :param board: The current board.
    :type board: Board
    :return: List of new boards after performing valid moves.
    :rtype: list[Board]
    """
    successor_boards = []
    # Check move to the right
    if 0 <= piece.coord_x + 2 <= 3:
        new_board = Board(board.height, board.pieces.copy())
        new_board.grid = [row[:] for row in board.grid]
        if board.grid[piece.coord_y][piece.coord_x + 2] == '.':
            new_board.grid[piece.coord_y][piece.coord_x + 2] = '>'
            new_board.grid[piece.coord_y][piece.coord_x + 1] = '<'
            new_board.grid[piece.coord_y][piece.coord_x] = '.'
            new_piece = piece.copy()
            new_piece.set_coords(piece.coord_x + 1, piece.coord_y)
            index = new_board.pieces.index(piece)
            new_board.pieces[index] = new_piece
            successor_boards.append(new_board)
    # Check move to the left
    if 0 <= piece.coord_x - 1 <= 3:
        new_board = Board(board.height, board.pieces.copy())
        new_board.grid = [row[:] for row in board.grid]
        if board.grid[piece.coord_y][piece.coord_x - 1] == '.':
            new_board.grid[piece.coord_y][piece.coord_x - 1] = '<'
            new_board.grid[piece.coord_y][piece.coord_x] = '>'
            new_board.grid[piece.coord_y][piece.coord_x + 1] = '.'
            new_piece = piece.copy()
            new_piece.set_coords(piece.coord_x - 1, piece.coord_y)
            index = new_board.pieces.index(piece)
            new_board.pieces[index] = new_piece
            successor_boards.append(new_board)
    # Check move upward
    if 0 <= piece.coord_y - 1 <= board.height - 1:
        new_board = Board(board.height, board.pieces.copy())
        new_board.grid = [row[:] for row in board.grid]
        if board.grid[piece.coord_y - 1][piece.coord_x] == '.' and board.grid[piece.coord_y - 1][piece.coord_x + 1] == '.':
            new_board.grid[piece.coord_y - 1][piece.coord_x] = '<'
            new_board.grid[piece.coord_y - 1][piece.coord_x + 1] = '>'
            new_board.grid[piece.coord_y][piece.coord_x] = '.'
            new_board.grid[piece.coord_y][piece.coord_x + 1] = '.'
            new_piece = piece.copy()
            new_piece.set_coords(piece.coord_x, piece.coord_y - 1)
            index = new_board.pieces.index(piece)
            new_board.pieces[index] = new_piece
            successor_boards.append(new_board)
    # Check move downward
    if 0 <= piece.coord_y + 1 <= board.height - 1:
        new_board = Board(board.height, board.pieces.copy())
        new_board.grid = [row[:] for row in board.grid]
        if board.grid[piece.coord_y + 1][piece.coord_x] == '.' and board.grid[piece.coord_y + 1][piece.coord_x + 1] == '.':
            new_board.grid[piece.coord_y + 1][piece.coord_x] = '<'
            new_board.grid[piece.coord_y + 1][piece.coord_x + 1] = '>'
            new_board.grid[piece.coord_y][piece.coord_x] = '.'
            new_board.grid[piece.coord_y][piece.coord_x + 1] = '.'
            new_piece = piece.copy()
            new_piece.set_coords(piece.coord_x, piece.coord_y + 1)
            index = new_board.pieces.index(piece)
            new_board.pieces[index] = new_piece
            successor_boards.append(new_board)
    return successor_boards

def check_vert_move(piece, board):
    """
    Generates successor boards by sliding a 1x2 vertical piece in all possible directions for the given board.

    :param piece: A 1x2 vertical piece on the board.
    :type piece: Piece
    :param board: The current board.
    :type board: Board
    :return: List of new boards after performing valid moves.
    :rtype: list[Board]
    """
    successor_boards = []
    # Check move downward
    if 0 <= piece.coord_y + 2 <= board.height - 1:
        new_board = Board(board.height, board.pieces.copy())
        new_board.grid = [row[:] for row in board.grid]
        if board.grid[piece.coord_y + 2][piece.coord_x] == '.':
            new_board.grid[piece.coord_y + 2][piece.coord_x] = 'v'
            new_board.grid[piece.coord_y + 1][piece.coord_x] = '^'
            new_board.grid[piece.coord_y][piece.coord_x] = '.'
            new_piece = piece.copy()
            new_piece.set_coords(piece.coord_x, piece.coord_y + 1)
            index = new_board.pieces.index(piece)
            new_board.pieces[index] = new_piece
            successor_boards.append(new_board)
    # Check move upward
    if 0 <= piece.coord_y - 1 <= board.height - 1:
        new_board = Board(board.height, board.pieces.copy())
        new_board.grid = [row[:] for row in board.grid]
        if board.grid[piece.coord_y - 1][piece.coord_x] == '.':
            new_board.grid[piece.coord_y - 1][piece.coord_x] = '^'
            new_board.grid[piece.coord_y][piece.coord_x] = 'v'
            new_board.grid[piece.coord_y + 1][piece.coord_x] = '.'
            new_piece = piece.copy()
            new_piece.set_coords(piece.coord_x, piece.coord_y - 1)
            index = new_board.pieces.index(piece)
            new_board.pieces[index] = new_piece
            successor_boards.append(new_board)
    # Check move to the right
    if 0 <= piece.coord_x + 1 <= 3:
        new_board = Board(board.height, board.pieces.copy())
        new_board.grid = [row[:] for row in board.grid]
        if board.grid[piece.coord_y][piece.coord_x + 1] == '.' and board.grid[piece.coord_y + 1][piece.coord_x + 1] == '.':
            new_board.grid[piece.coord_y][piece.coord_x + 1] = '^'
            new_board.grid[piece.coord_y + 1][piece.coord_x + 1] = 'v'
            new_board.grid[piece.coord_y][piece.coord_x] = '.'
            new_board.grid[piece.coord_y + 1][piece.coord_x] = '.'
            new_piece = piece.copy()
            new_piece.set_coords(piece.coord_x + 1, piece.coord_y)
            index = new_board.pieces.index(piece)
            new_board.pieces[index] = new_piece
            successor_boards.append(new_board)
    # Check move to the left
    if 0 <= piece.coord_x - 1 <= 3:
        new_board = Board(board.height, board.pieces.copy())
        new_board.grid = [row[:] for row in board.grid]
        if board.grid[piece.coord_y][piece.coord_x - 1] == '.' and board.grid[piece.coord_y + 1][piece.coord_x - 1] == '.':
            new_board.grid[piece.coord_y][piece.coord_x - 1] = '^'
            new_board.grid[piece.coord_y + 1][piece.coord_x - 1] = 'v'
            new_board.grid[piece.coord_y][piece.coord_x] = '.'
            new_board.grid[piece.coord_y + 1][piece.coord_x] = '.'
            new_piece = piece.copy()
            new_piece.set_coords(piece.coord_x - 1, piece.coord_y)
            index = new_board.pieces.index(piece)
            new_board.pieces[index] = new_piece
            successor_boards.append(new_board)
    return successor_boards

def check_single_move(piece, board):
    """
    Generates successor boards by sliding a 1x1 piece in all possible directions for the given board.

    :param piece: A 1x1 piece on the board.
    :type piece: Piece
    :param board: The current board.
    :type board: Board
    :return: List of new boards after performing valid moves.
    :rtype: list[Board]
    """
    successor_boards = []
    # Check move downward
    if 0 <= piece.coord_y + 1 <= board.height - 1:
        new_board = Board(board.height, board.pieces.copy())
        new_board.grid = [row[:] for row in board.grid]
        if board.grid[piece.coord_y + 1][piece.coord_x] == '.':
            new_board.grid[piece.coord_y + 1][piece.coord_x] = '2'
            new_board.grid[piece.coord_y][piece.coord_x] = '.'
            new_piece = piece.copy()
            new_piece.set_coords(piece.coord_x, piece.coord_y + 1)
            index = new_board.pieces.index(piece)
            new_board.pieces[index] = new_piece
            successor_boards.append(new_board)
    # Check move upward
    if 0 <= piece.coord_y - 1 <= board.height - 1:
        new_board = Board(board.height, board.pieces.copy())
        new_board.grid = [row[:] for row in board.grid]
        if board.grid[piece.coord_y - 1][piece.coord_x] == '.':
            new_board.grid[piece.coord_y - 1][piece.coord_x] = '2'
            new_board.grid[piece.coord_y][piece.coord_x] = '.'
            new_piece = piece.copy()
            new_piece.set_coords(piece.coord_x, piece.coord_y - 1)
            index = new_board.pieces.index(piece)
            new_board.pieces[index] = new_piece
            successor_boards.append(new_board)
    # Check move to the right
    if 0 <= piece.coord_x + 1 <= 3:
        new_board = Board(board.height, board.pieces.copy())
        new_board.grid = [row[:] for row in board.grid]
        if board.grid[piece.coord_y][piece.coord_x + 1] == '.':
            new_board.grid[piece.coord_y][piece.coord_x + 1] = '2'
            new_board.grid[piece.coord_y][piece.coord_x] = '.'
            new_piece = piece.copy()
            new_piece.set_coords(piece.coord_x + 1, piece.coord_y)
            index = new_board.pieces.index(piece)
            new_board.pieces[index] = new_piece
            successor_boards.append(new_board)
    # Check move to the left
    if 0 <= piece.coord_x - 1 <= 3:
        new_board = Board(board.height, board.pieces.copy())
        new_board.grid = [row[:] for row in board.grid]
        if board.grid[piece.coord_y][piece.coord_x - 1] == '.':
            new_board.grid[piece.coord_y][piece.coord_x - 1] = '2'
            new_board.grid[piece.coord_y][piece.coord_x] = '.'
            new_piece = piece.copy()
            new_piece.set_coords(piece.coord_x - 1, piece.coord_y)
            index = new_board.pieces.index(piece)
            new_board.pieces[index] = new_piece
            successor_boards.append(new_board)
    return successor_boards



def slide_piece(board, piece):
    """
    Returns the successor boards of the given state by
    sliding the given piece on the board.

    :param board: A given board.
    :type board: Board
    :param piece: A piece on the given board.
    :type piece: Piece
    :return: List of new boards after performing valid moves.
    :rtype: list[Board]
    """
    boards = []
    # Check if the piece is a 2x2 piece and generate possible moves for it
    if piece.is_2_by_2 == True:
        boards += check_2_by_2_move(piece, board)
    # Check if the piece is a 1x1 piece and generate possible moves for it
    elif piece.is_single == True:
        boards += check_single_move(piece, board)
    # Check if the piece is a 1x2 horizontal piece, generate horizontal moves
    elif piece.orientation == 'h':
        boards += check_horiz_move(piece, board)
    # Otherwise, generate vertical moves for 1x2 vertical pieces
    else:
        boards += check_vert_move(piece, board)
    # Return all generated successor boards
    return boards


def generate_successors(state, goal_state):
    """
    Returns the successor states of a given state.

    :param state: A given state.
    :type state: State
    :param goal_state: The goal state.
    :type goal_state: State
    :return: A list of successor states generated from the given state.
    :rtype: list[State]
    """
    successors = []
    # Iterate over each piece on the board
    for piece in state.board.pieces:
        # Generate possible successor boards for the current piece
        successor_boards = slide_piece(state.board, piece)
        # For each generated board, create a new state and compute its heuristic value
        for board in successor_boards:
            if board != None:
                new_state = State(board, heuristic, 0, state.depth + 1, state)
                new_state.f = heuristic(new_state, goal_state) + new_state.depth
                successors.append(new_state)
    # Return the list of successor states
    return successors

def get_solution(goal_state):
    """
    Constructs the solution path from the goal state to the initial state.

    :param goal_state: The final goal state from which to trace back the solution path.
    :type goal_state: State
    :return: A list of states representing the solution path, starting from the initial state and ending at the goal state.
    :rtype: list[State]
    """
    parent = goal_state.parent
    sequence = [goal_state]
    # Trace back through the parent chain of each state until the initial state is reached
    while parent != None:
        sequence.insert(0, parent)
        parent = parent.parent
    # Return the complete solution path
    return sequence

def dfs_search(state, goal_state):
    """
    Performs a depth-first search to find a solution from the initial state to the goal state.

    :param state: The initial state of the search.
    :type state: State
    :param goal_state: The goal state to reach.
    :type goal_state: State
    :return: A list of states representing the solution path if a solution is found; otherwise, None.
    :rtype: list[State] or None
    """
    # Check if the initial state is already the goal state.
    if state.board == goal_state.board:
        return [state, goal_state]
    # Initialize the frontier and explored set.
    frontier = [state]
    explored = set()
    while frontier:
        # Pop the last state from the frontier.
        curr_state = frontier.pop()
        curr_board = curr_state.board
        curr_tuple = tuple(map(tuple, curr_board.grid))
        # Process the state if it hasn't been explored.
        if curr_tuple not in explored:
            explored.add(curr_tuple)
            # Return solution if the goal state is reached.
            if curr_state.board == goal_state.board:
                return get_solution(curr_state)
            # Add successors of the current state to the frontier.
            successors = generate_successors(curr_state, goal_state)
            frontier += successors
    # Return None if no solution is found.
    return

def a_star_search(state, goal_state):
    """
    Performs an A* search to find a solution from the initial state to the goal state.

    :param state: The initial state of the search.
    :type state: State
    :param goal_state: The goal state to reach.
    :type goal_state: State
    :return: A list of states representing the solution path if a solution is found; otherwise, None.
    :rtype: list[State] or None
    """
    # Check if the initial state is already the goal state.
    if state.board == goal_state.board:
        return [state, goal_state]
    # Initialize the priority queue and explored set.
    frontier = [state]
    heapq.heapify(frontier)
    explored = set()
    while frontier:
        # Pop the state with the lowest cost from the frontier.
        curr_state = heapq.heappop(frontier)
        curr_board = curr_state.board
        curr_tuple = tuple(map(tuple, curr_board.grid))
        # Process the state if it hasn't been explored.
        if curr_tuple not in explored:
            explored.add(curr_tuple)
            # Return solution if the goal state is reached.
            if curr_state.board == goal_state.board:
                return get_solution(curr_state)
            # Add successors to the frontier and reorder it based on the f value and depth of both states
            successors = generate_successors(curr_state, goal_state)
            frontier += successors
            heapq.heapify(frontier)
    # Return None if no solution is found.
    return
        

def read_from_file(filename): # Function implementation from starter code
    """
    Load initial board from a given file.

    :param filename: The name of the given file.
    :type filename: str
    :return: A loaded board
    :rtype: Board
    """

    puzzle_file = open(filename, "r")

    line_index = 0
    pieces = []
    final_pieces = []
    final = False
    found_2by2 = False
    finalfound_2by2 = False
    height_ = 0
    count = 0
    track = set()
    final_count = 0
    final_track = set()
    for line in puzzle_file:
        height_ += 1
        if line == '\n':
            if not final:
                height_ = 0
                final = True
                line_index = 0
            continue
        if not final: #initial board
            for x, ch in enumerate(line):
                if ch != '\n':
                    count += 1
                if ch == '^': # found vertical piece
                    pieces.append(Piece(False, False, x, line_index, 'v'))
                elif ch == '<': # found horizontal piece
                    pieces.append(Piece(False, False, x, line_index, 'h'))
                elif ch == char_single:
                    pieces.append(Piece(False, True, x, line_index, None))
                # Modified error in starter code to track every 2x2 piece on the board
                elif ch == '1' and count not in track:
                    track.add(count+1)
                    track.add(count+4)
                    track.add(count+5)
                    pieces.append(Piece(True, False, x, line_index, None))
                if count in track:
                    track.remove(count)

                    
        else: #goal board
            for x, ch in enumerate(line):
                if ch != '\n':
                    final_count += 1
                if ch == '^': # found vertical piece
                    final_pieces.append(Piece(False, False, x, line_index, 'v'))
                elif ch == '<': # found horizontal piece
                    final_pieces.append(Piece(False, False, x, line_index, 'h'))
                elif ch == char_single:
                    final_pieces.append(Piece(False, True, x, line_index, None))
                # Modified error in starter code to track every 2x2 piece on the board
                elif ch == '1' and final_count not in final_track:
                    final_track.add(final_count+1)
                    final_track.add(final_count+4)
                    final_track.add(final_count+5)
                    final_pieces.append(Piece(True, False, x, line_index, None))
                if final_count in final_track:
                    final_track.remove(final_count)
        line_index += 1
        
    puzzle_file.close()
    board = Board(height_, pieces)
    goal_board = Board(height_, final_pieces)
    return board, goal_board


def grid_to_string(grid): # Function implementation from starter code (used for debugging)
    string = ""
    for i, line in enumerate(grid):
        for ch in line:
            string += ch
        string += "\n"
    return string


if __name__ == "__main__": # Implementation from starter code with minor changes

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The input file that contains the puzzles."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )
    parser.add_argument(
        "--algo",
        type=str,
        required=True,
        choices=['astar', 'dfs'],
        help="The searching algorithm."
    )
    args = parser.parse_args()

    # read the board from the file
    board, goal_board = read_from_file(args.inputfile)
    
    # write solutions to the output file using the algorithm inputted by the user (DFS or A*)
    if args.algo == "dfs":
        initial_state = State(board, heuristic, 0, 0, None)
        goal_state = State(goal_board, heuristic, 0, 0, None)
        initial_state.f = heuristic(initial_state, goal_state) + initial_state.depth
        solution = dfs_search(initial_state, goal_state)
    else:
        initial_state = State(board, heuristic, 0, 0, None)
        goal_state = State(goal_board, heuristic, 0, 0, None)
        initial_state.f = heuristic(initial_state, goal_state) + initial_state.depth
        solution = a_star_search(initial_state, goal_state)
    with open(args.outputfile, 'w') as sys.stdout:
        if solution is None:
            print("No solution")
        else:
            for state in solution:
                state.board.display()
                print("")
