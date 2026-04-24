
# perf stat -e cycles,instructions,L1-dcache-loads,L1-dcache-load-misses,LLC-loads,LLC-load-misses,branches,branch-misses,stalled-cycles-frontend,stalled-cycles-backend -M CPI ./membench/membench

import subprocess
import os

def profile(workload: str):

    cmd = [
        "perf",
        "stat",
        "-e cycles,instructions,L1-dcache-loads,L1-dcache-load-misses,LLC-loads,LLC-load-misses,branches,branch-misses,stalled-cycles-frontend,stalled-cycles-backend",
        # "-M CPI",
        workload,
    ]

    # todo taskset
        # if cores is not None:
        # cmd = ["taskset", "-c", f"{cores}"] + cmd

    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setpgrp
        )


    stdout_data, stderr_data = proc.communicate()

    return stdout_data.decode("utf-8") + "\n\n" + stderr_data.decode("utf-8")
