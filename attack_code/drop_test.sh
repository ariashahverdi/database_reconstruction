#!/bin/bash
for j in {1..4}
do
    for i in {1..10}
    do
        python main.py 'me' 0.002 $j $i
    done
done
