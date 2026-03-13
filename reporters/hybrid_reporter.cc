#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <time.h>
#include <math.h>
#include <float.h>
#include <sched.h>
#include <set>
#include <iostream>
#include <benchmark/benchmark.h>

#ifndef LBM_SIZE
  #define LBM_SIZE 16000000
#endif

typedef double LBMGrid[LBM_SIZE];
static double * srcGrid, * dstGrid;

void hybrid_access(benchmark::State& state) {
    const unsigned long margin = 400000;
    const unsigned long size = sizeof(LBMGrid) + 2 * margin;// * sizeof(double);
    srcGrid = new double[size];
    dstGrid = new double[size];
    srcGrid += margin;
    dstGrid += margin;
    for (auto _ : state) {
        for (int i = 0; i < LBM_SIZE; i += 20) {
            dstGrid[i] = srcGrid[i];
            dstGrid[i - 1998] = srcGrid[(1) + i];
            dstGrid[i + 2001] = srcGrid[(2) + i];
            dstGrid[i - 16] = srcGrid[(3) + i];
            dstGrid[i + 23] = srcGrid[(4) + i];
            dstGrid[i - 199994] = srcGrid[(5) + i];
            dstGrid[i + 200005] = srcGrid[(6) + i];
            dstGrid[i - 2010] = srcGrid[(7) + i];
            dstGrid[i - 1971] = srcGrid[(8) + i];
            dstGrid[i + 1988] = srcGrid[(9) + i];
            dstGrid[i + 2027] = srcGrid[(10) + i];
            dstGrid[i - 201986] = srcGrid[(11) + i];
            dstGrid[i + 198013] = srcGrid[(12) + i];
            dstGrid[i - 197988] = srcGrid[(13) + i];
            dstGrid[i + 202011] = srcGrid[(14) + i];
            dstGrid[i - 200002] = srcGrid[(15) + i];
            dstGrid[i + 199997] = srcGrid[(16) + i];
            dstGrid[i - 199964] = srcGrid[(17) + i];
            dstGrid[i + 200035] = srcGrid[(18) + i];
            }
        }

    delete[] (srcGrid - margin);
    delete[] (dstGrid - margin);
}

BENCHMARK(hybrid_access);

BENCHMARK_MAIN();
