import pygame, sys, random
from pygame.locals import *

pygame.init()

# Variables
TEMP = "Place Holder"
SCREEN_RATIO = 16 / 9
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = int(SCREEN_WIDTH / SCREEN_RATIO)
print (SCREEN_HEIGHT)
CAPTION = "At The Races"
FPS = 30
TRACK = pygame.image.load("track.png")
HORSE_IMG = TEMP
RACE_MUSIC = "William Tell Overture Finale.mp3"
MLG_MUSIC = "Sandstorm - Darude.mp3"
MLG_IMG = TEMP
LANE_WIDTH = 84
HL_BOX = TEMP
YOU_WIN = pygame.image.load("youWin.jpg")
YW_RECT = YOU_WIN.get_rect()
YW_RECT.x = 300
print(YW_RECT)
MLG_MODE = False


# Colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class Horse(object):
    all_horses = []

    def __init__(self, screen_x, screen_y, screen_width, screen_height, move_distance, move_rate, move_chance, image, id):
        self.screen_x = screen_x
        self.screen_y = screen_y
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen_rect = pygame.rect.Rect(self.screen_x, self.screen_y, self.screen_width, self.screen_height)

        self.direction = 1
        self.move_chance = move_chance
        self.move_distance = move_distance
        self.move_rate = move_rate
        self.last_move = 0

        self.original_image = image
        self.image = self.original_image

        self.win = False
        self.id = id

        Horse.all_horses.append(self)

    def random_move(self):
        r = random.randint(0, self.move_chance)
        if r == 0:
            self.move()

    def move(self):
        if self.direction == 1:
            self.screen_x += self.move_distance
        else:
            self.screen_x -= self.move_distance

        self.last_move = 0


    def rot_center(image, rect, angle):
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = rot_image.get_rect(center = rect.center)
        return rot_image, rot_rect

    
    def draw(self, SCREEN, freeze):
        angle = 0
        if MLG_MODE and not freeze:
            angle = random.randint(0, 360)
        img, scr_rect = Horse.rot_center(self.image, self.screen_rect, angle)
        SCREEN.blit(img, scr_rect)


    def checkOffScreen(self, SCREENWIDTH):
        if self.screen_x + self.screen_width > SCREEN_WIDTH:
            self.screen_x = SCREEN_WIDTH - self.screen_width
            self.direction = 0
            if self.direction == 0: # This part is quite necessary
                self.image = pygame.transform.flip(self.original_image, True, False)

        elif self.screen_x < 0:
            self.screen_x = 0
            self.win = True


    def update(self, SCREEN, SCREEN_WIDTH, winner_found, wait):
        self.last_move += 1
        self.screen_rect.x = self.screen_x

        if MLG_MODE and not wait and not winner_found:
            self.screen_rect.x = self.screen_x + random.randint(-10, 10)
            self.screen_rect.y = self.screen_y + random.randint(-10, 10)

        self.draw(SCREEN, wait or winner_found)

        self.checkOffScreen(SCREEN_WIDTH)

        if not (winner_found or wait):
            self.random_move()

        return self.win



def setup():
    global SCREEN, FPSCLOCK, HORSE_IMG, HL_BOX, MLG_MODE, MLG_IMG
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(CAPTION)
    FPSCLOCK = pygame.time.Clock()
    
    HORSE_IMG = pygame.image.load("horse_temp.png").convert_alpha()
    MLG_IMG = pygame.image.load("mlg_horse.png").convert_alpha()
    HL_BOX = pygame.image.load("highlightBox.png").convert_alpha()

    run()
    

def run():
    global MLG_MODE
    
    running = True
    resetHorses() # For convenience sake use reset and not setup
    winner_found = False
    race_start = True
    selecting = True
    loadMusic()
    chosen = 0
    p_win = False
    yw_timer = 0
    yw_max = 60

    cash = 100
    winner_id = -1

    m_down, l_down, g_down = False, False, False
    
    while running:
        SCREEN.fill(WHITE)
        #print(MLG_MODE)

        for i in range(8):
            val = i * LANE_WIDTH
            SCREEN.blit(TRACK, pygame.rect.Rect(0, val, SCREEN_WIDTH, 84))

        for h in Horse.all_horses:
            if race_start and not selecting:
                if MLG_MODE:
                    loadMLGMusic()
                else:
                    loadMusic()
                warmUpMusic()
                playMusic()
                race_start = False
                
            b = h.update(SCREEN, SCREEN_WIDTH, winner_found, selecting)

            if b and not winner_found:
                #print (b)
                stopMusic()
                winner_found = True
                print (h.id)
                winner_id = h.id
                #showHighlightBox(SCREEN, h.id * LANE_WIDTH)
                if h.id == chosen:
                    p_win = True
                else:
                    p_win = False

        if winner_id == -1 and not selecting and MLG_MODE:
            # QUEUE THE EPIC RAINBOW OVERLAY!!!!!
            drawRainbowOverlay(SCREEN)
        
        if winner_id != -1:
            showHighlightBox(SCREEN, winner_id * LANE_WIDTH)

        if p_win and yw_timer < yw_max:
            SCREEN.blit(YOU_WIN, YW_RECT)
            yw_timer += 1

        if selecting:
            mouse_pos = pygame.mouse.get_pos()
            mouse_state = pygame.mouse.get_pressed()
            lane = mouse_pos[1] - mouse_pos[1] % LANE_WIDTH
            showHighlightBox(SCREEN, lane)

            if mouse_state[0] == 1:
                selecting = False

                chosen = int(lane / LANE_WIDTH)
                resetHorses()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()

                elif event.key == K_r:
                    # Make sure a race is already complete
                    if winner_found:
                        resetHorses()
                        winner_found = False
                        race_start = True
                        selecting = True
                        yw_timer = 0
                        p_win = False
                        winner_id = -1
                elif event.key == K_m:
                    m_down = True
                elif event.key == K_l:
                    l_down = True
                elif event.key == K_g:
                    g_down = True
                    
        if m_down and l_down and g_down and selecting:
            changeMLG()
            m_down, l_down, g_down = False, False, False
            if MLG_MODE:
                print("MLG MODE ACTIVATED!!!")
            else:
                print("MLG mode deactivated :(")


        pygame.display.update()
        FPSCLOCK.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


def setupHorses():
    img = HORSE_IMG
    if MLG_MODE:
        img = MLG_IMG
    for i in range(8):
        h = Horse(0, 84 * i, 100, 84, 10, 1, 2, img, i)


def resetHorses():
    Horse.all_horses = []

    setupHorses()


def loadMusic():
    pygame.mixer.music.load(RACE_MUSIC)


def loadMLGMusic():
    pygame.mixer.music.load(MLG_MUSIC)


def playMusic():
    start_loc = 13.9
    if MLG_MODE:
        start_loc = 30
    pygame.mixer.music.play(0, start_loc)


def stopMusic():
    #print (1)
    pygame.mixer.music.stop()


def warmUpMusic():
    playMusic()
    stopMusic()


def showHighlightBox(SCREEN, h):
    r = pygame.rect.Rect(0, h, SCREEN_WIDTH, LANE_WIDTH)
    SCREEN.blit(HL_BOX, r)


def drawRainbowOverlay(SCREEN):
    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    s.set_alpha(200)
    s.fill((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    SCREEN.blit(s, (0, 0))


def changeMLG():
    global MLG_MODE
    MLG_MODE = not MLG_MODE


if __name__ == "__main__":
    setup()
