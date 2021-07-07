# Quantum Challenge Grader

Grading client for the IBM Quantum Challenge grading service.


## Installation

Follow one of these steps to install the grading client.

- [Run in IBM Quantum Lab](#run-in-ibm-quantum-lab)
- [Run locally](#run-locally)

### Run in IBM Quantum Lab

Pre-requisites:

- [IBM Quantum account](https://quantum-computing.ibm.com/)

To install the grader in IBM Quantum Lab:

1. Log in to [IBM Quantum Lab](https://quantum-computing.ibm.com/lab)
1. Create a new or open an existing Notebook
1. In a code cell, run the following code to install the grading client

    ```
    !pip install -I git+https://github.com/qiskit-community/Quantum-Challenge-Grader.git
    ```

### Run locally

Pre-requisites:

- [IBM Quantum account](https://quantum-computing.ibm.com/)
- [Python](https://www.python.org/) (3.7 or later) environment
- Classic [Jupyter Notebook](https://jupyter.readthedocs.io/en/latest/install/notebook-classic.html) interface or [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html)

To install the grader locally:

1. In the Python environment, install the grading client

    ```
    !pip install -I git+https://github.com/qiskit-community/Quantum-Challenge-Grader.git
    ```
1. Configure the following environment variables
    
    - `QC_GRADING_ENDPOINT` - the URL to the grading server
    - `QXAuthURL` - IBM Quantum Authentication API URL
    - `QXToken` - IBM Quantum API Token (can be found in **Account Details**)


## Usage

1. Open an exercise notebook

    - In IBM Quantum Lab, the notebooks can be found in the `
quantum-challenge` folder in the **Lab files** panel
    - For local install, download the notebooks (from IBM Quantum Lab or specific challenge repo) and import into local Jupyter environment

1. Run the notebook cells, answering the exercises and submitting solution for grading. For example

    ```python
    from qc_grader import grade_lab1_ex1 

    grade_lab1_ex1(qc_1)
    ```
    
    
    ```python
    from qc_grader import grade_lab1_ex2 

    grade_lab1_ex1(qc_2)
    ```

