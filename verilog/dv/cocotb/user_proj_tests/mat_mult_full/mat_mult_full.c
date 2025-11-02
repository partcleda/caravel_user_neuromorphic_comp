// SPDX-License-Identifier: Apache-2.0
// Written by: Claude (Anthropic AI Assistant)
//
// Matrix Multiplier Full 8x8 Test

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
#define MATMUL_CYCLES     (MATMUL_BASE + 0x008)
#define MATMUL_A_BASE     (MATMUL_BASE + 0x100)
#define MATMUL_B_BASE     (MATMUL_BASE + 0x200)
#define MATMUL_C_BASE     (MATMUL_BASE + 0x400)

#define CTRL_START        (1 << 0)
#define CTRL_SIGNED       (1 << 2)
#define STATUS_DONE       (1 << 1)
#define STATUS_STICKY_DONE (1 << 3)
#define MATRIX_SIZE       8
#define MAX_POLL_CYCLES   2000

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

uint8_t wait_for_done_no_clear(void)
{
    for (uint32_t i = 0; i < MAX_POLL_CYCLES; i++) {
        if (*((volatile uint32_t *)MATMUL_STATUS) & STATUS_STICKY_DONE) {
            // DON'T clear sticky bit to record cycles
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

    // Fill matrices with sequential values [0..63]
    for (int i = 0; i < MATRIX_SIZE; i++) {
        for (int j = 0; j < MATRIX_SIZE; j++) {
            mat_a[i][j] = i * MATRIX_SIZE + j;
            mat_b[i][j] = i * MATRIX_SIZE + j;
        }
    }

    write_matrix_a(mat_a);
    write_matrix_b(mat_b);

    // Start signed multiplication
    *((volatile uint32_t *)MATMUL_CTRL) = CTRL_START | CTRL_SIGNED;

    if (!wait_for_done_no_clear()) {
        while(1);  // Timeout
    }

    // Read cycle count
    uint32_t cycles = *((volatile uint32_t *)MATMUL_CYCLES);

    // Read result for spot checks
    volatile uint32_t *cache_c = (volatile uint32_t *)MATMUL_C_BASE;
    int32_t c_00 = (int32_t)cache_c[0];   // C[0][0]
    int32_t c_07 = (int32_t)cache_c[7];   // C[0][7]

    // Verify spot checks:
    // C[0][0] = sum(A[0][k] * B[k][0]) for k=0..7
    //         = 0*0 + 1*8 + 2*16 + 3*24 + 4*32 + 5*40 + 6*48 + 7*56
    //         = 0 + 8 + 32 + 72 + 128 + 200 + 288 + 392 = 1120
    // C[0][7] = sum(A[0][k] * B[k][7]) for k=0..7
    //         = 0*7 + 1*15 + 2*23 + 3*31 + 4*39 + 5*47 + 6*55 + 7*63
    //         = 0 + 15 + 46 + 93 + 156 + 235 + 330 + 441 = 1316

    uint8_t passed = 0;
    if (c_00 == 1120 && c_07 == 1316 && cycles >= 20 && cycles <= 50) {
        passed = 1;
    }

    wait_cycles(100);
    if (passed) {
        ManagmentGpio_write(0);
    }

    while (1) wait_cycles(1000);
}
