import yaml
from argparse import ArgumentParser
from .preprocessing import Splitter

parser = ArgumentParser(description = "Preprocess THOR dataset")

parser.add_argument(
    "--cfg",
    type = str,
    default = "pythor-tools/cfg/ds_params.yaml",
    required = False,
    help = "setup"
)

args = parser.parse_args()

with open(args.cfg, "r") as f:
    cfg = yaml.safe_load(f)
    
splitter = Splitter(cfg)
splitter.split()