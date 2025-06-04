#define CATCH_CONFIG_MAIN
#include "catch2.hpp"

int multiplyOdd(int n);
TEST_CASE("TEST 2")
{
    CHECK( multiplyOdd(1) == 1 );
    CHECK( multiplyOdd(456789) == 315 );
    CHECK( multiplyOdd(123) == 3 );
}