
import random
import copy
import os
import pybrain.rl.environments.twoplayergames
import sys, time
from pybrain.rl.environments.episodic import EpisodicTask
from inspect import isclass
from pybrain.utilities import  Named
from pybrain.rl.environments.twoplayergames.twoplayergame import TwoPlayerGame
from pybrain.structure.modules.module import Module
from pybrain.utilities import drawGibbs
from pybrain.optimization import ES
from pybrain.utilities import storeCallResults
from pybrain.structure.evolvables.cheaplycopiable import CheaplyCopiable
from pybrain.rl.agents.agent import Agent
from pybrain import SharedFullConnection, MotherConnection, MDLSTMLayer, IdentityConnection
from pybrain import ModuleMesh, LinearLayer, TanhLayer, SigmoidLayer
from pybrain.structure.networks import BorderSwipingNetwork
from pybrain.rl.learners.valuebased import ActionValueTable
from pybrain.rl.agents import LearningAgent, OptimizationAgent
from pybrain.rl.learners import Q, SARSA
from pybrain.rl.experiments import EpisodicExperiment
from pybrain.rl.environments import Task
from pybrain.rl.experiments.tournament import Tournament

from scipy import zeros, ones
import pylab

# ----------------------
# ENVIRONMENT CLASS
# ----------------------

class GoGame(TwoPlayerGame):
    """Go Game using simplified rules for Ko and for endgame territory calculation"""
    EMPTY = 0
    BLACK = 1
    WHITE = -1
    BLACK_SAFE = 2
    WHITE_SAFE = -2
    DISPUTED_TERRITORY = 5
    
    def __init__(self, size = 5, komi = 0.5):
        self.size = size
        self.komi = komi
        self.reset()
        
    @property
    def startcolor(self):
        return self.BLACK
    @property
    def spaces(self):
        return self.size ** 2
        
    @property
    def indim(self):
        return self.spaces + 1
        
    @property
    def outdim(self):
        return self.indim * 2
        
    def reset(self):
        TwoPlayerGame.reset(self)
        self.board = []
        for i in range(self.spaces):
            self.board.append(0)
        self.winner = None
        self.blackScore = 0
        self.whiteScore = 0
        self.passflag = False

    def getSensors(self):
        return self.board
    def getBoardArray(self):
        output = []
        for i in self.board:
            if i == self.BLACK:
                output += [1, 0]
            elif i == self.WHITE:
                output += [0, 1]
            else:
                output += [0, 0]
        output += [0, 0]
        return output
    def playGame(self, p1, p2):
        gameover = False
        currplayer = 0 if p1.colour == self.BLACK else 1
        players = [p1, p2]
        p1.game = self
        p2.game = self
        while not self.gameOver:
            player = players[currplayer]
            if self.performAction(player.getAction()):
                currplayer = 1 - currplayer
    
    def doMove(self, colour, move):
        #print(self.board)
        if move == self.spaces:
            self.handlePass()
            return True
        if not self.isLegal(colour, move):
            return False
        else:
            scored, newboard = self.checkCaptures(colour, move)
            self.board = newboard
            if colour == self.BLACK:
                self.blackScore += scored
            else:
                self.whiteScore += scored
            self.passflag = False
            return True
    
    def handlePass(self):
        if self.passflag:
            self.calculateTerritory()
        else:
            self.passflag = True
    
    def calculateTerritory(self):
        flag = True
        while flag:
            flag = False
            for i in range(self.spaces):
                if self.board[i] == self.EMPTY:
                    if (i % self.size != self.size - 1):
                        if (self.board[i + 1] == self.BLACK or self.board[i + 1] == self.BLACK_SAFE):
                            self.board[i] = self.BLACK_SAFE
                            flag = True
                        if (self.board[i + 1] == self.WHITE or self.board[i + 1] == self.WHITE_SAFE):
                            self.board[i] = self.WHITE_SAFE
                            flag = True
                    if (i % self.size != 0):
                        if (self.board[i - 1] == self.BLACK or self.board[i - 1] == self.BLACK_SAFE):
                            self.board[i] = self.BLACK_SAFE
                            flag = True
                        if (self.board[i - 1] == self.WHITE or self.board[i - 1] == self.WHITE_SAFE):
                            self.board[i] = self.WHITE_SAFE
                            flag = True
                    if (i + self.size < self.spaces):
                        if (self.board[i + self.size] == self.BLACK or self.board[i + self.size] == self.BLACK_SAFE):
                            self.board[i] = self.BLACK_SAFE
                            flag = True
                        if (self.board[i + self.size] == self.WHITE or self.board[i + self.size] == self.WHITE_SAFE):
                            self.board[i] = self.WHITE_SAFE
                            flag = True
                    if (i - self.size >= 0):
                        if (self.board[i - self.size] == self.BLACK or self.board[i - self.size] == self.BLACK_SAFE):
                            self.board[i] = self.BLACK_SAFE
                            flag = True
                        if (self.board[i - self.size] == self.WHITE or self.board[i - self.size] == self.WHITE_SAFE):
                            self.board[i] = self.WHITE_SAFE
                            flag = True
                elif self.board[i] == self.BLACK_SAFE:
                    if (i % self.size != self.size - 1):
                        if (self.board[i + 1] == self.WHITE or self.board[i + 1] == self.WHITE_SAFE or self.board[i + 1] == self.DISPUTED_TERRITORY):
                            self.board[i] = self.DISPUTED_TERRITORY
                            flag = True
                    if (i % self.size != 0):
                        if (self.board[i - 1] == self.WHITE or self.board[i - 1] == self.WHITE_SAFE or self.board[i - 1] == self.DISPUTED_TERRITORY):
                            self.board[i] = self.DISPUTED_TERRITORY
                            flag = True
                    if (i + self.size < self.spaces):
                        if (self.board[i + self.size] == self.WHITE or self.board[i + self.size] == self.WHITE_SAFE or self.board[i + self.size] == self.DISPUTED_TERRITORY):
                            self.board[i] = self.DISPUTED_TERRITORY
                            flag = True
                    if (i - self.size >= 0):
                        if (self.board[i - self.size] == self.WHITE or self.board[i - self.size] == self.WHITE_SAFE or self.board[i - self.size] == self.DISPUTED_TERRITORY):
                            self.board[i] = self.DISPUTED_TERRITORY
                            flag = True
                elif self.board[i] == self.WHITE_SAFE:
                    if (i % self.size != self.size - 1):
                        if (self.board[i + 1] == self.BLACK or self.board[i + 1] == self.BLACK_SAFE or self.board[i + 1] == self.DISPUTED_TERRITORY):
                            self.board[i] = self.DISPUTED_TERRITORY
                            flag = True
                    if (i % self.size != 0):
                        if (self.board[i - 1] == self.BLACK or self.board[i - 1] == self.BLACK_SAFE or self.board[i - 1] == self.DISPUTED_TERRITORY):
                            self.board[i] = self.DISPUTED_TERRITORY
                            flag = True
                    if (i + self.size < self.spaces):
                        if (self.board[i + self.size] == self.BLACK or self.board[i + self.size] == self.BLACK_SAFE or self.board[i + self.size] == self.DISPUTED_TERRITORY):
                            self.board[i] = self.DISPUTED_TERRITORY
                            flag = True
                    if (i - self.size >= 0):
                        if (self.board[i - self.size] == self.BLACK or self.board[i - self.size] == self.BLACK_SAFE or self.board[i - self.size] == self.DISPUTED_TERRITORY):
                            self.board[i] = self.DISPUTED_TERRITORY
                            flag = True
        for i in range(self.spaces):
            if self.board[i] == self.BLACK_SAFE:
                self.blackScore += 1
            if self.board[i] == self.WHITE_SAFE:
                self.whiteScore += 1
        self.winner = self.BLACK if self.blackScore > self.whiteScore + self.komi else self.WHITE
    def checkCaptures(self, colour, move):
        flag = True
        tempboard = copy.copy(self.board)
        tempboard[move] = colour
        while flag:
            flag = False
            for i in range(self.spaces):
                if tempboard[i] == self.BLACK:
                    if (i % self.size != self.size - 1):
                        if (tempboard[i + 1] == self.BLACK_SAFE or tempboard[i + 1] == self.EMPTY):
                            tempboard[i] = self.BLACK_SAFE
                            flag = True
                    if (i % self.size != 0):
                        if (tempboard[i - 1] == self.BLACK_SAFE or tempboard[i - 1] == self.EMPTY):
                            tempboard[i] = self.BLACK_SAFE
                            flag = True
                    if (i + self.size < self.spaces):
                        if (tempboard[i + self.size] == self.BLACK_SAFE or tempboard[i + self.size] == self.EMPTY):
                            tempboard[i] = self.BLACK_SAFE
                            flag = True
                    if (i - self.size >= 0):
                        if (tempboard[i - self.size] == self.BLACK_SAFE or tempboard[i - self.size] == self.EMPTY):
                            tempboard[i] = self.BLACK_SAFE
                            flag = True
                if tempboard[i] == self.WHITE:
                    if (i % self.size != self.size - 1):
                        if (tempboard[i + 1] == self.WHITE_SAFE or tempboard[i + 1] == self.EMPTY):
                            tempboard[i] = self.WHITE_SAFE
                            flag = True
                    if (i % self.size != 0):
                        if (tempboard[i - 1] == self.WHITE_SAFE or tempboard[i - 1] == self.EMPTY):
                            tempboard[i] = self.WHITE_SAFE
                            flag = True
                    if (i + self.size < self.spaces):
                        if (tempboard[i + self.size] == self.WHITE_SAFE or tempboard[i + self.size] == self.EMPTY):
                            tempboard[i] = self.WHITE_SAFE
                            flag = True
                    if (i - self.size >= 0):
                        if (tempboard[i - self.size] == self.WHITE_SAFE or tempboard[i - self.size] == self.EMPTY):
                            tempboard[i] = self.WHITE_SAFE
                            flag = True
        scored = 0
        capflag = False
        for i in range(self.spaces):
            if tempboard[i] == -colour * 2:
                tempboard[i] = -colour
            elif tempboard[i] == -colour:
                tempboard[i] = 0
                scored += 1
            elif tempboard[i] == colour*2:
                tempboard[i] = colour
            elif tempboard[i] == colour:
                capflag = True
        if capflag and scored == 0:
            return -1, []
        else:
            return scored, tempboard
    def isLegal(self, colour, move):
        if move < 0:
            return False
        if move > self.spaces:
            return False
        if move == self.spaces:
            return True
        if self.board[move] != self.EMPTY:
            return False
        flag = True
        tempboard = copy.copy(self.board)
        tempboard[move] = colour
        while flag:
            flag = False
            for i in range(self.spaces):
                if tempboard[i] == self.BLACK:
                    if (i % self.size != self.size - 1):
                        if (tempboard[i + 1] == self.BLACK_SAFE or tempboard[i + 1] == self.EMPTY):
                            tempboard[i] = self.BLACK_SAFE
                            flag = True
                    if (i % self.size != 0):
                        if (tempboard[i - 1] == self.BLACK_SAFE or tempboard[i - 1] == self.EMPTY):
                            tempboard[i] = self.BLACK_SAFE
                            flag = True
                    if (i + self.size < self.spaces):
                        if (tempboard[i + self.size] == self.BLACK_SAFE or tempboard[i + self.size] == self.EMPTY):
                            tempboard[i] = self.BLACK_SAFE
                            flag = True
                    if (i - self.size >= 0):
                        if (tempboard[i - self.size] == self.BLACK_SAFE or tempboard[i - self.size] == self.EMPTY):
                            tempboard[i] = self.BLACK_SAFE
                            flag = True
                if tempboard[i] == self.WHITE:
                    if (i % self.size != self.size - 1):
                        if (tempboard[i + 1] == self.WHITE_SAFE or tempboard[i + 1] == self.EMPTY):
                            tempboard[i] = self.WHITE_SAFE
                            flag = True
                    if (i % self.size != 0):
                        if (tempboard[i - 1] == self.WHITE_SAFE or tempboard[i - 1] == self.EMPTY):
                            tempboard[i] = self.WHITE_SAFE
                            flag = True
                    if (i + self.size < self.spaces):
                        if (tempboard[i + self.size] == self.WHITE_SAFE or tempboard[i + self.size] == self.EMPTY):
                            tempboard[i] = self.WHITE_SAFE
                            flag = True
                    if (i - self.size >= 0):
                        if (tempboard[i - self.size] == self.WHITE_SAFE or tempboard[i - self.size] == self.EMPTY):
                            tempboard[i] = self.WHITE_SAFE
                            flag = True
        scored = 0
        capflag = False
        for i in range(self.spaces):
            if tempboard[i] == -colour * 2:
                tempboard[i] = -colour
            elif tempboard[i] == -colour:
                tempboard[i] = 0
                scored += 1
            elif tempboard[i] == colour*2:
                tempboard[i] = colour
            elif tempboard[i] == colour:
                capflag = True
        if capflag and scored == 0:
            return False
        else:
            return True
    def getLegals(self, colour):
        output = []
        for i in range(self.spaces + 1):
            if self.isLegal(colour, i):
                output.append(i)
        return output
    def gameOver(self):
        return self.winner != None

# --------------------------
# PLAYER CLASSES
# --------------------------


class GoPlayer(Agent):
    def __init__(self, game, color = GoGame.BLACK, **args):
        self.game = game
        self.color = color
        #self.setArgs(**args)
class RandomGoPlayer(GoPlayer):
    def getAction(self):
        return [self.color, random.choice(self.game.getLegals(self.color))]
    
class ModuleDecidingPlayer(RandomGoPlayer):
    """ A Go player that plays according to the rules, but choosing its moves
    according to the output of a module that takes as input the current state of the board. """
    greedySelection = False
    # if the selection is not greedy, use Gibbs-sampling with this temperature
    temperature = 1.
    def __init__(self, module, *args, **kwargs):
        #RandomGoPlayer.__init__(self, *args, **kwargs)
        self.module = module
        if self.greedySelection:
            self.temperature = 0.
    def getAction(self):
        """ get suggested action, return them if they are legal, otherwise choose randomly. """
        ba = self.game.getBoardArray()
        # network is given inputs with self/other as input, not black/white
        if self.color != GoGame.BLACK:
            # invert values
            tmp = zeros(len(ba))
            tmp[:len(ba)-1:2] = ba[1:len(ba):2]
            tmp[1:len(ba):2] = ba[:len(ba)-1:2]
            ba = tmp
        self.module.reset()
        return [self.color, self._legalizeIt(self.module.activate(ba))]
    def newEpisode(self):
        self.module.reset()
    def _legalizeIt(self, a):
        """ draw index from an array of values, filtering out illegal moves. """
        if not min(a) >= 0:
            #print a
            #print min(a)
            #print self.module.params
            #print self.module.inputbuffer
            #print self.module.outputbuffer
            raise Exception('Non-positive value in array?')
        legals = self.game.getLegals(self.color)
        vals = ones(len(a))*(-100)*(1+self.temperature)
        for i in legals:
            vals[i] = a[i]
        drawn = drawGibbs(vals, self.temperature)
        assert drawn in legals
        return drawn
    def integrateObservation(self, obs = None):
        pass

# ----------------------
# TASK CLASS
# ----------------------

class GoGameTask(EpisodicTask, Named):
    """ The task of winning the maximal number of Go games against a fixed opponent. """
    # first game, opponent is black
    opponentStart = True
    # on subsequent games, starting players are alternating
    alternateStarting = False
    # numerical reward value attributed to winning
    winnerReward = 1.
    # average over some games for evaluations
    averageOverGames = 25
    noisy = True
    def __init__(self, size, opponent = None, **args):
        EpisodicTask.__init__(self, GoGame(size))
        self.setArgs(**args)
        if opponent == None:
            opponent = RandomGoPlayer(self.env)
        elif isclass(opponent):
            # assume the agent can be initialized without arguments then.
            opponent = opponent(self.env)
        else:
            opponent.game = self.env
        if not self.opponentStart:
            opponent.color = GoGame.WHITE
        self.opponent = opponent
        self.reset()
    def reset(self):
        self.switched = False
        EpisodicTask.reset(self)
        if self.opponent.color == GoGame.BLACK:
            # first move by opponent
            EpisodicTask.performAction(self, self.opponent.getAction())
    def isFinished(self):
        res = self.env.gameOver()
        if res and self.alternateStarting and not self.switched:
            # alternate starting player
            self.opponent.color *= -1
            self.switched = True
        return res
    def getReward(self):
        """ Final positive reward for winner, negative for loser. """
        if self.isFinished():
            win = (self.env.winner != self.opponent.color)
            res = self.winnerReward
            if not win:
                res *= -1
            if self.alternateStarting and self.switched:
                # opponent color has been inverted after the game!
                res *= -1
            return res
        else:
            return 0
    def performAction(self, action):
        EpisodicTask.performAction(self, action)
        if not self.isFinished():
            EpisodicTask.performAction(self, self.opponent.getAction())
    def f(self, x):
        """ If a module is given, wrap it into a ModuleDecidingAgent before evaluating it.
        Also, if applicable, average the result over multiple games. """
        if isinstance(x, Module):
            agent = ModuleDecidingPlayer(x, self.env, greedySelection = True)
        elif isinstance(x, GoPlayer):
            agent = x
        else:
            raise NotImplementedError('Missing implementation for '+x.__class__.__name__+' evaluation')
        res = 0
        agent.game = self.env
        self.opponent.game = self.env
        for _ in range(self.averageOverGames):
            agent.color = -self.opponent.color
            x = EpisodicTask.f(self, agent)
            res += x
        return res / float(self.averageOverGames)

# -----------------------------
# ACTION VALUE TABLE CLASS
# -----------------------------

class GoActionValueTable(Module):
    def __init__(self, numStates, numActions, name=None):
        Module.__init__(self, 25, 1, name)
        self.numRows = numStates
        self.numColumns = numActions
        self.actionvalues = {}
            

    @property
    def numActions(self):
        return self.numColumns

    def _forwardImplementation(self, inbuf, outbuf):
        """ Take a vector of length 1 (the state coordinate) and return
            the action with the maximum value over all actions for this state.
        """
        outbuf[0] = self.getMaxAction(inbuf[0])

    def getMaxAction(self, state):
        """ Return the action with the maximal value for the given state. """
        self._initState(state)
        maxes = []
        statelist = self.actionvalues[state]
        max = -1.0
        for i in range(self.numColumns):
            if statelist[i] > max:
                maxes = []
                max = statelist[i]
            if statelist[i] == max:
                maxes.append(i)
        action = random.choice(maxes)
        return action

    def getActionValues(self, state):
        self._initState(state)
        return self.actionvalues[state]

    def initialize(self, value=0.0):
        self.basestate = []
        for i in range(self.numColumns):
            self.basestate.append(value)
    
    def _initState(self, state):
        if not state in self.actionvalues:
            self.actionvalues[state] = copy.copy(self.basestate)

# -----------------------------
# PROVING IT WORKS HOPEFULLY
# -----------------------------


pylab.gray()
pylab.ion()

size = 5

#"""
task = GoGameTask(size, averageOverGames = 200, opponent = RandomGoPlayer)

# keep track of evaluations for plotting
res = storeCallResults(task)

from pybrain.tools.shortcuts import buildNetwork
from pybrain import SigmoidLayer
net = buildNetwork(task.outdim, task.indim, outclass = SigmoidLayer)

net = CheaplyCopiable(net)
print net.name, 'has', net.paramdim, 'trainable parameters.'

learner = ES(task, net, mu = 5, lambada = 5,
             verbose = True, evaluatorIsNoisy = True,
             maxEvaluations = 50)
newnet, f = learner.learn()

print newnet
print f
print learner
"""
task = GoGameTask(size, averageOverGames = 2000, opponent = RandomGoPlayer)

# keep track of evaluations for plotting
res = storeCallResults(task)

net2 = buildNetwork(task.outdim, task.indim, outclass = SigmoidLayer)

net2 = CheaplyCopiable(net)
print net.name, 'has', net.paramdim, 'trainable parameters.'

learner = ES(task, net2, mu = 5, lambada = 5,
             verbose = True, evaluatorIsNoisy = True,
             maxEvaluations = 50)
newnet2, f = learner.learn()

print newnet
print f
print learner"""

game = GoGame(5)
randAgent = RandomGoPlayer(game, name= "Random")
netAgent = ModuleDecidingPlayer(newnet, game, name = 'net')
netAgentGreedy = ModuleDecidingPlayer(newnet, game, name = 'greedy', greedySelection = True)"""
net2Agent = ModuleDecidingPlayer(newnet2, game, name = 'net')
net2AgentGreedy = ModuleDecidingPlayer(newnet2, game, name = 'greedy', greedySelection = True)"""

agents = [randAgent, netAgent, netAgentGreedy""", net2Agent, net2AgentGreedy"""]

print
print 'Starting tournament...'
tourn = Tournament(game, agents)
tourn.organize(50)
print tourn



"""
task = GoGameTask(size, averageOverGames = 200, opponent = RandomGoPlayer)

controller = GoActionValueTable(3**25 * 2, 26)
#Initialize at 1 to encourage exploration
controller.initialize(1.)

learner = Q(task)
agent = LearningAgent(controller, learner)
experiment = EpisodicExperiment(task, agent)

i=0
while True:
    i += 1
    print(str(i) + "x")
    experiment.doEpisodes(2)
    agent.learn(2)
    agent.reset()

"""
