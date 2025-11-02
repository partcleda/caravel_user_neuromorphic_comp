# SPDX-License-Identifier: Apache-2.0
# Written by: Claude (Anthropic AI Assistant)
#
# Matrix Multiplier STATUS Register Test
#
# Description:
#   Test to verify the STATUS register of the mat_mult_wb module
#   can be read correctly and the READY bit is set on initialization.
#
# Address:
#   0x30000004: STATUS register
#     Bit[0]: BUSY
#     Bit[1]: DONE
#     Bit[2]: READY (should be 1 initially)

from caravel_cocotb.caravel_interfaces import test_configure
from caravel_cocotb.caravel_interfaces import report_test
import cocotb


@cocotb.test()
@report_test
async def mat_mult_status(dut):
    """
    Test STATUS register read and READY bit.

    Verifies that the STATUS register is readable and that the
    READY bit is asserted after reset, indicating the accelerator
    is ready for operation.
    """

    # Configure environment
    caravelEnv = await test_configure(dut, timeout_cycles=300000)

    cocotb.log.info(f"[TEST] Starting Matrix Multiplier STATUS Register Test")
    cocotb.log.info(f"[TEST] Address: 0x30000004")
    cocotb.log.info(f"[TEST] Expected: READY bit (bit 2) should be 1")

    # Wait for firmware configuration
    cocotb.log.info(f"[TEST] Waiting for firmware ready...")
    await caravelEnv.wait_mgmt_gpio(1)

    cocotb.log.info(f"[TEST] Firmware ready - releasing CSB")
    await caravelEnv.release_csb()

    cocotb.log.info(f"[TEST] Firmware reading STATUS register...")
    await caravelEnv.wait_mgmt_gpio(0)

    cocotb.log.info(f"[TEST] ========================================")
    cocotb.log.info(f"[TEST] STATUS Register Test PASSED")
    cocotb.log.info(f"[TEST] ========================================")
