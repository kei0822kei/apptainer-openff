# OpenFF + OpenMM GPU Container

This repository provides a production-ready, GPU-accelerated environment for molecular dynamics simulations using **OpenMM** and **OpenFF**. It is built using **Apptainer (formerly Singularity)** to ensure reproducibility and ease of deployment on HPC or local GPU workstations.

## Features

- **GPU-Accelerated**: Optimized for NVIDIA CUDA 12.2.
- **Reproducible**: Built with Micromamba and Conda-forge (no `defaults` channel for commercial compliance).
- **Batteries Included**: Pre-configured with OpenMM, OpenFF Toolkit, AmberTools, and essential scientific libraries.
- **Easy Verification**: Built-in installation test using OpenMM's official test suite.

## Prerequisites

- **Apptainer/Singularity** installed on the host machine.
- **NVIDIA GPU** with appropriate drivers installed.
- **NVIDIA Container Toolkit** (for `--nv` flag support).

## License

MIT.

## Getting Started

### 1. Download Container

Donwload Container:

```bash
apptainer pull oras://ghcr.io/kei0822kei/apptainer-openff/openff-cu12:latest
```

### 2. Test

Test using OpenMM official test tool:

```bash
apptainer run --nv openff-cu12.sif
```

### 3. Run Sample

```bash
cd examples
apptainer exec ../openff-cu12.sif python prepare_params.py
apptainer exec --nv ../openff-cu12.sif python run_simulation.py
```
