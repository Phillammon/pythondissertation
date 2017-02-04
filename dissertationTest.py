import random

boardsize = 5

class Agent(object):
    def __init__(self):
        break
    def RequestMove(self):
        return random.randint(0,boardsize*boardsize)
    def HandleVictory(self, margin):
        break
    def HandleLoss(self,margin):
        break
    def LastMoveIllegal(self):
        break


    
class GoBoard(object):
    boardstate = []
    tempstate = []
    passflag = false
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
        self.tempstate = self.CheckCaptures(self.tempstate)
        if self.tempstate[movechoice] == 1:
            self.boardstate = self.tempstate
            return 1
        else:
            return 0
        
    def CheckCaptures(self, gamestate):
        flag = False
        while not flag:
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
                    if (i + 5 <= 24):
                        if (gamestate[i + 5] == 2 or gamestate[i + 5] == 0):
                            gamestate[i] = 2
                            flag = True
                    if (i - 5 >= 0):
                        if (gamestate[i - 5] == 2 or gamestate[i - 5] == 0):
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
                    if (i + 5 <= 24):
                        if (gamestate[i + 5] == -2 or gamestate[i + 5] == 0):
                            gamestate[i] = -2
                            flag = True
                    if (i - 5 >= 0):
                        if (gamestate[i - 5] == -2 or gamestate[i - 5] == 0):
                            gamestate[i] = -2
                            flag = True
        for i in range(boardsize*boardsize):
            
        return gamestate
    def ProcessPass(self):
        if self.passflag:
            return 2
        else:
            self.passflag = True
            self.FlipBoard()
            return 1
    def FlipBoard(self):
        for i in range(boardsize*boardsize):
            self.boardstate.[i] = -self.boardstate.[i]
    def GetBoardState(self):
        return str(self.boardstate)
    def PlayGame(self):
        gameover = False
        currplayer = 0
        while not gameover:
            legal = False
            while not legal:
                move = self.agents[currplayer].RequestMove(self.GetBoardState())
                verdict = self.ProcessMove(move)
                legal = (verdict == 1 or 2)
                gameover = (verdict == 2)
                if not legal:
                    self.agents[currplayer].LastMoveIllegal()
                else:
                    currplayer = 1 - currplayer
    def ReportBoardstate(self):
        output = ""
        for i in range(boardsize*boardsize):
            output += self.boardstate[i]
        return output
    
