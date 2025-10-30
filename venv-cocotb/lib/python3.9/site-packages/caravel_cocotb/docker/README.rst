===========
Dockerfile
===========

This Dockerfile provides instructions for building the `efabless/dv:cocotb` Docker image. This image includes various packages and tools for caravel Verification with vcs.

Docker Image Contents
---------------------

The Docker image is based on Ubuntu 22.04 and includes the following packages and tools:

- Python 3 and related libraries
- Git, Help2man, Perl, Make, Autoconf, G++, Flex, Bison, CCache, libgoogle-perftools-dev, Numactl, Perl-doc, libfl2, libfl-dev, zlib1g-dev, and other essential build tools
- Verilator v5.012
- cvc (commit b3e7fded6d4d79491886de40aec3a780efdd9d4e)
- Icarus Verilog v12
- RISC-V Toolchain v2023.07.07


The image installs the following Python packages using pip:

- `cocotb`: Coroutine-based cosimulation library for writing testbenches in Python.
- `cocotb-coverage`: A coverage analysis extension for cocotb.
- `cocotb-bus`: A library for generating bus transactions in cocotb testbenches.
- `coverage`: Code coverage measurement tool.
- `loremipsum`: A utility for generating random strings and text.
- `oyaml`: A YAML parser and emitter library.
- `prettytable`: A library for displaying tabular data in an ASCII table format.
- `anytree`: A library for building and navigating tree structures in Python.
- `caravel-cocotb`: Cocotb-based tests for the Caravel chip project.


Pulling the Docker Image
------------------------

You can pull the `efabless/dv:cocotb` Docker image from Docker Hub using the following command::

    docker pull efabless/dv:cocotb

Building the Docker Image
--------------------------

1. **Navigate to the directory containing this Dockerfile:**

    Navigate to this directory and build the Docker image using the following command::

         docker build -t efabless/dv:cocotb -f DockerFile . 

    To build diffrent image extend the image name with new tag::

        docker build -t efabless/dv:cocotb:<new_tag> . 



Pushing the Docker Image (if you have access)
-----------------------------------------------

1. Log in to Docker Hub:

    Log in to Docker Hub using the docker login command. You will need to enter your Docker Hub credentials (username and password or token).::

        docker login

2. Push the image to Docker Hub::

    push efabless/dv:cocotb
