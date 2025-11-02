// SPDX-License-Identifier: Apache-2.0
// Written by: Claude (Anthropic AI Assistant)
//
// Matrix Multiplier VERSION Register Test
//
// Description:
//   Simplest test - reads the VERSION register and verifies it matches
//   the expected value 0xA7770001. This validates basic Wishbone
//   connectivity to the mat_mult_wb module.

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
#define MATMUL_VERSION    (MATMUL_BASE + 0x00C)
#define EXPECTED_VERSION  0xA7770001

// Status bits (for reference)
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

    // Read VERSION register
    uint32_t version = *((volatile uint32_t *)MATMUL_VERSION);

    // Check if version matches expected value
    if (version == EXPECTED_VERSION) {
        test_passed = 1;
    }

    // Additional delay
    wait_cycles(100);

    // Signal completion to cocotb
    // GPIO = 0 for pass, stay at 1 for fail
    if (test_passed) {
        ManagmentGpio_write(0);
    }

    // Loop forever
    while (1) {
        wait_cycles(1000);
    }
}
