#include<stdlib.h>
#include <omp.h>

#ifndef LBM_SIZE
  #define LBM_SIZE 4000000
#endif

#define NUM_THREADS 4

typedef double LBMGrid[LBM_SIZE];
static double * srcGrid, * dstGrid;
int main() {
  const unsigned long margin = 400000;
  const unsigned long size = sizeof(LBMGrid) + 2 * margin * sizeof(double);
  srcGrid = malloc(size);
  dstGrid = malloc(size);
  srcGrid += margin;
  dstGrid += margin;
  omp_set_num_threads(NUM_THREADS);
  while (1) {
    int i;
    #pragma omp parallel for
    for (i = 0; i < LBM_SIZE; i += 20) {
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
  return 0;
}
