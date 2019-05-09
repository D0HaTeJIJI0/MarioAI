from time import sleep

import retro

env = retro.make(game='SuperMarioBros-Nes', state='Level1-1', record=True)

env.reset()
env.render()
sleep(3)
env.reset()
env.render()
sleep(3)
env.reset()