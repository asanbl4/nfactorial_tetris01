import pygame
from pygame import mixer
from copy import deepcopy
from random import choice

# window characteristics
Width, Height = 10, 15
Tile = 40
GAME_resolution = Width * Tile, Height * Tile
resolution = 650, 800
fps = 60
mixer.init()
mixer.Channel(0).play(pygame.mixer.Sound('tetris-assets/sounds/bg_music.mp3'), maxtime=-1)
mixer.Channel(0).set_volume(0.2)
# boolean if it is the game or the main menu current page
GGG = False

GAME_start = True

pygame.init()
sc = pygame.display.set_mode(resolution)
GAME_screen = pygame.Surface(GAME_resolution)
clock = pygame.time.Clock()

main_font = pygame.font.Font('tetris-assets/fonts/FiraSans-Bold.ttf', 65)
font = pygame.font.Font('tetris-assets/fonts/FiraMono-Medium.ttf', 45)

bg = pygame.image.load('img/bg.jpg').convert()
game_bg = pygame.image.load('img/bg2.jpeg').convert()


title_main_menu = main_font.render('Main menu', True, pygame.Color('darkorange'))
title_tetris = main_font.render('TETRIS', True, pygame.Color('darkorange'))
title_score = font.render('SCORE:', True, pygame.Color('green'))
title_record = font.render('RECORD:', True, pygame.Color('purple'))

Playground = [pygame.Rect(i * Tile, j * Tile, Tile, Tile) for i in range(Width) for j in range(Height)]

# figures' coordinates on the plane 4x4
figures_pos = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
               [(-1, 0), (-1, 1), (0, 0), (0, -1)],
               [(0, 0), (-1, 0), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, 0)]]

# transferring 4x4 coordinates into absolute coordinates 650x800
figures = [[pygame.Rect(x + Width / 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in figures_pos]
colors = ["#9254AB", "#C8C343", "#445CF0", "#5FCDE4", "#6BBE30", "#DE7126"]
figure_rect = pygame.Rect(0, 0, Tile - 2, Tile - 2)
field = [[0 for i in range(Width)] for j in range(Height)]

# animation characteristics
a_count, a_speed, a_limit = 0, 60, 2000

# getting current and the next figure
figure, next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))


def get_color(fig):
    for i in range(6):
        if fig == deepcopy(figures[i]):
            return colors[i]


color, next_color = get_color(figure), get_color(next_figure)

score, lines = 0, 0
# assessment of destroying the lines in a row
scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}


# making sure that figures won't go out of the grid
def check_borders():
    if figure[i].x < 0 or figure[i].x > Width - 1:
        return False
    elif figure[i].y > Height - 1 or field[figure[i].y][figure[i].x]:
        return False
    return True


# getting a record
def get_record():
    try:
        with open('record') as f:
            return f.readline()
    except FileNotFoundError:
        with open('record', 'w') as f:
            f.write('0')


# setting a record
def set_record(record, score):
    rec = max(int(record), score)
    with open('record', 'w') as f:
        f.write(str(rec))


while True:
    # main menu
    if not GGG:
        record = get_record()
        record_text = font.render("Current record", True, pygame.Color("black"))
        pygame.display.set_caption("Main menu")
        button_text = font.render("Start new game", True, pygame.Color("white"))
        sc.blit(bg, (0, 0))

        # cursor
        mouse = pygame.mouse.get_pos()

        # button characteristics
        button_x = 145
        button_y = 400
        button_width = 400
        button_height = 100

        # button changing color if cursor is on it
        if button_x <= mouse[0] <= button_x + button_width and button_y <= mouse[1] <= button_y + button_height:
            pygame.draw.rect(sc, pygame.Color("green"), pygame.Rect(button_x, button_y, button_width, button_height),
                             border_radius=10)
        else:
            pygame.draw.rect(sc, pygame.Color("darkgreen"), pygame.Rect(button_x, button_y, button_width, button_height)
                             , border_radius=10)

        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_x <= mouse[0] <= button_x + button_width and button_y <= mouse[1] <= button_y + button_height:
                    GGG = True

        # drawing
        sc.blit(title_main_menu, (182, 20))
        sc.blit(button_text, (button_x + 10, button_y + 20))
        sc.blit(record_text, (button_x + 10, button_y - 200))
        sc.blit(font.render(record, True, pygame.Color('gold')), (button_x + 140, button_y - 120))

    #######################
    # game
    else:
        record = get_record()
        dx, rotate = 0, False
        sc.blit(bg, (0, 0))
        sc.blit(GAME_screen, (50, 100))
        GAME_screen.blit(game_bg, (0, 0))

        # delay after destroying lines
        for i in range(lines):
            pygame.time.wait(200)

        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    dx = -1
                if event.key == pygame.K_RIGHT:
                    dx = 1
                if event.key == pygame.K_DOWN:
                    a_limit = 100
                if event.key == pygame.K_UP:
                    rotate = True

        temp = deepcopy(figure)

        # x moving
        for i in range(4):
            figure[i].x += dx
            if not check_borders():
                figure = deepcopy(temp)
                break

        # y moving
        a_count += a_speed
        if a_count > a_limit:
            a_count = 0
            for i in range(4):
                figure[i].y += 1
                if not check_borders():
                    for i in range(4):
                        field[temp[i].y][temp[i].x] = color
                    figure, color = next_figure, next_color
                    next_figure = deepcopy(choice(figures))
                    next_color = get_color(next_figure)
                    a_limit = 2000
                    mixer.Channel(2).play(pygame.mixer.Sound('tetris-assets/sounds/Drop.wav'))
                    mixer.Channel(2).set_volume(1)
                    break

        # rotating around center по часовой
        center = figure[0]
        temp = deepcopy(figure)
        if rotate:
            # print(figure)
            for i in range(4):
                x = figure[i].y - center.y
                y = figure[i].x - center.x
                figure[i].x = center.x - x
                figure[i].y = center.y + y
                if not check_borders():
                    figure = deepcopy(temp)
                    break

        # destroying full lines
        line, lines = Height - 1, 0
        for row in range(Height - 1, -1, -1):
            count = 0
            for i in range(Width):
                if field[row][i]:
                    count += 1
                field[line][i] = field[row][i]
            if count < Width:
                line -= 1
            else:
                mixer.Channel(1).play(pygame.mixer.Sound('tetris-assets/sounds/Lineclear.wav'))
                mixer.Channel(1).set_volume(1)
                a_speed += 3
                lines += 1
        score += scores[lines]

        ##############
        # DRAWING
        ##############

        # grid
        [pygame.draw.rect(GAME_screen, (40, 40, 40), i, 1) for i in Playground]

        # figure
        for i in range(4):
            figure_rect.x = figure[i].x * Tile
            figure_rect.y = figure[i].y * Tile
            pygame.draw.rect(GAME_screen, color, figure_rect)

        # field
        for y, raw in enumerate(field):
            for x, col in enumerate(raw):
                if col:
                    figure_rect.x, figure_rect.y = x * Tile, y * Tile
                    pygame.draw.rect(GAME_screen, col, figure_rect)

        # next_figure
        for i in range(4):
            figure_rect.x = next_figure[i].x * Tile + 355
            figure_rect.y = next_figure[i].y * Tile + 185
            pygame.draw.rect(sc, next_color, figure_rect)

        # titles
        sc.blit(title_tetris, (160, -10))
        sc.blit(title_score, (475, 540))
        sc.blit(font.render(str(score), True, pygame.Color('white')), (500, 590))
        sc.blit(title_record, (475, 440))
        sc.blit(font.render(record, True, pygame.Color('gold')), (500, 490))

        ##########

        # delay after main menu start button
        if GAME_start:
            pygame.time.wait(500)
            GAME_start = False

        # loss
        for i in range(Width):
            if field[0][i]:
                set_record(record, score)
                field = [[0 for i in range(Width)] for i in range(Height)]
                anim_count, anim_speed, anim_limit = 0, 60, 2000
                score = 0
                # game over
                mixer.Channel(0).stop()
                mixer.Channel(0).play(pygame.mixer.Sound('tetris-assets/sounds/Gameover.wav'))
                mixer.Channel(0).queue(pygame.mixer.Sound('tetris-assets/sounds/bg_music.mp3'))
                GGG = False

    pygame.display.flip()
    clock.tick(fps)
