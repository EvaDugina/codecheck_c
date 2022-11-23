#include <stdio.h>
#include <stdlib.h>

int main()
{
    int x; // unused variable
    char *str = malloc(128); // memory leak

    return 0;
}