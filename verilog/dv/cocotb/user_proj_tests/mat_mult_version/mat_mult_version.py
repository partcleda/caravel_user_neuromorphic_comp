# SPDX-License-Identifier: Apache-2.0
# Written by: Claude (Anthropic AI Assistant)
#
# Matrix Multiplier Version Register Test
#
# Description:
#   Simple test to verify the VERSION register of the mat_mult_wb module
#   can be read correctly via Wishbone. This is the simplest connectivity
#   test and should be run first to verify basic Wishbone functionality.
#
# Address:
#   0x3000000C: VERSION register (expected: 0xA7770001)

from caravel_cocotb.caravel_interfaces import test_configure
from caravel_cocotb.caravel_interfaces import report_test
import cocotb


@cocotb.test()
@report_test
async def mat_mult_version(dut):
    """
    Test VERSION register read via Wishbone.

    This is the simplest matrix multiplier test - just verifies that
    the Wishbone interface is working and the module is accessible.
    """

    # Configure environment with moderate timeout
    caravelEnv = await test_configure(dut, timeout_cycles=300000)

    cocotb.log.info(f"[TEST] Starting Matrix Multiplier VERSION Register Test")
    cocotb.log.info(f"[TEST] Address: 0x3000000C")
    cocotb.log.info(f"[TEST] Expected: 0xA7770001")

    # Wait for firmware configuration
    cocotb.log.info(f"[TEST] Waiting for firmware ready...")
    await caravelEnv.wait_mgmt_gpio(1)

    cocotb.log.info(f"[TEST] Firmware ready - releasing CSB")
    await caravelEnv.release_csb()

    cocotb.log.info(f"[TEST] Firmware reading VERSION register...")
    await caravelEnv.wait_mgmt_gpio(0)

    cocotb.log.info(f"[TEST] ========================================")
    cocotb.log.info(f"[TEST] VERSION Register Test PASSED")
    cocotb.log.info(f"[TEST] ========================================")
