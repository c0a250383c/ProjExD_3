import os
import random
import sys
import time
import pygame as pg

WIDTH = 1100
HEIGHT = 650
NUM_OF_BOMBS = 5
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate

class Bird:
    delta = {
        pg.K_UP: (0, -5), pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0), pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)
    imgs = {
        (+5, 0): img, (+5, -5): pg.transform.rotozoom(img, 45, 0.9),
        (0, -5): pg.transform.rotozoom(img, 90, 0.9), (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),
        (-5, 0): img0, (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),
        (0, +5): pg.transform.rotozoom(img, -90, 0.9), (+5, +5): pg.transform.rotozoom(img, -45, 0.9),
    }

    def __init__(self, xy: tuple[int, int]):
        self.dire = (+5, 0)  # 初期向き：右
        self.img = __class__.imgs[self.dire]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy

    def change_img(self, num: int, screen: pg.Surface):
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)  # 向きを更新
            self.img = __class__.imgs[self.dire]
        screen.blit(self.img, self.rct)

class Beam:
    def __init__(self, bird: Bird):
        self.img = pg.image.load("fig/beam.png")
        self.rct = self.img.get_rect()
        # スライド14：こうかとんの向き（vx, vy）をビームの速度にする
        self.vx, self.vy = bird.dire
        # スライド14：ビームの初期位置をこうかとんの中心に
        self.rct.center = bird.rct.center
        
        # 向きに合わせてビームの画像を回転させる（おまけ：見た目が良くなります）
        import math
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        self.img = pg.transform.rotozoom(self.img, angle, 1.0)

    def update(self, screen: pg.Surface):
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)

class Bomb:
    def __init__(self, color: tuple[int, int, int], rad: int):
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        yoko, tate = check_bound(self.rct)
        if not yoko: self.vx *= -1
        if not tate: self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)

def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200))
    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)]
    beam = None
    clock = pg.time.Clock()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                # スペースでビーム生成（今のbirdの状態を渡す）
                beam = Beam(bird)            
        
        screen.blit(bg_img, [0, 0])
        
        # 衝突判定
        for i, bomb in enumerate(bombs):
            if bomb is not None:
                if bird.rct.colliderect(bomb.rct):
                    bird.change_img(8, screen)
                    fonto = pg.font.Font(None, 80)
                    txt = fonto.render("Game Over", True, (255, 0, 0))
                    screen.blit(txt, [WIDTH//2-150, HEIGHT//2])
                    bird.change_img(8, screen)
                    pg.display.update()
                    time.sleep(1)
                    return
                if beam is not None and beam.rct.colliderect(bomb.rct):
                    beam = None
                    bombs[i] = None
                    bird.change_img(6, screen)
                    break 

        bombs = [b for b in bombs if b is not None]

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)

        
        if beam is not None:
            beam.update(screen)
            if check_bound(beam.rct) != (True, True):
                beam = None

        for bomb in bombs:
            bomb.update(screen)
            
        pg.display.update()
        clock.tick(50)
class Score:
    """
    打ち落とした爆弾の数を表示するクラス
    """
    def __init__(self):
        self.fonto = pg.font.SysFont(None, 30)
        self.color = (0, 0, 255) # 青
        self.score = 0
        self.img = self.fonto.render(f"Score: {self.score}", 0, self.color)
        # 画面左下（横100, 縦は下から50）
        self.rct = self.img.get_rect()
        self.rct.center = (100, 650 - 50)

    def update(self, screen: pg.Surface):
        self.img = self.fonto.render(f"Score: {self.score}", 0, self.color)
        screen.blit(self.img, self.rct)

def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200))
    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)]
    beam = None
    
    # 1. Scoreインスタンスの生成
    score = Score() 
    
    clock = pg.time.Clock()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beam = Beam(bird)            
        
        screen.blit(bg_img, [0, 0])
        
        for i, bomb in enumerate(bombs):
            if bomb is not None:
                if bird.rct.colliderect(bomb.rct):
                    # ゲームオーバー処理（省略）
                    return
                
                if beam is not None and beam.rct.colliderect(bomb.rct):
                    beam = None
                    bombs[i] = None
                    bird.change_img(6, screen)
                    
                    # 2. スコアアップ（1点）
                    score.score += 1 
                    break 

        bombs = [b for b in bombs if b is not None]
        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        
        if beam is not None:
            beam.update(screen)
            if check_bound(beam.rct) != (True, True):
                beam = None

        for bomb in bombs:
            bomb.update(screen)
            
        # 3. スコアの描画更新
        score.update(screen) 
            
        pg.display.update()
        clock.tick(50)

# ... (以下 init 等)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()