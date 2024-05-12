import warnings
from src.config import OPT_MODE, ADS_ROOT, DOCKER_CONTAINER_NAME, CONTAINER_NUM, DEFAULT_SCRIPT_PORT
from environment.Container import Container
from optimization_algorithms.baseline.TwayRunner import TwayRunner
from optimization_algorithms.baseline.ConfVDRunner import ConfVDRunner
from optimization_algorithms.genetic_algorithm.GARunner import GARunner
from prepare import init_prepare

warnings.filterwarnings('ignore')


def confve_main():
    init_prepare()

    containers = [Container(ADS_ROOT, f'{DOCKER_CONTAINER_NAME}_{x}', str(x), DEFAULT_SCRIPT_PORT + x) for x in
                  range(CONTAINER_NUM)]

    for ctn in containers:
        ctn.start_instance()
        ctn.env_init()
        ctn.setup_env()

    if OPT_MODE == "GA":
        GARunner(containers)
    elif OPT_MODE == "T-way":
        TwayRunner(containers)
    elif OPT_MODE == "ConfVD":
        ConfVDRunner(containers)


if __name__ == '__main__':
    confve_main()
