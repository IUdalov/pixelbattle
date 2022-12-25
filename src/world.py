import random

import numpy as np
from dataclasses import dataclass
from enum import Enum
from typing import Tuple
from collections import defaultdict

class Action(Enum):
    IDLE = 0
    LEFT = 1
    UP = 2
    RIGHT = 3
    DOWN = 4
    ATTACK = 5


class PixelType(Enum):
    GUN = 1
    SHELL = 2
    ENGINE = 3
    BULLET = 4
    EMPTY = 5

    def init_hp(self) -> int:
        assert self != PixelType.EMPTY
        if self == PixelType.SHELL:
            return 7
        return 1


@dataclass
class Pixel:
    ptype: PixelType
    hp: int
    player_idx: int
    bullet_direction: Action = Action.IDLE


class Actor:
    def action(self, world, player_idx: int) -> Action:
        return Action.IDLE


@dataclass
class DamageItem:
    ptype: PixelType
    damage: int
    self_destructed: bool



@dataclass
class World:
    field: np.ndarray
    is_player_alive: np.ndarray
    actors: np.ndarray
    damage_log: defaultdict
    iteration: int = 0

    def n_players(self) -> int:
        return len(self.is_player_alive)

    def n_alive_players(self) -> int:
        n_alive = 0
        for p in self.is_player_alive:
            if p:
                n_alive = n_alive + 1
        return n_alive


def next_state(world: World):
    actions = np.empty(world.n_players(), dtype=Action)
    for i in range(world.n_players()):
        if world.is_player_alive[i]:
            actions[i] = world.actors[i].action(world, i)
        else:
            actions[i] = Action.IDLE

    world.field = _resolve(_act(world, actions), world.is_player_alive, world.damage_log)
    world.iteration = world.iteration + 1


# IMPLEMENTATION ---
def _move_unsafe(x, y, action) -> Tuple[int, int]:
    if action == Action.UP:
        return x, y - 1
    elif action == Action.DOWN:
        return x, y + 1
    elif action == Action.LEFT:
        return x - 1, y
    elif action == Action.RIGHT:
        return x + 1, y
    else:
        assert False


def _move(x, y, width, height, action) -> Tuple[int, int]:
    new_x, new_y = _move_unsafe(x, y, action)
    return (new_x + width) % width, (new_y + height) % height


def _add_pixel(field, x, y, value):
    if field[x][y] is None:
        field[x][y] = list()
    field[x][y].append(value)


def _fire(field, x, y, new_field, player_idx):
    (width, height) = field.shape
    for action in [Action.DOWN, Action.RIGHT, Action.UP, Action.LEFT]:
        new_x, new_y = _move(x, y, width, height, action)
        if field[new_x][new_y] is None or field[new_x][new_y].player_idx != player_idx:
            bullet = Pixel(
                ptype=PixelType.BULLET,
                hp=PixelType.BULLET.init_hp(),
                player_idx=player_idx,
                bullet_direction=action
            )
            _add_pixel(new_field, new_x, new_y, bullet)


def _act(world, actions):
    new_field = np.empty(world.field.shape, dtype=object)
    (width, height) = world.field.shape
    for x in range(width):
        for y in range(height):
            if world.field[x][y] is None:
                continue

            pixel = world.field[x][y]
            if pixel.ptype != PixelType.BULLET and not world.is_player_alive[pixel.player_idx]:
                continue
            action = actions[pixel.player_idx] if pixel.ptype != PixelType.BULLET else pixel.bullet_direction
            if action == Action.IDLE:
                _add_pixel(new_field, x, y, pixel)
            elif action == Action.ATTACK:
                _add_pixel(new_field, x, y, pixel)
                if pixel.ptype != PixelType.GUN:
                    continue
                _fire(world.field, x, y, new_field, pixel.player_idx)
            elif pixel.ptype == PixelType.BULLET:
                new_x, new_y = _move_unsafe(x, y, action)
                if 0 <= new_x < width and 0 <= new_y < height:
                    _add_pixel(new_field, new_x, new_y, pixel)
            else:
                new_x, new_y = _move(x, y, width, height, action)
                _add_pixel(new_field, new_x, new_y, pixel)

    return new_field


def _resolve(field, is_player_alive, damage_log):
    (width, height) = field.shape
    for x in range(width):
        for y in range(height):
            if field[x][y] is None:
                continue
            field[x][y] = _resolve_pixels(field[x][y], is_player_alive, damage_log)

    return field


def _resolve_pixels(pixels, is_player_alive, damage_log) -> object:
    if len(pixels) == 1:
        return pixels[0]
    pixels = list(sorted(pixels, key=lambda p: p.hp, reverse=True))

    for i in range(1, len(pixels)):
        if pixels[i].ptype == PixelType.ENGINE:
            is_player_alive[pixels[i].player_idx] = False

    for i in range(len(pixels)):
        other = pixels[(i + 1) % len(pixels)]
        damage_log[pixels[i].player_idx].append(
            DamageItem(
                ptype=other.ptype,
                damage=min(pixels[i].hp, other.hp),
                self_destructed=other.hp >= pixels[i].hp
            )
        )

    pixels[0].hp = pixels[0].hp - pixels[1].hp
    if pixels[0].hp != 0:
        return pixels[0]
    else:
        if pixels[0].ptype == PixelType.ENGINE:
            is_player_alive[pixels[0].player_idx] = False
        return None


# HELPERS ---
def _try_place_player(field, player_desc, player_idx) -> bool:
    (width, height) = field.shape
    x = random.randint(0, width - 1)
    y = random.randint(0, height - 1)
    (pwidth, pheight) = player_desc.shape
    for i in range(pwidth):
        for j in range(pheight):
            if player_desc[i][j] == PixelType.EMPTY:
                continue
            if x + i < width and y + j < height and field[x + i][y + j] is None:
                pass
            else:
                return False

    for i in range(pwidth):
        for j in range(pheight):
            if player_desc[i][j] == PixelType.EMPTY:
                continue
            pixel_type = player_desc[i][j]
            field[x + i][y + j] = Pixel(ptype=pixel_type, hp=pixel_type.init_hp(), player_idx=player_idx)

    return True


def gen_world(width, height, players, actors) -> World:
    assert len(players) == len(actors)
    field = np.empty((width, height), dtype=object)
    i = 0
    while i < len(players):
        if _try_place_player(field, players[i], i):
            i = i + 1

    return World(
        field=field,
        is_player_alive=np.array([True]*len(players), dtype=bool),
        actors=np.array(actors, dtype=Actor),
        damage_log=defaultdict(list)
    )


class DummyActor(Actor):
    def action(self, world, player_idx: int) -> Action:
        return Action(random.randint(0, len(Action) - 1))
