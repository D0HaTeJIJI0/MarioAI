import retro
import numpy as np  # For image-matrix/vector operations
import cv2  # For image reduction
import neat
import pickle
import glob, os
import re

env = retro.make(game='SuperMarioBros-Nes', state='Level1-1', record=True)
owned_image = []


def eval_genome(genome, config):
    ob = env.reset()  # First image
    # random_action = env.action_spac1e.sample()
    inx, iny, inc = env.observation_space.shape  # inc = color
    # image reduction for faster processing
    inx = int(inx / 8)
    iny = int(iny / 8)
    # 20 Networks
    net = neat.nn.RecurrentNetwork.create(genome, config)
    current_max_fitness = 0
    fitness_current = 0
    frame = 0
    counter = 0

    done = False

    while not done:
        env.render()  # Optional
        frame += 1

        ob = cv2.resize(ob, (inx, iny))  # Ob is the current frame
        ob = cv2.cvtColor(ob, cv2.COLOR_BGR2GRAY)  # Colors are not important for learning
        ob = np.reshape(ob, (inx, iny))

        owned_image = np.ndarray.flatten(ob)
        neuralnet_output = net.activate(owned_image)  # Give an output for current frame from neural network
        ob, rew, done, info = env.step(neuralnet_output)  # Try given output from network in the game

        fitness_current += rew
        if fitness_current > current_max_fitness:
            current_max_fitness = fitness_current
            counter = 0
        else:
            counter += 1
            # count the frames until it successful

        # Train mario for max 250 frames
        if done or counter == 250:
            done = True
            # print(genome_id, fitness_current)

        genome.fitness = fitness_current
    return genome.fitness


def eval_genomes(genomes, config):
    for genome_id, genome in genomes:

        ob = env.reset()  # First image
        # random_action = env.action_spac1e.sample()
        inx, iny, inc = env.observation_space.shape  # inc = color
        # image reduction for faster processing
        inx = int(inx / 8)
        iny = int(iny / 8)
        # 20 Networks
        net = neat.nn.RecurrentNetwork.create(genome, config)
        current_max_fitness = 0
        fitness_current = 0
        frame = 0
        counter = 0

        done = False

        while not done:
            env.render()  # Optional
            frame += 1

            ob = cv2.resize(ob, (inx, iny))  # Ob is the current frame
            ob = cv2.cvtColor(ob, cv2.COLOR_BGR2GRAY)  # Colors are not important for learning
            ob = np.reshape(ob, (inx, iny))

            owned_image = np.ndarray.flatten(ob)
            neuralnet_output = net.activate(owned_image)  # Give an output for current frame from neural network
            ob, rew, done, info = env.step(neuralnet_output)  # Try given output from network in the game

            fitness_current += rew
            if fitness_current > current_max_fitness:
                current_max_fitness = fitness_current
                counter = 0
            else:
                counter += 1
                # count the frames until it successful

            # Train mario for max 250 frames
            if done or counter == 250:
                done = True
                print(genome_id, fitness_current)

            genome.fitness = fitness_current

def run(config_file, checkpoints_folder):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     config_file)

    # filepath_list = os.chdir("d:\\University\\diploma\\Mario\\MarioAI\\script\\NN\\com\\Neat\\checkpoints")
    

    file_list = glob.glob(os.path.join(checkpoints_folder, "neat-checkpoint-*"))
    p = None
    if (len(file_list) != 0):
        file_list.sort(key=lambda filename: int(re.findall('\d+', filename)[0]), reverse=True)
        print(file_list[0])
        p = neat.Checkpointer.restore_checkpoint(file_list[0])
    else:
        p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # Save the process after each 10 frames
    p.add_reporter(neat.Checkpointer(10))
    pe = neat.ParallelEvaluator(5, eval_genome)

    winner = p.run(pe.evaluate)
    # winner = p.run(eval_genomes)

    with open('winner.pkl', 'wb') as output:
        pickle.dump(winner, output, 1)

if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    os.chdir(os.path.dirname(__file__))
    # local_dir = 
    # config_path = os.path.join(local_dir, 'config\\config-feedforward')
    run('config\\config-feedforward', 'checkpoints')