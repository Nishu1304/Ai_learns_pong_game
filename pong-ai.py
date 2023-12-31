from game import Game
import pygame
import neat
import os
import pickle


class PongGame:
    def __init__(self, window, height, width):
        self.game = Game(window, width, height)
        self.left_paddle = self.game.left_paddle
        self.right_paddle = self.game.right_paddle
        self.ball = self.game.ball

    def ai_testing(self, genomes, config):
        net = neat.nn.FeedForwardNetwork.create(genomes, config)

        Fps = 60
        clock = pygame.time.Clock()
        run = True
        while run:

            clock.tick(Fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.game.move_paddle(True, True)
            if keys[pygame.K_s]:
                self.game.move_paddle(True, False)
            output = net.activate((self.right_paddle.y, self.ball.y, abs(self.right_paddle.x - self.ball.x)))
            decision = output.index(max(output))
            if decision == 0:
                pass
            elif decision == 1:
                self.game.move_paddle(False, True)
            else:
                self.game.move_paddle(False, False)

            self.game.loop()
            self.game.draw(True, False)
            pygame.display.update()

        pygame.quit()

    def train_ai(self, genome1, genome2, config):
        net1 = neat.nn.FeedForwardNetwork.create(genome1, config)
        net2 = neat.nn.FeedForwardNetwork.create(genome2, config)

        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()

            output1 = net1.activate((self.left_paddle.y, self.ball.y, abs(self.left_paddle.x - self.ball.x)))
            decision1 = output1.index(max(output1))
            if decision1 == 0:
                pass
            elif decision1 == 1:
                self.game.move_paddle(True, True)
            else:
                self.game.move_paddle(True, False)
            output2 = net2.activate((self.right_paddle.y, self.ball.y, abs(self.right_paddle.x - self.ball.x)))
            decision2 = output2.index(max(output2))
            if decision2 == 0:
                pass
            elif decision2 == 1:
                self.game.move_paddle(False, True)
            else:
                self.game.move_paddle(False, False)

            game_info = self.game.loop()
            self.game.draw(False, True)
            pygame.display.update()
            if game_info.left_score >= 1 or game_info.right_score >= 1 or game_info.left_hits > 50:
                self.calculate_fitness(genome1, genome2, game_info)
                break

    def calculate_fitness(self, genomes1, genomes2, game_info):
        genomes1.fitness += game_info.left_hits
        genomes2.fitness += game_info.right_hits


def eval_genomes(genomes, config):
    width, height = 700, 500
    window = pygame.display.set_mode((width, height))

    for i, (genomes_id1, genome1) in enumerate(genomes):
        if i == len(genomes) - 1:
            break
        genome1.fitness = 1
        for genome_id2, genome2 in genomes[i + 1:]:
            genome2.fitness = 0 if genome2.fitness is None else genome2.fitness
            game = PongGame(window, height, width)
            game.train_ai(genome1, genome2, config)


def run_neat(config):
    p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-3')
    # p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))

    winner = p.run(eval_genomes, 50)
    """Keep it 1 for testing against \ smaller generation if the best version is not trained yet"""
    with open("best.pickle", "wb") as f:
        pickle.dump(winner, f)


def test_ai(config):
    width, height = 700, 500
    window = pygame.display.set_mode((width, height))
    with open("best.pickle", "rb") as f:
        winner = pickle.load(f)
    game = PongGame(window, height, width)
    game.ai_testing(winner, config)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'configfile')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    # run_neat(config)"""initially this needs to run for almost 21 generation for ai to be trained till it reaches a 400 avrage score"""
    test_ai(config)"""This needs to be trained after the best.pickle file is loaded so that the best score till now is updated"""
