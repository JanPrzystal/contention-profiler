from time import sleep
import logging

import spec
import atexit
import os
import signal
import sys

if __name__ == "__main__":

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    bench = spec.SpecWorkload("620.omnetpp_s", "train")

    process = spec.run_background_benchmark("605.mcf_s", "1", "train")

    bench.profile("0")

    spec.stop_benchmark(process)