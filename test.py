from time import sleep
import logging

import spec
import atexit
import os
import signal
import sys
import prediction
import validation
import contentiousness
from contention_synthesis import Bubble, BUILD_DIR
import config

if __name__ == "__main__":

    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # bubble = Bubble(32, 2)
    # sleep(1)
    # bubble.run()
    # sleep(1)
    # print("Running bubble for 500 seconds")
    # sleep(500)
    # bubble.stop()


    # spec.run_background_benchmark("600.perlbench_s", "1", "train")
    # spec.run_background_benchmark("602.gcc_s", "2", "train")
    # spec.run_background_benchmark("631.deepsjeng_s", "3", "train")
    # spec.run_background_benchmark("649.fotonik3d_s", "4", "train")
    # spec.run_background_benchmark("628.pop2_s", "5", "train")
    # spec.run_background_benchmark("607.cactuBSSN_s", "6", "train")

    bench = spec.SpecWorkload("607.cactuBSSN_s", "train")

    # process = spec.run_background_benchmark("605.mcf_s", "1", "train")
    for i in range(6):
        result = bench.profile("0")
        sleep(2)

        logger.info(f"Cactu alone: {result}")
        
        proc = spec.run_background_benchmark("619.lbm_s", "1", "train")
        sleep(2)
        result = bench.profile("0")
        spec.stop_benchmark(proc)
        sleep(2)

        logger.info(f"Cactu with lbm: {result}")

        proc = spec.run_background_benchmark("631.deepsjeng_s", "2", "train")
        sleep(2)
        result = bench.profile("0")
        spec.stop_benchmark(proc)
        sleep(2)

        logger.info(f"Cactu with deepsjeng: {result}")

        proc = spec.run_background_benchmark("628.pop2_s", "3", "train")
        sleep(2)
        result = bench.profile("0")
        spec.stop_benchmark(proc)
        sleep(2)

        logger.info(f"Cactu with pop2: {result}")

