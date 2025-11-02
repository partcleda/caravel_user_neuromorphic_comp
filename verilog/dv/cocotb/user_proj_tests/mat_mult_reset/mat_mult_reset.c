// SPDX-License-Identifier: Apache-2.0
// Written by: Claude (Anthropic AI Assistant)
//
// Matrix Multiplier Reset Test

#define USER_ADDR_SPACE_C_HEADER_FILE
#include <firmware_apis.h>
#include <custom_user_space.h>
#include <stddef.h>
#include <stdint.h>

void *memset(void *s, int c, size_t n)
{
    unsigned char *p = (unsigned char *)s;
    while (n--) *p++ = (unsigned char)c;
    return s;
}

#define MATMUL_BASE       0x31000000
#define MATMUL_CTRL       (MATMUL_BASE + 0x000)
#define MATMUL_STATUS     (MATMUL_BASE + 0x004)

#define CTRL_RESET        (1 << 1)
#define STATUS_READY      (1 << 2)
#define STATUS_STICKY_DONE (1 << 3)

static inline void wait_cycles(uint32_t cycles)
{
    for (uint32_t i = 0; i < cycles; i++) {
        __asm__ volatile ("nop");
    }
}

void main()
{
    ManagmentGpio_outputEnable();
    ManagmentGpio_write(0);
    GPIOs_configureAll(GPIO_MODE_USER_STD_OUT_MONITORED);
    GPIOs_loadConfigs();
    User_enableIF(1);
    ManagmentGpio_write(1);
    wait_cycles(100);

    // Issue soft reset
    *((volatile uint32_t *)MATMUL_CTRL) = CTRL_RESET;

    // Wait for reset to take effect
    wait_cycles(200);

    // Check that STATUS returns to READY
    uint32_t status = *((volatile uint32_t *)MATMUL_STATUS);
    uint8_t passed = (status & STATUS_READY) ? 1 : 0;

    wait_cycles(100);
    if (passed) {
        ManagmentGpio_write(0);
    }

    while (1) wait_cycles(1000);
}
