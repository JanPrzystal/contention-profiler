#include <benchmark/benchmark.h>
#include <vector>
#include <numeric>
#include <algorithm>
#include <random>
#include <cstdint>

#define FOOTPRINT_SIZE 8388608 // 64MiB of uint64_t
#define STREAM_SIZE (FOOTPRINT_SIZE / 2)
#define RAND_SIZE (FOOTPRINT_SIZE / 2)
#define STRIDE 512 // 4096 bytes / sizeof(uint64_t)

// Non-volatile static arrays
static uint64_t bw_data[STREAM_SIZE];
static uint64_t data_chunk[RAND_SIZE];

void streaming_access(benchmark::State& state) {
    for (auto _ : state) {
        for (size_t offset = 0; offset < STRIDE; offset++) {
            // Ensure loop bound safely accounts for the unrolled offset (+64)
            for (size_t i = offset; i + 64 < STREAM_SIZE; i += STRIDE) {
                bw_data[i]      += 1;
                bw_data[i + 8]  += 1;
                bw_data[i + 16] += 1;
                bw_data[i + 24] += 1;
                bw_data[i + 32] += 1;
                bw_data[i + 40] += 1;
                bw_data[i + 48] += 1;
                bw_data[i + 56] += 1;
                bw_data[i + 64] += 1;
            }
        }
        benchmark::ClobberMemory();
    }
    state.SetBytesProcessed(int64_t(state.iterations()) * STREAM_SIZE * sizeof(uint64_t));
}

void random_access(benchmark::State& state) {
    // 1. Pre-generate random indices outside the timed benchmark loop
    std::vector<uint32_t> indices(RAND_SIZE);
    std::iota(indices.begin(), indices.end(), 0);
    
    std::mt19937 rng(1337);
    std::shuffle(indices.begin(), indices.end(), rng);

    uint64_t sum = 0;

    for (auto _ : state) {
        for (size_t i = 0; i < RAND_SIZE; i += 10) {
            sum += data_chunk[indices[i]];
            sum += data_chunk[indices[i + 1]];
            sum += data_chunk[indices[i + 2]];
            sum += data_chunk[indices[i + 3]];
            sum += data_chunk[indices[i + 4]];
            sum += data_chunk[indices[i + 5]];
            sum += data_chunk[indices[i + 6]];
            sum += data_chunk[indices[i + 7]];
            sum += data_chunk[indices[i + 8]];
            sum += data_chunk[indices[i + 9]];
        }
        benchmark::DoNotOptimize(sum);
        benchmark::ClobberMemory();
    }
    state.SetItemsProcessed(int64_t(state.iterations()) * RAND_SIZE);
}

BENCHMARK(streaming_access);
BENCHMARK(random_access);

BENCHMARK_MAIN();