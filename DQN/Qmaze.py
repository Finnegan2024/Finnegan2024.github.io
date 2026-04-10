## This class controls functionality for the maze environment
import numpy as np

class Qmaze(object):
    visitedMark = 0.8
    ratMark = 0.5

    LEFT = 0
    UP = 1
    RIGHT = 2
    DOWN = 3

    # Actions dictionary
    actions_dict = {
    LEFT: 'left',
    UP: 'up',
    RIGHT: 'right',
    DOWN: 'down',
    }

    def __init__(self, maze, rat=(0,0)):
        self._maze = np.array(maze)
        nRows, nCols = self._maze.shape
        self.cheeseCell = (nRows-1, nCols-1)
        self.freeCells = [(r,c) for r in range(nRows) for c in range(nCols) if self._maze[r,c] == 1.0]
        self.freeCells.remove(self.cheeseCell)
        if self._maze[self.cheeseCell] == 0.0:
            raise Exception("Invalid cheese cell location: cell is blocked")
        if not rat in self.freeCells:
            raise Exception("Invalid rate cell location: rat must be in free cell")
        self.reset(rat)

    def reset(self, rat):
        self.rat = rat
        self.maze = np.copy(self._maze)
        # nRows, nCols = self.maze.shape
        row, col = rat
        self.maze[row, col] = Qmaze.ratMark
        self.state = (row, col, 'start')
        self.minReward = self.maze.size * -0.5
        self.totalReward = 0
        self.visited = set()

    def update_state(self, action):
        #nRows, nCols = self.maze.shape
        nRow, nCol, nMode = self.state

        if self.maze[nRow, nCol] > 0.0:
            self.visited.add((nRow, nCol))

        validActions = self.valid_actions()

        if not validActions:
            nMode = 'blocked'
        elif action in validActions:
            nMode = 'valid'
            if action == self.LEFT:
                nCol -= 1
            elif action == self.UP:
                nRow -= 1
            elif action == self.RIGHT:
                nCol += 1
            elif action == self.DOWN:
                nRow += 1
        else:
            nMode = 'invalid'

        self.state = (nRow, nCol, nMode)

    def get_reward(self):
        rat_row, rat_col, mode = self.state
        nRows, nCols = self.maze.shape
        
        if rat_row == nRows - 1 and rat_col == nCols - 1:
            return 1.0
        
        if mode == 'blocked':
            return self.minReward - 1
        
        if (rat_row, rat_col) in self.visited:
            return -0.25
        
        if mode == 'invalid':
            return -0.75
        
        if mode == 'valid':
            return -0.04
        
    def act(self, action):
        self.update_state(action)
        reward = self.get_reward()
        self.totalReward += reward
        status = self.game_status()
        envState = self.observe()
        return envState, reward, status
    
    def observe(self):
        canvas = self.draw_env()
        envState = canvas.reshape((1, -1))
        return envState
    
    def draw_env(self):
        canvas = np.copy(self.maze)
        nRows, nCols = self.maze.shape

        # clear visual marks?
        for row in range(nRows):
            for col in range(nCols):
                if canvas[row, col] > 0.0:
                    canvas[row, col] = 1.0
        
        # draw rat
        ratRow, ratCol, mode = self.state
        canvas[ratRow, ratCol] = Qmaze.ratMark
        return canvas
    
    def game_status(self):
        if self.totalReward < self.minReward:
            return 'lose'
        row, col, mode = self.state
        nRows, nCols = self.maze.shape
        if row == nRows - 1 and col == nCols - 1:
            return 'win'
        
        return 'not_over'
    
    def valid_actions(self, cell=None):
        if cell is None:
            row, col, mode = self.state
        else:
            row, col = cell
        
        actions = [0, 1, 2, 3]
        nRows, nCols = self.maze.shape
        
        if row == 0:
            actions.remove(1)
        elif row == nRows - 1:
            actions.remove(3)

        if col == 0:
            actions.remove(0)
        elif col == nCols - 1:
            actions.remove(2)

        if row > 0 and self.maze[row - 1, col] == 0.0:
            actions.remove(1)
        if row < nRows - 1 and self.maze[row + 1, col] == 0.0:
            actions.remove(3)

        if col > 0 and self.maze[row, col - 1] == 0.0:
            actions.remove(0)
        if col < nCols - 1 and self.maze[row, col + 1] == 0.0:
            actions.remove(2)

        return actions
