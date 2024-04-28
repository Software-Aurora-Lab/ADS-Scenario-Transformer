import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TEST_ROOT = os.path.join(PROJECT_ROOT, "tests")
SAMPLE_ROOT = os.path.join(PROJECT_ROOT, "samples")
SRC_ROOT = os.path.join(PROJECT_ROOT, "scenario_transformer")

DEFAULT_ENTITIES_PATH = os.path.join(SRC_ROOT, "builder/default_entities.yaml")
