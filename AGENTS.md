# Agents.md

## About the project

This project is a Python library for students to submit their answers to quantum computing challenges to a grader server. The server will return back whether the answer was correct or not.

Users use this Python library through a REPL or Jupyter notebook, rather than a traditional Python program.

Users are primarily students and are sometimes beginners to either programming or quantum computing. So, where reasonable, we try to make the program user-friendly, such as useful error messages.

## Workflows

* Format: `just fmt`
* Linter and type checker: `just lint`
* Test: `just test`
* Add new labs and exercises: refer to `CONTRIBUTING.md`
* Releases: refer to `CONTRIBUTING.md`. All user-facing changes should have a new release.
