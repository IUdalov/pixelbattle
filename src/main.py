from render import Render
from world import *

import gentetic as gn
from random import randint
from typing import List

_TANKY = np.array([
    [PixelType.SHELL, PixelType.GUN, PixelType.SHELL],
    [PixelType.GUN, PixelType.ENGINE, PixelType.GUN],
    [PixelType.SHELL, PixelType.GUN, PixelType.SHELL]
])

_EDGY = np.array([
    [PixelType.GUN, PixelType.SHELL, PixelType.GUN],
    [PixelType.SHELL, PixelType.ENGINE, PixelType.SHELL],
    [PixelType.GUN, PixelType.SHELL, PixelType.GUN]]
)

_GOOFY = np.array([
    [PixelType.SHELL, PixelType.GUN, PixelType.SHELL],
    [PixelType.EMPTY, PixelType.ENGINE, PixelType.EMPTY],
    [PixelType.GUN, PixelType.SHELL, PixelType.GUN]]
)


class UserActor(Actor):
    def action(self, world, player_idx: int) -> Action:
        return Render.read_action()


class _CONFIG:
    width = 110
    height = 70
    render_block_size = 15
    fps = 25
    max_iterations = 200

    @staticmethod
    def make_render():
        return Render((_CONFIG.width * _CONFIG.render_block_size, _CONFIG.height * _CONFIG.render_block_size), _CONFIG.fps)


def easy_infinite_sim():
    gen = lambda: gen_world(_CONFIG.width, _CONFIG.height, [_TANKY, _EDGY, _GOOFY], [UserActor(), DummyActor(), Actor()])
    world = gen()
    render = _CONFIG.make_render()

    while render.ok():
        world = next_state(world)
        if not world.has_next_state():
            world = gen()
        render.draw(world)
        render.delay()

    render.stop()


def _simulate_generation(render, genomes, player_type) -> defaultdict:
    world = gen_world(
        _CONFIG.width,
        _CONFIG.height,
        [player_type] * len(genomes),
        [gn.GenomeActor(genom) for genom in genomes]
    )

    while render.ok() and world.n_alive_players() > 2 and world.iteration < _CONFIG.max_iterations:
        next_state(world)
        render.draw(world)
        render.delay()
    return world.damage_log


def genetic(n_players, player_type, genome_size):
    genomes = np.array([gn.rand_genome(genome_size) for i in range(n_players)])
    render = _CONFIG.make_render()

    generation = 0
    while True:
        render.debug_message = "Generation #{}".format(generation)
        genome_scores = _simulate_generation(render, genomes, player_type)
        genomes = gn.select(genomes, genome_scores, drop_rate=0.5)
        genomes = gn.breed(genomes, n_players)
        genomes = gn.mutate(genomes, rate=1 / ((generation + 1) * 1.5))

        generation = generation + 1


if __name__ == "__main__":
    #easy_infinite_sim()
    genetic(25, _TANKY, 7)

