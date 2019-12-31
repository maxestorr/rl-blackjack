# Finite Decks, Aces = reactive
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

# stage 1 of learning - learn to maximize score.
def learning(e, nodecks):
    Qtable = np.zeros(
        (34, 2, 5)
    )  # columns for twitsing and sticking. Extra dimension for divisions of count.
    # divisions of count will be c<-10, -10<=c<-3, -3<=c<=3, 3<c<=10, c>10
    Instances = np.zeros((34, 2, 5))  # columns for twitsing and sticking.
    # repeat following process n times (higher number = better learning)
    for n in range(2000):
        drawpile = initializedrawpile(nodecks)

        # until drawpile is empty.
        while any(drawpile != 0):
            # simulation function represents 1 game (until fold or bust.)
            Qtable, Instances, drawpile = simulation(Qtable, Instances, drawpile, e)

    # once model has learned how to maximize score, test it.
    testscore, winnings, initialcount = test(Qtable, nodecks)

    return Qtable, testscore, winnings, initialcount


# function to test the results of the Qtable on unseen data. No exploration.
# this test function includes playing against a dealer, and a calculation of the
# winnings of each game.
def test(Qtable, nodecks):
    # set up empty arrays
    testscore = np.asarray([])
    winnings = np.asarray([])
    initialcounts = np.asarray([])

    # repeat process x times (needs to be high as large variance. )
    # most of the following is the same as simulation except no exploration and
    # at the end we play against dealer.
    for x in range(1000):
        drawpile = initializedrawpile(nodecks)

        while any(drawpile != 0):
            ##initialcounts should be here.
            initialcounts = np.append(
                initialcounts, countcalc(drawpile)
            )  ##not where i want

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

            if all(drawpile == 0):
                initialcounts = initialcounts[0:-1]
                break
            else:
                score = scorecalc(sum(cardsinhand), len(cardsinhand))
                testscore = np.append(testscore, score)
                # now player has played, dealer plays.
                dealerscore, drawpile = dealer(drawpile)
                # winningscalc function to work out winnings.
                winnings = np.append(winnings, winningscalc(score, dealerscore))

    plotwinnings(winnings, initialcounts)
    return np.mean(testscore), sum(winnings), initialcounts


# policy for casino bot is to always twist for h<17 and fold for h>=17. Create
# function where input drawpile and outputs score obtained by dealer, and updated drawpile.
def dealer(drawpile):
    # recieve first card.
    card, drawpile = twist(drawpile)
    cardsinhand = np.asarray([card])
    newaction = 1
    while (
        newaction == 1
        and (sum(cardsinhand) < 22 or 11 in cardsinhand)
        and any(drawpile != 0)
    ):
        if sum(cardsinhand) > 21:
            cardsinhand = acecheck(sum(cardsinhand), cardsinhand)
            newaction = dealeractioncalc(cardsinhand)
        else:
            card, drawpile = newcard(newaction, drawpile)

            # append the card that was drawn (to test for aces)
            cardsinhand = np.append(cardsinhand, card)

            newaction = dealeractioncalc(cardsinhand)
    score = scorecalc(sum(cardsinhand), len(cardsinhand))
    return score, drawpile


# dealer always folds if above 16
def dealeractioncalc(cardsinhand):
    if sum(cardsinhand) >= 17:
        newaction = 0
    else:
        newaction = 1
    return newaction


def winningscalc(score, dealerscore):
    if score == 0:  # lose money if go bust
        winnings = -1
    elif dealerscore > score:  # dealer wins if they have bigger score
        winnings = -1
    elif dealerscore == score:  # get back what you put in if draw.
        winnings = 0
    elif score == 661.5:  # if we get blackjack (and dealer doesnt)
        winnings = 1.5
    elif score > dealerscore:  # win otherway
        winnings = 1
    return winnings


def plotwinnings(winnings, initialcounts):
    x = np.asarray([])
    y = np.asarray([])
    for i in range(5):
        if len(initialcounts[initialcounts == i]) != 0:
            x = np.append(x, i)
            mean = np.mean(winnings[initialcounts == i])
            y = np.append(y, mean)
    fig, ax = plt.subplots()
    labels = ["C<-10", "-10<=C<-4", "-4<=C<=4", "4<C<=10", "C>10"]
    ax.bar(x, y)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Average Winnings")
    ax.set_title("Average winnings at different Counts")

