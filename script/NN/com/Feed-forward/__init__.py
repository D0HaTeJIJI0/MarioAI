import retro
import numpy as np  # For image-matrix/vector operations
import cv2  # For image reduction
import neat
import pickle
import glob, os
import re
import time
import threading

env = retro.make(game='SuperMarioBros-Nes', state='Level1-1', record=True)
owned_image = []
done = False

def extractLastNumberFromFilename(file_path):
    filename = os.path.splitext(file_path)[0]
    last_number = re.findall('\d+', filename)[-1]
    return int(last_number)


def clear_checkpoints(checkpoint_path):
    while not done:
        checkpoint_file_list = glob.glob(os.path.join(checkpoint_path, "neat-checkpoint-*"))
        bk_file_list = glob.glob(os.path.join(checkpoint_path, "*.bk2"))
        last_checkpoint = max(checkpoint_file_list, key=extractLastNumberFromFilename)
        last_bk = max(bk_file_list, key=extractLastNumberFromFilename)
        try:
            for file_path in checkpoint_file_list:
                if not file_path.endswith(last_checkpoint):
                    os.remove(os.path.join(checkpoint_path, file_path))
            for file_path in bk_file_list:
                if not file_path.endswith(last_bk):
                    os.remove(os.path.join(checkpoint_path, file_path))
        except:
            print("Error while deleting file : ", last_checkpoint)
        time.sleep(10)


def eval_genome_parallel(genome, config):
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


def eval_genomes_sequential(genomes, config):
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
    

def run(config_file_path, checkpoints_folder):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     config_file_path)
    
    # Change dir to save checkpoints in suitable folder
    os.chdir(checkpoints_folder)
    # Clear checkpoint folder each 10 seconds
    threading.Thread(target = clear_checkpoints, args = os.curdir).start()
    file_list = glob.glob(os.path.join(os.curdir, "neat-checkpoint-*"))
    p = None
    if (len(file_list) != 0):
        last_checkpoint = max(file_list, key=extractLastNumberFromFilename)
        print(last_checkpoint)
        p = neat.Checkpointer.restore_checkpoint(last_checkpoint)
    else:
        p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # Save the process after each 10 frames
    p.add_reporter(neat.Checkpointer(10))
    pe = neat.ParallelEvaluator(5, eval_genome_parallel)

    # Parallel run
    winner = p.run(pe.evaluate)
    done = True

    # Sequential run
    # winner = p.run(eval_genomes_sequential)

    path_to_winner_file = os.path.join(os.path.dirname(__file__), 'winner.pkl')
    with open(path_to_winner_file, 'wb') as output:
        pickle.dump(winner, output, 1)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    os.chdir(os.path.dirname(__file__))
    run('config\\config-feedforward', 'checkpoints')