import random

class Agent(object):
    def __init__(self):
        break
    def RequestMove(self):
        return random.randint(0,25)
    def HandleVictory(self, margin):
        break
    def HandleLoss(self,margin):
        break
    def LastMoveIllegal(self):
        break
    
class GoBoard(object):
    boardstate = []
    passflag = false
    def __init__(self):
        self.InitBoardstate()
    def InitBoardstate(self):
        for i in range(25):
            self.boardstate.append(0)
    def ProcessMove(self, movechoice):
        if movechoice == 25:
            return self.ProcessPass()
        elif self.boardstate[movechoice] != 0:
            return 0
        elif 
    def ProcessPass(self):
        if self.passflag:
            return 2
        else:
            self.passflag = True
            self.FlipBoard()
            return 1
    def FlipBoard(self):
        for i in range(25):
            self.boardstate.[i] = -self.boardstate.[i]
    def GetBoardState(self):
        return str(self.boardstate)
    def PlayGame(self):
        gameover = False
        agents = [Agent(), Agent()]
        currplayer = 0
        while not gameover:
            legal = False
            while not legal:
                move = agents[currplayer].RequestMove(self.GetBoardState())
                verdict = self.ProcessMove(move)
                legal = (verdict == 1 or 2)
                gameover = (verdict == 2)
                if not legal:
                    agents[currplayer].LastMoveIllegal()
                else:
                    currplayer = 1 - currplayer
            
        
        