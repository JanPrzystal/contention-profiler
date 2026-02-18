// #include <omp.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>

#ifndef FOOTPRINT_SIZE
    #define FOOTPRINT_SIZE 16000000
#endif

#ifndef PADDING_SIZE
    #define PADDING_SIZE 40000
#endif

#ifndef BUBBLE_TYPE
    #define BUBBLE_TYPE 0
#endif

#ifndef NUM_THREADS
    #define NUM_THREADS 1
#endif

static size_t stream_size = (FOOTPRINT_SIZE / 2) + (2 * PADDING_SIZE);
static size_t rand_size = FOOTPRINT_SIZE / 2 + (2 * PADDING_SIZE);

static double *bw_data;
static int64_t *data_chunk;
static double scalar = 3.0;
static volatile int64_t dump[200];

void streaming_access() {
    while(1) {
        double *mid = bw_data + PADDING_SIZE;
        // #pragma omp parallel for
        for (int i = 0; i < stream_size / 2; i += 10) {
            bw_data[i]= scalar*mid[i];
            bw_data[i+1]= scalar*mid[i+1];
            bw_data[i+2]= scalar*mid[i+2];
            bw_data[i+3]= scalar*mid[i+3];
            bw_data[i+4]= scalar*mid[i+4];
            bw_data[i+5]= scalar*mid[i+5];
            bw_data[i+6]= scalar*mid[i+6];
            bw_data[i+7]= scalar*mid[i+7];
            bw_data[i+8]= scalar*mid[i+8];
            bw_data[i+9]= scalar*mid[i+9];
        }
        // #pragma omp parallel for
        for (int i = 0; i < stream_size / 2; i += 10) {
            mid[i]= scalar*bw_data[i];
            mid[i+1]= scalar*bw_data[i+1];
            mid[i+2]= scalar*bw_data[i+2];
            mid[i+3]= scalar*bw_data[i+3];
            mid[i+4]= scalar*bw_data[i+4];
            mid[i+5]= scalar*bw_data[i+5];
            mid[i+6]= scalar*bw_data[i+6];
            mid[i+7]= scalar*bw_data[i+7];
            mid[i+8]= scalar*bw_data[i+8];
            mid[i+9]= scalar*bw_data[i+9];
        }
    }
}

void random_access() {
    unsigned lfsr = 0xACE1u;
    #define MASK 0xd0000001u
    #define rand (lfsr = (lfsr >> 1) ^ (-(int)(lfsr & 1u) & MASK))
    #define r (rand % rand_size)
    while(1) {
        // #pragma omp parallel for
        for (int i = 0; i < 20; i++) {
            dump[0]  += data_chunk[r]++;
            dump[1]  += data_chunk[r]++;
            dump[2]  += data_chunk[r]++;
            dump[3]  += data_chunk[r]++;
            dump[4]  += data_chunk[r]++;
            dump[5]  += data_chunk[r]++;
            dump[6]  += data_chunk[r]++;
            dump[7]  += data_chunk[r]++;
            dump[8]  += data_chunk[r]++;
            dump[9]  += data_chunk[r]++;
            dump[10] += data_chunk[r]++;
            dump[11] += data_chunk[r]++;
            dump[12] += data_chunk[r]++;
            dump[13] += data_chunk[r]++;
            dump[14] += data_chunk[r]++;
            dump[15] += data_chunk[r]++;
            dump[16] += data_chunk[r]++;
            dump[17] += data_chunk[r]++;
            dump[18] += data_chunk[r]++;
            dump[19] += data_chunk[r]++;
            dump[20] += data_chunk[r]++;
            dump[21] += data_chunk[r]++;
            dump[22] += data_chunk[r]++;
            dump[23] += data_chunk[r]++;
            dump[24] += data_chunk[r]++;
            dump[25] += data_chunk[r]++;
            dump[26] += data_chunk[r]++;
            dump[27] += data_chunk[r]++;
            dump[28] += data_chunk[r]++;
            dump[29] += data_chunk[r]++;
            dump[30] += data_chunk[r]++;
            dump[31] += data_chunk[r]++;
            dump[32] += data_chunk[r]++;
            dump[33] += data_chunk[r]++;
            dump[34] += data_chunk[r]++;
            dump[35] += data_chunk[r]++;
            dump[36] += data_chunk[r]++;
            dump[37] += data_chunk[r]++;
            dump[38] += data_chunk[r]++;
            dump[39] += data_chunk[r]++;
            dump[40] += data_chunk[r]++;
            dump[41] += data_chunk[r]++;
            dump[42] += data_chunk[r]++;
            dump[43] += data_chunk[r]++;
            dump[44] += data_chunk[r]++;
            dump[45] += data_chunk[r]++;
            dump[46] += data_chunk[r]++;
            dump[47] += data_chunk[r]++;
            dump[48] += data_chunk[r]++;
            dump[49] += data_chunk[r]++;
            dump[50] += data_chunk[r]++;
            dump[51] += data_chunk[r]++;
            dump[52] += data_chunk[r]++;
            dump[53] += data_chunk[r]++;
            dump[54] += data_chunk[r]++;
            dump[55] += data_chunk[r]++;
            dump[56] += data_chunk[r]++;
            dump[57] += data_chunk[r]++;
            dump[58] += data_chunk[r]++;
            dump[59] += data_chunk[r]++;
            dump[60] += data_chunk[r]++;
            dump[61] += data_chunk[r]++;
            dump[62] += data_chunk[r]++;
            dump[63] += data_chunk[r]++;
            dump[64] += data_chunk[r]++;
            dump[65] += data_chunk[r]++;
            dump[66] += data_chunk[r]++;
            dump[67] += data_chunk[r]++;
            dump[68] += data_chunk[r]++;
            dump[69] += data_chunk[r]++;
            dump[70] += data_chunk[r]++;
            dump[71] += data_chunk[r]++;
            dump[72] += data_chunk[r]++;
            dump[73] += data_chunk[r]++;
            dump[74] += data_chunk[r]++;
            dump[75] += data_chunk[r]++;
            dump[76] += data_chunk[r]++;
            dump[77] += data_chunk[r]++;
            dump[78] += data_chunk[r]++;
            dump[79] += data_chunk[r]++;
            dump[80] += data_chunk[r]++;
            dump[81] += data_chunk[r]++;
            dump[82] += data_chunk[r]++;
            dump[83] += data_chunk[r]++;
            dump[84] += data_chunk[r]++;
            dump[85] += data_chunk[r]++;
            dump[86] += data_chunk[r]++;
            dump[87] += data_chunk[r]++;
            dump[88] += data_chunk[r]++;
            dump[89] += data_chunk[r]++;
            dump[90] += data_chunk[r]++;
            dump[91] += data_chunk[r]++;
            dump[92] += data_chunk[r]++;
            dump[93] += data_chunk[r]++;
            dump[94] += data_chunk[r]++;
            dump[95] += data_chunk[r]++;
            dump[96] += data_chunk[r]++;
            dump[97] += data_chunk[r]++;
            dump[98] += data_chunk[r]++;
            dump[99] += data_chunk[r]++;
            dump[100] += data_chunk[r]++;
            dump[101] += data_chunk[r]++;
            dump[102] += data_chunk[r]++;
            dump[103] += data_chunk[r]++;
            dump[104] += data_chunk[r]++;
            dump[105] += data_chunk[r]++;
            dump[106] += data_chunk[r]++;
            dump[107] += data_chunk[r]++;
            dump[108] += data_chunk[r]++;
            dump[109] += data_chunk[r]++;
            dump[110] += data_chunk[r]++;
            dump[111] += data_chunk[r]++;
            dump[112] += data_chunk[r]++;
            dump[113] += data_chunk[r]++;
            dump[114] += data_chunk[r]++;
            dump[115] += data_chunk[r]++;
            dump[116] += data_chunk[r]++;
            dump[117] += data_chunk[r]++;
            dump[118] += data_chunk[r]++;
            dump[119] += data_chunk[r]++;
            dump[120] += data_chunk[r]++;
            dump[121] += data_chunk[r]++;
            dump[122] += data_chunk[r]++;
            dump[123] += data_chunk[r]++;
            dump[124] += data_chunk[r]++;
            dump[125] += data_chunk[r]++;
            dump[126] += data_chunk[r]++;
            dump[127] += data_chunk[r]++;
            dump[128] += data_chunk[r]++;
            dump[129] += data_chunk[r]++;
            dump[130] += data_chunk[r]++;
            dump[131] += data_chunk[r]++;
            dump[132] += data_chunk[r]++;
            dump[133] += data_chunk[r]++;
            dump[134] += data_chunk[r]++;
            dump[135] += data_chunk[r]++;
            dump[136] += data_chunk[r]++;
            dump[137] += data_chunk[r]++;
            dump[138] += data_chunk[r]++;
            dump[139] += data_chunk[r]++;
            dump[140] += data_chunk[r]++;
            dump[141] += data_chunk[r]++;
            dump[142] += data_chunk[r]++;
            dump[143] += data_chunk[r]++;
            dump[144] += data_chunk[r]++;
            dump[145] += data_chunk[r]++;
            dump[146] += data_chunk[r]++;
            dump[147] += data_chunk[r]++;
            dump[148] += data_chunk[r]++;
            dump[149] += data_chunk[r]++;
            dump[150] += data_chunk[r]++;
            dump[151] += data_chunk[r]++;
            dump[152] += data_chunk[r]++;
            dump[153] += data_chunk[r]++;
            dump[154] += data_chunk[r]++;
            dump[155] += data_chunk[r]++;
            dump[156] += data_chunk[r]++;
            dump[157] += data_chunk[r]++;
            dump[158] += data_chunk[r]++;
            dump[159] += data_chunk[r]++;
            dump[160] += data_chunk[r]++;
            dump[161] += data_chunk[r]++;
            dump[162] += data_chunk[r]++;
            dump[163] += data_chunk[r]++;
            dump[164] += data_chunk[r]++;
            dump[165] += data_chunk[r]++;
            dump[166] += data_chunk[r]++;
            dump[167] += data_chunk[r]++;
            dump[168] += data_chunk[r]++;
            dump[169] += data_chunk[r]++;
            dump[170] += data_chunk[r]++;
            dump[171] += data_chunk[r]++;
            dump[172] += data_chunk[r]++;
            dump[173] += data_chunk[r]++;
            dump[174] += data_chunk[r]++;
            dump[175] += data_chunk[r]++;
            dump[176] += data_chunk[r]++;
            dump[177] += data_chunk[r]++;
            dump[178] += data_chunk[r]++;
            dump[179] += data_chunk[r]++;
            dump[180] += data_chunk[r]++;
            dump[181] += data_chunk[r]++;
            dump[182] += data_chunk[r]++;
            dump[183] += data_chunk[r]++;
            dump[184] += data_chunk[r]++;
            dump[185] += data_chunk[r]++;
            dump[186] += data_chunk[r]++;
            dump[187] += data_chunk[r]++;
            dump[188] += data_chunk[r]++;
            dump[189] += data_chunk[r]++;
            dump[190] += data_chunk[r]++;
            dump[191] += data_chunk[r]++;
            dump[192] += data_chunk[r]++;
            dump[193] += data_chunk[r]++;
            dump[194] += data_chunk[r]++;
            dump[195] += data_chunk[r]++;
            dump[196] += data_chunk[r]++;
            dump[197] += data_chunk[r]++;
            dump[198] += data_chunk[r]++;
            dump[199] += data_chunk[r]++;
        }
    }
}

int main() {
    size_t bw_data_size = stream_size * sizeof(double);
    bw_data = malloc(bw_data_size);
    size_t rand_data_size = rand_size * sizeof(int64_t);
    data_chunk = malloc(rand_data_size);
    data_chunk += PADDING_SIZE;
    // omp_set_num_threads(NUM_THREADS);
    char *bub_type = BUBBLE_TYPE == 0 ? "stream" : "rand";
    printf("Bubble type = %s, threads = %d\n", bub_type, NUM_THREADS);
    if (BUBBLE_TYPE == 0) {
        streaming_access();
    } else {
        random_access();
    }

    return 0;
}