#!/usr/bin/env bash
set -euo pipefail

INCLUDES="-I../benchmark/include"
LIB_FLAGS="-L../benchmark/build/src"
LIBS="-lbenchmark -pthread -static-libstdc++ -static-libgcc"
BUILD_DIR="../build"

mkdir -p "$BUILD_DIR"

for src in altern_reporter.cc hybrid_reporter.cc rand_reporter.cc stream_reporter.cc; do
  base="${src%.cc}"
  out="${BUILD_DIR}/${base}"
  echo "Compiling $src -> $out"
  
  g++ -O3 -march=native $INCLUDES $LIB_FLAGS "$src" -o "$out" $LIBS
done

echo "All done."