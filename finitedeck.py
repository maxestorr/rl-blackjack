#Finite Decks, Aces = reactive
import numpy as np
import matplotlib.pyplot as plt
import random


e=0.1
nodecks = 50000

def learning(e, nodecks):
    drawpile = initializedrawpile(nodecks)
    Qtable = np.zeros((34,2,10)) #columns for twitsing and sticking.
    Instances = np.zeros((34,2,10)) #columns for twitsing and sticking.
    # for 10000 runs
    while any(drawpile!=0): 
        exp=int(np.round(np.dot(np.asarray([1,2,3,4,5,6,7,8,9,10]),drawpile)/np.sum(drawpile)))
        expectation = np.asarray([exp])
        #recieve first card
        card, drawpile = twist(drawpile)
        exp=int(np.round(np.dot(np.asarray([1,2,3,4,5,6,7,8,9,10]),drawpile)/np.sum(drawpile)))
        expectation = np.append(expectation, exp)
        newaction=actionupdate(Qtable,card,e,exp)
        action=np.asarray([1,newaction])
        cardsinhand=np.asarray([0,card])
        
        
        #while they havent folded or gone bust (if they have gone bust then 
        #check for an ace.)
        while newaction == 1 and (sum(cardsinhand) < 22 or 11 in cardsinhand) and any(drawpile!=0):
                    
            #find the new value of their hand
            card,drawpile = newcard(newaction, drawpile)
            
            #append the card that was drawn (to test for aces)
            cardsinhand=np.append(cardsinhand, card)
            
            #if over 21 replace 11 with 1 for aces.
            cardsinhand = acecheck(sum(cardsinhand),cardsinhand)

            exp=int(np.round(np.dot(np.asarray([1,2,3,4,5,6,7,8,9,10]),drawpile)/np.sum(drawpile)))

            #determine whether to stick or twist
            newaction=actionupdate(Qtable,sum(cardsinhand),e,exp)
            #append new action to array
            action=np.append(action,newaction)
            

            #calculate expected next card
            expectation = np.append(expectation, exp)

        #calculate final score
        score = scorecalc(sum(cardsinhand))

        #update values in Qtable with the means of the scores obtained.
        Qtable,Instances = qtableupdate(Qtable,Instances,cardsinhand,action,score,expectation)        

    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    ax1.plot(range(34),np.sum(Qtable[:,1,:],axis=1))
    ax1.plot(range(34),np.sum(Qtable[:,0,:],axis = 1),color='red')
    ax1.legend(['Twist', 'Fold'])
    ax1.set_ylabel('Average Score')
    ax1.set_xlabel('Hand value')
    ax1.set(xlim=(-1,22),ylim=(0,max(np.sum(Qtable[:,0,:],axis=1))*1.1))
    plt.xticks(np.arange(0, 22, 1))
    plt.show()
    
  #  stickon = stickonno(Qtable)
   # testscore = test(Qtable,nodecks)
    return Qtable#, testscore, stickon

def initializedrawpile(nodecks):
    #start by creating an array for a single deck
    deck=np.zeros((10))
    deck[0:-1]=4 #4 of each number (4 suits)
    deck[9]=16 #16 cards worth 10 [10,j,q,k]
    drawpile=deck*nodecks
    return drawpile

#function to generate value of new hand. 
def newcard(action,drawpile):    
    if action == 1:
        card, drawpile = twist(drawpile)
    return card, drawpile

def actionupdate(Qtable,handvalue,e,exp):
    #if no exploration
    if random.random()>e:
        #calculate new value of action from q table
        action=np.argmax(Qtable[handvalue,:,exp])
    # if there is exploration
    else: 
        action = 1 - np.argmax(Qtable[handvalue,:,exp])
    return action

def acecheck(handvalue,cardsinhand):
    #if hand is above 21 and there is an ace in the hand
    if handvalue>21 and len(cardsinhand[cardsinhand == 11])!=0:
        #find the index of the ace
        findace=np.where(cardsinhand==11)[0]
        #replace it with a 1. 
        cardsinhand[findace]=1
        #now calculate how far ace is from last card
    return cardsinhand
        
        

#function to give a new card (twisting)
def twist(drawpile):
    cardnumber = random.randint(1,sum(drawpile)) #identify number card
    card = cardvalue(drawpile, cardnumber)
    drawpile[card-1]+= -1
    return card, drawpile
    
def cardvalue(drawpile,cardnumber):
    a=0
    while cardnumber>0:
        cardnumber=cardnumber-drawpile[a] 
        a=a+1 #a = card value
    return a

def scorecalc(value):
    if value<=21:
        score = value**(2)
    else: 
        score = 0 
    return score


#function to test the results of the Qtable on unseen data. No exploration. 
def test(Qtable,nodecks):
    testscore=np.asarray([])
    drawpile = initializedrawpile(round(nodecks/3))
    while any(drawpile!=0): 
        #recieve first card
        hand, drawpile = twist(drawpile)
        newaction=np.argmax(Qtable[hand,:])
        #while they havent folded or gone bust
        while newaction == 1 and hand < 22 and any(drawpile!=0):
            #find the new value of their hand
            card, drawpile = newcard(newaction,drawpile)
            hand+=card
            #determine whether to stick or twist
            newaction=np.argmax(Qtable[hand,:])
        score = scorecalc(hand)
        testscore=np.append(testscore , score)
    return np.mean(testscore)            
            
def stickonno(Qtable):
    priority = Qtable[:,0] - Qtable[:,1]
    stickon = np.where(priority >0)[0][0]
    return stickon     
            

def qtableupdate(Qtable, Instances, cardsinhand, action,score, expectation):
    total = 0
    for i in range(len(cardsinhand)):
        total+=cardsinhand[i]
        Qtable[total, action[i],expectation[i]]=(Qtable[total,action[i],expectation[i]]*Instances[total,action[i],expectation[i]]+score)/(Instances[total,action[i],expectation[i]]+1)
        Instances[total , action[i],expectation[i]]+=1
    return Qtable,Instances
            
# class hand(object):
#     def __init__(self,value,action):
#         if action == 1:
#             value = twist(value)
#         self.value = value
#         self.action = action 
    


