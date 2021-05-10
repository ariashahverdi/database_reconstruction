You can access the paper on [Arxiv](https://arxiv.org/abs/2006.15007)


There are two main directories. 
## measurement_code/
- *commands.txt* : Contains the command to get gcov running and simulating noide
- *compile.sh* : run it to compile the neccessary programs
- *generic_query.c* : you can run ./generic_query "db_name" "SQL command" to run the query on your database
- *parse_traces.m*, *parse_traces_nonuniform_simulator.m* : The matlab code to parse the traces and extract the volume found in each trace, the "simulator.m" is for simulating the non-uniform query. 
- *range_query.c* : The main code to run range queries, make sure you edit line 109 to have the correct name of your table in the db file. To simulate the non-uniform query, first gather large amount of traces (in our case 200 traces per query) and then simulate your query using the *parse_traces_nonuniform_simulator.m* file. To do this comment line 102 and uncomment line 103 with desired number in line 103. 
- *run_fr.sh*, *run_query.sh* : in one terminal run run_query.sh and in the other terminal run run_fr.sh. This will simulate running range queries on one terminal and running flush and reload on the other terminal. 
- *db/* : Put your test database here 
- *Mastik../* : The codes for running the Flush and Reload based on Mastik library
- *mat_files/* : Once you run the .m files the traces inside Traces/Test will be parsed and the result of mat workspace will be saved here. If you have Traces/Test1 Traces/Test2 each containing different experiment there will be two workspace saved there. 
- *Traces/* : The traces gathered using run_fr.sh will be saved in Traces/Test


## attack_code/

Make sure you have **networkx** package installed. The main program can be run as follows.

```
python main.py MODE NOISE_BUDGET DROP_NUM SEED 
```
- MODE can be 'clique' if you just want to run noisy clique finding or else it can be anything else
- NOISE_BUDGET is the value of noise budget for example 0.002 if you want to run the clique finding with noise budget of 0.002
- DROP_NUM and SEED are for future experiments and DROP_NUM has to be set to 0 for now

The following run noisy clique finding with noise budget of 0.002
```
python main.py 'clique' 0.002 0 0 
```

The following run Match & Extend with noise budget of 0.002
```
python main.py 'me' 0.002 0 0 
```

To run the experiment for random dropping volumes run *drop_test.sh*. The files run 10 different experiments for each case where 1, 2, 4, 6 and 8 volumes are dropped. To check the scenario where you want to drop high volumes go to file *main_drop.py* and uncomment line 575 to 577 and on line 575 set VOLUME_UPPER_BOUND*0.7 if you want to drop all volumes greater than 70% of the total size of database. 

- *CVP.ipynb* : The code to run closest vector problem to reduce the noise in some of the experiments. 