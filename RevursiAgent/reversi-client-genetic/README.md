# cs-470-reversi-python-client

This is a Python 3 Client for the BYU CS 470 Reversi Lab, with some modifications to the original code. bots are now genetic and weights need to be specified when running the clients.

For instance:

```
python reversi_python_client.py localhost 1 4 -0.9724278637348411 -0.9575917958507336 0.49051641446111605 -0.11043431912527724 0.9305262003315051 0.005978367003628637 
```

will run the first client with the weights specified.

To train the bots, run the following command:

```
python genetic_trainer.py
```

This will run the genetic algorithm for 100 generations (can be changed in the genetic_trainer.py file). Every 5 generations, the best weights and fitness will be saved to a file. The weights can then be used to run the clients with the following command:

```
python reversi_python_client.py localhost 1 4 w_1 w_2 w_3 w_4 w_5 w_6
```

where w_1, w_2, w_3, w_4, w_5, and w_6 are the weights from the best individual in the last generation.



