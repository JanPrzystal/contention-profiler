# Performance Prediction of Co-Deployed Applications
This project implements a framework for profiling and predicting performance degradation caused by shared-resource contention between co-deployed applications. It automates the deployment of benchmark and interference workloads, measures application sensitivity and contentiousness, generates performance predictions for pairwise or multi-competitor deployments, and validates these predictions through experiments.

## Prerequisites
* Python 3.11+

## Installation

1. Create new virtual env
```shell
python -m venv venv
source venv/bin/activate
```
2. Install dependencies
```shell
pip install -r requirements.txt
```
3. Install Google Benchmark by following https://github.com/google/benchmark?tab=readme-ov-file#installation
4. Move Benchmark to repo root
5. Compile reporters:
```shell
cd reporters
chmod 700 compileReporters.sh
./compileReporters.sh
```


## Running experiments
Define experiments and their configuration in `experiments.yaml`. 

To run experiments with the SPEC2017 benchmarks the SPEC_PATH variable in `config.py` needs to point to the folder correct folder. Default value is "../cpu2017"

To run experiments, use `screen`. This is necessary because they take so long that your ssh connection will time out.

Run:

```shell
screen
python main.py
```

