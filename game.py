import pygame as pg
import math
import random
from threading import Thread
import time

# Handle all game logics
class Game:

    def __init__(self, window):
        self.window = window
        self.board = Board(self.window)
        self.isClick = False
        self.bot = 'X' if random.randint(0, 1) == 0 else 'O'
        self.player = 'X' if self.bot == 'O' else 'O'
        self.font = pg.font.SysFont('OpenSans-Regular.ttf', 38)
        self.currentPlayer = self.bot if self.bot == 'X' else self.player
        self.game_over = False
        self.restartButton = None
        self._initConstants()

    def _initConstants(self):
        self.wins = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
    
    def handleEvents(self, event):
        x, y = pg.mouse.get_pos()
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.restartButton is not None and pg.Rect(self.restartButton).collidepoint(x, y):
                self.restartButton = None
                return True
        if self.currentPlayer == self.player and not self.game_over:
            if event.type == pg.MOUSEBUTTONDOWN and not self.isClick:
                self.isClick = True
                selected = self.board.handlePlayer(self.currentPlayer, x=x, y=y)
                if selected:
                    self.currentPlayer = 'X' if self.currentPlayer == 'O' else 'O'
                    time.sleep(0.5)
            elif event.type == pg.MOUSEBUTTONUP and self.isClick:
                self.isClick = False
        return False
    
    def _player(self, board):
        if board.count('X') > board.count('O'):
            return 'O'
        else:
            return 'X'

    def _actions(self, board):
        return [i for i, space in enumerate(board) if space == 'EMPTY']

    def _result(self, board, action):
        if action not in self._actions(board):
            raise Exception('Invalid Action')
        boardCopy = board.copy()
        currentPlayer = self._player(boardCopy)
        boardCopy[action] = currentPlayer
        return boardCopy

    def _winner(self, board):
        for winState in self.wins:
            if board[winState[0]] != 'EMPTY' and board[winState[0]] == board[winState[1]] == board[winState[2]]:
                return board[winState[0]]
        return None

    def _terminal(self, board):
        if self._winner(board) is not None or len(self._actions(board)) == 0:
            return True
        
        return False

    def _utility(self, board):
        if not self._terminal(board):
            raise Exception('The game has not ended')
        
        if self._winner(board) == self.player:
            return 1
        elif self._winner(board) == self.bot:
            return -1
        else:
            return 0

    def _minimax(self, board):
        if self._terminal(board):
            return None

        minimalVal = math.inf
        optimalAction = None

        for action in self._actions(board):
            value = min(minimalVal, self._max_value(self._result(board, action)))
            if value < minimalVal:
                minimalVal = value
                optimalAction = action
        
        return optimalAction

    def _max_value(self, board):
        if self._terminal(board):
            return self._utility(board)
        
        value = -math.inf
        for action in self._actions(board):
            value = max(value, self._min_value(self._result(board, action)))
        
        return value
    
    def _min_value(self, board):
        if self._terminal(board):
            return self._utility(board)
        
        value = math.inf
        for action in self._actions(board):
            value = min(value, self._max_value(self._result(board, action)))
        
        return value

    def play(self):
        self.board.render()

        text = self.font.render('You: ', True, (0, 255, 0) if self.player == 'O' else (255, 0, 0))
        self.window.blit(text, (800, 200))
        text = self.font.render('Bot: ', True, (0, 255, 0) if self.bot == 'O' else (255, 0, 0))
        self.window.blit(text, (800, 350))
        pg.draw.rect(self.window, (215, 224, 218), (880, 157, 100, 100))
        pg.draw.rect(self.window, (215, 224, 218), (880, 307, 100, 100))
        crossY = (167, 247) if self.player == 'X' else (317, 397)
        circleY = 207 if self.player == 'O' else 357
        pg.draw.line(self.window, (255, 0, 0), (890, crossY[0]), (970, crossY[1]), width=8)
        pg.draw.line(self.window, (255, 0, 0), (970, crossY[0]), (890, crossY[1]), width=8)
        pg.draw.circle(self.window, (0, 255, 0), (930, circleY), 45, width=8)

        board = self.board.get_state()
        self.game_over = self._terminal(board)

        if self.game_over:
            winner = self._winner(board)
            if winner == self.player:
                text = self.font.render('You Win!', True, (0, 255, 0))
            elif winner == self.bot:
                text = self.font.render('Bot Wins!', True, (255, 0, 0))
            else:
                text = self.font.render('It\'s a Draw!', True, (0, 100, 255))
            self.window.blit(text, (800, 500))
            text = self.font.render('Restart', True, (255, 255, 255))
            self.restartButton = pg.draw.rect(self.window, (0, 100, 255), (800, 550, 150, 50))
            self.window.blit(text, (828, 564))

        if self.currentPlayer == self.bot and not self.game_over:
            optimalAction = self._minimax(board)
            self.board.handleBot(optimalAction, self.currentPlayer)
            self.currentPlayer = 'X' if self.currentPlayer == 'O' else 'O'

# Handles all board renders
class Board:

    def __init__(self, window, color=(0, 0, 0)):
        self.window = window
        self.screen = pg.Surface((650, 650))
        self.screen.fill(color)
        self._init()
    
    def _init(self):
        self.cellsSelected = set()
        self.cells = []
        for y in range(5, 650, 215):
            for x in range(5, 650, 215):
                self.cells.append(self.Cell((x, y, 210, 210)))
    
    def get_state(self):
        return [cell.value for cell in self.cells]

    def render(self):
        self.window.blit(self.screen, (75, 75))
        for cell in self.cells:
            cell.render(self.screen)
        self._renderSymbols()

    def handleBot(self, action, player):
        self.cells[action].setValue(player)
        self.cellsSelected.add(self.cells[action])

    def handlePlayer(self, player, x, y):
        for cell in self.cells:
            if cell.rect.collidepoint(x-75, y-75) and cell not in self.cellsSelected:
                cell.setValue(player)
                self.cellsSelected.add(cell)
                return True
        return False
    
    def _renderSymbols(self):
        for cell in self.cellsSelected:
            cell.renderSymbol(self.window)
    
    class Cell:

        def __init__(self, rect):
            self.value = 'EMPTY'
            self.rect = pg.Rect(rect)
        
        def setValue(self, value):
            self.value = value
        
        def render(self, window):
            pg.draw.rect(window, (255, 255, 255), self.rect)
        
        def renderSymbol(self, window):
            if self.value == 'X':
                pg.draw.line(window, (255, 0, 0), (self.rect.x + 15 + 75, self.rect.y + 15 + 75), (self.rect.x + self.rect.width - 15 + 75, self.rect.y + self.rect.height - 15 + 75), width=10)
                pg.draw.line(window, (255, 0, 0), (self.rect.x + self.rect.width - 15 + 75, self.rect.y + 15 + 75), (self.rect.x + 15 + 75, self.rect.y + self.rect.height - 15 + 75), width=10)
            else:
                pg.draw.circle(window, (0, 255, 0), (self.rect.x + self.rect.width//2 + 75, self.rect.y + self.rect.height//2 + 75), self.rect.width//2 - 15, width=10)
