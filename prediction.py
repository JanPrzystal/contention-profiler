import json
from typing import List, Dict
from workload import Workload
from collections import namedtuple

import constants

def _get_contentiousness() -> dict[str, int]:
    scores = {}
    with open(f"{constants.RESULTS_DIR}/contentiousness_scores.csv", "r") as f:
        for line in f:
            name, score = line.split(",")
            scores[name] = int(score)
    return scores


def _get_sensitivity(name: str) -> dict[int, float]:
    res = {}
    sensitivity_file = name.replace(".", "_")
    with open(f"{constants.RESULTS_DIR}/sensitivity/{sensitivity_file}_data.csv", "r") as f:
        next(f)
        for line in f:
            dial, perf = line.split(",")
            res[int(dial)] = float(perf)
    return res

Prediction = namedtuple("Prediction", ["app", "competitor", "perf"])

def _predict_pair_performance(
    app: str,
    competitor: str,
    scores: Dict[str, int],
    sensitivity: dict[str, dict[int, float]],
) -> Prediction:
    prediction = sensitivity[app][scores[competitor]]
    # Divide isolated performance by predicted performance to normalize
    return Prediction(app=app, competitor=competitor, perf=sensitivity[app][0] / prediction)


def predict_performance(applications: List[Workload], competitors: List[Workload]):
    scores = _get_contentiousness()

    sensitivity = {app.name: _get_sensitivity(app.name) for app in applications}

    res = []
    for app in applications:
        for competitor in competitors:
            perf = _predict_pair_performance(app.name, competitor.name, scores, sensitivity)
            res.append(perf._asdict())

    json_data = json.dumps({"predictions": res})

    with open(f"{constants.RESULTS_DIR}/predictions.json", "w") as f:
        f.write(json_data)

