from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame

from world import *
from collections import defaultdict

import time


_KEY_TO_ACTION = {
    pygame.K_SPACE: Action.ATTACK,
    pygame.K_UP: Action.UP,
    pygame.K_DOWN: Action.DOWN,
    pygame.K_LEFT: Action.LEFT,
    pygame.K_RIGHT: Action.RIGHT
}

# https://www.color-hex.com/color-palette/1872
_PALLET = {
    "background": (238,238,238),
    "pixels": {
        PixelType.GUN: (214,45,32),
        PixelType.SHELL: (0,87,231),
        PixelType.ENGINE:  (0,135,68),
        PixelType.BULLET: (255,167,0),
        PixelType.EMPTY: (255,255,255),
    },
    "debug_message": (13, 13, 13),
}


class Render():
    def __init__(self, screen_size, fps):
        self.screen_size = screen_size
        self.fps = fps
        self.debug_message = None
        successes, failures = pygame.init()
        print("{0} successes and {1} failures".format(successes, failures))
        self.screen = pygame.display.set_mode(screen_size)
        self.clock = pygame.time.Clock()
        self.last_debug_info_printed = time.monotonic()
        self.font = pygame.font.SysFont(None, 24)

        pygame.display.set_caption("PixelBattle")

    def ok(self):
        return True

    def delay(self):
        self.clock.tick(self.fps)

    def stop(self):
        pygame.quit()

    def draw(self, world: World):
        for _ in pygame.event.get():
            pass

        self.screen.fill(_PALLET["background"])
        self._draw_pixels(world)

        self._log_debug_info(world)
        if self.debug_message is not None:
            img = self.font.render(self.debug_message, True, _PALLET["debug_message"])
            rect = img.get_rect()
            self.screen.blit(img, (20, 20))

        pygame.display.flip()

    def _draw_pixels(self, world):
        (p_width, p_height) = world.field.shape
        (s_width, s_height) = self.screen_size
        margin = 0.1
        block_width = s_width / p_width
        block_height = s_height / p_height

        w_margin = block_width * margin
        h_margin = block_height * margin

        for i in range(p_width):
            for j in range(p_height):
                pixel_type = PixelType.EMPTY if world.field[i][j] is None else world.field[i][j].ptype
                pygame.draw.rect(
                    self.screen,
                    _PALLET["pixels"][pixel_type],
                    pygame.Rect(
                        block_width * i + w_margin,
                        block_height * j + h_margin,

                        block_width - w_margin,
                        block_height - h_margin,
                    )
                )

    @staticmethod
    def read_action() -> Action:
        keys = pygame.key.get_pressed()
        for key, action in _KEY_TO_ACTION.items():
            if keys[key]:
                return action
        return Action.IDLE

    def _log_debug_info(self, world: World):
        if self.last_debug_info_printed > time.monotonic() - 1:
            return
        print("Iteration: {i}, FPS: {fps:.0f}".format(
            i=world.iteration,
            fps=self.clock.get_fps()
        ))
        self.last_debug_info_printed = time.monotonic()
