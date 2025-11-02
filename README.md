# Extreme-Low-Power Edge Inference Accelerator with ReRAM-based Compute 

**ChipFoundry BM Labs NVM Power-Up Design Contest Submission**

## Project Overview

This project implements a small matrix multiplication accelerator utilizing systolic arrays that, paired with BM Labs' ReRAM and Analog In-Memory Compute, enables extreme-low-power yet fast edge AI inference.

### Key Innovation Points

- **Leverage Analog In-Memory Compute**: Utilize automatic quantization for low-power AI
- **Small and Mighty**: Slim design minimizes power consumption

### Technical Highlights

- 8x8 byte matrix multiplication accelerator
- Wishbone bus interface for Caravel SoC integration
- Extreme-low-power operation

### Architecture

<img src="./Extreme-Low-Power Accelerator Block Diagram.png" alt="Block Diagram" />

## Get Started Quickly

### Follow these steps to set up your environment and harden the design:

1. **Clone the Repository:**

```bash
git clone https://github.com/partcleda/caravel_user_neuromorphic_comp.git 
```

2. **Prepare Your Environment:**

```bash
cd caravel_user_neuromorphic_comp
make setup
```

3. **Install IPM:**

```bash
pip install cf-ipm
```

4. **Install the Neuromorphic X1 IP:**

```bash
ipm install Neuromorphic_X1_32x32
```

5. **Harden the Design:**

```bash
make user_project_wrapper
```

6. **Run Testbenches:**

```bash
make cocotb-verify-all-rtl
```

## Application: Extreme-Low-Power AI

This neuromorphic accelerator targets real-time inference in extremely power-limited environments:

- **Deep space, sea inference** where on-board power limited
- **Low-cost chiplet integration** with minimal heat and cost

## Why This Design Wins

**Innovation:** Novel approach that exploits ReRAM's unique analog computing capabilities for in-memory compute, not just simple data storage.

**Practicality:** Hyper-focus on minimalist efficiency simplifes design and makes for low-risk integration in any project.

**Differentiation:** While most designs use NVM for basic memory, this leverages it for neural network inference acceleration.

## Documentation

- Details about the Neuromorphic X1 IP: [Neuromorphic X1 documentation](https://github.com/BMsemi/Neuromorphic_X1_32x32)
- Competition details: [ChipFoundry BM Labs Challenge](https://chipfoundry.io/challenges/bmlabs)

## License

This project is licensed under Apache 2.0 - see LICENSE file for details.
