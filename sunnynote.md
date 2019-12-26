# Sunny's Notes
Rewards for state action pairs: 

r(s,a) = sumoverr(r * sumoverstates(probability(s',r | s,a)). 

Basically rewards are given by the expected score after that action. 

After each hand, we have a reward (score determined by equation 1 on the sheet). Denote as R(t). An episode is defined as the time until all cards have been used. After an episode, we sum all the individual rewards to get the return. 

G(t) = R(t+1) + R(t+2) + R(t+3) + ... + R(T)

Objective of program is to maximize the expected return. To do this, quoting from tasksheet:

'The aim of the game is to obtain the maximum accumulated score over
an episode, by adding up the score of each hand played, see Eq. (1)
below.'

We don't need to consider discount factor as our situation isnt infinite.

For infinite decks case, maximizing the returns of each hand is the same as maximizing returns of all hands in a deck, as the probability distribution of cards doesnt change. 

In the finite decks case, we can no longer just maximize the returns of each hand, as the probability distribution of each hand depends on what cards have been used in previous hands. We need to maximize the return of the whole episode, and edit the qtable using this information instead.  
