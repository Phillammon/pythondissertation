
from __future__ import print_function

import random
import copy
import os
import sys, time
import cPickle
from pybrain.utilities import drawGibbs
from scipy import zeros, ones


learning = 0.2
discount = 0.9

# ----------------------
# ENVIRONMENT CLASS
# ----------------------

class GoGame():
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
    def startcolour(self):
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
        self.board = [0]*self.spaces
        self.winner = None
        self.blackScore = 0
        self.whiteScore = 0
        self.blackTerritory = 0
        self.whiteTerritory = 0
        self.passflag = False
        self.lastCapture = 0
    def getSensors(self):
        output = ""
        for element in self.board:
            output = output + str(element+self.BLACK)
        if self.passflag:
            output = output + "1"
        else:
            output = output + "0"
        return output
    def getBoardArray(self):
        output = []
        for i in self.board:
            if i == self.BLACK:
                output += [1, 0]
            elif i == self.WHITE:
                output += [0, 1]
            else:
                output += [0, 0]
        if self.passflag:
            output += [1, 1]
        else:
            output += [0, 0]
        return output
    def playGame(self, p1, p2):
        currplayer = 0 if p1.colour == self.BLACK else 1
        players = [p1, p2]
        p1.game = self
        p2.game = self
        while not self.gameOver():
            player = players[currplayer]
            if self.doMove(player.getAction()):
                currplayer = 1 - currplayer
    def doMove(self, args):
        colour = args[0]
        move = args[1]
        if move == self.spaces:
            self.handlePass()
            self.lastCapture = 0
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
            self.lastCapture = scored
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
                self.blackTerritory += 1
            if self.board[i] == self.WHITE_SAFE:
                self.whiteTerritory += 1
        if self.blackScore + self.blackTerritory > self.whiteScore + self.whiteTerritory + self.komi:
            self.winner = self.BLACK
        else:
            self.winner = self.WHITE
            """
        print("Game over. Black scores " + str(self.blackScore) + ", White scores " + str(self.whiteScore) + " plus a komi of " + str(self.komi) + ".")
        if self.winner == self.BLACK:
            print("Black wins")
        else:
            print("White wins")
            """
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
    
    
### PLAYERS ###

class GoPlayer():
    def __init__(self, game, colour = GoGame.BLACK):
        self.game = game
        self.colour = colour
class RandomGoPlayer(GoPlayer):
    def getAction(self):
        return [self.colour, random.choice(self.game.getLegals(self.colour))]
class ModuleGoPlayer(GoPlayer):
    def __init__(self, game, module, colour = GoGame.BLACK, greedy = False):
        self.temperature = 1.
        self.game = game
        self.colour = colour
        self.module = module
        self.greedy = greedy
        self.moves = []
        if self.greedy:
            self.temperature = 0.
    def getAction(self):
        legals = self.game.getLegals(self.colour)
        a = self.module.activate(self.game.getSensors())
        """
        vals = ones(len(a))*(-100)*(1+self.temperature)
        for i in legals:
            vals[i] = a[i]
        drawn = drawGibbs(vals, self.temperature)
        """
        vals = zeros(len(a))
        for i in legals:
            vals[i] = a[i]
        drawn = self.weightedPick(vals)
        
        #"""
        assert drawn in legals
        self.moves.append([self.game.getSensors(), drawn, self.game.lastCapture])
        return self.colour, drawn
    def weightedPick(self, li):
        d = {i: li[i] for i in range(len(li))}
        r = random.uniform(0, sum(d.itervalues()))
        s = 0.0
        for k, w in d.iteritems():
            s += w
            if r < s: return k
        return k
    
### MODULES ###
        
class Module():
    def __init__(self, outsize):
        self.size = outsize
    def activate(self, state):
        return [0]*self.size

class GoActionValueTable(Module):
    def __init__(self, outsize):
        self.numColumns = outsize
        self.actionvalues = {}
        self.initialize(0.)
            
    @property
    def numActions(self):
        return self.numColumns

    def getActionValues(self, state):
        self._initState(state)
        return self.actionvalues[state]
        
    def activate(self, state):
        statelist = self.getActionValues(state)
        max = -1.
        for i in range(self.numColumns):
            if statelist[i] > max:
                maxes = []
                max = statelist[i]
        return [element / max for element in statelist]

    def initialize(self, value=0.0):
        self.basestate = []
        for i in range(self.numColumns):
            self.basestate.append(value)
    
    def _initState(self, state):
        if not state in self.actionvalues:
            self.actionvalues[state] = copy.copy(self.basestate)
            
    def acceptReward(self, rewardlist):
        rewards = []
        for i in range(len(rewardlist)-1, -1, -1):
            element = rewardlist[i]
            curr = self.actionvalues[element[0]][element[1]]
            r = 0.
            rewards.insert(0, element[2])
            for i in range(len(rewards)):
                r = r + rewards[i] * pow(discount, i)
            self.actionvalues[element[0]][element[1]] = curr + learning * (r - curr)
        
        
        
def basic():
    size = 3
    module = GoActionValueTable(size*size + 1)
    module.initialize(1.)
    scores = []
    for i in range(100000):
        task = GoGame(size)
        if i % 2 == 0:
            p1 = ModuleGoPlayer(task, module, colour = GoGame.BLACK, greedy = False)
            p2 = RandomGoPlayer(task, colour = GoGame.WHITE)
        else:
            p1 = ModuleGoPlayer(task, module, colour = GoGame.WHITE, greedy = False)
            p2 = RandomGoPlayer(task, colour = GoGame.BLACK)
        task.playGame(p1, p2)
        reward = 0
        if (task.winner == p1.colour):
            reward = 1
        scores.append(reward)
        for element in p1.moves:
            element[2] = 0.
        if len(p1.moves) > 0:
            p1.moves[-1][2] = reward
            module.acceptReward(p1.moves)
    cPickle.dump( module.actionvalues, open( "actionvalue.table", "w" ) )
    f = open("winrate.txt", "w")
    for element in scores:
        print(str(element), file=f)
    f.close()
    
def scorebased():
    size = 3
    module = GoActionValueTable(size*size + 1)
    module.initialize(1.)
    scores = []
    for i in range(10000):
        task = GoGame(size)
        if i % 2 == 0:
            p1 = ModuleGoPlayer(task, module, colour = GoGame.BLACK, greedy = False)
            p2 = RandomGoPlayer(task, colour = GoGame.WHITE)
        else:
            p1 = ModuleGoPlayer(task, module, colour = GoGame.WHITE, greedy = False)
            p2 = RandomGoPlayer(task, colour = GoGame.BLACK)
        task.playGame(p1, p2)
        reward = 0
        if (task.winner == p1.colour):
            reward = 1
        scores.append(reward)
        for element in p1.moves:
            element[2] = 0.
        if len(p1.moves) > 0:
            if p1.colour == GoGame.WHITE:
                p1.moves[-1][2] = task.whiteTerritory
            else:
                p1.moves[-1][2] = task.blackTerritory
            module.acceptReward(p1.moves)
    cPickle.dump( module.actionvalues, open( "actionvalue.table", "w" ) )
    f = open("winrate.txt", "w")
    for element in scores:
        print(str(element), file=f)
    f.close()
scorebased()