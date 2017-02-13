
import random
import copy
import os
import pybrain.rl.environments.twoplayergames
from pybrain.rl.environments.episodic import EpisodicTask
from inspect import isclass
from pybrain.utilities import  Named
from pybrain.rl.environments.twoplayergames import CaptureGame
from pybrain.structure.modules.module import Module
from pybrain.utilities import drawGibbs

from scipy import zeros, ones

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
    def spaces(self):
        return self.size ** 2
        
    def reset(self):
        TwoPlayerGame.reset(self)
        self.board = []
        for i in range(self.spaces):
            self.board.append = 0
        self.winner = None
        self.blackScore = 0
        self.whiteScore = 0

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
    def playGame(self, p1, p2):
        gameover = False
        currplayer = 0 if p1.colour = selfBLACK else 1
        players = [p1, p2]
        p1.game = self
        p2.game = self
        while not self.gameOver:
            player = players[currplayer]
            if self.performAction(player.getAction()):
                currplayer = 1 - currplayer
    
    def doMove(self, colour, move):
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
                        if (self.board[i - 1] == self.BLACK or self.board[i - 1] == BLACK_SAFE):
                            self.board[i] = BLACK_SAFE
                            flag = True
                        if (self.board[i - 1] == self.WHITE or self.board[i - 1] == self.WHITE_SAFE):
                            self.board[i] = self.WHITE_SAFE
                            flag = True
                    if (i + self.size < self.spaces):
                        if (self.board[i + self.size] == self.BLACK or self.board[i + self.size] == BLACK_SAFE):
                            self.board[i] = BLACK_SAFE
                            flag = True
                        if (self.board[i + self.size] == self.WHITE or self.board[i + self.size] == self.WHITE_SAFE):
                            self.board[i] = self.WHITE_SAFE
                            flag = True
                    if (i - self.size >= 0):
                        if (self.board[i - self.size] == self.BLACK or self.board[i - self.size] == BLACK_SAFE):
                            self.board[i] = BLACK_SAFE
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
        for i in self.spaces:
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
        for i in self.spaces:
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
        for i in self.spaces:
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


class GoPlayer():
    def __init__(self, game, color = GoGame.BLACK, **args):
        self.game = game
        self.color = color
        self.setArgs(**args)
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
        RandomGoPlayer.__init__(self, *args, **kwargs)
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
            print a
            print min(a)
            print self.module.params
            print self.module.inputbuffer
            print self.module.outputbuffer
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
    
