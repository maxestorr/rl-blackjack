#Infinite Decks, Aces = 1
import numpy as np
import matplotlib.pyplot as plt
import random


e=0.1

def learning(e):
    Qtable = np.zeros((32,2)) #columns for twitsing and sticking.
    Instances = np.zeros((32,2)) #columns for twitsing and sticking.
    # for 10000 runs
    for i in range(20000): 
        #recieve first card
        newvalue = twist(0)
        value = np.asarray([0,newvalue])
        newaction=actionupdate(Qtable,newvalue,e)
        action=np.asarray([1,newaction])
        #while they havent folded or gone bust
        while newaction == 1 and newvalue < 22:
            #find the new value of their hand
            newvalue = newhand(Qtable,newvalue,newaction,e)
            #append new value to array
            value=np.append(value, newvalue)
            #determine whether to stick or twist
            newaction=actionupdate(Qtable,newvalue,e)
            #append new action to array
            action=np.append(action,newaction)
        #calculate final score
        score = scorecalc(newvalue)
        #update values in Qtable with the means of the scores obtained.
        Qtable[value.astype(np.int64),action.astype(np.int64)] = (Qtable[value.astype(np.int64),action.astype(np.int64)]* Instances[value.astype(np.int64),action.astype(np.int64)] + score)/ (Instances[value.astype(np.int64),action.astype(np.int64)]+1)
        
        Instances[value.astype(np.int64),action.astype(np.int64)]+=1

    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    ax1.plot(range(32),Qtable[:,1])
    ax1.plot(range(32),Qtable[:,0],color='red')
    ax1.legend(['Twist', 'Fold'])
    ax1.set_ylabel('Average Score')
    ax1.set_xlabel('Hand value')
    ax1.set(xlim=(-1,22),ylim=(0,max(Qtable[:,0])*1.1))
    plt.xticks(np.arange(0, 22, 1))
    plt.show()
    return Qtable

#function to generate value of new hand. 
def newhand(Qtable,value,action,e):    
    if action == 1:
        value = twist(value)
    return value

def actionupdate(Qtable,value,e):
    #if no exploration
    if random.random()>e:
        #calculate new value of action from q table
        action=np.argmax(Qtable[value])
    # if there is exploration
    else: 
        action = 1 - np.argmax(Qtable[value])
    return action


#function to give a new card (twisting)
def twist(hand):
    card = random.randint(1,13)
    if card >10:
        card = 10
    hand=hand+card
    return hand
    
def scorecalc(value):
    if value<=21:
        score = value**(2)
    else: 
        score = 0 
    return score

# class hand(object):
#     def __init__(self,value,action):
#         if action == 1:
#             value = twist(value)
#         self.value = value
#         self.action = action 
    





 