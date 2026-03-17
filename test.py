from time import sleep
import logging

import spec
import atexit
import os
import signal
import sys
import prediction
import validation

if __name__ == "__main__":

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    # bench = spec.SpecWorkload("620.omnetpp_s", "train")

    # process = spec.run_background_benchmark("605.mcf_s", "1", "train")

    # bench.profile("0")

    # spec.stop_benchmark(process)

    pred = prediction.Prediction(app="620.omnetpp_s", competitor="605.mcf_s", perf=1.5)
    valid = validation.ValidatedPrediction(app="620.omnetpp_s", competitor="605.mcf_s", perf=1.5, actual_perf=1.2)
    row = [str(c) for c in list(pred._asdict().values())]
    print(row)
    vals = [str(c) for c in list(valid._asdict().values())]
    print(f"{vals}")