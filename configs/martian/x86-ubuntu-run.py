# This originally comes from the tutorial found here:
# https://www.gem5.org/documentation/gem5-stdlib/x86-full-system-tutorial

import os
import shutil

import hetcores
import switchable_hetproc

from m5.objects.X86KvmCPU import X86KvmCPU

from gem5.coherence_protocol import CoherenceProtocol
from gem5.components.boards.x86_board import X86Board
from gem5.components.cachehierarchies.ruby.mesi_two_level_cache_hierarchy import (
    MESITwoLevelCacheHierarchy,
)
from gem5.components.memory.single_channel import DIMM_DDR5_8400
from gem5.components.processors.cpu_types import CPUTypes
from gem5.isas import ISA
from gem5.resources.resource import (
    DiskImageResource,
    obtain_resource,
)
from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator
from gem5.utils.override import overrides
from gem5.utils.requires import requires

requires(
    isa_required=ISA.X86,
    coherence_protocol_required=CoherenceProtocol.MESI_TWO_LEVEL,
    kvm_required=True,  # Only works if the host and the simulator are the same.
)

system_config = int(os.environ["SYSTEM_CONFIG"])
workload = os.environ["SYS_WORKLOAD"]

l1d_assoc = 8

cache_hierarchy = MESITwoLevelCacheHierarchy(
    l1d_size="32KiB",
    l1d_assoc=l1d_assoc,
    l1i_size="32KiB",
    l1i_assoc=8,
    l2_size="256KiB",
    l2_assoc=16,
    num_l2_banks=1,
)

memory = DIMM_DDR5_8400(size="3GiB")

num_big_cores = 0
num_small_cores = 0
num_int_cores = 0
num_fp_cores = 0
num_superslow_cores = 0
num_speed_demons = 0

if system_config == 0:  # Homogeneous
    num_big_cores = 4

elif system_config == 1:  # big.LITTLE
    num_big_cores = 2
    num_small_cores = 4

elif system_config == 2:  # IntAndAccel
    num_int_cores = 2
    num_fp_cores = 2

elif system_config == 3:  # HighHet
    num_big_cores = 1
    num_small_cores = 2
    num_int_cores = 2
    num_fp_cores = 2

elif system_config == 4:  # Only Float
    num_fp_cores = 4

elif system_config == -1:  # SuperSlow (for debugging only)
    num_superslow_cores = 4

elif system_config == -2:
    num_speed_demons = 4

# TODO: make a nicer way to do this sort of thing.
cores = []
next_id = 0
for i in range(num_big_cores):
    cores.append(
        (
            hetcores.BigKvmCore(cpu_id=next_id),
            hetcores.DummyCore(cpu_id=next_id),
        )
    )
    next_id += 1
for i in range(num_small_cores):
    cores.append(
        (
            hetcores.SmallKvmCore(cpu_id=next_id),
            hetcores.DummyCore(cpu_id=next_id),
        )
    )
    next_id += 1
for i in range(num_int_cores):
    cores.append(
        (
            hetcores.IntKvmCore(cpu_id=next_id),
            hetcores.DummyCore(cpu_id=next_id),
        )
    )
    next_id += 1
for i in range(num_fp_cores):
    cores.append(
        (
            hetcores.FpKvmCore(cpu_id=next_id),
            hetcores.DummyCore(cpu_id=next_id),
        )
    )
    next_id += 1
for i in range(num_superslow_cores):
    cores.append(
        (
            hetcores.SuperSlowCore(cpu_id=next_id),
            hetcores.DummyCore(cpu_id=next_id),
        )
    )
    next_id += 1
for i in range(num_speed_demons):
    cores.append(
        (
            hetcores.SpeedDemonCore(cpu_id=next_id),
            hetcores.DummyCore(cpu_id=next_id),
        )
    )
    next_id += 1

processor = switchable_hetproc.CoreSwitchableHetProcessor(
    cores=cores,
    isa=ISA.X86,
)


class X86Board_sda(X86Board):
    @overrides(X86Board)
    def get_disk_device(self):
        return "/dev/sda"

    @overrides(X86Board)
    def get_default_kernel_args(self) -> list[str]:
        return [
            "earlyprintk=ttyS0",
            "console=ttyS0",
            "lpj=7999923",
            "root={root_value}",
            "disk_device={disk_device}",
            # "cpu_init_udelay=100000" # Adding this to see if it helps with bringing up additional cores.
        ]


# Set up the workload to run in the simulation.

board = X86Board_sda(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

command = (
    ""
    + "date;"
    + "cat /proc/version;"
    + "cat /proc/cmdline;"
    + "cat /proc/cpuinfo;"
    # + "ls /sys/kernel/tracing;"
    + "echo 50000 > /sys/kernel/tracing/buffer_size_kb;"  # Increase the trace buffer so we can get everything
    + f"trace_prog ~/programs/{workload};"
    + "echo done;"
    + "sleep 1;"
)

board.set_kernel_disk_workload(
    kernel=obtain_resource(resource_id="martian-linux"),
    disk_image=DiskImageResource(
        local_path="../gem5-resources-ubuntu22/src/x86-gapbs-ubuntu-22.04/qemu_files/x86_64-hpc-2204.img",
        root_partition="1",
    ),
    readfile_contents=command,
)

simulator = Simulator(
    board=board,
    on_exit_event={
        # The first time "m5 exit;" is called, switch processor models instead of
        # exiting the system entirely.
        ExitEvent.EXIT: (func() for func in [processor.switch] * 0),
    },
)

simulator.run()
