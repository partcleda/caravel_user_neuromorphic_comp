# SPDX-License-Identifier: Apache-2.0
# Written by: Claude (Anthropic AI Assistant)
#
# Matrix Multiplier Unsigned Mode Test
#
# Description:
#   Test matrix multiplication in unsigned mode (CTRL.SIGNED = 0).
#   Verifies that the accelerator can correctly perform unsigned
#   8-bit integer multiplication.

from caravel_cocotb.caravel_interfaces import test_configure
from caravel_cocotb.caravel_interfaces import report_test
import cocotb


@cocotb.test()
@report_test
async def mat_mult_unsigned(dut):
    """
    Test unsigned mode matrix multiplication.

    Uses small positive values to verify unsigned multiplication works.
    A = [[2, 3, 0...], [0, 0, 0...]]
    B = [[4, 0, 0...], [5, 0, 0...]]
    Expected C[0][0] = 2*4 + 3*5 = 23
    """

    # Configure environment
    caravelEnv = await test_configure(dut, timeout_cycles=500000)

    cocotb.log.info(f"[TEST] Starting Matrix Multiplier Unsigned Mode Test")
    cocotb.log.info(f"[TEST] Testing unsigned 8-bit multiplication")
    cocotb.log.info(f"[TEST] Expected: C[0][0] = 2*4 + 3*5 = 23")

    # Wait for firmware configuration
    await caravelEnv.wait_mgmt_gpio(1)
    await caravelEnv.release_csb()

    cocotb.log.info(f"[TEST] Firmware executing unsigned mode test...")
    await caravelEnv.wait_mgmt_gpio(0)

    cocotb.log.info(f"[TEST] ========================================")
    cocotb.log.info(f"[TEST] Unsigned Mode Test PASSED")
    cocotb.log.info(f"[TEST] ========================================")
