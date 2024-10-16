import time
from dataclasses import dataclass
from typing import Generator

import psutil as ps
from psutil._common import scpufreq, scpustats, sdiskio, sdiskpart, sdiskusage
from psutil._pslinux import scputimes

ps.cpu_count()
ps.cpu_stats()  # change
ps.cpu_percent()  # change
ps.cpu_times_percent()  # change
ps.cpu_freq()  # change


@dataclass
class CPUStats:
    pysical_count: int
    logical_count: int
    percent: float
    stats: scpustats
    times_percent: scputimes
    freq: scpufreq


@dataclass
class DiskPartitionStats:
    partition: sdiskpart
    usage: sdiskusage


@dataclass
class DiskStats:
    parititons_stats: list[DiskPartitionStats]
    io: sdiskio | None


class HardwareObserver:
    def __init__(self, cpu_interval_s: int, disk_interval_s: int) -> None:
        self._cpu_interval_s = cpu_interval_s
        self._disk_interval_s = disk_interval_s
        self._cpu_pysical_count = ps.cpu_count(False)
        self._cpu_logical_count = ps.cpu_count(True)

    def cpu_monitor(self) -> Generator[CPUStats, None, None]:
        while True:
            time.sleep(self._cpu_interval_s)
            yield CPUStats(
                pysical_count=self._cpu_pysical_count,
                logical_count=self._cpu_logical_count,
                percent=ps.cpu_percent(),
                stats=ps.cpu_stats(),
                times_percent=ps.cpu_times_percent(),
                freq=ps.cpu_freq()
            )

    def disk_monitor(self) -> Generator[DiskStats, None, None]:
        while True:
            time.sleep(self._disk_interval_s)
            yield DiskStats(
                parititons_stats=[
                    DiskPartitionStats(p, ps.disk_usage(p.device))
                    for p in ps.disk_partitions()
                ],
                io=ps.disk_io_counters()
            )
