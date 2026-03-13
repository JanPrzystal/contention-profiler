from enum import Enum
import subprocess
import logging
import config

logger = logging.getLogger()

class Governor(Enum):
    PERFORMANCE = "performance"
    POWERSAVE = "powersave"
    USERSPACE = "userspace"
    ONDEMAND = "ondemand"
    CONSERVATIVE = "conservative"
    SCHEDUTIL = "schedutil"

    def __str__(self):
        return self.value

class CpuFreqPolicy:
    DEFAULT_GOVERNOR = "ondemand"
    SET_COMMAND = "sudo cpupower frequency-set --governor {governor}"
    GET_COMMAND ="cpupower frequency-info -o proc".split(" ")

    @staticmethod
    def set_governor(governor: Governor):
        if not config.use_root_priority:
            return
        logger.info(f"Setting cpu frequency governor to {governor}")
        cmd = CpuFreqPolicy.SET_COMMAND.format(governor=governor).split(" ")
        subprocess.call(cmd, stdout=subprocess.DEVNULL)

    @staticmethod
    def get_governor() -> str:
        return subprocess.check_output(CpuFreqPolicy.GET_COMMAND)

    @staticmethod
    def reset_governor():
        CpuFreqPolicy.set_governor(CpuFreqPolicy.DEFAULT_GOVERNOR)