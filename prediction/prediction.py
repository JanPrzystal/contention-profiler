from typing import List, Dict
from experiment_setup.workload import Workload
from collections import namedtuple
from profiling.contentiousness import read_contentiousness

from scipy.interpolate import PchipInterpolator

import config
from itertools import combinations
import csv
import prediction.prediction as prediction

from experiment_setup.log import log, setup_logging, DEBUG

from concurrent.futures import ProcessPoolExecutor
from itertools import repeat
from collections import defaultdict


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

def _form_pair_prediction(
    app: str,
    competitor: str,
    scores: Dict[str, float],
    sensitivity: dict[str, PchipInterpolator],
) -> Prediction:
    contention = scores[competitor]
    prediction = sensitivity[app](contention)
    # Divide isolated performance by predicted performance to normalize
    return Prediction(app=app, competitor=competitor, perf=sensitivity[app](0) / prediction, contentiousness=contention)


def predict_total_contention(competitors: List[Workload]) -> float:
    if config.USE_SIMPLE_CONTENTIOUSNESS:
        contentiousness = _get_contentiousness()

        # Sum the sensitivity of all competitors
        total_contention = sum(contentiousness[comp.name] for comp in competitors)
        return total_contention
    
    else:
        # TODO calculate the contentiousness equilibrium
        raise NotImplementedError() 

def predict_app_performance(application: Workload, competitors: List[Workload]) -> Prediction:
    sensitivity = get_sensitivity(application.name)

    total_contention = predict_total_contention(competitors)

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

    return Prediction(app=application.name, competitor=" + ".join(comp.name for comp in competitors), perf=sensitivity(0) / prediction, contentiousness=total_contention)

def predict_pair_performance(applications: List[Workload], competitors: List[Workload]) -> List[Prediction]:
    scores = _get_contentiousness()

    sensitivity = {app.name: get_sensitivity(app.name) for app in applications}

    res = []
    for app in applications:
        for competitor in competitors:
            if competitor.name == app.name:
                continue
            prediction = _form_pair_prediction(app.name, competitor.name, scores, sensitivity)
            res.append(prediction)

    with open(f"{config.RESULTS_DIR}/predictions_pairs.csv", "w") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(Prediction._fields)
        for pred in res:
            row = [str(c) for c in list(pred._asdict().values())]
            writer.writerow(row)

    return res

def _predict_app(app, all_apps):
    # setup_logging()
    # log(f"Forming predictions for {app.name}")
    result = defaultdict(list)
    all_competitors = [x for x in all_apps if x != app]
    # Generate predictions for all combinations of competitors
    # Currently just combinations, no multisets
    for k in range(1, len(all_competitors) + 1):
        if k > config.MAX_COMPETITORS:
            break

        result[k].extend(
            _predict_with_competitors(app, all_competitors, k)
        )

    return result

def predict_performance(applications: List[Workload]) -> dict[int, List[Prediction]]:
    predictions = defaultdict(list)

    # with ProcessPoolExecutor() as executor:

    #     results = executor.map(
    #         _predict_app,
    #         applications,
    #         repeat(applications)
    #     )
    #     for result in results:
    #         for k, values in result.items():
    #             predictions[k].extend(values)
    
    # return dict(predictions)
    
    for app in applications:
        log(f"Forming predictions for {app.name}")
        prediction = _predict_app(app, applications)

        for k, values in prediction.items():
            predictions[k].extend(values)

    return predictions

def _predict_with_competitors(application: Workload, competitors: List[Workload], n_competitors: int) -> List[Prediction]:
    predictions = []
    for competitors in combinations(competitors, n_competitors):
        predictions.append(prediction.predict_app_performance(application, competitors))
    
    return predictions

def save_predictions(predictions: dict[int, List[Prediction]]) -> None:
    for k, pred_list in predictions.items():
        with open(f"{config.RESULTS_DIR}/predictions_{k}comp.csv", "w") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(prediction.Prediction._fields)
            for pred in pred_list:
                row = [str(c) for c in list(pred._asdict().values())]
                writer.writerow(row)