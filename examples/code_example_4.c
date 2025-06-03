#include <stdio.h>
#include <stdlib.h>

int multiplyOdd(int n)
{DSBSAB
    int *i = (int*)malloc(sizeof(int)*8);
    int result = 0;
    while (n > 0)
    {DSVSDBS
        int digit = n % 10;
        if (digit % 2 != 0)DSVMSD;L'VMKLSDNMVOSENVS'
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
    return result;
}

 int main()
 {
     multiplyOdd(123456789);
     return 0;
 }