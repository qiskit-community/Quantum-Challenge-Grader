# Quantum Challenge Grader

Grading client for the IBM Quantum Challenge grading service.


## Installation

Follow one of these steps to install the grading client.

- [Run in IBM Quantum Lab](#run-in-ibm-quantum-lab)
- [Run locally](#run-locally)


### Run in IBM Quantum Lab

Pre-requisites:

- [IBM Quantum account](https://quantum-computing.ibm.com/)

The grader comes pre-installed in Quantum Lab and does not need to be installed.
You can confirm and check version with the following command in a notebook cell:

```
!pip show qc_grader
```


### Run locally

Pre-requisites:

- [IBM Quantum account](https://quantum-computing.ibm.com/)
- [Python](https://www.python.org/) (3.10 or later) environment with
    - Classic [Jupyter Notebook](https://jupyter.readthedocs.io/en/latest/install/notebook-classic.html) interface or [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html)
    - [Qiskit](https://qiskit.org/documentation/index.html)

To install the grader locally:

1. In the Python environment, install the grading client

    ```
    pip install git+https://github.com/qiskit-community/Quantum-Challenge-Grader.git
    ```

    Alternatively, if you also need to install JupyterLab and Qiskit along with the grader you can instead run:

    ```
    pip install 'git+https://github.com/qiskit-community/Quantum-Challenge-Grader.git[qiskit,jupyter]'
    ```

1. Configure the following environment variables

    - `QXAuthURL` - IBM Quantum Authentication API URL
    - `QXToken` - IBM Quantum API Token (can be found in **Account Details**)


## Usage

1. Open an exercise notebook

    - In IBM Quantum Lab, the notebooks can be found in the `
quantum-challenge` folder in the **Lab files** panel
    - For local install, download the notebooks (from IBM Quantum Lab or specific challenge repo) and import into local Jupyter environment

1. Run the notebook cells, answering the exercises and submitting solution for grading. For example

    ```python
    from qc_grader.challenges.challenge_2021 import grade_lab1_ex1 

    grade_lab1_ex1(qc_1)
    ```
    
    
    ```python
    from qc_grader.challenges.challenge_2021 import grade_lab1_ex2 

    grade_lab1_ex2(qc_2)
    ```

