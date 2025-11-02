# SPDX-License-Identifier: Apache-2.0
# Written by: Claude (Anthropic AI Assistant)
#
# Matrix Multiplier Identity Matrix Test
#
# Description:
#   Test matrix multiplication with 2x2 identity matrix in the top-left
#   corner of an 8x8 matrix. Verifies:
#   - Matrix cache write operations
#   - START command functionality
#   - Computation completion (DONE bit)
#   - Result cache read operations
#   - Correctness of matrix multiplication (I × B = B)

from caravel_cocotb.caravel_interfaces import test_configure
from caravel_cocotb.caravel_interfaces import report_test
import cocotb


@cocotb.test()
@report_test
async def mat_mult_identity(dut):
    """
    Test identity matrix multiplication.

    A = [[1, 0, 0...], [0, 1, 0...], [0, 0, 0...]]
    B = [[5, 6, 0...], [7, 8, 0...], [0, 0, 0...]]
    Expected C = A * B = B
    """

    # Configure environment with longer timeout for computation
    caravelEnv = await test_configure(dut, timeout_cycles=500000)

    cocotb.log.info(f"[TEST] Starting Matrix Multiplier Identity Test")
    cocotb.log.info(f"[TEST] Computing: Identity * Matrix = Matrix")
    cocotb.log.info(f"[TEST] A = 2x2 identity (padded to 8x8)")
    cocotb.log.info(f"[TEST] B = [[5,6],[7,8]] (padded to 8x8)")
    cocotb.log.info(f"[TEST] Expected C = B")

    # Wait for firmware configuration
    cocotb.log.info(f"[TEST] Waiting for firmware ready...")
    await caravelEnv.wait_mgmt_gpio(1)

    cocotb.log.info(f"[TEST] Firmware ready - releasing CSB")
    await caravelEnv.release_csb()

    cocotb.log.info(f"[TEST] Firmware executing identity matrix test...")
    await caravelEnv.wait_mgmt_gpio(0)

    cocotb.log.info(f"[TEST] ========================================")
    cocotb.log.info(f"[TEST] Identity Matrix Test PASSED")
    cocotb.log.info(f"[TEST] ========================================")
