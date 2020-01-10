# tools.py
# Contains functions that are mutual between the two RL agents we've developed.

import numpy as np
import matplotlib.pyplot as plt
import random

# simulation represents each hand.
def simulation(Qtable, Instances, drawpile, e):
    # calculate the count based on what is remaining in the drawpile.
    truecount = countcalc(drawpile)
    countarray = np.asarray([truecount])
    # recieve first card
    card, drawpile = twist(drawpile)
    truecount = countcalc(drawpile)
    countarray = np.append(countarray, truecount)
    # now choose the next action based on q table, the value of agents hand, and current count.
    newaction = actionupdate(Qtable, card, e, truecount)
    # save this action in array
    action = np.asarray([1, newaction])
    cardsinhand = np.asarray([0, card])

    # while they havent folded or gone bust (if they have gone bust then
    # check for an ace.)
    while (
        newaction == 1
        and (sum(cardsinhand) < 21 or 11 in cardsinhand)
        and any(drawpile != 0)
    ):

        if sum(cardsinhand) > 21:
            # if over 21 replace 11 with 1 for aces.
            cardsinhand = acecheck(sum(cardsinhand), cardsinhand)
            # now we have changed 11 to 1, find new action.
            newaction = actionupdate(Qtable, sum(cardsinhand), e, truecount)
            # change the action for that handvalue
            action[-1] = newaction
        else:
            # find the new value of their hand
            card, drawpile = newcard(newaction, drawpile)

            # append the card that was drawn (to test for aces)
            cardsinhand = np.append(cardsinhand, card)

            # calculate new count of deck.
            truecount = countcalc(drawpile)

            countarray = np.append(countarray, truecount)

            # determine whether to stick or twist, again based on count.
            newaction = actionupdate(Qtable, sum(cardsinhand), e, truecount)

            # append new action to array
            action = np.append(action, newaction)

    # calculate final score
    score = scorecalc(sum(cardsinhand), len(cardsinhand))

    # update values in Qtable with the means of the scores obtained.
    Qtable, Instances = qtableupdate(
        Qtable, Instances, cardsinhand, action, score, countarray
    )
    return Qtable, Instances, drawpile


def initializedrawpile(nodecks):
    # start by creating an array for a single deck
    deck = np.zeros((10))
    deck[0:-1] = 4  # 4 of each number (4 suits)
    deck[9] = 16  # 16 cards worth 10 [10,j,q,k]
    drawpile = deck * nodecks
    return drawpile


# function to generate value of new hand.
def newcard(action, drawpile):
    if action == 1:
        card, drawpile = twist(drawpile)
    return card, drawpile


def actionupdate(Qtable, handvalue, e, truecount):
    # if no exploration
    if random.random() > e:
        # calculate new value of action from q table
        action = np.argmax(Qtable[handvalue, :, truecount])
    # if there is exploration
    else:
        action = 1 - np.argmax(Qtable[handvalue, :, truecount])
    return action


def acecheck(handvalue, cardsinhand):
    # if hand is above 21 and there is an ace in the hand
    if handvalue > 21 and len(cardsinhand[cardsinhand == 11]) != 0:
        # find the index of the ace
        findace = np.where(cardsinhand == 11)[0]
        # replace it with a 1.
        cardsinhand[findace] = 1
        # now calculate how far ace is from last card
    return cardsinhand


# count gives +1 for any 2,3,4,5,6 and -1 for any ace, 10
def countcalc(drawpile):
    count = (drawpile[0] + drawpile[9]) - sum(drawpile[1:6])
    if count != 0:
        # true count is count divided by number of decks left.
        truecount = count / (sum(drawpile) / 52)
    else:
        truecount = 0
    # now we have truecount, put it in one of the divisions for the qtable
    if truecount < -8:
        truecount = 0
    elif (truecount >= -8) & (truecount < -4):
        truecount = 1
    elif (truecount >= -4) & (truecount < 0):
        truecount = 2
    elif (truecount >= 0) & (truecount <= 4):
        truecount = 3
    elif (truecount > 4) & (truecount <= 8):
        truecount = 4
    elif truecount > 8:
        truecount = 5
    return truecount


# function to give a new card (twisting)
def twist(drawpile):
    cardnumber = random.randint(1, sum(drawpile))  # identify number card
    card, a = cardvalue(drawpile, cardnumber)
    drawpile[a - 1] += -1
    return card, drawpile


def cardvalue(drawpile, cardnumber):
    a = 0
    while cardnumber > 0:
        cardnumber = cardnumber - drawpile[a]
        a = a + 1
    card = a
    if a == 1:
        card = 11
    return card, a


def scorecalc(value, numberofcards):
    if value == 21 and numberofcards == 3:
        score = 1649  # (21**2.3)*1.5
    elif value <= 21:
        score = value ** (2.3)
    else:
        score = 0
    return score


def qtableupdate(Qtable, Instances, cardsinhand, action, score, countarray):
    total = 0
    for i in range(len(cardsinhand)):
        total += cardsinhand[i]
        Qtable[total, action[i], countarray[i]] = (
            Qtable[total, action[i], countarray[i]]
            * Instances[total, action[i], countarray[i]]
            + score
        ) / (Instances[total, action[i], countarray[i]] + 1)
        Instances[total, action[i], countarray[i]] += 1
    return Qtable, Instances

