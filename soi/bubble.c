// #include <omp.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include "xorshift.h"
#include <assert.h>

#ifndef FOOTPRINT_SIZE
    #define FOOTPRINT_SIZE 16000000
#endif

#ifndef PADDING_SIZE
    #define PADDING_SIZE 32768
#endif

#ifndef BUBBLE_TYPE
    #define BUBBLE_TYPE 0
#endif

#ifndef NUM_THREADS
    #define NUM_THREADS 1
#endif

#define STRIDE 64

#define STREAM_SIZE (FOOTPRINT_SIZE + (2 * PADDING_SIZE))
#define RAND_SIZE (FOOTPRINT_SIZE + (2 * PADDING_SIZE))

static int64_t *bw_data;
static int64_t *data_chunk;
static volatile int64_t dump[200];

static uint32_t seed = 0xACE1u;
#define r (xorshift32(&seed) % RAND_SIZE)

void streaming_access() {
    while(1) {
        int64_t volatile *mid = bw_data + PADDING_SIZE;
        size_t offset = 0;
        // #pragma omp parallel for
        for (int i = offset; i < STREAM_SIZE - PADDING_SIZE - 4096; i += (STRIDE * 8)) {
            mid[i] = bw_data[i]++;
            mid[i + STRIDE] = bw_data[i + STRIDE]++;
            mid[i + (STRIDE * 2)] = bw_data[i + (STRIDE * 2)]++;
            mid[i + (STRIDE * 3)] = bw_data[i + (STRIDE * 3)]++;
            mid[i + (STRIDE * 4)] = bw_data[i + (STRIDE * 4)]++;
            mid[i + (STRIDE * 5)] = bw_data[i + (STRIDE * 5)]++;
            mid[i + (STRIDE * 6)] = bw_data[i + (STRIDE * 6)]++;
            mid[i + (STRIDE * 7)] = bw_data[i + (STRIDE * 7)]++;
        }

        offset = (offset + (STRIDE * 8)) % 4096;

        // #pragma omp parallel for
        // for (int i = 0; i < STREAM_SIZE - PADDING_SIZE; i += 10) {
        //     bw_data[i] = mid[i];
        //     bw_data[i+1] = mid[i+1];
        //     bw_data[i+2] = mid[i+2];
        //     bw_data[i+3] = mid[i+3];
        //     bw_data[i+4] = mid[i+4];
        //     bw_data[i+5] = mid[i+5];
        //     bw_data[i+6] = mid[i+6];
        //     bw_data[i+7] = mid[i+7];
        //     bw_data[i+8] = mid[i+8];
        //     bw_data[i+9] = mid[i+9];
        // }
    }
}

void random_access() {
    for (int i = 0; 1; i++) {
        dump[0]  = data_chunk[r]++;
        dump[1]  = data_chunk[r]++;
        dump[2]  = data_chunk[r]++;
        dump[3]  = data_chunk[r]++;
        dump[4]  = data_chunk[r]++;
        dump[5]  = data_chunk[r]++;
        dump[6]  = data_chunk[r]++;
        dump[7]  = data_chunk[r]++;
        dump[8]  = data_chunk[r]++;
        dump[9]  = data_chunk[r]++;
        dump[10] = data_chunk[r]++;
        dump[11] = data_chunk[r]++;
        dump[12] = data_chunk[r]++;
        dump[13] = data_chunk[r]++;
        dump[14] = data_chunk[r]++;
        dump[15] = data_chunk[r]++;
        dump[16] = data_chunk[r]++;
        dump[17] = data_chunk[r]++;
        dump[18] = data_chunk[r]++;
        dump[19] = data_chunk[r]++;
        dump[20] = data_chunk[r]++;
        dump[21] = data_chunk[r]++;
        dump[22] = data_chunk[r]++;
        dump[23] = data_chunk[r]++;
        dump[24] = data_chunk[r]++;
        dump[25] = data_chunk[r]++;
        dump[26] = data_chunk[r]++;
        dump[27] = data_chunk[r]++;
        dump[28] = data_chunk[r]++;
        dump[29] = data_chunk[r]++;
        dump[30] = data_chunk[r]++;
        dump[31] = data_chunk[r]++;
        dump[32] = data_chunk[r]++;
        dump[33] = data_chunk[r]++;
        dump[34] = data_chunk[r]++;
        dump[35] = data_chunk[r]++;
        dump[36] = data_chunk[r]++;
        dump[37] = data_chunk[r]++;
        dump[38] = data_chunk[r]++;
        dump[39] = data_chunk[r]++;
        dump[40] = data_chunk[r]++;
        dump[41] = data_chunk[r]++;
        dump[42] = data_chunk[r]++;
        dump[43] = data_chunk[r]++;
        dump[44] = data_chunk[r]++;
        dump[45] = data_chunk[r]++;
        dump[46] = data_chunk[r]++;
        dump[47] = data_chunk[r]++;
        dump[48] = data_chunk[r]++;
        dump[49] = data_chunk[r]++;
        dump[50] = data_chunk[r]++;
        dump[51] = data_chunk[r]++;
        dump[52] = data_chunk[r]++;
        dump[53] = data_chunk[r]++;
        dump[54] = data_chunk[r]++;
        dump[55] = data_chunk[r]++;
        dump[56] = data_chunk[r]++;
        dump[57] = data_chunk[r]++;
        dump[58] = data_chunk[r]++;
        dump[59] = data_chunk[r]++;
        dump[60] = data_chunk[r]++;
        dump[61] = data_chunk[r]++;
        dump[62] = data_chunk[r]++;
        dump[63] = data_chunk[r]++;
        dump[64] = data_chunk[r]++;
        dump[65] = data_chunk[r]++;
        dump[66] = data_chunk[r]++;
        dump[67] = data_chunk[r]++;
        dump[68] = data_chunk[r]++;
        dump[69] = data_chunk[r]++;
        dump[70] = data_chunk[r]++;
        dump[71] = data_chunk[r]++;
        dump[72] = data_chunk[r]++;
        dump[73] = data_chunk[r]++;
        dump[74] = data_chunk[r]++;
        dump[75] = data_chunk[r]++;
        dump[76] = data_chunk[r]++;
        dump[77] = data_chunk[r]++;
        dump[78] = data_chunk[r]++;
        dump[79] = data_chunk[r]++;
        dump[80] = data_chunk[r]++;
        dump[81] = data_chunk[r]++;
        dump[82] = data_chunk[r]++;
        dump[83] = data_chunk[r]++;
        dump[84] = data_chunk[r]++;
        dump[85] = data_chunk[r]++;
        dump[86] = data_chunk[r]++;
        dump[87] = data_chunk[r]++;
        dump[88] = data_chunk[r]++;
        dump[89] = data_chunk[r]++;
        dump[90] = data_chunk[r]++;
        dump[91] = data_chunk[r]++;
        dump[92] = data_chunk[r]++;
        dump[93] = data_chunk[r]++;
        dump[94] = data_chunk[r]++;
        dump[95] = data_chunk[r]++;
        dump[96] = data_chunk[r]++;
        dump[97] = data_chunk[r]++;
        dump[98] = data_chunk[r]++;
        dump[99] = data_chunk[r]++;
    }
}

int main() {
    char *bub_type = BUBBLE_TYPE == 0 ? "stream" : "rand";
    // printf("Bubble type = %s, threads = %d\n", bub_type, NUM_THREADS);
    if (BUBBLE_TYPE == 0) {
        size_t bw_data_size = STREAM_SIZE * sizeof(int64_t);
        bw_data = malloc(bw_data_size);
        assert(bw_data != NULL);
        streaming_access();
    } else {
        size_t rand_data_size = RAND_SIZE * sizeof(int64_t);
        data_chunk = malloc(rand_data_size);
        assert(data_chunk != NULL);
        random_access();
    }

    return 0;
}