#!/bin/bash

export LD_LIBRARY_PATH=$PWD

rm sleep1.txt
seed=10
# 15600 for non-uniform case
for i in {1..12000}
do	
	echo $i
	taskset -c 2 ./range_query db/nis2008_1.db nis2008_1 12 $i $seed

  	while [ ! -f sleep1.txt ]; do sleep 1; done
  	sleep 0.1
  	rm sleep1.txt
  	
done
echo 'Done'