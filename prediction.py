import json
from typing import List, Dict
from workload import Workload
from collections import namedtuple
from contentiousness import read_contentiousness

from scipy.interpolate import PchipInterpolator

import config
import logging
from itertools import combinations
import csv
import prediction

logger = logging.getLogger(__name__)

Prediction = namedtuple("Prediction", ["app", "competitor", "perf", "contentiousness"])

def _get_contentiousness() -> dict[str, float]:
    return read_contentiousness(force_update=False)


def get_sensitivity(name: str) -> PchipInterpolator:
    res = {}
    sensitivity_file = name.replace(".", "_")
    with open(f"{config.RESULTS_DIR}/sensitivity/{sensitivity_file}_data.csv", "r") as f:
        next(f)
        for line in f:
            dial, perf = line.split(",")
            res[float(dial)] = float(perf)

    return PchipInterpolator(list(res.keys()), list(res.values()))

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

def predict_app_performance(app: Workload, competitors: List[Workload], sensitivity: PchipInterpolator) -> Prediction:
    contentiousness = _get_contentiousness()

    # Combine the sensitivity of all competitors
    total_contention = sum(contentiousness[comp.name] for comp in competitors)

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

def predict_pair_performance(applications: List[Workload], competitors: List[Workload]) -> None:
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

def predict_performance(applications: List[Workload]) -> List[Prediction]:
    predictions = []
    for app in applications:
        all_competitors = [x for x in applications if x != app]
        logger.debug(f"Competitors for {app.name}: {', '.join(c.name for c in all_competitors)}")
        # Generate predictions for all combinations of competitors
        # Currently just combinations, no multisets
        for k in range(1, len(all_competitors)):
            for competitors in combinations(all_competitors, k):
                logger.debug(f"Predicting performance for {app.name} with competitors: {', '.join(c.name for c in competitors)}")
                predictions.append(prediction.predict_app_performance(app, competitors, prediction.get_sensitivity(app.name)))

    # logger.debug(f"Predictions: {'\n'.join(str(p) for p in predictions)}")

def save_predictions(predictions: List[Prediction]) -> None:
    with open(f"{config.RESULTS_DIR}/predictions.csv", "w") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(prediction.Prediction._fields)
        for pred in predictions:
            row = [str(c) for c in list(pred._asdict().values())]
            writer.writerow(row)