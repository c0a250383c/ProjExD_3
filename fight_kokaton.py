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
class Explosion:
    """
    爆弾が爆発するエフェクトを表示するクラス
    """
    def __init__(self, obj_rct: pg.Rect):
        # 元の画像と、上下左右にフリップした画像の2つをリストに格納
        img = pg.image.load("fig/explosion.gif")
        self.imgs = [img, pg.transform.flip(img, True, True)]
        self.rct = img.get_rect()
        self.rct.center = obj_rct.center  # 爆発した爆弾の中心座標を設定
        self.life = 40  # 表示時間（爆発時間）を設定

    def update(self, screen: pg.Surface):
        self.life -= 1  # 爆発経過時間を減算
        # lifeが正の間、2つの画像を交互に切り替えて表示
        if self.life > 0:
            # 2で割った余り(0 or 1)を使うことで、1フレームごとに画像が入れ替わる
            img_idx = self.life % 2
            screen.blit(self.imgs[img_idx], self.rct)



# ... (以下 init 等)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()