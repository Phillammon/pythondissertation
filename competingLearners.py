
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
    
    def __init__(self, size = 3, komi = 0.5):
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
    def getSensors(self, colour):
        output = ""
        for element in self.board:
            if colour == self.BLACK:
                output = output + str(element+self.BLACK)
            else:
                output = output + str(2 - (element+self.BLACK))
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
                player.logCapture(self.lastCapture)
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
    def logCapture(self, points):
        pass
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
        a = self.module.activate(self.game.getSensors(self.colour))
        """
        vals = ones(len(a))*(-100)*(1+self.temperature)
        for i in legals:
            vals[i] = a[i]
        drawn = drawGibbs(vals, self.temperature)
        """
        vals = zeros(len(a))
        for i in legals:
            vals[i] = a[i]
            if vals[i] < 0.:
                vals[i] = 0.
        if not self.greedy:
            drawn = self.weightedPick(vals)
        else:
            drawn = -1
            max = -1.
            for i in range(len(vals)):
                if vals[i] > max:
                    max = vals[i]
                    drawn = i
        #"""
        assert drawn in legals
        self.moves.append([self.game.getSensors(self.colour), drawn])
        return self.colour, drawn
    def weightedPick(self, li):
        d = {i: li[i] for i in range(len(li))}
        r = random.uniform(0, sum(d.itervalues()))
        s = 0.0
        for k, w in d.iteritems():
            s += w
            if r < s: return k
        return k
    def logCapture(self, points):
        self.moves[-1].append(points)
    
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
        min = 0
        for i in range(self.numColumns):
            if statelist[i] < min:
                min = statelist[i]
        statelist = [element + min for element in statelist]
        max = -1.
        for i in range(self.numColumns):
            if statelist[i] > max:
                max = statelist[i]
        if max != 0:
            return [element / max for element in statelist]
        else:
            return [element + 1 for element in statelist]

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
        
        
def pool():
    size = 3
    module_pool = []
    for i in range(10):
        module_pool.append( GoActionValueTable(size*size + 1))
        module_pool[i].initialize(1.)
    scores = []
    for i in range(100000):
        task = GoGame(size)
        p1 = ModuleGoPlayer(task, module_pool[i % 10], colour = GoGame.BLACK, greedy = False)
        p2 = ModuleGoPlayer(task, module_pool[(i // 10) % 10], colour = GoGame.WHITE, greedy = False)
        task.playGame(p1, p2)
        reward = 0
        if (task.winner == p1.colour):
            reward = 1.
        scores.append(reward)
        for element in p1.moves:
            element[2] = 0.
        for element in p2.moves:
            element[2] = 0.
        p1.moves[-1][2] = reward
        p2.moves[-1][2] = 1. - reward
        p1.module.acceptReward(p1.moves)
        p2.module.acceptReward(p2.moves)
    for i in range(10):
        cPickle.dump( module_pool[i].actionvalues, open( "actionvalue" + str(i) + ".table", "w" ) )
    f = open("winrate.txt", "w")
    for element in scores:
        print(str(element), file=f)
    f.close()
    
def selfrun(modifier = "", exp = 6, komi = 0.5):
    size = 3
    module = GoActionValueTable(size*size + 1)
    module.initialize(1.)
    scores = []
    results = []
    for i in range(pow(10, exp)):
        task = GoGame(size, komi)
        p1 = ModuleGoPlayer(task, module, colour = GoGame.BLACK, greedy = False)
        p2 = ModuleGoPlayer(task, module, colour = GoGame.WHITE, greedy = False)
        task.playGame(p1, p2)
        reward = 0.
        if (task.winner == None):
            print("FAILOUT")
            break
        if (task.winner == p1.colour):
            results.append("Black wins game " + str(i) + " in " + str(len(p1.moves) + len(p2.moves)) + " turns, with a score of " + str(task.blackTerritory + task.blackScore) + " to " + str(task.whiteTerritory + task.whiteScore + task.komi) + ".")
            reward = 1.
        else:
            results.append("White wins game " + str(i) + " in " + str(len(p1.moves) + len(p2.moves)) + " turns, with a score of " + str(task.blackTerritory + task.blackScore) + " to " + str(task.whiteTerritory + task.whiteScore + task.komi) + ".")
        scores.append(reward)
        for element in p1.moves:
            element[2] = 0.
        for element in p2.moves:
            element[2] = 0.
        p1.moves[-1][2] = reward
        p2.moves[-1][2] = 1. - reward
        module.acceptReward(p1.moves)
        module.acceptReward(p2.moves)
    cPickle.dump( module.actionvalues, open( "actionvalueself" + modifier + ".table", "w" ) )
    f = open("winrate" + modifier + ".txt", "w")
    for element in scores:
        print(str(element), file=f)
    f.close()
    f = open("results" + modifier + ".txt", "w")
    for element in results:
        print(str(element), file=f)
    f.close()
    return module

def selfmargin(modifier = "", exp = 6):
    size = 3
    module = GoActionValueTable(size*size + 1)
    module.initialize(1.)
    scores = []
    results = []
    for i in range(pow(10, exp)):
        task = GoGame(size)
        p1 = ModuleGoPlayer(task, module, colour = GoGame.BLACK, greedy = False)
        p2 = ModuleGoPlayer(task, module, colour = GoGame.WHITE, greedy = False)
        task.playGame(p1, p2)
        reward = 0.
        if (task.winner == None):
            print("FAILOUT")
            break
        if (task.winner == p1.colour):
            results.append("Black wins game " + str(i) + " in " + str(len(p1.moves) + len(p2.moves)) + " turns, with a score of " + str(task.blackTerritory + task.blackScore) + " to " + str(task.whiteTerritory + task.whiteScore + task.komi) + ".")
            reward = 1.
        else:
            results.append("White wins game " + str(i) + " in " + str(len(p1.moves) + len(p2.moves)) + " turns, with a score of " + str(task.blackTerritory + task.blackScore) + " to " + str(task.whiteTerritory + task.whiteScore + task.komi) + ".")
        scores.append(reward)
        for element in p1.moves:
            element[2] = 0.
        for element in p2.moves:
            element[2] = 0.
        p1.moves[-1][2] = task.blackTerritory + task.blackScore - task.whiteTerritory - task.whiteScore - task.komi
        p2.moves[-1][2] = task.whiteTerritory + task.whiteScore - task.blackTerritory - task.blackScore + task.komi
        module.acceptReward(p1.moves)
        module.acceptReward(p2.moves)
    cPickle.dump( module.actionvalues, open( "actionvaluemargin" + modifier + ".table", "w" ) )
    f = open("winrate" + modifier + ".txt", "w")
    for element in scores:
        print(str(element), file=f)
    f.close()
    f = open("results" + modifier + ".txt", "w")
    for element in results:
        print(str(element), file=f)
    f.close()
    return module
    
    
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
        if (i%2 == 0):
            scores.append(reward)
        for element in p1.moves:
            element[2] = 0.
        p1.moves[-1][2] = reward
        module.acceptReward(p1.moves)
        if i % 10000 == 0:
            print("Playing game " + str(i))
    cPickle.dump( module.actionvalues, open( "actionvalue_basic.table", "w" ) )
    f = open("winrate.txt", "w")
    for element in scores:
        print(str(element), file=f)
    f.close()
    
def margin():
    size = 3
    module = GoActionValueTable(size*size + 1)
    module.initialize(1.)
    scores = []
    i = 0
    for i in range(1000000):
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
                p1.moves[-1][2] = task.whiteTerritory + task.whiteScore - task.blackTerritory - task.blackScore
            else:
                p1.moves[-1][2] =  task.blackTerritory + task.blackScore - task.whiteTerritory - task.whiteScore
            module.acceptReward(p1.moves)
        if i % 10000 == 0:
            print("Playing game " + str(i))
    cPickle.dump( module.actionvalues, open( "actionvalue_margin.table", "w" ) )
    f = open("winrate_margin.txt", "w")
    for element in scores:
        print(str(element), file=f)
    f.close()
    
def assess(module = None, modifier = "", komi = 0.5):
    size = 3
    if module == None:
        module = GoActionValueTable(size*size + 1)
        module.initialize(1.)
        module.actionvalues = cPickle.load( open( "actionvalue.table", "r" ) )
    blackwins = 0
    whitewins = 0
    for i in range(1000):
        task = GoGame(size, komi)
        p1 = ModuleGoPlayer(task, module, colour = GoGame.BLACK, greedy = True)
        p2 = RandomGoPlayer(task, colour = GoGame.WHITE)
        task.playGame(p1, p2)
        if task.winner == p1.colour:
            blackwins = blackwins + 1
    for i in range(1000):
        task = GoGame(size, komi)
        p1 = ModuleGoPlayer(task, module, colour = GoGame.WHITE, greedy = True)
        p2 = RandomGoPlayer(task, colour = GoGame.BLACK)
        task.playGame(p1, p2)
        if task.winner == p1.colour:
            whitewins = whitewins + 1
    f = open("winrate" + modifier + ".txt", "w")
    print(str(blackwins), file=f)
    print(str(whitewins), file=f)
    f.close()
        
    
for i in range(-2, 11):
    assess(selfrun(str(i) + "-5komihundredthousand", 5, i+0.5), str(i) + "-5komihundredthousand", i+0.5)
for i in range(-2, 11):
    assess(selfrun(str(i) + "-5komimillion", 6, i+0.5), str(i) + "-5komimillion", i+0.5)