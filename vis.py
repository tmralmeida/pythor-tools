from argparse import ArgumentParser


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





# visualize wrt to the arguments



