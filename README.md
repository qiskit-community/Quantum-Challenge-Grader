# Quantum Challenge Grader

Grading client for the IBM Quantum Challenge grading service.


### Run locally

Pre-requisites:

- [IBM Quantum account](https://quantum.cloud.ibm.com/)
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

1. Configure the `IBMCLOUD_API_KEY` environment variables

    From a terminal (before launching your JupyterLab environment), enter

    ```
    export IBMCLOUD_API_KEY=your_ibmcloud_api_key
    ```

    where `your_ibmcloud_api_key` is your IBM Cloud API Key found in your **[Account page](https://cloud.ibm.com/iam/apikeys)**.

    Alternatively, if you prefer you can instead run the following at the top cell of a notebook cell (whenever you start/restart the kernel)

    ```
    %set_env IBMCLOUD_API_KEY=your_ibmcloud_api_key
    ```


    > 
    > **Note1**: you can check if the environment variable has been set by running the following in a notebook cell:
    > 
    > ```python
    > import os
    > print(os.getenv('IBMCLOUD_API_KEY'))
    > ```
    > 
    > **Note2**: If you already installed [qiskit-ibm-runtime](https://github.com/Qiskit/qiskit-ibm-runtime) and saved your token by using `QiskitRuntimeService` by following [this instruction](https://quantum.cloud.ibm.com/docs/en/guides/cloud-setup#set-up-to-use-ibm-cloud) once, you don't need to set-up the env variable. You can save your token by using `QiskitRuntimeService` like below:
    >
    > ``` python
    > from qiskit_ibm_runtime import QiskitRuntimeService
    > QiskitRuntimeService.save_account(
    >     channel="ibm_quantum",
    >     token="<YOUR_TOKEN>",
    >     set_as_default=True,
    >     overwrite=True,
    > )
    > ```
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
