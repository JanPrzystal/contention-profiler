#define _POSIX_C_SOURCE 199309L
// #include <omp.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include "xorshift.h"
#include <assert.h>
#include <errno.h>

#ifndef FOOTPRINT_SIZE
#define FOOTPRINT_SIZE (8ULL * 1000 * 1000)
#endif

static uint64_t *data;
static int64_t deadline_ms = -1;

static uint32_t seed = 0xACE1u;


static int64_t get_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000LL + ts.tv_nsec / 1000000LL;
}

/*
 * GCC/Clang compiler barrier.
 *
 * This emits no machine instruction, but tells the compiler that memory may
 * have been read or modified. It prevents removal or inappropriate movement
 * of accesses across the barrier.
 */
static inline void compiler_barrier(void) {
    __asm__ __volatile__("" ::: "memory");
}

/* Equivalent in purpose to benchmark::DoNotOptimize for this scalar value. */
static inline void consume_u64(uint64_t value) {
    __asm__ __volatile__("" : : "r"(value) : "memory");
}

/*
 * Maps a 32-bit random value to [0, elements) without division or modulo.
 *
 * This requires elements <= UINT32_MAX.
 */
static inline uint32_t random_index(uint32_t *seed, size_t elements) {
    uint32_t random_value = xorshift32(seed);

    return (uint32_t)(((uint64_t)random_value * elements) >> 32);
}

static inline int infinite_condition(void) {
    return 1;
}

static inline int timed_condition(void) {
    return get_time_ms() < deadline_ms;
}

static void streaming_read(size_t elements) {
    uint64_t sum = 0;

    for (size_t i = 0; i < elements; ++i) {
        sum += data[i];
    }

    consume_u64(sum);
    compiler_barrier();
}

static void random_read(size_t elements) {
    uint64_t sum = 0;
    size_t index;

    for (size_t i = 0; i < elements; ++i) {
        index = random_index(&seed, elements);
        sum += data[index];
        index = random_index(&seed, elements);
        sum -= data[index];
    }

    consume_u64(sum);
    compiler_barrier();

}

static void streaming_write(size_t elements) {
    uint64_t value = (uint64_t)xorshift32(&seed);

    for (size_t i = 0; i < elements; ++i) {
        data[i] = value++;
    }

    compiler_barrier();
}

static void random_write(size_t elements) {
    uint64_t value = (uint64_t)xorshift32(&seed);

    for (size_t i = 0; i < elements; ++i) {
        size_t index = random_index(&seed, elements);
        data[index] = value++;
    }

    compiler_barrier();
}

static size_t parse_positive_size(const char *text) {
    char *endptr = NULL;
    size_t value;

    if (text == NULL || text[0] == '-') {
        return FOOTPRINT_SIZE;
    }

    errno = 0;
    value = strtoull(text, &endptr, 10);

    if (errno != 0 || endptr == text || *endptr != '\0' ||
        value == 0 || value > SIZE_MAX) {
        return FOOTPRINT_SIZE;
    }

    return value;
}

int main(int argc, char *argv[]) {
    int64_t duration_ms = 0;

    // int bubble_type = BUBBLE_TYPE;
    // if (argc > 1) {
    //     char *endptr = NULL;
    //     long long parsed = strtoll(argv[1], &endptr, 10);
    //     if (endptr != NULL && *endptr == '\0') {
    //         duration_ms = parsed;
    //     } else if (strcmp(argv[1], "rand") == 0) {
    //         bubble_type = 1;
    //     } else if (strcmp(argv[1], "stream") == 0) {
    //         bubble_type = 0;
    //     }
    // }

    // if (argc > 2) {
    //     if (strcmp(argv[2], "rand") == 0) {
    //         bubble_type = 1;
    //     } else if (strcmp(argv[2], "stream") == 0) {
    //         bubble_type = 0;
    //     } else {
    //         fprintf(stderr, "Unknown bubble type '%s', using '%s'.\n",
    //                 argv[2], bubble_type == 0 ? "stream" : "rand");
    //     }
    // }

    // if (duration_ms > 0) {
    //     deadline_ms = get_time_ms() + duration_ms;
    // }

    // int (*condition)(void) = (duration_ms > 0) ? timed_condition : infinite_condition;
    int (*condition)(void) = infinite_condition;

    const char *elements_arg = (argc > 1) ? argv[1] : NULL;
    const size_t elements = parse_positive_size(elements_arg);
    printf("SoI elem arg: %s, elems: %zu\n", elements_arg ? elements_arg : "(default)", elements);

    /*
     * Initialisation pre-faults the pages before the contention phase.
     * This avoids charging first-touch page faults to the SoI behaviour.
     */
    data = malloc(elements * sizeof(*data));

    if (data == NULL) {
        perror("malloc");
        return 1;
    }

    for (size_t i = 0; i < elements; ++i) {
        data[i] = (uint64_t)i;
    }

    compiler_barrier();

    const size_t elements_short = elements / 64;

    while (condition()) {
        streaming_write(elements);
        random_read(elements_short);
        random_write(elements);
        random_read(elements_short);
    }

    return 0;
}