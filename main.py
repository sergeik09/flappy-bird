import pygame as pg
import random
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800
TILE_SCALE = 3

pg.init()

font = pg.font.Font(None, 30)
score_font = pg.font.Font(None, 70)

FPS = 60

class Pipe(pg.sprite.Sprite):
    def __init__(self, is_top=False, height=0):
        super(Pipe, self).__init__()

        pipe_size_x = 32
        pipe_size_y = 80
        spritesheet = pg.image.load('assets/Tiles/Style 1/PipeStyle1.png')
        pipe_len = random.randint(0, 7)

        x = pipe_len % 4 * pipe_size_x
        y = pipe_len // 4 * pipe_size_y
        rect = pg.Rect(x, y, pipe_size_x, pipe_size_y)
        pipe_image = spritesheet.subsurface(rect)
        
        if is_top:
            pipe_image = pg.transform.flip(pipe_image, False, True)
            
        pipe_image = pg.transform.scale(pipe_image, (pipe_size_x * TILE_SCALE, pipe_size_y * TILE_SCALE))
        
        num_pipes = height // (pipe_size_y * TILE_SCALE) + 1
        self.image = pg.Surface((pipe_size_x * TILE_SCALE, height), pg.SRCALPHA)
        
        for i in range(num_pipes):
            y_pos = i * (pipe_size_y * TILE_SCALE)
            if is_top:
                y_pos = height - (i + 1) * (pipe_size_y * TILE_SCALE)
            self.image.blit(pipe_image, (0, y_pos))
            
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        
        if is_top:
            self.rect.top = 0
        else:
            self.rect.bottom = SCREEN_HEIGHT
            
        self.timer = pg.time.get_ticks()
        self.speed_interval = 100

    def update(self, speed):
        self.rect.x -= speed

class Player(pg.sprite.Sprite):
    def __init__(self, map_width, map_height):
        super(Player, self).__init__()

        self.load_animations()
        self.current_animation = self.flying_animation
        self.current_image = 0
        self.image = self.current_animation[self.current_image]
        self.timer = pg.time.get_ticks()
        self.interval = 300
        self.rect = self.image.get_rect()
        self.rect.center = (200, 400)
        self.velocity_y = 0
        self.gravity = 0.5
        self.map_width = map_width
        self.map_height = map_height

    def update(self):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1
            if self.current_image >= len(self.current_animation):
                self.current_image = 0

            self.image = self.current_animation[self.current_image]
            self.timer = pg.time.get_ticks()

    def load_animations(self):
        tile_size = 16

        self.flying_animation = []
        num_images = 4

        spritesheet = pg.image.load("assets/Player/StyleBird1/Bird1-6.png")

        for i in range(num_images):
            x = i*tile_size
            y = 0
            rect = pg.Rect(x, y, tile_size, tile_size)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale_by(image, TILE_SCALE)
            self.flying_animation.append(image)

    def jump(self):
        self.velocity_y = -TILE_SCALE * 3

class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Flappy Bird")
        self.setup()
        self.record = 0

    def setup(self):
        self.background = pg.image.load('assets/Background/Background2.png')
        self.background = pg.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pg.time.Clock()
        self.mode = 'game'

        self.player = Player(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.all_sprites = pg.sprite.Group()
        self.all_sprites.add(self.player)
        self.pipes = pg.sprite.Group()
        self.timer = pg.time.get_ticks()
        self.points = 0
        self.score_timer = pg.time.get_ticks()
        menu_box = pg.image.load('assets/menu_box.png')
        self.menu_box = pg.transform.scale(menu_box, (330, 636))
        self.speed = 5

        self.speed_interval = 2500
        self.speed_timer = pg.time.get_ticks()

        self.interval = 2000
        self.gap_size = 200

    def create_pipe_pair(self):
        min_height = 50
        max_height = SCREEN_HEIGHT - self.gap_size - min_height
        top_height = random.randint(min_height, max_height)
        
        bottom_height = SCREEN_HEIGHT - (top_height + self.gap_size)
        
        top_pipe = Pipe(is_top=True, height=top_height)
        bottom_pipe = Pipe(is_top=False, height=bottom_height)
        
        self.pipes.add(top_pipe)
        self.pipes.add(bottom_pipe)

    def run(self):
        self.is_running = True
        while self.is_running:
            self.update()
            self.event()
            self.draw()
            self.clock.tick(FPS)

    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_running = False

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.mode == 'game':
                self.player.jump()

            if self.mode=='game_over' and event.type == pg.MOUSEBUTTONDOWN:
                self.setup()

    def update(self):
        self.player.update()
        if self.mode == 'game':
            self.pipes.update(self.speed)
            if pg.time.get_ticks() - self.timer > self.interval:
                self.create_pipe_pair()
                self.timer = pg.time.get_ticks()

            if pg.time.get_ticks() - self.speed_timer > self.speed_interval:
                self.speed += 1
                self.interval = (600 / (self.speed * FPS)) * 1000
                self.speed_timer = pg.time.get_ticks()

        if pg.sprite.spritecollide(self.player, self.pipes, False) or self.player.rect.y > SCREEN_HEIGHT:
            self.mode = 'game_over'

        if pg.time.get_ticks() - self.score_timer > 1000:
            if self.mode=='game':
                self.points += 1
            self.score_timer = pg.time.get_ticks()

        if self.points > self.record:
            self.record = self.points

    def draw(self):
        self.screen.blit(self.background, (0,0))
        self.all_sprites.draw(self.screen)
        self.pipes.draw(self.screen)

        if self.mode == 'game_over':
            menu_rect = self.menu_box.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(self.menu_box, menu_rect)
            text = font.render(f"Score : {self.points}", True, pg.Color("white"))
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2-60, SCREEN_HEIGHT//2-40))
            self.screen.blit(text, text_rect)
            record_text = font.render(f"Record : {self.record}", True, pg.Color("white"))
            record_text_rect = text.get_rect(center=(SCREEN_WIDTH//2-60, SCREEN_HEIGHT//2-65))
            self.screen.blit(record_text, record_text_rect)
            restart_text = font.render('Press LMB to continue', True, pg.Color('white'))
            restart_text_rect = text.get_rect(center=(SCREEN_WIDTH//2-60, SCREEN_HEIGHT//2))
            self.screen.blit(restart_text, restart_text_rect)
        elif self.mode == 'game':
            self.screen.blit(score_font.render(f'{self.points}', False, pg.Color('Yellow')), (SCREEN_WIDTH - 50, 20))

        pg.display.flip()

if __name__ == '__main__':
    game = Game()
    game.run()
