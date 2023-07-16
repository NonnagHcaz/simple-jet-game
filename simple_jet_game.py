import random
from pathlib import Path

import pygame
from pygame.locals import (
    K_DOWN,
    K_ESCAPE,
    K_F5,
    K_F9,
    K_LCTRL,
    K_LEFT,
    K_LSHIFT,
    K_RIGHT,
    K_SPACE,
    K_UP,
    KEYDOWN,
    QUIT,
    RLEACCEL,
    K_a,
    K_d,
    K_s,
    K_w,
)

ADDENEMY = pygame.USEREVENT + 1
ADDCLOUD = pygame.USEREVENT + 2
ADDHEALTH = pygame.USEREVENT + 3
ADDMANA = pygame.USEREVENT + 4
ADDSTAMINA = pygame.USEREVENT + 5

SKY_BLUE = (135, 206, 250)

# region Display

DEFAULT_DISPLAY_RESOLUTIONS = {
    "720p": {"width": 1280, "height": 720},
    "1080p": {"width": 1920, "height": 1080},
    "1440p": {"width": 2560, "height": 1440},
}

DEFAULT_DISPLAY_RESOLUTION = "720p"
DEFAULT_DISPLAY_HEIGHT = DEFAULT_DISPLAY_RESOLUTIONS[DEFAULT_DISPLAY_RESOLUTION][
    "height"
]
DEFAULT_DISPLAY_WIDTH = DEFAULT_DISPLAY_RESOLUTIONS[DEFAULT_DISPLAY_RESOLUTION]["width"]

# endregion Display

# region Entities

DEFAULT_DROP_HEALTH_TIMER = 60000
DEFAULT_DROP_MANA_TIMER = 60000
DEFAULT_DROP_STAMINA_TIMER = 60000

# region Player

DEFAULT_PLAYER_DAMAGE = 2
DEFAULT_PLAYER_DAMAGE_SCALE = 0.25

DEFAULT_PLAYER_HEALTH = 100
DEFAULT_PLAYER_HEALTH_BAR_BORDER = 2
DEFAULT_PLAYER_HEALTH_BAR_COLOR = (255, 0, 0)
DEFAULT_PLAYER_HEALTH_BAR_HEIGHT = 7
DEFAULT_PLAYER_HEALTH_BAR_ORDER = 1
DEFAULT_PLAYER_HEALTH_SCALE = 0.1

DEFAULT_PLAYER_SPEED = 5
DEFAULT_PLAYER_SPEED_CROUCH_MODIFIER = -2
DEFAULT_PLAYER_SPEED_SPRINT_MODIFIER = 2

DEFAULT_PLAYER_SPRITE = "assets/image/jet.png"

DEFAULT_PLAYER_STAMINA = 100
DEFAULT_PLAYER_STAMINA_BAR_BORDER = 2
DEFAULT_PLAYER_STAMINA_BAR_COLOR = (0, 255, 0)
DEFAULT_PLAYER_STAMINA_BAR_HEIGHT = 7
DEFAULT_PLAYER_STAMINA_BAR_ORDER = 2
DEFAULT_PLAYER_STAMINA_SCALE = 0.25

DEFAULT_PLAYER_MANA = 100
DEFAULT_PLAYER_MANA_BAR_BORDER = 2
DEFAULT_PLAYER_MANA_BAR_COLOR = (0, 0, 255)
DEFAULT_PLAYER_MANA_BAR_HEIGHT = 7
DEFAULT_PLAYER_MANA_BAR_ORDER = 3
DEFAULT_PLAYER_MANA_SCALE = 0.1

# endregion Player

# region Cloud

DEFAULT_CLOUD_SPEED = 5
DEFAULT_CLOUD_SPEED_CROUCH_MODIFIER = -1
DEFAULT_CLOUD_SPEED_SPRINT_MODIFIER = 1

DEFAULT_CLOUD_SPAWN_TIMER = 1000

DEFAULT_CLOUD_SPRITE = "assets/image/cloud.png"

# endregion Cloud

# region Enemy

DEFAULT_ENEMY_DAMAGE = 5
DEFAULT_ENEMY_DAMAGE_SCALE = 0.1

DEFAULT_ENEMY_HEALTH = 5
DEFAULT_ENEMY_HEALTH_SCALE = 0.1

DEFAULT_ENEMY_SPEED = 10
DEFAULT_ENEMY_SPEED_CROUCH_MODIFIER = -5
DEFAULT_ENEMY_SPEED_SPRINT_MODIFIER = 5

DEFAULT_ENEMY_SPAWN_TIMER = 250

DEFAULT_ENEMY_SPRITE = "assets/image/missile.png"

# endregion Enemy

# endregion Entities

# region StatusBar

DEFAULT_STATUS_BAR_HEIGHT = 32
DEFAULT_STATUS_BAR_FONT_SIZE = 32
DEFAULT_STATUS_BAR_FONT_COLOR = (0, 0, 0)
DEFAULT_STATUS_BAR_BACKGROUND_COLOR = (255, 255, 255)

# endregion StatusBar


def draw_player_status_bar(
    surf, pos, size, border_color, background_color, progress_color, progress
):
    pygame.draw.rect(surf, background_color, (*pos, *size))
    pygame.draw.rect(surf, border_color, (*pos, *size), 1)
    innerPos = (pos[0] + 1, pos[1] + 1)
    innerSize = ((size[0] - 2) * progress, size[1] - 2)
    rect = (
        round(innerPos[0]),
        round(innerPos[1]),
        round(innerSize[0]),
        round(innerSize[1]),
    )
    pygame.draw.rect(surf, progress_color, rect)


class Entity(pygame.sprite.Sprite):
    def __init__(
        self,
        parent,
        sprite_path,
        health=0,
        stamina=0,
        mana=0,
        damage=0,
        walk_speed=1,
        sprint_speed=0,
        crouch_speed=0,
        colorkey=pygame.Color("white"),
        *args,
        **kwargs,
    ):
        super(Entity, self).__init__()
        self.parent = parent

        self.max_health = health
        self.health = self.max_health

        self.max_mana = mana
        self.mana = self.max_mana

        self.max_stamina = stamina
        self.stamina = self.max_stamina

        self.damage = damage
        self.colorkey = colorkey

        self.walk_speed = walk_speed
        self.sprint_speed = sprint_speed
        self.crouch_speed = crouch_speed
        self.is_crouching = 0
        self.is_sprinting = 0
        self.speed = self.update_speed()

        self.sprite_path = sprite_path
        self.surf = pygame.image.load(self.sprite_path).convert()
        self.surf.set_colorkey(self.colorkey, RLEACCEL)
        self.rect = self.surf.get_rect()

    def update_speed(self):
        self.speed = (
            self.walk_speed
            + self.is_crouching * self.crouch_speed
            + self.is_sprinting * self.sprint_speed
        )

    def draw_health_bar(self):
        self._draw_bar(
            DEFAULT_PLAYER_HEALTH_BAR_ORDER,
            DEFAULT_PLAYER_HEALTH_BAR_HEIGHT,
            DEFAULT_PLAYER_HEALTH_BAR_COLOR,
            self.health,
            self.max_health,
        )

    def draw_stamina_bar(self):
        self._draw_bar(
            DEFAULT_PLAYER_STAMINA_BAR_ORDER,
            DEFAULT_PLAYER_STAMINA_BAR_HEIGHT,
            DEFAULT_PLAYER_STAMINA_BAR_COLOR,
            self.stamina,
            self.max_stamina,
        )

    def draw_mana_bar(self):
        self._draw_bar(
            DEFAULT_PLAYER_MANA_BAR_ORDER,
            DEFAULT_PLAYER_MANA_BAR_HEIGHT,
            DEFAULT_PLAYER_MANA_BAR_COLOR,
            self.mana,
            self.max_mana,
        )

    def _draw_bar(self, order, height, color, value, max_value):
        top = self.rect.top - order * (1 + height)
        _rect = pygame.Rect(
            self.rect.left,
            top,
            self.rect.width,
            height,
        )
        _rect.midbottom = self.rect.centerx, top
        draw_player_status_bar(
            self.parent.screen,
            _rect.topleft,
            _rect.size,
            pygame.Color("black"),
            pygame.Color("white"),
            color,
            value / max_value,
        )


class RandomEntity(Entity):
    def __init__(self, *args, **kwargs):
        super(RandomEntity, self).__init__(*args, **kwargs)
        self.rect = self.surf.get_rect(
            center=(
                random.randint(
                    self.parent.display_width + 20, self.parent.display_width + 100
                ),
                random.randint(
                    self.parent.status_bar_height * 2,
                    self.parent.display_height - self.parent.status_bar_height * 2,
                ),
            )
        )
        self.speed = random.randint(
            self.walk_speed + self.crouch_speed, self.walk_speed + self.sprint_speed
        )

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()


class Projectile(Entity):
    pass


class Player(Entity):
    def __init__(
        self,
        parent,
        sprite_path=DEFAULT_PLAYER_SPRITE,
        health=DEFAULT_PLAYER_HEALTH,
        damage=DEFAULT_PLAYER_DAMAGE,
        stamina=DEFAULT_PLAYER_STAMINA,
        mana=DEFAULT_PLAYER_MANA,
        walk_speed=DEFAULT_PLAYER_SPEED,
        sprint_speed=DEFAULT_PLAYER_SPEED_SPRINT_MODIFIER,
        crouch_speed=DEFAULT_PLAYER_SPEED_CROUCH_MODIFIER,
        **kwargs,
    ):
        super(Player, self).__init__(
            parent=parent,
            sprite_path=sprite_path,
            health=health,
            damage=damage,
            stamina=stamina,
            mana=mana,
            walk_speed=walk_speed,
            crouch_speed=crouch_speed,
            sprint_speed=sprint_speed,
            **kwargs,
        )

    def update(self, pressed_keys):
        if pressed_keys[K_LSHIFT]:
            self.is_crouching = 0
            self.is_sprinting = 1
        elif pressed_keys[K_LCTRL]:
            self.is_crouching = 1
            self.is_sprinting = 0
        else:
            self.is_crouching = 0
            self.is_sprinting = 0

        self.update_speed()

        _x = 0
        _y = 0

        if pressed_keys[K_UP] or pressed_keys[K_w]:
            _y -= self.speed
        if pressed_keys[K_DOWN] or pressed_keys[K_s]:
            _y += self.speed
        if pressed_keys[K_LEFT] or pressed_keys[K_a]:
            _x -= self.speed
        if pressed_keys[K_RIGHT] or pressed_keys[K_d]:
            _x += self.speed

        self.rect.move_ip(_x, _y)
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > self.parent.display_width:
            self.rect.right = self.parent.display_width
        if self.rect.top <= self.parent.status_bar_height:
            self.rect.top = self.parent.status_bar_height
        elif self.rect.bottom >= self.parent.display_height:
            self.rect.bottom = self.parent.display_height


class Enemy(RandomEntity):
    def __init__(
        self,
        parent,
        sprite_path=DEFAULT_ENEMY_SPRITE,
        health=DEFAULT_ENEMY_HEALTH,
        damage=DEFAULT_ENEMY_DAMAGE,
        walk_speed=DEFAULT_ENEMY_SPEED,
        sprint_speed=DEFAULT_ENEMY_SPEED_SPRINT_MODIFIER,
        crouch_speed=DEFAULT_ENEMY_SPEED_CROUCH_MODIFIER,
        **kwargs,
    ):
        super(Enemy, self).__init__(
            parent=parent,
            sprite_path=sprite_path,
            health=health,
            damage=damage,
            walk_speed=walk_speed,
            crouch_speed=crouch_speed,
            sprint_speed=sprint_speed,
            **kwargs,
        )


class HealthPack(RandomEntity):
    def __init__(
        self,
        parent,
        sprite_path=DEFAULT_PLAYER_SPRITE,
        health=1,
        damage=0,
        walk_speed=DEFAULT_PLAYER_SPEED,
        sprint_speed=DEFAULT_PLAYER_SPEED_SPRINT_MODIFIER,
        crouch_speed=DEFAULT_PLAYER_SPEED_CROUCH_MODIFIER,
        **kwargs,
    ):
        super(HealthPack, self).__init__(
            parent=parent,
            sprite_path=sprite_path,
            health=health,
            damage=damage,
            walk_speed=walk_speed,
            crouch_speed=crouch_speed,
            sprint_speed=sprint_speed,
            **kwargs,
        )


class Cloud(RandomEntity):
    def __init__(
        self,
        parent,
        sprite_path=DEFAULT_CLOUD_SPRITE,
        walk_speed=DEFAULT_CLOUD_SPEED,
        sprint_speed=DEFAULT_CLOUD_SPEED_SPRINT_MODIFIER,
        crouch_speed=DEFAULT_CLOUD_SPEED_CROUCH_MODIFIER,
        colorkey=pygame.Color("black"),
        **kwargs,
    ):
        super(Cloud, self).__init__(
            parent=parent,
            sprite_path=sprite_path,
            walk_speed=walk_speed,
            crouch_speed=crouch_speed,
            sprint_speed=sprint_speed,
            colorkey=colorkey,
            **kwargs,
        )


class Game:
    def __init__(
        self,
        parent=None,
        display_width=DEFAULT_DISPLAY_WIDTH,
        display_height=DEFAULT_DISPLAY_HEIGHT,
        save_file=None,
    ):
        self.parent = parent
        self.display_width = display_width
        self.display_height = display_height
        self.status_bar_width = self.display_width
        self.status_bar_height = DEFAULT_STATUS_BAR_HEIGHT
        self.game_width = self.display_width
        self.game_height = self.display_height - self.status_bar_height
        self.save_file = save_file
        self.screen = None
        self.running = False
        self.background_color = SKY_BLUE
        self.frame_rate = 30
        self.deaths = 0
        self.kills = 0
        self.init()

    def init(self):
        pygame.init()
        pygame.time.set_timer(ADDENEMY, DEFAULT_ENEMY_SPAWN_TIMER)
        pygame.time.set_timer(ADDCLOUD, DEFAULT_CLOUD_SPAWN_TIMER)
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode([self.display_width, self.display_height])
        self.enemies = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.player = None
        self.init_player()

    def init_player(self):
        if self.player:
            self.player.kill()
            self.deaths += 1
        self.player = Player(parent=self)
        self.all_sprites.add(self.player)

    def draw_status_bar(
        self, background_color=pygame.Color("white"), text_color=pygame.Color("black")
    ):
        font = pygame.font.Font(None, DEFAULT_STATUS_BAR_FONT_SIZE)
        string = f"Health: {self.player.health}/{self.player.max_health} • Deaths: {self.deaths}"
        text = font.render(string, True, text_color, background_color)

        # create a rectangular object for the
        # text surface object
        rect = pygame.Rect(0, 0, self.status_bar_width, self.status_bar_height)

        # set the center of the rectangular object.
        # rect.center = (self.status_bar_width // 2, self.status_bar_height // 2)
        self.screen.blit(text, rect)

    def load(self, save_file=None):
        if not save_file:
            save_file = self.save_file

        # TODO: init game params

        self.save_file = save_file

    def save(self):
        pass

    def play(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        # TODO: Create pause menu
                        self.running = False
                    elif event.key == K_F5:
                        # TODO: quick save
                        pass
                    elif event.key == K_F9:
                        # TODO: quick load
                        pass
                elif event.type == ADDENEMY:
                    new_enemy = Enemy(parent=self)
                    self.enemies.add(new_enemy)
                    self.all_sprites.add(new_enemy)
                elif event.type == ADDCLOUD:
                    new_cloud = Cloud(parent=self)
                    self.clouds.add(new_cloud)
                    self.all_sprites.add(new_cloud)

            pressed_keys = pygame.key.get_pressed()
            self.player.update(pressed_keys)

            self.enemies.update()
            self.clouds.update()
            self.screen.fill(self.background_color)

            self.draw_status_bar()
            self.player.draw_health_bar()
            self.player.draw_stamina_bar()
            self.player.draw_mana_bar()

            for entity in self.all_sprites:
                self.screen.blit(entity.surf, entity.rect)

            enemy_collisions = pygame.sprite.spritecollide(
                self.player, self.enemies, False
            )
            for enemy in enemy_collisions:
                self.player.health -= enemy.damage
                self.draw_status_bar()
                self.player.draw_health_bar()
                enemy.kill()

            if self.player.health <= 0:
                self.init_player()

            pygame.display.flip()

            self.clock.tick(self.frame_rate)

        self.quit()

    def quit(self):
        pygame.quit()


if __name__ == "__main__":
    Game().play()
