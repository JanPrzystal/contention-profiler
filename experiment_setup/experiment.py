from pathlib import Path
import yaml
from dataclasses import dataclass
from analysis import draw_sensitivity, draw_validation
from experiment_setup import spec
from experiment_setup.cpu_freq import CpuFreqPolicy, Governor
import config

import experiment_setup.reporter as rp
from experiment_setup.workload import Workload

from prediction.deployment import Deployment, MULTI_VALIDATION_DEPLOYMENTS, CPU_VALIDATION_DEPLOYMENTS, create_random_deployment
from profiling import profile_workload
from profiling import profile_reporter
from prediction import prediction, validation
from experiment_setup.spec import SpecWorkload
from time import time
from datetime import datetime
from experiment_setup.log import log, DEBUG, ERROR
import experiment_setup.core_manager as cm


@dataclass
class SoIConfig:
    type: str
    number: int

# Experiment class holds the data of the configuration of a single experiment run
@dataclass
class Experiment:
    name: str
    benchmarks: list[str]
    reporter: str
    soi: SoIConfig
    max_mem_footprint: int
    mem_interval: int
    max_competitors: int
    reporter_repetitions: int
    deployment: str
    root: bool
    data_size: str
    profiling_repetitions: int
    use_interpolation: bool
    progressive_profiling: bool
    validations: int
    simple_contentiousness: bool
    background_cores: list[int]


def parse_config():
    with open("experiments.yaml", "r") as f:
        config = yaml.safe_load(f)

    experiments = []
    for exp in config["experiments"]:
        soi = SoIConfig(**exp["soi"])
        experiment = Experiment(
            name=exp["name"],
            benchmarks=exp["benchmarks"],
            reporter=exp["reporter"],
            soi=soi,
            max_mem_footprint=exp["max_mem_footprint"],
            max_competitors=exp["max_competitors"],
            mem_interval=exp["mem_interval"],
            reporter_repetitions=exp["reporter_repetitions"],
            deployment=exp["deployment"],
            root=exp["root"],
            data_size=exp["data_size"],
            profiling_repetitions=exp["profiling_repetitions"],
            use_interpolation=exp["use_interpolation"],
            progressive_profiling=exp["progressive_profiling"],
            validations=exp["validations"],
            simple_contentiousness=exp["simple_contentiousness"],
            background_cores=exp["background_cores"].split(","),
        )
        experiments.append(experiment)
        log(exp)

    return experiments



def predict_performance_applications(applications: list[Workload]) -> dict[int, list[prediction.Prediction]]:
    predictions = prediction.predict_performance(applications)
    prediction.save_predictions(predictions)

    return predictions

def predict_performance_deployments(deployments: list[Deployment]) -> dict[int, list[prediction.Prediction]]:
    predictions = prediction.predict_deployments(deployments)
    prediction.save_predictions(predictions)

    return predictions

def sample_deployments(
        applications: list[Workload], 
        ncompetitors: int, 
        random_samples: int, 
        add_predefined: bool = True,
        only_max_competitors: bool = False
    ) -> list[Deployment]:
    deployments = []

    if add_predefined:
        if ncompetitors < 8:
            deployments += MULTI_VALIDATION_DEPLOYMENTS
        else:
            deployments += CPU_VALIDATION_DEPLOYMENTS

    if only_max_competitors:
        for _ in range(random_samples):
            deployment = create_random_deployment(ncompetitors, applications)
            deployments.append(deployment)

    else:
        samples = random_samples // ncompetitors
        for i in range(1, ncompetitors + 1):
            for _ in range(samples):    
                deployment = create_random_deployment(i, applications)
                deployments.append(deployment)

    return deployments
    

def check_profiling_state() -> int:
    reporter_file = Path(config.RESULTS_DIR + "/reporter_sensitivity.csv")
    if not reporter_file.is_file() or reporter_file.stat().st_size == 0:
        # log(f"Reporter file {reporter_file} does not exist or is empty", ERROR)
        return 0 

    contentiousness = Path(config.RESULTS_DIR + "/contentiousness.csv").is_file() or Path(config.RESULTS_DIR + "/contentiousness").is_dir()
    if not contentiousness:
        return 1
    
    sensitivity_dir = Path(config.RESULTS_DIR + "/sensitivity")
    if not sensitivity_dir.is_dir() or not any(sensitivity_dir.iterdir()):
        return 2

    return 3

def conduct_experiment(reporter: Workload, applications: list[Workload], pairwise: bool):
    # Timers
    tstart, treporter, tcontentiousness, tsensitivity = 0, 0, 0, 0

    # Check if the experiment can be resumed
    profiling_state = check_profiling_state()
    log(f"Profiling state: {profiling_state}")
    if profiling_state < 1:
        # Sensitivity and contentiousness profiling
        tstart = time()
        profile_reporter.profile_reporter(reporter)
        treporter = time() - tstart

    if profiling_state < 2:
        max_contentiousness = profile_workload.profile_contentiousness(applications, reporter)
        tcontentiousness = time() - tstart - treporter
        if max_contentiousness is not None and pairwise:
            # For multi-competitor the maximum contentiousness cannot be easily assumed
            log(f"Max contentiousness across all workloads: {max_contentiousness}")
            config.DIAL_END_MB = int(max_contentiousness) + 1

    if profiling_state < 3:
        profile_workload.profile_sensitivity(applications)
        tsensitivity = time() - tstart - treporter - tcontentiousness

    # contentiousness.save_contentiousness_chart()
    # draw_contentiousness()

    ttotal = time() - tstart
    log("Profiling complete")

    # Predictions and validations
    if pairwise:
        log("Starting pairwise prediction and validation")
        predictions = prediction.predict_pair_performance(applications, applications)
        validated_predictions = validation.validate_pair_predictions(applications, applications, predictions)
        validation.save_validated_predictions(validated_predictions)
    else:
        deployments = sample_deployments(
            applications, 
            config.MAX_COMPETITORS, 
            config.VALIDATIONS, 
            config.PREDEFINED_VALIDATIONS,
            True
        )

        predictions = predict_performance_deployments(deployments)

        prediction_list = []
        for plist in list(predictions.values()):
            prediction_list.extend(plist)

        log(f"Formed {len(prediction_list)} predictions")

        validated_predictions = []
        validated_predictions = validation.validate_predictions(prediction_list)

        validation.save_validated_predictions(validated_predictions)

    texperiment = time() - tstart
    log(f"Experiment timings: \nreporter={treporter:.3f}s, \ncontentiousness={tcontentiousness:.3f}s, \nsensitivity={tsensitivity:.3f}s, \nprofiling total={ttotal:.3f}s, \nexperiment total={texperiment:.3f}s")

    # Write the times to a file
    with open(f"{config.RESULTS_DIR}/timings.txt", "w") as f:
        f.write(f"reporter={treporter:.3f}s\n")
        f.write(f"contentiousness={tcontentiousness:.3f}s\n")
        f.write(f"sensitivity={tsensitivity:.3f}s\n")
        f.write(f"profiling_total={ttotal:.3f}s\n")
        f.write(f"experiment_total={texperiment:.3f}s\n")


def setup_config(experiment: Experiment) -> None:
    config.DIAL_STEP_MB = experiment.mem_interval
    config.DIAL_END_MB = experiment.max_mem_footprint
    config.DIAL_RANGE_MB = config.DIAL_END_MB
    config.NSOI = experiment.soi.number
    config.BUBBLE_TYPE = experiment.soi.type
    config.REPORTER_REPETITIONS = experiment.reporter_repetitions
    config.DATA_SIZE = experiment.data_size
    config.USE_ROOT_PRIORITY = experiment.root
    config.PROFILING_REPETITIONS = experiment.profiling_repetitions
    config.USE_INTERPOLATION = experiment.use_interpolation
    config.PROGRESSIVE_PROFILING = experiment.progressive_profiling
    config.VALIDATIONS = experiment.validations
    config.USE_SIMPLE_CONTENTIOUSNESS = experiment.simple_contentiousness
    config.MAX_COMPETITORS = experiment.max_competitors
    if len(experiment.background_cores) < 1:
        log("NO BACKGROUND CORES SPECIFIED!", ERROR)
    else:
        cm.background_core_dispenser = cm.CoreManager(experiment.background_cores)

def setup_reporter(experiment: Experiment) -> Workload:
    reporter = None

    if experiment.reporter == "tinymembench":
        script = "tinymembench"
        reporter = rp.MembenchReporter(script)
    elif experiment.reporter == "omnetpp":
        reporter = spec.omnetpp
    elif experiment.reporter == "alternating":
        reporter = rp.AveragingReporter(experiment.reporter)
    else:
        log(f"Unknown Reporter {experiment.reporter}\nDefaulting to alternating", ERROR)
        reporter = rp.AveragingReporter("alternating")

    return reporter

def write_description_file(experiment: Experiment) -> None:
    with open(f"{config.RESULTS_DIR}/description.txt", "w") as f:
        f.write(f"Time of experiment: {datetime.now()}\n")
        f.write(f"Experiment: {experiment.name}\n")
        f.write(f"Benchmarks: {', '.join(experiment.benchmarks)}\n")
        f.write(f"Reporter: {experiment.reporter}\n")
        f.write(f"SOI: {experiment.soi.type} ({experiment.soi.number})\n")
        f.write(f"Max Memory Footprint: {experiment.max_mem_footprint} MB\n")
        f.write(f"Memory Interval: {experiment.mem_interval} MB\n")
        f.write(f"Reporter Repetitions: {experiment.reporter_repetitions}\n")
        f.write(f"Profiling Repetitions: {experiment.profiling_repetitions}\n")
        f.write(f"Data Size: {experiment.data_size}\n")
        f.write(f"Root Priority: {experiment.root}\n")
        f.write(f"Progressive Profiling: {experiment.progressive_profiling}\n")
        f.write(f"Interpolation: {experiment.use_interpolation}\n")
        f.write(f"Simple Contentiousness: {experiment.simple_contentiousness}\n")
        f.write(f"Background Cores: {experiment.background_cores}\n")

        f.flush()

    log(f"Wrote description file for experiment {experiment.name}, DEBUG")

def spec_experiment(experiment: Experiment):
    setup_config(experiment)

    reporter = setup_reporter(experiment)
        
    applications = [SpecWorkload(name, config.DATA_SIZE) for name in experiment.benchmarks]

    # CPU Governor set here to take into account root priviledge configuration
    CpuFreqPolicy.set_governor(config.GOVERNOR)

    # Create a description file 
    write_description_file(experiment)

    conduct_experiment(reporter, applications, experiment.deployment == "pairwise")

    draw_sensitivity.draw_sensitivity()
    draw_validation.draw_validation()

    if experiment.deployment != "pairwise":
        data = draw_validation.get_validated_df(True)
        draw_validation.draw_errors_by_competitors([data])

