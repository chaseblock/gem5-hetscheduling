# This file defines a bunch of different configurations of
# the O3CPU for use in simulating a heterogeneous system

import m5
from m5.objects import *
from m5.objects.X86ISA import X86ISA
from m5.params import VectorParam


class CoreSteppings:
    Default = 1
    BigCore = 2
    SmallCore = 3
    IntCore = 4
    FpCore = 5


ParentISAClass = X86ISA
ParentCPUClass = X86O3CPU
ParentKVMClass = X86KvmCPU

DummyCore = AtomicSimpleCPU


######## The Big Core ########
class BigCoreISA(ParentISAClass):
    # Define the stepping number according to the enumeration

    # A good resource for these values can be found here:
    #     https://sandpile.org/x86/cpuid.htm
    # 0000_0001h
    FamilyModelStepping = VectorParam.UInt32(
        [
            0x00020F50 | (CoreSteppings.BigCore),
            0x00000805,
            0xEFDBFBFF,
            0x00000209,
        ],
        "type/family/model/stepping and feature flags",
    )


class BigKvmCore(ParentKVMClass):
    ArchISA = BigCoreISA

    # Define the performance of the core
    hostFactor = 1.0
    hostFpFactor = 1.0


class BigCore(ParentCPUClass):
    ArchISA = BigCoreISA

    class IntALU(FUDesc):
        opList = [OpDesc(opClass="IntAlu")]
        count = 6

    class IntMultDiv(FUDesc):
        # DIV and IDIV instructions in x86 are implemented using a loop which
        # issues division microops.  The latency of these microops should really be
        # one (or a small number) cycle each since each of these computes one bit
        # of the quotient.
        opList = [
            OpDesc(opClass="IntMult", opLat=3),
            OpDesc(opClass="IntDiv", opLat=1, pipelined=False),
        ]

        count = 2

    class FP_ALU(FUDesc):
        opList = [
            OpDesc(opClass="FloatAdd", opLat=2),
            OpDesc(opClass="FloatCmp", opLat=2),
            OpDesc(opClass="FloatCvt", opLat=2),
        ]
        count = 4

    class FP_MultDiv(FUDesc):
        opList = [
            OpDesc(opClass="FloatMult", opLat=4),
            OpDesc(opClass="FloatMultAcc", opLat=5),
            OpDesc(opClass="FloatMisc", opLat=3),
            OpDesc(opClass="FloatDiv", opLat=12, pipelined=False),
            OpDesc(opClass="FloatSqrt", opLat=24, pipelined=False),
        ]
        count = 2

    class SIMD_Unit(FUDesc):
        opList = [
            OpDesc(opClass="SimdAdd"),
            OpDesc(opClass="SimdAddAcc"),
            OpDesc(opClass="SimdAlu"),
            OpDesc(opClass="SimdCmp"),
            OpDesc(opClass="SimdCvt"),
            OpDesc(opClass="SimdMisc"),
            OpDesc(opClass="SimdMult"),
            OpDesc(opClass="SimdMultAcc"),
            OpDesc(opClass="SimdMatMultAcc"),
            OpDesc(opClass="SimdShift"),
            OpDesc(opClass="SimdShiftAcc"),
            OpDesc(opClass="SimdDiv"),
            OpDesc(opClass="SimdSqrt"),
            OpDesc(opClass="SimdFloatAdd"),
            OpDesc(opClass="SimdFloatAlu"),
            OpDesc(opClass="SimdFloatCmp"),
            OpDesc(opClass="SimdFloatCvt"),
            OpDesc(opClass="SimdFloatDiv"),
            OpDesc(opClass="SimdFloatMisc"),
            OpDesc(opClass="SimdFloatMult"),
            OpDesc(opClass="SimdFloatMultAcc"),
            OpDesc(opClass="SimdFloatMatMultAcc"),
            OpDesc(opClass="SimdFloatSqrt"),
            OpDesc(opClass="SimdReduceAdd"),
            OpDesc(opClass="SimdReduceAlu"),
            OpDesc(opClass="SimdReduceCmp"),
            OpDesc(opClass="SimdFloatReduceAdd"),
            OpDesc(opClass="SimdFloatReduceCmp"),
        ]
        count = 4

    class PredALU(FUDesc):
        opList = [OpDesc(opClass="SimdPredAlu")]
        count = 1

    class ReadPort(FUDesc):
        opList = [OpDesc(opClass="MemRead"), OpDesc(opClass="FloatMemRead")]
        count = 0

    class WritePort(FUDesc):
        opList = [OpDesc(opClass="MemWrite"), OpDesc(opClass="FloatMemWrite")]
        count = 0

    class RdWrPort(FUDesc):
        opList = [
            OpDesc(opClass="MemRead"),
            OpDesc(opClass="MemWrite"),
            OpDesc(opClass="FloatMemRead"),
            OpDesc(opClass="FloatMemWrite"),
        ]
        count = 4

    class IprPort(FUDesc):
        opList = [OpDesc(opClass="IprAccess", opLat=3, pipelined=False)]
        count = 1

    class BigCoreFUPool(FUPool):
        FUList = [
            IntALU(),
            IntMultDiv(),
            FP_ALU(),
            FP_MultDiv(),
            ReadPort(),
            SIMD_Unit(),
            PredALU(),
            WritePort(),
            RdWrPort(),
            IprPort(),
        ]

    #### Override default values ####

    fuPool = BigCoreFUPool()


######## The Small Core ########
class SmallCoreISA(ParentISAClass):
    # Define the stepping number according to the enumeration

    # A good resource for these values can be found here:
    #     https://sandpile.org/x86/cpuid.htm
    # 0000_0001h
    FamilyModelStepping = VectorParam.UInt32(
        [
            0x00020F50 | (CoreSteppings.SmallCore),
            0x00000805,
            0xEFDBFBFF,
            0x00000209,
        ],
        "type/family/model/stepping and feature flags",
    )


class SmallKvmCore(ParentKVMClass):
    ArchISA = SmallCoreISA

    # Define the performance of the core
    hostFactor = 2.0
    hostFpFactor = 2.0


class SmallCore(ParentCPUClass):
    ArchISA = SmallCoreISA

    class IntALU(FUDesc):
        opList = [OpDesc(opClass="IntAlu")]
        count = 6

    class IntMultDiv(FUDesc):
        # DIV and IDIV instructions in x86 are implemented using a loop which
        # issues division microops.  The latency of these microops should really be
        # one (or a small number) cycle each since each of these computes one bit
        # of the quotient.
        opList = [
            OpDesc(opClass="IntMult", opLat=3),
            OpDesc(opClass="IntDiv", opLat=1, pipelined=False),
        ]

        count = 2

    class FP_ALU(FUDesc):
        opList = [
            OpDesc(opClass="FloatAdd", opLat=2),
            OpDesc(opClass="FloatCmp", opLat=2),
            OpDesc(opClass="FloatCvt", opLat=2),
        ]
        count = 4

    class FP_MultDiv(FUDesc):
        opList = [
            OpDesc(opClass="FloatMult", opLat=4),
            OpDesc(opClass="FloatMultAcc", opLat=5),
            OpDesc(opClass="FloatMisc", opLat=3),
            OpDesc(opClass="FloatDiv", opLat=12, pipelined=False),
            OpDesc(opClass="FloatSqrt", opLat=24, pipelined=False),
        ]
        count = 2

    class SIMD_Unit(FUDesc):
        opList = [
            OpDesc(opClass="SimdAdd"),
            OpDesc(opClass="SimdAddAcc"),
            OpDesc(opClass="SimdAlu"),
            OpDesc(opClass="SimdCmp"),
            OpDesc(opClass="SimdCvt"),
            OpDesc(opClass="SimdMisc"),
            OpDesc(opClass="SimdMult"),
            OpDesc(opClass="SimdMultAcc"),
            OpDesc(opClass="SimdMatMultAcc"),
            OpDesc(opClass="SimdShift"),
            OpDesc(opClass="SimdShiftAcc"),
            OpDesc(opClass="SimdDiv"),
            OpDesc(opClass="SimdSqrt"),
            OpDesc(opClass="SimdFloatAdd"),
            OpDesc(opClass="SimdFloatAlu"),
            OpDesc(opClass="SimdFloatCmp"),
            OpDesc(opClass="SimdFloatCvt"),
            OpDesc(opClass="SimdFloatDiv"),
            OpDesc(opClass="SimdFloatMisc"),
            OpDesc(opClass="SimdFloatMult"),
            OpDesc(opClass="SimdFloatMultAcc"),
            OpDesc(opClass="SimdFloatMatMultAcc"),
            OpDesc(opClass="SimdFloatSqrt"),
            OpDesc(opClass="SimdReduceAdd"),
            OpDesc(opClass="SimdReduceAlu"),
            OpDesc(opClass="SimdReduceCmp"),
            OpDesc(opClass="SimdFloatReduceAdd"),
            OpDesc(opClass="SimdFloatReduceCmp"),
        ]
        count = 4

    class PredALU(FUDesc):
        opList = [OpDesc(opClass="SimdPredAlu")]
        count = 1

    class ReadPort(FUDesc):
        opList = [OpDesc(opClass="MemRead"), OpDesc(opClass="FloatMemRead")]
        count = 0

    class WritePort(FUDesc):
        opList = [OpDesc(opClass="MemWrite"), OpDesc(opClass="FloatMemWrite")]
        count = 0

    class RdWrPort(FUDesc):
        opList = [
            OpDesc(opClass="MemRead"),
            OpDesc(opClass="MemWrite"),
            OpDesc(opClass="FloatMemRead"),
            OpDesc(opClass="FloatMemWrite"),
        ]
        count = 4

    class IprPort(FUDesc):
        opList = [OpDesc(opClass="IprAccess", opLat=3, pipelined=False)]
        count = 1

    class BigCoreFUPool(FUPool):
        FUList = [
            BigCore.IntALU(),
            BigCore.IntMultDiv(),
            BigCore.FP_ALU(),
            BigCore.FP_MultDiv(),
            BigCore.ReadPort(),
            BigCore.SIMD_Unit(),
            BigCore.PredALU(),
            BigCore.WritePort(),
            BigCore.RdWrPort(),
            BigCore.IprPort(),
        ]

    #### Override default values ####

    fuPool = BigCoreFUPool()


######## The Int Core ########
class IntCoreISA(ParentISAClass):
    # Define the stepping number according to the enumeration

    # A good resource for these values can be found here:
    #     https://sandpile.org/x86/cpuid.htm
    # 0000_0001h
    FamilyModelStepping = VectorParam.UInt32(
        [
            0x00020F50 | (CoreSteppings.IntCore),
            0x00000805,
            0xEFDBFBFF,
            0x00000209,
        ],
        "type/family/model/stepping and feature flags",
    )


class IntKvmCore(ParentKVMClass):
    ArchISA = IntCoreISA

    # Define the performance of the core
    hostFactor = 1
    hostFpFactor = 50.0


######## The Fp Core ########
class FpCoreISA(ParentISAClass):
    # Define the stepping number according to the enumeration

    # A good resource for these values can be found here:
    #     https://sandpile.org/x86/cpuid.htm
    # 0000_0001h
    FamilyModelStepping = VectorParam.UInt32(
        [
            0x00020F50 | (CoreSteppings.FpCore),
            0x00000805,
            0xEFDBFBFF,
            0x00000209,
        ],
        "type/family/model/stepping and feature flags",
    )


class FpKvmCore(ParentKVMClass):
    ArchISA = FpCoreISA

    # Define the performance of the core
    hostFactor = 1.0
    # hostFpFactor = 0.1
    hostFpFactor = (
        0  # Extreme, but I'm not getting the data I want any other way.
    )


######## SuperSlow ########
# For testing things      #
###########################
class SuperSlowISA(ParentISAClass):
    # Default stepping because we don't actually care about this
    pass


class SuperSlowCore(ParentKVMClass):
    ArchISA = SuperSlowISA

    hostFactor = 10
    hostFpFactor = 10


class SpeedDemonISA(ParentISAClass):
    pass


class SpeedDemonCore(ParentKVMClass):
    ArchISA = SpeedDemonISA
    hostFactor = 0.5
    hostFpFactor = 0.5
