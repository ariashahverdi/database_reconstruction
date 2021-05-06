echo "** We first compile the Mastik Code **"
cd Mastik-0.02-AyeAyeCapn
make clean
make
cd ..
echo "** Now compiling the sqlite files **"
gcc -c -fPIC sqlite3.c -g
gcc -shared -o libsqlite3.so -fPIC sqlite3.o -g
gcc generic_query.c libsqlite3.so -o generic_query -lpthread -ldl -g
gcc range_query.c libsqlite3.so -o range_query -lpthread -ldl -g

export LD_LIBRARY_PATH=$PWD

chmod 777 run_query.sh
chmod 777 run_fr.sh
