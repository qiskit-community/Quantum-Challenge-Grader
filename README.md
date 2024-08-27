# Quantum Challenge Grader

Grading client for the IBM Quantum Challenge grading service.


### Run locally

Pre-requisites:

- [IBM Quantum account](https://quantum.ibm.com/)
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
    pip install 'qc-grader[qiskit,jupyter] @ git+https://github.com/qiskit-community/Quantum-Challenge-Grader.git'
    ```

1. Configure the `QXToken` environment variables

    From a terminal (before launching your JupyterLab environment), enter

    ```
    export QXToken=your_quantum_api_token
    ```

    where `your_quantum_api_token` is your IBM Quantum API Token found in your **[Account Profile](https://quantum.ibm.com/account)**.

    Alternatively, if you prefer you can instead run the following at the top cell of a notebook cell (whenever you start/restart the kernel)

    ```
    %set_env QXToken=your_quantum_api_token
    ```


    > 
    > **Note1**: you can check if the environment variable has been set by running the following in a notebook cell:
    > 
    > ```python
    > import os
    > print(os.getenv('QXToken'))
    > ```
    > 
    > **Note2**: If you already installed [qiskit-ibm-runtime](https://github.com/Qiskit/qiskit-ibm-runtime) and saved your token by using `QiskitRuntimeService` by following [this instruction](https://docs.quantum.ibm.com/guides/setup-channel) once, you don't need to set-up the env variable
    > 

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
