from argparse import ArgumentParser
import os
import yaml
import _pickle as cPickle


parser = ArgumentParser(description = "Visualization of trajetctories from THOR  data set.")

parser.add_argument(
    "--num_trajs_overall",
    "-nt",
    type = int,
    default = 100,
    required = False,
    help = "Number of trajectories"
)

parser.add_argument(
    "--num_trajs_per_class",
    "-ntc",
    type = int,
    default = 100,
    required = False,
    help = "Number of trajectories"
)


parser.add_argument(
    "--cfg",
    type = str,
    default = "pythor-tools/cfg/ds_params.yaml",
    required = False,
    help = "setup"
)



# open every file and append trajectories


args = parser.parse_args()

with open(args.cfg, "r") as f:
    cfg = yaml.safe_load(f)

saved_dir = os.path.join(cfg["data"]["save_dir"], "raw") 

files = os.listdir(saved_dir)
trajs  = [] 

for file in files:
    fp = os.path.join(saved_dir, file)
    with open(fp, "rb") as f:
        trajs.extend(cPickle.load(f))
    
print("Total number of trajectories is", len(trajs))

# visualize wrt to the arguments



