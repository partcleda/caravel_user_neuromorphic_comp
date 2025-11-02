// SPDX-License-Identifier: Apache-2.0
// Written by: Claude (Anthropic AI Assistant)
//
// Matrix Multiplier Identity Matrix Test
//
// Description:
//   Test with 2x2 identity matrix multiplied by a simple 2x2 matrix.
//   This is the first test that performs actual computation.
//   Result should equal the input matrix B (since I × B = B).

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
#define MATMUL_CTRL       (MATMUL_BASE + 0x000)
#define MATMUL_STATUS     (MATMUL_BASE + 0x004)
#define MATMUL_A_BASE     (MATMUL_BASE + 0x100)
#define MATMUL_B_BASE     (MATMUL_BASE + 0x200)
#define MATMUL_C_BASE     (MATMUL_BASE + 0x400)

// Control bits
#define CTRL_START        (1 << 0)
#define CTRL_SIGNED       (1 << 2)

// Status bits
#define STATUS_BUSY       (1 << 0)
#define STATUS_DONE       (1 << 1)
#define STATUS_READY      (1 << 2)
#define STATUS_STICKY_DONE (1 << 3)

#define MATRIX_SIZE       8
#define MAX_POLL_CYCLES   1000

// Simple delay
static inline void wait_cycles(uint32_t cycles)
{
    for (uint32_t i = 0; i < cycles; i++) {
        __asm__ volatile ("nop");
    }
}

// Pack 4 8-bit elements into 32-bit word
static inline uint32_t pack_elements(int8_t e0, int8_t e1, int8_t e2, int8_t e3)
{
    return ((uint32_t)(uint8_t)e0) |
           (((uint32_t)(uint8_t)e1) << 8) |
           (((uint32_t)(uint8_t)e2) << 16) |
           (((uint32_t)(uint8_t)e3) << 24);
}

// Write 8x8 matrix to cache A
void write_matrix_a(int8_t matrix[MATRIX_SIZE][MATRIX_SIZE])
{
    volatile uint32_t *cache = (volatile uint32_t *)MATMUL_A_BASE;

    for (int row = 0; row < MATRIX_SIZE; row++) {
        for (int col = 0; col < MATRIX_SIZE; col += 4) {
            uint32_t packed = pack_elements(
                matrix[row][col],
                matrix[row][col+1],
                matrix[row][col+2],
                matrix[row][col+3]
            );
            cache[row * 2 + col/4] = packed;
        }
    }
}

// Write 8x8 matrix to cache B
void write_matrix_b(int8_t matrix[MATRIX_SIZE][MATRIX_SIZE])
{
    volatile uint32_t *cache = (volatile uint32_t *)MATMUL_B_BASE;

    for (int row = 0; row < MATRIX_SIZE; row++) {
        for (int col = 0; col < MATRIX_SIZE; col += 4) {
            uint32_t packed = pack_elements(
                matrix[row][col],
                matrix[row][col+1],
                matrix[row][col+2],
                matrix[row][col+3]
            );
            cache[row * 2 + col/4] = packed;
        }
    }
}

// Read result matrix from cache C
void read_matrix_c(int32_t result[MATRIX_SIZE][MATRIX_SIZE])
{
    volatile uint32_t *cache = (volatile uint32_t *)MATMUL_C_BASE;

    for (int row = 0; row < MATRIX_SIZE; row++) {
        for (int col = 0; col < MATRIX_SIZE; col++) {
            result[row][col] = (int32_t)cache[row * MATRIX_SIZE + col];
        }
    }
}

// Start multiplication
void start_multiplication(uint8_t signed_mode)
{
    uint32_t ctrl = CTRL_START;
    if (signed_mode) {
        ctrl |= CTRL_SIGNED;
    }
    *((volatile uint32_t *)MATMUL_CTRL) = ctrl;
}

// Wait for STICKY_DONE bit and clear it
uint8_t wait_for_done(void)
{
    uint32_t poll_count = 0;

    while (poll_count < MAX_POLL_CYCLES) {
        uint32_t status = *((volatile uint32_t *)MATMUL_STATUS);
        if (status & STATUS_STICKY_DONE) {
            // Clear the sticky bit by writing to status register
            *((volatile uint32_t *)MATMUL_STATUS) = 0;
            return 1;  // Success
        }
        wait_cycles(10);
        poll_count++;
    }

    return 0;  // Timeout
}

void main()
{
    uint8_t test_passed = 0;

    // Initialize hardware
    ManagmentGpio_outputEnable();
    ManagmentGpio_write(0);
    GPIOs_configureAll(GPIO_MODE_USER_STD_OUT_MONITORED);
    GPIOs_loadConfigs();
    User_enableIF(1);

    // Signal ready to cocotb
    ManagmentGpio_write(1);
    wait_cycles(100);

    // Create matrices
    int8_t mat_a[MATRIX_SIZE][MATRIX_SIZE];
    int8_t mat_b[MATRIX_SIZE][MATRIX_SIZE];
    int32_t result[MATRIX_SIZE][MATRIX_SIZE];

    // Initialize to zero
    memset(mat_a, 0, sizeof(mat_a));
    memset(mat_b, 0, sizeof(mat_b));

    // A = 2x2 identity in top-left corner
    mat_a[0][0] = 1;
    mat_a[1][1] = 1;

    // B = simple 2x2 matrix
    mat_b[0][0] = 5;
    mat_b[0][1] = 6;
    mat_b[1][0] = 7;
    mat_b[1][1] = 8;

    // Write matrices to accelerator
    write_matrix_a(mat_a);
    write_matrix_b(mat_b);

    // Start computation (signed mode)
    start_multiplication(1);

    // Wait for completion
    if (!wait_for_done()) {
        // Timeout - fail
        while(1);
    }

    // Read results
    read_matrix_c(result);

    // Verify: C should equal B (identity multiplication)
    if (result[0][0] == 5 && result[0][1] == 6 &&
        result[1][0] == 7 && result[1][1] == 8) {
        test_passed = 1;
    }

    wait_cycles(100);

    // Signal completion
    if (test_passed) {
        ManagmentGpio_write(0);
    }

    // Loop forever
    while (1) {
        wait_cycles(1000);
    }
}
