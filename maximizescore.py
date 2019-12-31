# Finite Decks, Aces = reactive
# this program just uses the count information to maximize score.
import numpy as np
import matplotlib.pyplot as plt
import random
from rl_tools import (
    simulation,
    scorecalc,
    countcalc,
    initializedrawpile,
    actionupdate,
    acecheck,
    cardvalue,
    newcard,
    twist,
    qtableupdate,
)

e = 0.1
nodecks = 6


def learning(e, nodecks):
    Qtable = np.zeros(
        (34, 2, 5)
    )  # columns for twitsing and sticking. Extra dimension for divisions of count.
    # divisions of count will be c<-10, -10<=c<-3, -3<=c<=3, 3<c<=10, c>10
    Instances = np.zeros((34, 2, 5))  # columns for twitsing and sticking.
    for n in range(1000):
        drawpile = initializedrawpile(nodecks)
        while any(drawpile != 0):
            Qtable, Instances, drawpile = simulation(Qtable, Instances, drawpile, e)
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    ax1.plot(range(34), np.sum(Qtable[:, 1, :], axis=1))
    ax1.plot(range(34), np.sum(Qtable[:, 0, :], axis=1), color="red")
    ax1.legend(["Twist", "Fold"])
    ax1.set_ylabel("Average Score")
    ax1.set_xlabel("Hand value")
    ax1.set(xlim=(-1, 22), ylim=(0, max(np.sum(Qtable[:, 0, :], axis=1)) * 1.1))
    plt.xticks(np.arange(0, 22, 1))
    plt.show()

    testscore = test(Qtable, nodecks)
    return Qtable, testscore


# function to test the results of the Qtable on unseen data. No exploration.
def test(Qtable, nodecks):
    testscore = np.asarray([])
    drawpile = initializedrawpile(nodecks)
    while any(drawpile != 0):
        # recieve first card
        card, drawpile = twist(drawpile)
        truecount = countcalc(drawpile)
        cardsinhand = np.array([0, card])
        newaction = np.argmax(Qtable[sum(cardsinhand), :, truecount])
        # while they havent folded or gone bust
        while (
            newaction == 1
            and (sum(cardsinhand) < 22 or 11 in cardsinhand)
            and any(drawpile != 0)
        ):
            if sum(cardsinhand) > 21:
                # if over 21 replace 11 with 1 for aces.
                cardsinhand = acecheck(sum(cardsinhand), cardsinhand)
                # now we have changed 11 to 1, find new action.
                newaction = actionupdate(Qtable, sum(cardsinhand), e, truecount)
            else:
                card, drawpile = newcard(newaction, drawpile)
                cardsinhand = np.append(cardsinhand, card)
                cardsinhand = acecheck(sum(cardsinhand), cardsinhand)
                truecount = countcalc(drawpile)
                # determine whether to stick or twist
                newaction = np.argmax(Qtable[sum(cardsinhand), :, truecount])
        score = scorecalc(sum(cardsinhand), len(cardsinhand))
        testscore = np.append(testscore, score)
    return np.mean(testscore)

