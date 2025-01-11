# Python Monorepos

Utilities for working with monorepos in Python.

## Installation

```bash
git clone https://github.com/JenspederM/uvmono
cd uvmono
pip install .
```

## Usage

```bash
# Show help
uvmono --help

# List all packages in the monorepo
uvmono list

# Add a package to the monorepo
uvmono new <package-name>

# Add dev-containers for a package in the monorepo
uvmono add-devcontainer <package-name>

# Add dev-containers for all packages in the monorepo
uvmono add-devcontainer --all

# Create a Matrix Strategy for a GitHub Actions workflow
uvmono matrix_strategy <key-name>
# Returns a JSON object with the matrix strategy for the packages in the monorepo:
# {
#   "matrix": {
#     "inputs": [ 
#       { 
#           "path": "packages/package1", 
#           "name": "package1", 
#           "dependencies": ["package2"], 
#           "filter":  "..." # outputs `is_changed` in dorny/paths-filter@v3
#       },
#       ...
#     ]
#   }
# }
```

# Examples

## List all packages in the monorepo

```bash
uvmono list
```

## Add a package to the monorepo

Create a new package in the monorepo with the name `my-package`.
```bash
uvmono new my-package
```

This will automatically create a new directory `packages/my-package` with the following structure:

```
.
└── packages/my-package
    ├── src
    │   └── my_package
    │       └── __init__.py
    ├── tests
    │   ├── __init__.py
    │   ├── conftest.py
    │   └── test_main.py
    ├── pyproject.toml
    └── README.md
```

## Create a Matrix Strategy for a GitHub Actions workflow

Create a matrix strategy for a GitHub Actions workflow with the key `inputs`.
```bash
uvmono matrix_strategy inputs
```

This will automatically generate a matrix strategy for the packages in the monorepo,
which can be used in a GitHub Actions workflow:

```yaml
name: CI

on:
  pull_request:
    branches:
      - main

jobs:
  build_matrix:
    name: Build Package Matrix
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.matrix_strategy.outputs.matrix }}
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true
          cache-dependency-glob: "uv.lock"
      - name: Install the project
        run: uv sync --all-extras --dev
      - name: Create Package Matrix
        id: matrix_strategy
        run: uv run uvmono matrix_strategy inputs

  test_package:
    runs-on: ubuntu-latest
    needs: build_matrix
    strategy:
      matrix: ${{ fromJson(needs.build_matrix.outputs.matrix) }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Print Inputs
        run: |
          echo "Path: ${{ matrix.inputs.path }}"
          echo "Name: ${{ matrix.inputs.name }}"
          echo "Shared: ${{ matrix.inputs.shared }}"
      - name: "Check if ${{ matrix.inputs.name }} has changed"
        uses: dorny/paths-filter@v3
        id: changes
        with:
          filters: |
            is_changed:
              - '${{ matrix.inputs.path }}/**'
            is_shared_changed:
              - 'packages/shared/**'
      ...
```