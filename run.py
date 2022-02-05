import yaml
from argparse import ArgumentParser
from .preprocessing import Preprocessor

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

exps = cfg["data"]["experiments"]
runs = cfg["data"]["runs"]
exp_run = list(zip(exps, runs))

total_nst = []
for er in exp_run:
    exp = er[0]
    run = range(1, er[1] + 1)
    for r in run:
        pp = Preprocessor(exp, r, cfg)
        st = pp.preprocessing()
        pp.save_files(st)
        total_nst.append(len(st))
 

print(f"Preprocessed a total amount of {sum(total_nst)} trajectories.")

# split into three different sets