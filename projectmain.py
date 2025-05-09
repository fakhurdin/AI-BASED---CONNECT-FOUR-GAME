import os
import sys
import time
import logging
import pygame
from pygame import mixer

# Optional Python beep fallback
try:
    import winsound
    def beep(frequency=440, duration=100): winsound.Beep(frequency, duration)
except ImportError:
    def beep(frequency=440, duration=100): pass

# Initialize modules
pygame.init()
logging.basicConfig(level=logging.INFO)
mixer.init()

# === Fonts & Colors ===
TITLE_FONT = pygame.font.SysFont("Calibri", 56, bold=True)
MENU_FONT  = pygame.font.SysFont("Calibri", 40, bold=True)
INFO_FONT  = pygame.font.SysFont("Calibri", 28)
BUTTON_FONT= pygame.font.SysFont("Calibri", 32, bold=True)

COLORS = {
    'bg_top': (20,20,60),
    'bg_bot': (0,0,30),
    'text': (240,240,240),
    'highlight': (255,215,0),
    'board': (0,100,200),
    'human': (200,50,50),
    'ai': (200,200,50),
    'button': (50,50,100),
    'button_hover': (80,80,140)
}

# === Asset paths & sounds ===
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')

def play_sound(key):
    """Play a WAV from assets or fallback to system beep."""
    path = os.path.join(ASSETS_DIR, f"{key}.wav")
    if os.path.exists(path):
        try:
            mixer.Sound(path).play()
        except Exception:
            beep()
    else:
        beep()

# === UI Helpers ===
def draw_text_center(surface, text, font, color, center):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=center)
    surface.blit(surf, rect)
    return rect

def draw_gradient(surface, w, h):
    top, bot = COLORS['bg_top'], COLORS['bg_bot']
    for y in range(h):
        ratio = y / h
        r = int(top[0] + (bot[0] - top[0]) * ratio)
        g = int(top[1] + (bot[1] - top[1]) * ratio)
        b = int(top[2] + (bot[2] - top[2]) * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (w, y))

def button(surface, rect, text, hover):
    color = COLORS['button_hover'] if hover else COLORS['button']
    pygame.draw.rect(surface, color, rect, border_radius=8)
    draw_text_center(surface, text, BUTTON_FONT, COLORS['text'], rect.center)

# === Main Menu ===
BOARD_OPTIONS = [(6,7), (7,8), (8,9)]
DIFF_OPTIONS  = [("Easy",2), ("Medium",4), ("Hard",6)]

def menu_screen():
    W, H = 700, 500
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Connect Four Setup")
    clock = pygame.time.Clock()
    idx_b, idx_d, stage = 0, 1, 0
    while True:
        draw_gradient(screen, W, H)
        draw_text_center(screen, "Connect Four", TITLE_FONT, COLORS['highlight'], (W//2, 80))
        prompt = "Select Grid Size" if stage == 0 else "Select Difficulty"
        draw_text_center(screen, prompt, INFO_FONT, COLORS['text'], (W//2, 160))
        opts = BOARD_OPTIONS if stage == 0 else DIFF_OPTIONS
        for i, opt in enumerate(opts):
            label = f"{opt[0]}×{opt[1]}" if stage == 0 else opt[0]
            x = (i+1) * W // (len(opts) + 1)
            color = COLORS['highlight'] if (i == (idx_b if stage == 0 else idx_d)) else COLORS['text']
            draw_text_center(screen, label, MENU_FONT, color, (x, 260))
        draw_text_center(screen, "←/→ to change, ENTER to confirm", INFO_FONT, COLORS['text'], (W//2, 420))
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RIGHT:
                    if stage == 0: idx_b = (idx_b + 1) % len(BOARD_OPTIONS)
                    else:        idx_d = (idx_d + 1) % len(DIFF_OPTIONS)
                if e.key == pygame.K_LEFT:
                    if stage == 0: idx_b = (idx_b - 1) % len(BOARD_OPTIONS)
                    else:        idx_d = (idx_d - 1) % len(DIFF_OPTIONS)
                if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if stage == 0:
                        stage = 1
                    else:
                        return BOARD_OPTIONS[idx_b], DIFF_OPTIONS[idx_d][1]
        pygame.display.flip()
        clock.tick(60)

# === Game Logic ===
def is_full(board):
    return all(cell != 0 for cell in board[0])

def is_winner(board, pl, win_len):
    rows, cols = len(board), len(board[0])
    for r in range(rows):
        for c in range(cols):
            if board[r][c] != pl: continue
            for dr, dc in [(0,1),(1,0),(1,1),(-1,1)]:
                if all(0 <= r+dr*i < rows and 0 <= c+dc*i < cols and board[r+dr*i][c+dc*i] == pl for i in range(win_len)):
                    return True
    return False

def generate_moves(board, pl):
    rows, cols = len(board), len(board[0])
    moves = []
    for c in range(cols):
        if board[0][c] == 0:
            for r in range(rows-1, -1, -1):
                if board[r][c] == 0:
                    nb = [row[:] for row in board]
                    nb[r][c] = pl
                    moves.append((c, nb))
                    break
    return moves

def evaluate(board, win_len):
    score = 0
    rows, cols = len(board), len(board[0])
    for r in range(rows):
        for c in range(cols):
            if board[r][c] == 0: continue
            for dr, dc in [(0,1),(1,0),(1,1),(-1,1)]:
                cells = []
                for i in range(win_len):
                    rr, cc = r+dr*i, c+dc*i
                    if 0 <= rr < rows and 0 <= cc < cols:
                        cells.append(board[rr][cc])
                if len(cells) == win_len:
                    h = cells.count(1)
                    a = cells.count(-1)
                    if h == 0 and a > 0:
                        score += 10**(a-1) + 10
                    elif a == 0 and h > 0:
                        score -= 10**(h-1) + 10
    return score

def alpha_beta(board, depth, alpha, beta, pl, win_len):
    if is_winner(board,1,win_len) or is_winner(board,-1,win_len) or is_full(board) or depth == 0:
        return evaluate(board, win_len), None
    if pl == -1:
        best, best_col = -float('inf'), None
        for col, nb in generate_moves(board, -1):
            val, _ = alpha_beta(nb, depth-1, alpha, beta, 1, win_len)
            if val > best:
                best, best_col = val, col
            alpha = max(alpha, val)
            if beta <= alpha: break
        return best, best_col
    else:
        best, best_col = float('inf'), None
        for col, nb in generate_moves(board, 1):
            val, _ = alpha_beta(nb, depth-1, alpha, beta, -1, win_len)
            if val < best:
                best, best_col = val, col
            beta = min(beta, val)
            if beta <= alpha: break
        return best, best_col

# === Rendering & Animation ===
def animate_drop(board, pl, col, screen, DISC, GAP, LEFT_M, TOP_BAR, TOP_M, COLORS, win_len, clock):
    rows = len(board)
    x = LEFT_M + col*(DISC+GAP) + DISC//2
    y = TOP_BAR//2
    target_r = next(r for r in range(rows-1, -1, -1) if board[r][col] == 0)
    target_y = TOP_BAR + TOP_M + target_r*(DISC+GAP) + DISC//2
    while y < target_y:
        y += max(2, DISC//5)
        draw_board(board, screen, DISC, GAP, LEFT_M, TOP_BAR, TOP_M, COLORS)
        pygame.draw.circle(screen, COLORS['human'] if pl==1 else COLORS['ai'], (x, int(y)), DISC//2-8)
        pygame.display.flip()
        clock.tick(120)
    board[target_r][col] = pl
    play_sound('drop')

def draw_board(board, screen, DISC, GAP, LEFT_M, TOP_BAR, TOP_M, COLORS):
    W, H = screen.get_size()
    draw_gradient(screen, W, H)
    width = len(board[0])*DISC + (len(board[0])-1)*GAP
    height = len(board)*DISC + (len(board)-1)*GAP
    pygame.draw.rect(screen, COLORS['board'], (LEFT_M, TOP_BAR+TOP_M, width, height), border_radius=12)
    for r in range(len(board)):
        for c in range(len(board[0])):
            x = LEFT_M + c*(DISC+GAP) + DISC//2
            y = TOP_BAR + TOP_M + r*(DISC+GAP) + DISC//2
            pygame.draw.circle(screen, COLORS['text'], (x, y), DISC//2-4)
            if board[r][c] != 0:
                clr = COLORS['human'] if board[r][c]==1 else COLORS['ai']
                pygame.draw.circle(screen, clr, (x, y), DISC//2-8)
                pygame.draw.circle(screen, COLORS['bg_top'], (x, y), DISC//2-8, 2)
    mx, my = pygame.mouse.get_pos()
    if my < TOP_BAR:
        col = (mx - LEFT_M) // (DISC + GAP)
        if 0 <= col < len(board[0]):
            surf = pygame.Surface((DISC, DISC), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255,255,255,100), (DISC//2, DISC//2), DISC//2-8, 4)
            screen.blit(surf, (LEFT_M + col*(DISC+GAP), TOP_BAR+TOP_M - DISC//2))

# === Game Runner ===
def run_game(rows, cols, difficulty):
    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    gap, margin = 5, 10
    max_w, max_h = int(sw*0.8), int(sh*0.8)
    disc_w = (max_w - 2*margin - (cols-1)*gap) / cols
    disc_h = (max_h - 2*margin - (rows-1)*gap) / (rows + 1)
    DISC = int(max(20, min(disc_w, disc_h)))
    GAP = gap
    LEFT_M = margin
    TOP_BAR = DISC
    TOP_M = margin
    W = LEFT_M*2 + cols*DISC + (cols-1)*GAP
    H = TOP_BAR + TOP_M*2 + rows*DISC + (rows-1)*GAP
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Connect Four")
    clock = pygame.time.Clock()
    board = [[0]*cols for _ in range(rows)]
    state, current, result = 'running', 1, None
    play_btn = pygame.Rect(W//2-160, H//2+50, 140, 50)
    quit_btn = pygame.Rect(W//2+20, H//2+50, 140, 50)
    win_len = 4
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return
            if state == 'running' and current == 1 and e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                if my < TOP_BAR:
                    col = (mx - LEFT_M) // (DISC + GAP)
                    if 0 <= col < cols and board[0][col] == 0:
                        animate_drop(board, 1, col, screen, DISC, GAP, LEFT_M, TOP_BAR, TOP_M, COLORS, win_len, clock)
                        current = -1
            if state == 'over' and e.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.collidepoint(e.pos):
                    return run_game(rows, cols, difficulty)
                if quit_btn.collidepoint(e.pos):
                    pygame.quit(); sys.exit()
        if state == 'running' and current == -1:
            pygame.time.delay(200)
            _, col = alpha_beta(board, difficulty, -1e9, 1e9, -1, win_len)
            if col is not None:
                animate_drop(board, -1, col, screen, DISC, GAP, LEFT_M, TOP_BAR, TOP_M, COLORS, win_len, clock)
                current = 1
        if state == 'running':
            if is_winner(board, 1, win_len):
                state, result = 'over', 'win'; play_sound('win')
            elif is_winner(board, -1, win_len):
                state, result = 'over', 'lose'; play_sound('lose')
            elif is_full(board):
                state, result = 'over', 'draw'; play_sound('draw')
        draw_board(board, screen, DISC, GAP, LEFT_M, TOP_BAR, TOP_M, COLORS)
        if state == 'over':
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0,0,0,200))
            screen.blit(overlay, (0,0))
            txt = {'win':'You win!','lose':'You lose!','draw':'Draw!'}[result]
            draw_text_center(screen, txt, TITLE_FONT, COLORS['highlight'], (W//2, H//2-40))
            button(screen, play_btn, 'Play Again', play_btn.collidepoint(pygame.mouse.get_pos()))
            button(screen, quit_btn, 'Quit', quit_btn.collidepoint(pygame.mouse.get_pos()))
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    while True:
        (rows, cols), difficulty = menu_screen()
        play_sound('drop')
        run_game(rows, cols, difficulty)