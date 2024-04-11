import pygame
import requests
import time
from solver import solve

pygame.font.init()


class Grid:
    def __init__(self, rows: int, cols: int, width: int, height: int, win, board):
        self.rows = rows
        self.cols = cols
        self.board = board
        self.cubes = [[Cube(self.board[i][j], i, j, width, height) for j in range(cols)] for i in range(rows)]
        self.width = width
        self.height = height
        self.model = None
        self.update_model()
        self.selected = (1, 1)
        self.win = win
        # A correct sudoku puzzle should only have 1 unique solution
        self.solved_board = [[self.board[i][j] for j in range(self.cols)] for i in range(self.rows)]
        solve(self.solved_board)
        self.solved_cube = [[Cube(self.solved_board[i][j], i, j, width, height) for j in range(cols)] for i in range(rows)]

    def update_model(self, row=None, col=None):
        if row and col:
            self.model[row][col] = self.cubes[row][col].value
        else:
            self.model = [[self.cubes[i][j].value for j in range(self.cols)] for i in range(self.rows)]

    def place(self, val):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set(val)
            self.update_model(row, col)

            if self.solved_board[row][col] == val:
                self.cubes[row][col].draw_change(self.win, True)
                pygame.display.update()
                pygame.time.delay(500)
                self.update_model(row, col)
                return True
            else:
                self.cubes[row][col].set(0)
                self.cubes[row][col].set_temp(0)
                self.cubes[row][col].draw_change(self.win, False)
                pygame.display.update()
                pygame.time.delay(200)
                self.update_model(row, col)
                return False

    def sketch(self, val):
        row, col = self.selected
        self.cubes[row][col].set_temp(val)

    def draw(self):
        # Draw Grid Lines
        gap = self.width / 9
        for i in range(self.rows+1):
            if i % 3 == 0 and i != 0:
                thick = 4
            else:
                thick = 1
            pygame.draw.line(self.win, (0,0,0), (0, i*gap), (self.width, i*gap), thick)
            pygame.draw.line(self.win, (0, 0, 0), (i * gap, 0), (i * gap, self.height), thick)

        # Draw Cubes
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].draw(self.win)

    def select(self, row, col):
        # Reset all other
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].selected = False

        self.cubes[row][col].selected = True
        self.selected = (row, col)

    def clear(self):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set_temp(0)

    def click(self, pos):
        """
        :param: pos
        :return: (row, col)
        """
        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width / 9
            x = pos[0] // gap
            y = pos[1] // gap
            return (int(y),int(x))
        else:
            return None

    def is_finished(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.cubes[i][j].value == 0:
                    return False
        return True

    def solve_gui(self):
        self.update_model()
        for row in range(self.rows):
            for col in range(self.cols):
                if self.model[row][col] != self.solved_board[row][col]:
                    if self.model[row][col] != 0:
                        self.cubes[row][col].draw_change(self.win, False)
                        pygame.display.update()
                        pygame.time.delay(500)
                    self.model[row][col] = self.solved_board[row][col]
                    self.cubes[row][col].set(self.solved_board[row][col])

                self.cubes[row][col].draw_change(self.win, True)
                self.update_model()
                pygame.display.update()
                pygame.time.delay(30)

class Cube:
    rows = 9
    cols = 9

    def __init__(self, value, row, col, width, height):
        self.value = value
        self.temp = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False

    def draw(self, win):
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        if self.temp != 0 and self.value == 0:
            text = fnt.render(str(self.temp), 1, (128,128,128))
            win.blit(text, (x+5, y+5))
        elif not(self.value == 0):
            text = fnt.render(str(self.value), 1, (0, 0, 0))
            win.blit(text, (x + (gap/2 - text.get_width()/2), y + (gap/2 - text.get_height()/2)))

        if self.selected:
            pygame.draw.rect(win, (0,0,255), (x,y, gap ,gap), 3)

    def draw_change(self, win, g=True):
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        pygame.draw.rect(win, (255, 255, 255), (x, y, gap, gap), 0)

        text = fnt.render(str(self.value), 1, (0, 0, 0))
        win.blit(text, (x + (gap / 2 - text.get_width() / 2), y + (gap / 2 - text.get_height() / 2)))
        if g:
            pygame.draw.rect(win, (0, 255, 0), (x, y, gap, gap), 3)
        else:
            pygame.draw.rect(win, (255, 0, 0), (x, y, gap, gap), 3)

    def set(self, val):
        self.value = val

    def set_temp(self, val):
        self.temp = val

def redraw_window(win, board, time, strikes):
    win.fill((255,255,255))
    # Draw time
    fnt = pygame.font.SysFont("comicsans", 40)
    text = fnt.render("Time: " + format_time(time), 1, (0,0,0))
    win.blit(text, (540 - 160, 560))
    # Draw Strikes
    text = fnt.render("X " * strikes, 1, (255, 0, 0))
    win.blit(text, (20, 560))
    # Draw grid and board
    board.draw()


def format_time(secs):
    sec = secs%60
    minute = secs//60

    mat = " " + str(minute) + ":" + str(sec)
    return mat

def generate_board():
    response = requests.post("https://youdosudoku.com/api/", json={
        "difficulty": "medium",
        "solution": False,
        "array": True,
    }, headers={"Content-Type": "application/json"})
    board = response.json()["puzzle"]
    return [[int(column) for column in row] for row in board]

def main():
    sudoku_board = generate_board()
    win = pygame.display.set_mode((540,600))
    board = Grid(9, 9, 540, 540, win, sudoku_board)
    pygame.display.set_caption("Sudoku")
    key = None
    run = True
    start = time.time()
    strikes = 0
    while run:
        play_time = round(time.time() - start)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                for i in range(1, 10):
                    if event.key == getattr(pygame, f"K_{i}"):
                        key = i
                        break
                    if event.key == getattr(pygame, f"K_KP{i}"):
                        key = i
                        break
                if event.key == pygame.K_DELETE:
                    board.clear()
                    key = None

                if event.key == pygame.K_SPACE:
                    board.solve_gui()

                if event.key == pygame.K_RETURN:
                    i, j = board.selected
                    if board.cubes[i][j].temp != 0:
                        if board.place(board.cubes[i][j].temp):
                            print("Success")
                        else:
                            print("Wrong")
                            strikes += 1
                        key = None

                        if board.is_finished():
                            print("Game over")

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked = board.click(pos)
                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None

        if board.selected and key != None:
            board.sketch(key)

        redraw_window(win, board, play_time, strikes)
        pygame.display.update()


main()
pygame.quit()
