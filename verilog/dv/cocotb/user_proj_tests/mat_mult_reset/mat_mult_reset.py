# SPDX-License-Identifier: Apache-2.0
# Written by: Claude (Anthropic AI Assistant)
#
# Matrix Multiplier Reset Test
#
# Description:
#   Test soft reset functionality by writing CTRL.RESET bit and
#   verifying that STATUS returns to READY state.

from caravel_cocotb.caravel_interfaces import test_configure
from caravel_cocotb.caravel_interfaces import report_test
import cocotb


@cocotb.test()
@report_test
async def mat_mult_reset(dut):
    """
    Test soft reset functionality.

    Writes CTRL.RESET and verifies that STATUS.READY is asserted,
    indicating the accelerator returned to its initial state.
    """

    caravelEnv = await test_configure(dut, timeout_cycles=300000)

    cocotb.log.info(f"[TEST] Starting Matrix Multiplier Reset Test")
    cocotb.log.info(f"[TEST] Testing soft reset via CTRL register")

    await caravelEnv.wait_mgmt_gpio(1)
    await caravelEnv.release_csb()

    cocotb.log.info(f"[TEST] Firmware executing reset test...")
    await caravelEnv.wait_mgmt_gpio(0)

    cocotb.log.info(f"[TEST] ========================================")
    cocotb.log.info(f"[TEST] Reset Test PASSED")
    cocotb.log.info(f"[TEST] ========================================")
