from experiment_setup.workload import Workload
from dataclasses import dataclass
import random
from experiment_setup.spec import perlbench, xalancbmk, x264, deepsjeng, leela, exchange2, nab, gcc, mcf, omnetpp, cactu, lbm, cam4, pop2, fotonik3d, roms, bwaves, xz, imagick

@dataclass
class Deployment:
    application: Workload
    competitors: list[Workload]

    def __str__(self):
        competitors_str = ", ".join([str(c) for c in self.competitors])
        return f"Application: {self.application}, Competitors: [{competitors_str}]"
    

def create_random_deployment(ncompetitors: int, all_workloads: list[Workload]) -> Deployment:
    app = random.choice(all_workloads)
    competitors = random.sample([b for b in all_workloads if b != app], ncompetitors)
    return Deployment(application=app, competitors=competitors)



MULTI_VALIDATION_DEPLOYMENTS = [
    # 7c, highest contentiousness, lowest performance
    Deployment(xz, [omnetpp, bwaves, cactu, lbm, pop2, fotonik3d, roms]),
    # 7c, highest contentiousness, high performance
    Deployment(imagick, [omnetpp, bwaves, lbm, cam4, pop2, fotonik3d, roms]),
    # 7c, lowest contentiousness, high performance
    Deployment(imagick, [perlbench, xalancbmk, x264, deepsjeng, leela, exchange2, nab]),
    Deployment(bwaves, [perlbench, xalancbmk, x264, deepsjeng, leela, exchange2, nab]),
    # 7c, lowest contentiousness, low performance
    Deployment(xz, [perlbench, xalancbmk, x264, deepsjeng, leela, exchange2, nab]),
    # 7c, lowest performance, high contentiousness
    Deployment(omnetpp, [bwaves, cactu, lbm, cam4, pop2, fotonik3d, roms]),
    Deployment(fotonik3d, [omnetpp, xalancbmk, bwaves, lbm, cam4, pop2, roms]),
    # 7c, low performance, medium contentiousness
    Deployment(roms, [gcc, mcf, omnetpp, xz, cactu, lbm, pop2]),
    # 7c, high performance, medium contentiousness
    Deployment(bwaves, [perlbench, x264, deepsjeng, leela, exchange2, lbm, imagick]),
    # 7c, high performance, low contentiousness
    Deployment(lbm, [gcc, x264, deepsjeng, leela, exchange2, imagick, nab]),
    # 7c, high performance, medium contentiousness
    Deployment(nab, [gcc, perlbench, xalancbmk, deepsjeng, leela, exchange2, fotonik3d]),
#---11---
    # bad results
    Deployment(deepsjeng, [omnetpp, bwaves, lbm]),
    Deployment(lbm, [mcf, deepsjeng, pop2, fotonik3d]),
    Deployment(cam4, [x264, deepsjeng, exchange2, pop2, nab, fotonik3d, roms]),
    Deployment(perlbench, [lbm]),
    Deployment(xalancbmk, [mcf, deepsjeng, leela, xz, bwaves, lbm]),

    Deployment(lbm, [mcf, omnetpp, bwaves, pop2, nab, fotonik3d, roms]),
    Deployment(roms, [x264, leela, lbm, pop2, nab, fotonik3d]),

    Deployment(deepsjeng, [lbm, fotonik3d]),
    Deployment(xz, [mcf, deepsjeng, leela, bwaves, lbm, nab]),
    Deployment(lbm, [perlbench, deepsjeng, bwaves, cactu, cam4]),
    Deployment(fotonik3d, [gcc, xalancbmk, deepsjeng, lbm, cam4 , pop2, nab]),
#---22---
    Deployment(lbm, [gcc, xalancbmk, deepsjeng, fotonik3d, cam4 , pop2, nab]),

    Deployment(deepsjeng, [bwaves, lbm, fotonik3d, roms]),

    Deployment(omnetpp, [bwaves, lbm, fotonik3d]),
    Deployment(roms, [mcf, bwaves, lbm, fotonik3d]),

    Deployment(omnetpp, [leela, xz, pop2, imagick]),
    Deployment(omnetpp, [mcf, deepsjeng, bwaves, lbm, fotonik3d, roms]),

    Deployment(lbm, [mcf, omnetpp, bwaves, fotonik3d, roms]),
    Deployment(lbm, [perlbench, mcf, omnetpp, deepsjeng, bwaves, fotonik3d, roms]),
#---30---
    Deployment(omnetpp, [perlbench, gcc, deepsjeng, leela, lbm, nab]),
    Deployment(roms, [gcc, omnetpp, deepsjeng, cam4]),
    Deployment(deepsjeng, [perlbench, gcc, lbm]),

    Deployment(xz, [perlbench, mcf, omnetpp, cactu]),

    Deployment(gcc, [lbm, cactu]),

    Deployment(xz, [mcf, omnetpp, cactu, lbm, fotonik3d, roms]),
    Deployment(fotonik3d, [perlbench, mcf, omnetpp, xz, cactu, lbm, roms]),

    Deployment(bwaves, [perlbench, mcf, omnetpp, xalancbmk, lbm, fotonik3d, roms]),

    Deployment(omnetpp, [perlbench, xz, cactu, lbm, fotonik3d, roms]),
    Deployment(omnetpp, [perlbench, mcf, xz, lbm, fotonik3d, roms]),
#---40---
    Deployment(perlbench, [xalancbmk, bwaves, lbm, nab]),
    # Make every benchmark be profiled and be the competitor at least once
    # 7c to look at the case when all cores are utilized
    # 7c near worst for pearlbench
    Deployment(perlbench, [mcf, omnetpp, x264, bwaves, lbm, fotonik3d, roms]),
    # 7c bad for gcc
    Deployment(gcc, [mcf, leela, bwaves, lbm, pop2, nab, fotonik3d]),
    
    Deployment(bwaves, [omnetpp, xalancbmk, deepsjeng, exchange2, xz, lbm, fotonik3d]),

    Deployment(mcf, [gcc, omnetpp, cactu, lbm, cam4, pop2, nab]),

    Deployment(cactu, [mcf, omnetpp, xalancbmk, leela, xz, bwaves, lbm]),

    Deployment(lbm, [mcf, omnetpp, bwaves, cam4, pop2, fotonik3d, roms]),

    Deployment(omnetpp, [perlbench, mcf, deepsjeng, bwaves, lbm, pop2, fotonik3d]),

    Deployment(xalancbmk, [mcf, x264, exchange2, xz, bwaves, cam4, nab]),

    Deployment(x264, [omnetpp, deepsjeng, xz, cactu, lbm, imagick, fotonik3d]),

    Deployment(cam4, [gcc, omnetpp, x264, bwaves, lbm, imagick, fotonik3d]),

    Deployment(pop2, [mcf, omnetpp, leela, exchange2, lbm, nab, roms]),

    Deployment(deepsjeng, [omnetpp, xz, bwaves, lbm, pop2, fotonik3d, roms]),

    Deployment(imagick, [omnetpp, xalancbmk, deepsjeng, exchange2, xz, lbm, fotonik3d]),

    Deployment(leela, [perlbench, gcc, xalancbmk, exchange2, xz, lbm, fotonik3d]),

    Deployment(nab, [gcc, x264, exchange2, xz, cam4, pop2, roms]),

    Deployment(exchange2, [perlbench, gcc, mcf, xalancbmk, cactu, fotonik3d, roms]),

    Deployment(fotonik3d, [gcc, mcf, omnetpp, xz, lbm, pop2, roms]),

    Deployment(xz, [x264, leela, exchange2, bwaves, lbm, pop2, fotonik3d]),
#---59---
    Deployment(x264, [xz, leela, exchange2, bwaves, lbm, pop2, fotonik3d])
]


# lbm, fotonik3d, roms, bwaves, omnetpp, pop2, cactu, mcf, cam4, gcc, xz, x264, imagick, nab, deepsjeng, xalancbmk, leela, perlbench, exchange2

CPU_VALIDATION_DEPLOYMENTS = [
    Deployment(perlbench, [lbm, fotonik3d, roms, bwaves, omnetpp, pop2, cactu, mcf, cam4, gcc, xz, x264, imagick, nab, deepsjeng]),

    Deployment(gcc, [lbm, fotonik3d, roms, bwaves, omnetpp, pop2, cactu, mcf, cam4, gcc, xz, x264, imagick, nab, deepsjeng]),
    
    Deployment(bwaves, [lbm, fotonik3d, roms, omnetpp, pop2, cactu, mcf, cam4, gcc, xz, x264, imagick, nab, deepsjeng, xalancbmk]),

    Deployment(mcf, [lbm, fotonik3d, roms, bwaves, omnetpp, pop2, cactu, cam4, gcc, xz, x264, imagick, nab, deepsjeng, perlbench]),

    Deployment(cactu, [lbm, fotonik3d, roms, bwaves, omnetpp, pop2, mcf, cam4, gcc, xz, x264, imagick, nab, deepsjeng, xalancbmk]),

    Deployment(lbm, [fotonik3d, roms, bwaves, omnetpp, pop2, cactu, mcf, cam4, gcc, xz, x264, imagick, nab, deepsjeng, leela]),

    Deployment(omnetpp, [lbm, fotonik3d, roms, bwaves, pop2, cactu, mcf, cam4, gcc, xz, x264, imagick, nab, deepsjeng, xalancbmk]),

    Deployment(xalancbmk, [lbm, fotonik3d, roms, bwaves, omnetpp, pop2, cactu, mcf, cam4, gcc, xz, x264, imagick, nab, deepsjeng]),

    Deployment(x264, [lbm, fotonik3d, roms, bwaves, omnetpp, pop2, cactu, mcf, cam4, gcc, xz, imagick, nab, deepsjeng, exchange2]),

    Deployment(cam4, [lbm, fotonik3d, roms, bwaves, omnetpp, pop2, cactu, mcf, gcc, xz, x264, imagick, nab, deepsjeng, xalancbmk]),

    Deployment(pop2, [lbm, fotonik3d, roms, bwaves, omnetpp, cactu, mcf, cam4, gcc, xz, x264, imagick, nab, deepsjeng, leela]),

    Deployment(deepsjeng, [lbm, fotonik3d, roms, bwaves, omnetpp, pop2, cactu, mcf, cam4, gcc, xz, x264, imagick, nab, leela]),

    Deployment(imagick, [lbm, fotonik3d, roms, bwaves, omnetpp, pop2, cactu, mcf, cam4, gcc, xz, x264, nab, deepsjeng, exchange2]),

    Deployment(leela, [lbm, fotonik3d, roms, bwaves, omnetpp, pop2, cactu, mcf, cam4, gcc, xz, x264, imagick, nab, deepsjeng]),

    Deployment(nab, [lbm, fotonik3d, roms, bwaves, omnetpp, pop2, cactu, mcf, cam4, gcc, xz, x264, imagick, deepsjeng, xalancbmk]),

    Deployment(exchange2, [lbm, fotonik3d, roms, bwaves, omnetpp, pop2, cactu, mcf, cam4, gcc, xz, x264, imagick, nab, deepsjeng]),

    Deployment(fotonik3d, [lbm, roms, bwaves, omnetpp, pop2, cactu, mcf, cam4, gcc, xz, x264, imagick, nab, deepsjeng, xalancbmk]),

    Deployment(xz, [lbm, fotonik3d, roms, bwaves, omnetpp, pop2, cactu, mcf, cam4, gcc, x264, imagick, nab, deepsjeng, perlbench]),

    Deployment(roms, [lbm, fotonik3d, bwaves, omnetpp, pop2, cactu, mcf, cam4, gcc, xz, x264, imagick, nab, deepsjeng, xalancbmk])
]

