#!/bin/bash


#-m "sqlite3.c:80523"
# For AND
# Main
#-m "sqlite3.c:71263" -m "sqlite3.c:80417"
# Extra 
#-m "sqlite3.c:77719"
# AND Detect
#-m "sqlite.c:131533" -m "sqlite3.c:93698" This helped to detect AND vs not, 
# the time of the hits was sort of relevant to the query, refer to TEST folder
# 3: AND/OR 1: OR
#-m "sqlite3.c:96522"
export LD_LIBRARY_PATH=$PWD
rm sleep1.txt
# 15600
for i in {1..12000}
do
	echo $i
	taskset -c 1 Mastik-0.02-AyeAyeCapn/demo/FR-trace_main -s 5000 -c 20000000 -h 100 -i 15000 -f libsqlite3.so -m "sqlite3.c:71263" -m "sqlite3.c:80417" > Traces/Test/tr$i.txt
	#-m "sqlite3.c:93698"
	touch sleep1.txt
	sleep 0.2
		
done

echo 'Done'

