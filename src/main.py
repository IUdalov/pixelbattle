from render import Render
from world import *


_TANKY = np.array([
    [PixelType.SHELL] * 5 + [PixelType.GUN] + [PixelType.SHELL] * 5,
    [PixelType.SHELL] * 5 + [PixelType.ENGINE] + [PixelType.SHELL] * 5,
    [PixelType.SHELL] * 5 +  [PixelType.GUN] + [PixelType.SHELL] * 5
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


def easy_infinite_sim():
    width = 100
    height = 50
    block_size = 15
    world = gen_world(width, height, [_TANKY, _EDGY, _GOOFY], [UserActor(), DummyActor(), Actor(),])
    render = Render((width * block_size, height * block_size))
    while render.ok():
        world = next_state(world)
        if not world.has_next_state():
            world = gen_world(width, height, [_TANKY, _EDGY, _GOOFY], [UserActor(), DummyActor(), Actor(),])
        render.draw(world)
        render.delay()

    render.stop()


if __name__ == "__main__":
    easy_infinite_sim()
