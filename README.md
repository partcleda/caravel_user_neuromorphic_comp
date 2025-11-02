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

## Replicating Locally

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

5. **Edit Behavioral Model Name in IP:**

The cocotb simulation flow uses `verilog/includes/includes.rtl.caravel_user_project` as its source files, which includes a path to the Neuromorphic IP behavioral model. In order to avoid making a second `user_project_wrapper.v`, it is simpler to modify the behavioral model module name from `Neuromorphic_X1` to `Neuromorphic_X1_wb` to align with the stub that is used when actually hardening. With this change, the same `user_project_wrapper.v` works for both (cocotb) testbenching as well as hardening.

In other words, rename line 16...
```
File: ip/Neuromorphic_X1_32x32/hdl/beh_model/Neuromorphic_X1_Beh.v
16: module Neuromorphic_X1_wb (
```

6. **Run Testbenches:**

```bash
make cocotb-verify-all-rtl
```

7. **Harden the Design:**

```bash
make user_project_wrapper
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
