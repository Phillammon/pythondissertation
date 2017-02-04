import random
import copy

boardsize = 5
komi = 0.5

class Agent(object):
    def __init__(self):
        pass
    def RequestMove(self, gamestate, board):
        return random.randint(0,boardsize*boardsize)
    def HandleVictory(self, margin):
        pass
    def HandleLoss(self,margin):
        pass
    def LastMoveIllegal(self):
        pass

class PlayerAgent(Agent):
    def RequestMove(self, gamestate, board):
        board.PrintBoard()
        print("Pass the turn? Y/N")
        choice = input(">")
        if choice == "Y" or choice == "y":
            return boardsize * boardsize
        choicex = -1
        choicey = -1
        while choicex == -1:
            print ("X coordinate:")
            try:
                choicex = int(input(">"))
                if choicex > boardsize or choicex < 0:
                    print("Number out of bounds")
                    choicex = -1
            except:
                print("No number recognised")
        while choicey == -1:
            print ("Y coordinate:")
            try:
                choicey = int(input(">"))
                if choicey > boardsize or choicey < 0:
                    print("Number out of bounds")
                    choicey = -1
            except:
                print("No number recognised")
        return 5*(choicey-1) + (choicex-1)
    def LastMoveIllegal(self):
        print("That is not a legal play")
    def HandleVictory(self, margin):
        print("You win by a margin of " + str(margin) + " points")
    def HandleLoss(self,margin):
        print("You lose by a margin of " + str(margin) + " points")
    
class GoBoard(object):
    boardstate = []
    tempstate = []
    passflag = False
    activescore = 0
    inactivescore = 0
    def __init__(self, agent1, agent2):
        self.InitBoardstate()
        self.agents = [agent1, agent2]
    def InitBoardstate(self):
        for i in range(boardsize*boardsize):
            self.boardstate.append(0)
    def ProcessMove(self, movechoice):
        if movechoice == boardsize*boardsize:
            return self.ProcessPass()
        elif self.boardstate[movechoice] != 0:
            return 0
        self.tempstate = copy.copy(self.boardstate)
        self.tempstate[movechoice] = 1
        points = self.CheckCaptures(self.tempstate)
        if points == -1:
            return 0
        else:
            self.boardstate = self.tempstate
            self.activescore += points
            return 1
        
    def CheckCaptures(self, gamestate):
        flag = True
        while flag:
            flag = False
            for i in range(boardsize*boardsize):
                if gamestate[i] == 1:
                    if (i % boardsize != boardsize - 1):
                        if (gamestate[i + 1] == 2 or gamestate[i + 1] == 0):
                            gamestate[i] = 2
                            flag = True
                    if (i % boardsize != 0):
                        if (gamestate[i - 1] == 2 or gamestate[i - 1] == 0):
                            gamestate[i] = 2
                            flag = True
                    if (i + boardsize < boardsize*boardsize):
                        if (gamestate[i + boardsize] == 2 or gamestate[i + boardsize] == 0):
                            gamestate[i] = 2
                            flag = True
                    if (i - boardsize >= 0):
                        if (gamestate[i - boardsize] == 2 or gamestate[i - boardsize] == 0):
                            gamestate[i] = 2
                            flag = True
                elif gamestate[i] == -1:
                    if (i % boardsize != boardsize - 1):
                        if (gamestate[i + 1] == -2 or gamestate[i + 1] == 0):
                            gamestate[i] = -2
                            flag = True
                    if (i % boardsize != 0):
                        if (gamestate[i - 1] == -2 or gamestate[i - 1] == 0):
                            gamestate[i] = -2
                            flag = True
                    if (i + boardsize < boardsize*boardsize):
                        if (gamestate[i + boardsize] == -2 or gamestate[i + boardsize] == 0):
                            gamestate[i] = -2
                            flag = True
                    if (i - boardsize >= 0):
                        if (gamestate[i - boardsize] == -2 or gamestate[i - boardsize] == 0):
                            gamestate[i] = -2
                            flag = True
        scored = 0
        capflag = False
        for i in range(boardsize*boardsize):
            if gamestate[i] == -2:
                gamestate[i] = -1
            elif gamestate[i] == -1:
                gamestate[i] = 0
                scored += 1
            elif gamestate[i] == 2:
                gamestate[i] = 1
            elif gamestate[i] == 1:
                capflag = True
        if capflag and scored == 0:
            return -1
        else:
            return scored
    def ScoreTerritory(self, gamestate):
        flag = True
        while flag:
            flag = False
            for i in range(boardsize*boardsize):
                if gamestate[i] == 0:
                    if (i % boardsize != boardsize - 1):
                        if (gamestate[i + 1] == 2 or gamestate[i + 1] == 1):
                            gamestate[i] = 2
                            flag = True
                        if (gamestate[i + 1] == -2 or gamestate[i + 1] == -1):
                            gamestate[i] = -2
                            flag = True
                    if (i % boardsize != 0):
                        if (gamestate[i - 1] == 2 or gamestate[i - 1] == 1):
                            gamestate[i] = 2
                            flag = True
                        if (gamestate[i - 1] == -2 or gamestate[i - 1] == -1):
                            gamestate[i] = -2
                            flag = True
                    if (i + boardsize < boardsize*boardsize):
                        if (gamestate[i + boardsize] == 2 or gamestate[i + boardsize] == 1):
                            gamestate[i] = 2
                            flag = True
                    if (i + boardsize < boardsize*boardsize):
                        if (gamestate[i + boardsize] == -2 or gamestate[i + boardsize] == -1):
                            gamestate[i] = -2
                            flag = True
                    if (i - boardsize >= 0):
                        if (gamestate[i - boardsize] == 2 or gamestate[i - boardsize] == 1):
                            gamestate[i] = 2
                            flag = True
                        if (gamestate[i - boardsize] == -2 or gamestate[i - boardsize] == -1):
                            gamestate[i] = -2
                            flag = True
                elif gamestate[i] == 2:
                    if (i % boardsize != boardsize - 1):
                        if (gamestate[i + 1] == -2 or gamestate[i + 1] == -1 or gamestate[i + 1] == 5):
                            gamestate[i] = 5
                            flag = True
                    if (i % boardsize != 0):
                        if (gamestate[i - 1] == -2 or gamestate[i - 1] == -1 or gamestate[i - 1] == 5):
                            gamestate[i] = 5
                            flag = True
                    if (i + boardsize < boardsize*boardsize):
                        if (gamestate[i + boardsize] == -2 or gamestate[i + boardsize] == -1 or gamestate[i + boardsize] == 5):
                            gamestate[i] = 5
                            flag = True
                    if (i - boardsize >= 0):
                        if (gamestate[i - boardsize] == -2 or gamestate[i - boardsize] == -1 or gamestate[i - boardsize] == 5):
                            gamestate[i] = 5
                            flag = True
                elif gamestate[i] == -2:
                    if (i % boardsize != boardsize - 1):
                        if (gamestate[i + 1] == 2 or gamestate[i + 1] == 1 or gamestate[i + 1] == 5):
                            gamestate[i] = 5
                            flag = True
                    if (i % boardsize != 0):
                        if (gamestate[i - 1] == 2 or gamestate[i - 1] == 1 or gamestate[i - 1] == 5):
                            gamestate[i] = 5
                            flag = True
                    if (i + boardsize < boardsize*boardsize):
                        if (gamestate[i + boardsize] == 2 or gamestate[i + boardsize] == 1 or gamestate[i + boardsize] == 5):
                            gamestate[i] = 5
                            flag = True
                    if (i - boardsize >= 0):
                        if (gamestate[i - boardsize] == 2 or gamestate[i - boardsize] == 1 or gamestate[i - boardsize] == 5):
                            gamestate[i] = 5
                            flag = True
        for i in range(boardsize*boardsize):
            if gamestate[i] == -2:
                self.inactivescore += 1
            elif gamestate[i] == 2:
                self.activescore += 1
    def ProcessPass(self):
        if self.passflag:
            return 2
        else:
            self.passflag = True
            self.FlipBoard()
            return 1
    def FlipBoard(self):
        for i in range(boardsize*boardsize):
            self.boardstate[i] = -self.boardstate[i]
        tmp = self.activescore
        self.activescore = self.inactivescore
        self.inactivescore = tmp
    def GetBoardState(self):
        return str(self.boardstate)
    def PlayGame(self, doPrint = False):
        gameover = False
        currplayer = 0
        while not gameover:
            legal = False
            while not legal:
                move = self.agents[currplayer].RequestMove(self.GetBoardStateString(), self)
                if move >= 0 and move <= boardsize*boardsize:
                    verdict = self.ProcessMove(move)
                    legal = (verdict == 1 or verdict == 2)
                    gameover = (verdict == 2)
                if not legal:
                    self.agents[currplayer].LastMoveIllegal()
                else:
                    if move != boardsize * boardsize:
                        self.passflag = False
                        self.FlipBoard()
                    currplayer = 1 - currplayer
        self.ScoreTerritory(self.boardstate)
        if currplayer == 0:
            self.inactivescore -= komi
        else:
            self.activescore -= komi
        margin = self.activescore - self.inactivescore
        if margin < 0:
            self.agents[currplayer].HandleVictory(-margin)
            self.agents[1-currplayer].HandleLoss(-margin)
        else:
            self.agents[currplayer].HandleLoss(margin)
            self.agents[1-currplayer].HandleVictory(margin)
        if doPrint:
            self.PrintBoard()
    def GetBoardStateString(self):
        output = ""
        for i in range(boardsize*boardsize):
            output += str(self.boardstate[i]+1)
        return output
    def PrintBoard(self):
        for i in range(boardsize):
            linestring = ""
            for j in range(boardsize):
                if self.boardstate[5*i+j] == 1:
                    linestring += "o"
                elif self.boardstate[5*i+j] == -1:
                    linestring += "+"
                else:
                    linestring += " "
                if j != boardsize-1:
                    linestring += "-"
            print(linestring)
            if i != boardsize-1:
                print("| | | | |")
    
board = GoBoard(PlayerAgent(), Agent())
board.PlayGame(True)
