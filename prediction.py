import json
from typing import List, Dict
from workload import Workload
from collections import namedtuple

from scipy.interpolate import PchipInterpolator

import config

def _get_contentiousness() -> dict[str, float]:
    scores = {}
    with open(f"{config.RESULTS_DIR}/contentiousness_scores.csv", "r") as f:
        for line in f:
            name, score = line.split(",")
            scores[name] = float(score.strip())
    return scores


def get_sensitivity(name: str) -> PchipInterpolator:
    res = {}
    sensitivity_file = name.replace(".", "_")
    with open(f"{config.RESULTS_DIR}/sensitivity/{sensitivity_file}_data.csv", "r") as f:
        next(f)
        for line in f:
            dial, perf = line.split(",")
            res[float(dial)] = float(perf)

    return PchipInterpolator(list(res.keys()), list(res.values()))

Prediction = namedtuple("Prediction", ["app", "competitor", "perf", "contentiousness"])

def _predict_pair_performance(
    app: str,
    competitor: str,
    scores: Dict[str, float],
    sensitivity: dict[str, PchipInterpolator],
) -> Prediction:
    contention = scores[competitor]
    prediction = sensitivity[app](contention)
    # Divide isolated performance by predicted performance to normalize
    return Prediction(app=app, competitor=competitor, perf=sensitivity[app](0) / prediction, contentiousness=contention)

def predict_app_performance(app: Workload, competitors: List[Workload], contention: Dict[str, float], sensitivity: PchipInterpolator) -> Prediction:
    # Combine the sensitivity of all competitors
    total_contention = sum(contention[comp.name] for comp in competitors)

    prediction = sensitivity(total_contention)
    y_min = sensitivity(0) 
    y_max = sensitivity(sensitivity.x[-1])
    for x in sensitivity.x:
        y = sensitivity(x)
        if y > y_max:
            y_max = y
            
    if prediction > y_max:
        prediction = y_max
    elif prediction < y_min:
        prediction = y_min

    return Prediction(app=app.name, competitor=" + ".join(comp.name for comp in competitors), perf=sensitivity(0) / prediction, contentiousness=total_contention)

def predict_pair_performance(applications: List[Workload], competitors: List[Workload]):
    scores = _get_contentiousness()

    sensitivity = {app.name: get_sensitivity(app.name) for app in applications}

    res = []
    for app in applications:
        for competitor in competitors:
            perf = _predict_pair_performance(app.name, competitor.name, scores, sensitivity)
            res.append(perf._asdict())

    json_data = json.dumps({"predictions": res})

    with open(f"{config.RESULTS_DIR}/predictions.json", "w") as f:
        f.write(json_data)

