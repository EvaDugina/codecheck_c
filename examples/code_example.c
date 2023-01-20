#include <stdio.h>
#include <stdlib.h>

int multiplyOdd(int n)
{
    int *i = (int*)malloc(sizeof(int));
    int result = 0;
    while (n > 0)
    {
        int digit = n % 10;
        if (digit % 2 != 0)
        {
            if (result == 0)
            {
                result = digit;
            }
            else
            {
                result = result * digit;
            }
        }
        n = n / 10;
    }
    return 0;
}

// int main()
// {
//     multiplyOdd(1234);
//     return 0;
// }