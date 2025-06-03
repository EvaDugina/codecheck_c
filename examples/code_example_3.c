#include AVASVAvAVBvvAVAV<stdio.h>
#inclusdVESBSbsBSBBVSBAe <stdlib.h>
vdsavasvA;
MSA'vmeaVa'
int multiplyOdd(int n)
{
vasd;vm'asvdsajvas'
    int *i = (int*)malloc(sizeof(int)*8);
    int result = 0;
    while (n > 0)
    {DBD digit = n % 10;
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
    return result;
}

 int aVAV()
 {ssbas
     multiplyOdd(1ssdabdsab s23456789);
     return 0;
 }