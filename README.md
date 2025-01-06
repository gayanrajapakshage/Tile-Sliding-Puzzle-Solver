# Tile-Sliding-Puzzle-Solver
 
## Overview
This project implements a solver for a variant of the Hua Rong Dao tile sliding puzzle, where the goal is to manipulate a set of pieces on a board from an intial state to reach a goal state. The puzzle board is 4 columns wide and can have any number of rows. The puzzle pieces can be 2x2, 1x2 (horizontal or vertical), or 1x1. The user provides an intial and goal state of a puzzle board. The user can then solve the puzzle using either the Depth-First-Search (DFS) or A* Search algorithm, both of which utilize state space search to find the optimal solution (the least number of moves needed to go from the initial state to the goal state).

## Installation
1. Clone the repository.
    ```sh
    git clone https://github.com/<your-username>/Tile-Sliding-Puzzle-Solver.git
    ```
2. Add any additional input files to the project directory you'd like to solve.
3. Ensure Python3 is installed and configured. To check your Python version:
    ```sh
    python3 --version
    ```

## Usage
1. Navigate to the project directory.
    
    ```sh
    cd <project-directory>
    ```
2. Input and Output File Formats  

    The input and output files contain each state of the puzzle using a grid of characters. The grid of each state in these files consists of rows, with each row containing exactly 4 characters. The characters used to represent the different elements are as follows:

    - The empty squares are denoted by: .
    - The 2x2 pieces are denoted by: 1 (the four cells of the piece)
    - A single piece is denoted by: 2
    - A horizontal 1x2 piece is denoted by: < (on the left) and > (on the right)
    - A vertical 1x2 piece is denoted by: ^ (on the top) and v (on the bottom)
    
    Here is an example of a state:
    ```php
    <>^.
    ..v.
    <>11
    ..11
    2..2
    ```
    Each input file contains two states with an empty line between them:

    - The first state represents the initial configuration of the puzzle.
    - The second state represents the goal configuration of the puzzle.

    med1.txt is an example of a valid input file found in the project repository.

    After the code is run on an input file, the output file should contain the solution path to the puzzle. If no solution exists (meaning no sequence of valid moves can transform the initial state into the goal state), the output should contain a single line:

    ```python3
    No solution
    ```

    If a solution exists, the output should contain a sequence of states, where:

    - The first state is the initial state.
    - The last state is the goal state.
    - There should be one empty line between any two consecutive states.

    med1sol.txt is an example of a valid output found in the project repository after running the code on the input file, med1.txt.

3. Run either of the following commands to run the code and solve the tile puzzle with the DFS algorithm or the A* Search algorithm respectively on a particular input file. Ensure the input file is in the project directory.
    
    ```sh
    python3 TileSlidingPuzzleSolver.py --algo dfs --inputfile <input file> --outputfile <output file>    
    ```
    ```sh
    python3 TileSlidingPuzzleSolver.py --algo astar --inputfile <input file> --outputfile <output file>
    ```
    
    The following commands are examples of running the project on the input file, med1.txt, provided in the project repository using the DFS algorithm and the A* Search algorithm respectively.
    ```sh
    python3 TileSlidingPuzzleSolver.py --algo dfs --inputfile med1.txt --outputfile med1sol.txt 
    ```
    ```sh
    python3 TileSlidingPuzzleSolver.py --algo astar --inputfile med1.txt --outputfile med1sol.txt 
    ```

## Testing

The input files easy1.txt, med1.text, and hard1.txt contain valid puzzle configurations that can be used to test the functionality and performance of the solver. Each file represents a different difficulty level and provides an initial state and a goal state to be solved.

The output files easy1sol.txt, med1sol.text, and hard1sol.txt correspond to the solutions for the respective input files and can be used to verify the correctness of the puzzle solver during testing. These solution files contain the optimal sequence of states that lead from the initial state to the goal state in the least number of possible moves. All output files compile within a maximum of 4 minutes for all valid input files.

## References

The starter code for this project was provided by the University of Toronto as part of the course requirements for the Tile Sliding Puzzle Solver assignment. The provided code served as a foundation for the implementation of the solver and is indicated within the project file, TileSlidingPuzzleSolver.py. A full copy of the unmodified starter code is provided in StarterCode.py. The input files and output files easy1.txt, med1.text, hard1.txt, easy1sol.txt, med1sol.text, and hard1sol.txt were also provided by the University of Toronto. Additional references are also acknowledged within the project file.

## License

Copyright © 2024 (modifications). All rights reserved.
The starter code is provided by the University of Toronto and is used with permission.
This code may not be copied, modified, or distributed in any way without explicit permission.