import matplotlib.pyplot as plt

win = 0
loss = 0
games = 0
winlist = []
gamelist = []

with open("winrate.txt") as fp:
    for line in fp:
        if "1" in line:
            win = win + 1
        else:
            loss = loss + 1
        games = games + 1
        winlist.append(float(win-loss) / games)
        gamelist.append(games)

plt.xscale("log")
plt.plot(winlist)
plt.ylabel("Black winrate among 10 Q-Learner pool over " + str(len(winlist)) + " episodes")
plt.axis([0, len(winlist), -1, 1])
plt.show()