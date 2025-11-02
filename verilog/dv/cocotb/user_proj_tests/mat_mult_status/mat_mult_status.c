// SPDX-License-Identifier: Apache-2.0
// Written by: Claude (Anthropic AI Assistant)
//
// Matrix Multiplier STATUS Register Test
//
// Description:
//   Reads the STATUS register and verifies the READY bit is set.
//   This validates that the accelerator initializes to a ready state.

#define USER_ADDR_SPACE_C_HEADER_FILE
#include <firmware_apis.h>
#include <custom_user_space.h>
#include <stddef.h>
#include <stdint.h>

// Custom memset for compiler-generated calls
void *memset(void *s, int c, size_t n)
{
    unsigned char *p = (unsigned char *)s;
    while (n--) {
        *p++ = (unsigned char)c;
    }
    return s;
}

// Address definitions
#define MATMUL_BASE       0x31000000
#define MATMUL_STATUS     (MATMUL_BASE + 0x004)

// Status bits
#define STATUS_BUSY       (1 << 0)
#define STATUS_DONE       (1 << 1)
#define STATUS_READY      (1 << 2)
#define STATUS_STICKY_DONE (1 << 3)

// Simple delay
static inline void wait_cycles(uint32_t cycles)
{
    for (uint32_t i = 0; i < cycles; i++) {
        __asm__ volatile ("nop");
    }
}

void main()
{
    uint8_t test_passed = 0;

    // Initialize hardware
    ManagmentGpio_outputEnable();
    ManagmentGpio_write(0);
    GPIOs_configureAll(GPIO_MODE_USER_STD_OUT_MONITORED);
    GPIOs_loadConfigs();

    // Enable Wishbone interface to user project
    User_enableIF(1);

    // Signal ready to cocotb
    ManagmentGpio_write(1);

    // Small delay for stability
    wait_cycles(100);

    // Read STATUS register
    uint32_t status = *((volatile uint32_t *)MATMUL_STATUS);

    // Check if READY bit is set
    if (status & STATUS_READY) {
        test_passed = 1;
    }

    // Additional delay
    wait_cycles(100);

    // Signal completion to cocotb
    if (test_passed) {
        ManagmentGpio_write(0);
    }

    // Loop forever
    while (1) {
        wait_cycles(1000);
    }
}
