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

#define FOOTPRINT_SIZE 8388608 / sizeof(uint64_t) // 8MiB
#define STREAM_SIZE (FOOTPRINT_SIZE / 2)
#define RAND_SIZE (FOOTPRINT_SIZE / 2)
#define PADDING_SIZE 32768 * 4 // 128KiB

// unsigned lfsr;
// #define MASK 0xd0000001u
// #define rand (lfsr = (lfsr >> 1) ^ (-(int)(lfsr & 1u) & MASK))
// #define r (rand % RAND_SIZE)

#define STRIDE 4096

static volatile uint64_t bw_data [STREAM_SIZE + 2 * PADDING_SIZE];
static volatile uint64_t data_chunk [RAND_SIZE];
static volatile uint64_t dump[10];

static uint32_t seed = 0xACE1u;
#define r (xorshift32(&seed) % RAND_SIZE)

void streaming_access(benchmark::State& state) {
    //std::cout << "STREAM thread: " << state.thread_index() << " executed on CPU: " << sched_getcpu() << std::endl;
    for (auto _ : state) {
        volatile uint64_t *mid = bw_data + PADDING_SIZE;
        benchmark::DoNotOptimize(mid);

        for (int i = 0; i < STREAM_SIZE - PADDING_SIZE; i+= STRIDE) {
            bw_data[i] = mid[i]++;
            bw_data[i + 64] = mid[i + 64]++;
            bw_data[i + 128] = mid[i + 128]++;
            bw_data[i + 192] = mid[i + 192]++;
            bw_data[i + 256] = mid[i + 256]++;
            bw_data[i + 384] = mid[i + 384]++;
            bw_data[i + 512] = mid[i + 512]++;
        }

        benchmark::ClobberMemory();
    }
}

void random_access(benchmark::State& state) {
    //std::cout << "RAND thread: " << state.thread_index() << " executed on CPU: " << sched_getcpu() << std::endl;
    for (auto _ : state) {
        for (int i = 0; i < RAND_SIZE / STRIDE; i++) {
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
