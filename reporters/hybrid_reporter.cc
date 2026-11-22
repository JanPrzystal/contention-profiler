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

#define FOOTPRINT_SIZE 8388608 // 64MiB (8MiB*8)
#define PADDING_SIZE 32768 // 256KiB (32KiB*8)

static void hybrid_access(benchmark::State& state) {
    const unsigned long size = FOOTPRINT_SIZE + 2 * PADDING_SIZE;

    // Allocate outside the benchmark loop
    double* raw_src = new double[size]();
    double* raw_dst = new double[size]();

    double* srcGrid = raw_src + PADDING_SIZE;
    double* dstGrid = raw_dst + PADDING_SIZE;

    for (auto _ : state) {
        for (int i = 0; i < FOOTPRINT_SIZE; i += 20) {
            dstGrid[i]           = srcGrid[i];
            dstGrid[i - 1998]    = srcGrid[i + 1];
            dstGrid[i + 2001]    = srcGrid[i + 2];
            dstGrid[i - 16]      = srcGrid[i + 3];
            dstGrid[i + 23]      = srcGrid[i + 4];
            dstGrid[i - 19994]  = srcGrid[i + 5];
            dstGrid[i + 20005]  = srcGrid[i + 6];
            dstGrid[i - 2010]    = srcGrid[i + 7];
            dstGrid[i - 1971]    = srcGrid[i + 8];
            dstGrid[i + 198]    = srcGrid[i + 9];
            dstGrid[i - 207]    = srcGrid[i + 10];
            dstGrid[i - 21986]  = srcGrid[i + 11];
            dstGrid[i + 19813]  = srcGrid[i + 12];
            dstGrid[i - 17988]  = srcGrid[i + 13];
            dstGrid[i + 22011]  = srcGrid[i + 14];
            dstGrid[i - 20002]  = srcGrid[i + 15];
            dstGrid[i + 19997]  = srcGrid[i + 16];
            dstGrid[i - 19964]  = srcGrid[i + 17];
            dstGrid[i + 20035]  = srcGrid[i + 18];
        }
        // Force compiler to flush writes to memory
        benchmark::ClobberMemory();
    }

    // Set processed bytes metric for Google Benchmark output
    state.SetBytesProcessed(int64_t(state.iterations()) * FOOTPRINT_SIZE * sizeof(double) * 2);

    delete[] raw_src;
    delete[] raw_dst;
}

BENCHMARK(hybrid_access);
BENCHMARK_MAIN();
