#include <stdio.h>
#include "sqlite3.h"
#include <unistd.h>
#include <stdlib.h>
#include <sys/time.h> 

///// Tools for adjusting the time
#define __STDC_FORMAT_MACROS
#include <inttypes.h>
static inline uint64_t rdtscp64() {
  uint32_t low, high;
  asm volatile ("rdtscp": "=a" (low), "=d" (high) :: "ecx");
  return (((uint64_t)high) << 32) | low;
}


/* A linked list node */
struct Node
{
    // Any data type can be stored in this node
    void  *data;
    struct Node *next;
};

/* Function to add a node at the beginning of Linked List.
   This function expects a pointer to the data to be added
   and size of the data type */
void push(struct Node** head_ref, void *new_data, size_t data_size)
{
    // Allocate memory for node
    struct Node* new_node = (struct Node*)malloc(sizeof(struct Node));
 
    new_node->data  = malloc(data_size);
    new_node->next = (*head_ref);
 
    // Copy contents of new_data to newly allocated memory.
    // Assumption: char takes 1 byte.
    int i;
    for (i=0; i<data_size; i++)
        *(char *)(new_node->data + i) = *(char *)(new_data + i);
 
    // Change head pointer as new node is added at the beginning
    (*head_ref)    = new_node;
}

struct Node* head;

static int callback(void *NotUsed, int argc, char **argv, char **azColName){
	unsigned char_size = sizeof(char);
	unsigned int_size = sizeof(int);
	int i;
	for(i=0; i<argc; i++){		
		push(&head, &azColName[i], char_size);
		push(&head, &argv[i], int_size);
		//printf("%s = %s\n", azColName[i], argv[i] ? argv[i] : "NULL");
	}

	return 0;
}

/*
// Original Callback Function
static int callback(void *NotUsed, int argc, char **argv, char **azColName){
	FILE *fp;
	fp = fopen("Query_Result.txt", "a");// "w" means that we are going to write on this file
	int i;
	for(i=0; i<argc; i++){		
		fprintf(fp,"%s = %s\n", azColName[i], argv[i] ? argv[i] : "NULL");
	}
	fclose(fp); //Don't forget to close the file when finished
	return 0;
}
*/

int main(int argc, char **argv){
	
	struct timeval time;
	gettimeofday(&time,NULL);
	
	int N = atoi(argv[3]);

	int tot_range = N * (N+1) / 2; 

	int ranges[2*tot_range];

	int count = 0;

	for(int i=1;i<=N;i++){
		for(int j=i;j<=N;j++){
			ranges[2*count] = i;
			ranges[2*count+1] = j;
		count ++;
		}
	}   

	int flag = 0;
	char buf[100];
	int r, idx1, idx2;
	
	// Create a random range query
	//r = rand() % tot_range;
	r = (atoi(argv[4])-1) % tot_range; // For Uniform Query
	//r = (atoi(argv[4])-1) / 200; // For Nonuniform Query

	idx1 = ranges[2*r];
	idx2 = ranges[(2*r)+1];
	
	// ** RANGE QUERY ** //
	sprintf(buf, "SELECT * from nis2008_1 Where AMONTH Between %d AND %d", idx1, idx2);
	
	sqlite3 *db;
	char *zErrMsg = 0;
	int rc;
 
	if( argc!=6 ){
		fprintf(stderr, "Usage: %s DATABASE SQL-STATEMENT\n", argv[0]);
		return(1);
	}
	rc = sqlite3_open(argv[1], &db);
	if( rc ){
		fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db));
		sqlite3_close(db);
		return(1);
	}

	//time = rdtscp64();
  	//printf("sqlite time 3 : ");
  	//printf("%"PRIu64"\n", time3);

	rc = sqlite3_exec(db, buf, callback, 0, &zErrMsg);
	//rc = sqlite3_exec(db, argv[2], callback, 0, &zErrMsg);
	//rc = sqlite3_exec(db, argv[2], NULL, 0, &zErrMsg);
	
	if( rc!=SQLITE_OK ){
		fprintf(stderr, "SQL error: %s\n", zErrMsg);
		sqlite3_free(zErrMsg);
	}
	sqlite3_close(db);
	
	return 0;
}
