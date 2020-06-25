# Match_Extend

Make sure you have networkx package installed.

python main.py MODE NOISE_BUDGET DROP_NUM SEED 
- MODE can be 'clique' if you just want to run noisy clique finding or else it can be anything else
- NOISE_BUDGET is the value of noise budget for example 0.002 if you want to run the clique finding with noise budget of 0.002
- DROP_NUM and SEED are for future experiments and DROP_NUM has to be set to 0 for now

# The following run noisy clique finding with noise budget of 0.002
python main.py 'clique' 0.002 0 0 

# The following run Match & Extend with noise budget of 0.002
python main.py 'me' 0.002 0 0 