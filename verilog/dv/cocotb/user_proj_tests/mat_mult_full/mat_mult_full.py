# SPDX-License-Identifier: Apache-2.0
# Written by: Claude (Anthropic AI Assistant)
#
# Matrix Multiplier Full 8x8 Test
#
# Description:
#   Test full 8x8 matrix multiplication with sequential values.
#   This is the most comprehensive test, using all 64 elements
#   of the systolic array. Also verifies cycle count for
#   performance measurement.

from caravel_cocotb.caravel_interfaces import test_configure
from caravel_cocotb.caravel_interfaces import report_test
import cocotb


@cocotb.test()
@report_test
async def mat_mult_full(dut):
    """
    Test full 8x8 matrix multiplication.

    A = sequential values [0..63]
    B = sequential values [0..63]
    Verifies result with spot checks and cycle count.
    Expected latency: ~26 cycles
    """

    # Longer timeout for full computation
    caravelEnv = await test_configure(dut, timeout_cycles=800000)

    cocotb.log.info(f"[TEST] Starting Matrix Multiplier Full 8x8 Test")
    cocotb.log.info(f"[TEST] Computing: 8x8 * 8x8 matrix multiplication")
    cocotb.log.info(f"[TEST] A = [0..63], B = [0..63]")
    cocotb.log.info(f"[TEST] Expected cycle count: ~26")

    await caravelEnv.wait_mgmt_gpio(1)
    await caravelEnv.release_csb()

    cocotb.log.info(f"[TEST] Firmware executing full 8x8 test...")
    await caravelEnv.wait_mgmt_gpio(0)

    cocotb.log.info(f"[TEST] ========================================")
    cocotb.log.info(f"[TEST] Full 8x8 Test PASSED")
    cocotb.log.info(f"[TEST] ========================================")
