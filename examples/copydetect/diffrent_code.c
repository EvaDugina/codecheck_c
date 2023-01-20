#include <stdio.h>
#include <stdlib.h>

int multiplyOdd(int n)
{
    int result = 0;
    while (n > 0)
    {
        int digit = n % 10;
        if (digit % 2 > 0) {
            if (result == 0) {
                result = digit;
            } else {
                result *= digit;
            }
        }
        n /= 10;
    }
    return result;
}