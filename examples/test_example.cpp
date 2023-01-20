#define CATCH_CONFIG_MAIN
#include "catch.hpp"

int multiplyOdd(int n);
TEST_CASE("the product of odd digits")
{
    CHECK( multiplyOdd(1) == 1 );
    CHECK( multiplyOdd(456789) == 315 );
    CHECK( multiplyOdd(123) == 3 );
    CHECK( multiplyOdd(0) == 0 );
    CHECK( multiplyOdd(246) == 0 );
}   