# Quantum Challenge Grader

Grading client for the IBM Quantum Challenge grading service.


## Installation

Follow one of these steps to install the grading client.

- [Run in IBM Quantum Lab](#run-in-ibm-quantum-lab)
- [Run in Docker](#run-in-docker)
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


### Run in Docker

Pre-requisites:

- [IBM Quantum account](https://quantum-computing.ibm.com/)
- [Docker](https://www.docker.com/products/docker-desktop) installed

To install the [dockerized grader client](https://hub.docker.com/r/qiskitcommunity/qc-grader) environment:

1. Create an `env` setting the following parameters. All parameters are optional and can be changed later
    
    - `QXToken` - IBM Quantum API Token (can be found in **Account Details**)
    - `QC_GH_REPO` - the org/repo name where exercise notebooks can be downloaded (e.g., `qiskit-community/ibm-quantum-challenge-2021`)
    - `QC_GH_BRANCH` - the branch in the repo to download notebooks (e.g., `main`)

    > **Note**: All parameters are optional and can be updated later

    Example `env` file:

    ```
    QC_GH_REPO=qiskit-community/ibm-quantum-challenge-2021
    QC_GH_BRANCH=main
    QXToken=1df75f29d97a46caa689bae3e3f05f477376c81b7a1157b7fe413811f6cb13c0c032f3
    ```

1. From a command prompt, run

    ```
    docker run -it -p 8888:8888 --env-file=<env_file> qiskitcommunity/qc-grader
    ```

    where `<env_file>` is the path to the `env` created in step (1).

Once running open a browser and go to `http://localhost:8888/lab` to access the Jupyter environment. Additional information is available in the `README.md` in the Jupyter environment.


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

    grade_lab1_ex2(qc_2)
    ```

