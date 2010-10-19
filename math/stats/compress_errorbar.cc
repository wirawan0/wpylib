/*

$Id: compress_errorbar.cc,v 1.1 2010-10-19 20:19:25 wirawan Exp $

Date: 20101007
Wirawan Purwanto

Small C++ utility to quickly compress an errorbar.

*/

#include <cstdio>

#include "cp.inc/pcharlib.cpp"
#include "cp.inc/pcharconv.cpp"

using namespace std;

int main(int argc, char *argv[], char *env[])
{
    double v, e;
    int errdigits = 2;

    if (argc < 3)
    {
        fprintf(stderr, "Minimum of two arguments required.\n");
        return 2;
    }

    if (EOF == sscanf(argv[1], "%lg", &v))
    {
        fprintf(stderr, "Invalid value: %s", argv[1]);
        return 1;
    }

    if (EOF == sscanf(argv[2], "%lg", &e))
    {
        fprintf(stderr, "Invalid errorbar: %s", argv[2]);
        return 1;
    }

    if (argc > 3)
    {
        if (EOF == sscanf(argv[3], "%d", &errdigits))
        {
            fprintf(stderr, "Invalid errorbar digits: %s", argv[3]);
            return 1;
        }
    }

    avgtostr compress_errorbar;
    fputs(+compress_errorbar(v, e, errdigits), stdout);
    fputs("\n", stdout);

    return 0;
}
