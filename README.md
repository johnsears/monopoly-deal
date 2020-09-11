# monopoly-deal
Really simple repo for simulating the Monopoly Deal card game. Almost all game dynamics are captured,
and there is also a very basic Monte Carlo Tree Search agent implemented. 

## Installation
```
pip install -r requirements.txt
```

## Demo
There is a really simple POC script to prove that the MCTS is able to win at a higher rate than a random agent.
With even just a bit more time to consider moves, the MCTS agent should win the vast majority of the time. Note that 
in a sense the agent is currently cheating, in that it has oracle knowledge of the game state. What I'd like to do
is to actually implement the partial observability and also build a simple UI so that it can be used in actual games
of Monopoly Deal :) 
```
python -m monopoly_deal.run
```

## Acknowledgments
Used the deck contents from [brylee123](https://github.com/brylee123/MonopolyDeal)'s repo. 
