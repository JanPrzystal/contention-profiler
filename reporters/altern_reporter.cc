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
#include "../soi/xorshift.h"

#define FOOTPRINT_SIZE 8388608 // 64MiB (8MiB*8)
#define STREAM_SIZE (FOOTPRINT_SIZE / 2)
#define RAND_SIZE (FOOTPRINT_SIZE / 2)
#define PADDING_SIZE 32768 // 256KiB (32KiB*8)

#define STRIDE 4096

static volatile uint64_t bw_data [STREAM_SIZE + 2 * PADDING_SIZE];
static volatile uint64_t data_chunk [RAND_SIZE];
static volatile uint64_t dump[10];

static uint32_t seed = 0xACE1u;
#define r (xorshift32(&seed) % RAND_SIZE)

void streaming_access(benchmark::State& state) {
    for (auto _ : state) {
        volatile uint64_t *mid = bw_data + PADDING_SIZE;
        benchmark::DoNotOptimize(mid);

        for (int offset = 0; offset < STRIDE/sizeof(uint64_t); offset++) {
            for (int i = offset; i < STREAM_SIZE - PADDING_SIZE; i+= STRIDE/sizeof(uint64_t)) {
                bw_data[i] = mid[i]++;
                bw_data[i + 8] = mid[i + 8]++;
                bw_data[i + 16] = mid[i + 16]++;
                bw_data[i + 24] = mid[i + 24]++;
                bw_data[i + 32] = mid[i + 32]++;
                bw_data[i + 40] = mid[i + 40]++;
                bw_data[i + 48] = mid[i + 48]++;
                bw_data[i + 56] = mid[i + 56]++;
                bw_data[i + 64] = mid[i + 64]++;
            }
            benchmark::ClobberMemory();
        }
    }
}

void random_access(benchmark::State& state) {
    for (auto _ : state) {
        for (int i = 0; i < RAND_SIZE; i++) {
            dump[0] += data_chunk[r]++;
            dump[1] += data_chunk[r]++;
            dump[2] += data_chunk[r]++;
            dump[3] += data_chunk[r]++;
            dump[4] += data_chunk[r]++;
            dump[5] += data_chunk[r]++;
            dump[6] += data_chunk[r]++;
            dump[7] += data_chunk[r]++;
            dump[8] += data_chunk[r]++;
            dump[9] += data_chunk[r]++;
        }
        benchmark::ClobberMemory();
    }
}

BENCHMARK(streaming_access);
BENCHMARK(random_access);

BENCHMARK_MAIN();
