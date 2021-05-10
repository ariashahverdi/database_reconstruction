#!/bin/bash
for i in {1..10}
do
    for j in 1 2 4 6 8
    do
        python main_drop.py 'me' 0.002 $j $i
    done
done
