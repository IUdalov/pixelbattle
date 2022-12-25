from world import *

from dataclasses import dataclass
from random import randint
import numpy as np

# GENOME of size N is 5 layers: heart, shell, gun, bullet_v, bullet_h
# EMatrix (2 * N + 1) x len(Action) * 5

_N_CHANNELS = 5


class GenomeActor(Actor):
    def __init__(self, genome: np.ndarray):
        self.genome = genome

    def action(self, world: World, player_idx: int) -> Action:
        return self._choose_action(self._make_mask(world, player_idx))

    def _choose_action(self, mask) -> Action:
        (width, height, channels) = mask.shape
        res = np.zeros(shape=(width, len(Action)), dtype=float)
        for c in range(channels):
            res = res + np.matmul(mask[:, :, c], self.genome[:, :, c])

        logits = np.matmul(np.ones((1, width), dtype=float), res).reshape(len(Action))
        max_val = logits[0]
        max_ind = 0
        for i in range(len(logits)):
            if logits[i] > max_val:
                max_val= logits[i]
                max_ind = i
        return Action(max_ind)

    def _make_mask(self, world: World, player_idx: int) -> np.ndarray:
        (genome_size, _, _) = self.genome.shape
        mask = np.zeros((genome_size, genome_size, _N_CHANNELS), dtype=float)
        (engine_x, engine_y) = self._find_engine(world, player_idx)
        (f_width, f_height) = world.field.shape
        (m_width, m_height, _) = mask.shape
        for x in range(m_width):
            for y in range(m_height):
                f_x = int((engine_x - (m_width - 1) / 2 + x + f_width) % f_width)
                f_y = int((engine_y - (m_height - 1) / 2 + y + f_height) % f_height)
                pixel = world.field[f_x][f_y]
                if pixel is None:
                    pass
                elif pixel.ptype == PixelType.ENGINE:
                    mask[x][y][0] = 1 if pixel.player_idx == player_idx else -1
                elif pixel.ptype == PixelType.SHELL:
                    mask[x][y][1] = 1 if pixel.player_idx == player_idx else -1
                elif pixel.ptype == PixelType.GUN:
                    mask[x][y][2] = 1 if pixel.player_idx == player_idx else -1
                elif pixel.ptype == PixelType.BULLET:
                    if pixel.bullet_direction == Action.LEFT:
                        mask[x][y][3] = -1
                    if pixel.bullet_direction == Action.RIGHT:
                        mask[x][y][3] = 1
                    if pixel.bullet_direction == Action.UP:
                        mask[x][y][4] = -1
                    if pixel.bullet_direction == Action.DOWN:
                        mask[x][y][4] = 1
                else:
                    assert False
        return mask

    def _find_engine(self, world, player_idx):
        (width, height) = world.field.shape
        for x in range(width):
            for y in range(height):
                pixel = world.field[x][y]
                if pixel is not None and pixel.player_idx == player_idx and pixel.ptype == PixelType.ENGINE:
                    return x, y
        assert False


def rand_genome(size):
    # heart, attack, shells, bullets, directions
    return np.random.normal(0, 1, size=(size * 2 + 1, len(Action), _N_CHANNELS))


def count_score(player_idx, log):
    score = 0
    for damage_item in log:
        if damage_item.ptype == PixelType.ENGINE:
            score = score + 20
        elif damage_item.ptype == PixelType.GUN:
            score = score + 5
        elif damage_item.ptype != PixelType.BULLET and not damage_item.self_destructed:
            score = score + damage_item.damage * 2
        elif damage_item.ptype != PixelType.BULLET:
            score = score + damage_item.damage
    return score


def select(genomes, damage_log, drop_rate):
    scores_and_genome = list()
    for i in range(genomes.shape[0]):
        scores_and_genome.append((count_score(i, damage_log[i]), genomes[i]))

    return np.array(
        [sg[1] for sg in scores_and_genome[:int(genomes.shape[0] * (1 - drop_rate))]]
    )


def breed(genomes, target_len):
    new_gen = list()
    for genome in genomes:
        new_gen.append(genome)
    while len(new_gen) != target_len:
        new_gen.append((genomes[randint(0, genomes.shape[0] - 1)] + genomes[randint(0, genomes.shape[0] - 1)]) / 2)
    return np.array(new_gen)


def mutate(genomes, rate):
    return genomes + (np.random.random(size=genomes.shape) - 0.5) * rate

