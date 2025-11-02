// SPDX-License-Identifier: Apache-2.0
// Written by: Claude (Anthropic AI Assistant)
//
// Matrix Multiplier Unsigned Mode Test

#define USER_ADDR_SPACE_C_HEADER_FILE
#include <firmware_apis.h>
#include <custom_user_space.h>
#include <stddef.h>
#include <stdint.h>

// Custom memset
void *memset(void *s, int c, size_t n)
{
    unsigned char *p = (unsigned char *)s;
    while (n--) *p++ = (unsigned char)c;
    return s;
}

#define MATMUL_BASE       0x31000000
#define MATMUL_CTRL       (MATMUL_BASE + 0x000)
#define MATMUL_STATUS     (MATMUL_BASE + 0x004)
#define MATMUL_A_BASE     (MATMUL_BASE + 0x100)
#define MATMUL_B_BASE     (MATMUL_BASE + 0x200)
#define MATMUL_C_BASE     (MATMUL_BASE + 0x400)

#define CTRL_START        (1 << 0)
#define STATUS_DONE       (1 << 1)
#define STATUS_STICKY_DONE (1 << 3)
#define MATRIX_SIZE       8
#define MAX_POLL_CYCLES   1000

static inline void wait_cycles(uint32_t cycles)
{
    for (uint32_t i = 0; i < cycles; i++) {
        __asm__ volatile ("nop");
    }
}

static inline uint32_t pack_elements(int8_t e0, int8_t e1, int8_t e2, int8_t e3)
{
    return ((uint32_t)(uint8_t)e0) | (((uint32_t)(uint8_t)e1) << 8) |
           (((uint32_t)(uint8_t)e2) << 16) | (((uint32_t)(uint8_t)e3) << 24);
}

void write_matrix_a(int8_t matrix[MATRIX_SIZE][MATRIX_SIZE])
{
    volatile uint32_t *cache = (volatile uint32_t *)MATMUL_A_BASE;
    for (int row = 0; row < MATRIX_SIZE; row++) {
        for (int col = 0; col < MATRIX_SIZE; col += 4) {
            cache[row * 2 + col/4] = pack_elements(
                matrix[row][col], matrix[row][col+1],
                matrix[row][col+2], matrix[row][col+3]
            );
        }
    }
}

void write_matrix_b(int8_t matrix[MATRIX_SIZE][MATRIX_SIZE])
{
    volatile uint32_t *cache = (volatile uint32_t *)MATMUL_B_BASE;
    for (int row = 0; row < MATRIX_SIZE; row++) {
        for (int col = 0; col < MATRIX_SIZE; col += 4) {
            cache[row * 2 + col/4] = pack_elements(
                matrix[row][col], matrix[row][col+1],
                matrix[row][col+2], matrix[row][col+3]
            );
        }
    }
}

uint8_t wait_for_done(void)
{
    for (uint32_t i = 0; i < MAX_POLL_CYCLES; i++) {
        if (*((volatile uint32_t *)MATMUL_STATUS) & STATUS_STICKY_DONE) {
            // Clear the sticky bit by writing to status register
            *((volatile uint32_t *)MATMUL_STATUS) = 0;
            return 1;
        }
        wait_cycles(10);
    }
    return 0;
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

    int8_t mat_a[MATRIX_SIZE][MATRIX_SIZE];
    int8_t mat_b[MATRIX_SIZE][MATRIX_SIZE];
    memset(mat_a, 0, sizeof(mat_a));
    memset(mat_b, 0, sizeof(mat_b));

    // Small test: A[0][0]=2, A[0][1]=3, B[0][0]=4, B[1][0]=5
    mat_a[0][0] = 2;
    mat_a[0][1] = 3;
    mat_b[0][0] = 4;
    mat_b[1][0] = 5;

    write_matrix_a(mat_a);
    write_matrix_b(mat_b);

    // Start UNSIGNED multiplication (no CTRL_SIGNED bit)
    *((volatile uint32_t *)MATMUL_CTRL) = CTRL_START;

    if (!wait_for_done()) {
        while(1);  // Timeout
    }

    // Read result C[0][0] - should be 2*4 + 3*5 = 23
    int32_t result = *((volatile uint32_t *)MATMUL_C_BASE);

    uint8_t passed = (result == 23);

    wait_cycles(100);
    if (passed) {
        ManagmentGpio_write(0);
    }

    while (1) wait_cycles(1000);
}
