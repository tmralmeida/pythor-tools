from operator import sub
import pandas as pd
import os
import re
import numpy as np
import yaml
from argparse import ArgumentParser
import _pickle as cPickle
from .roles import get_roles_mapping

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
data_info = cfg["data"]
params = cfg["parameters"]

# data
exp = data_info["experiment"]
run = data_info["run"]
path = data_info["path"]
save_dir = data_info["save_dir"]

# parameters
resample_rule = params["resample_rule"]
average_window = params["average_window"]
obs_len = params["obs_len"]
pred_len = params["pred_len"]
full_traj_len = obs_len + pred_len

# path 
exp_path =  os.path.join(path, f"Exp_{exp}_run_{run}_6D.tsv")


# initial df
df = pd.read_csv(exp_path, sep = "\t", header = 10).dropna(axis = 1)

# changing column names
col_list = df.columns.tolist()
new_columns = []
prev_column = col_list[0]
for i, column in enumerate(col_list):
    if re.match("Y.*", column) and re.match("Helmet.*",prev_col_name):
        new_columns.append(prev_col_name + " Y")
    else:
        new_columns.append(column)
    prev_col_name = column.split(" ")[0]
df.columns = new_columns


# Checking if all data is here:
# * 13 rigid bodies
# * 16 coordinates
# * 2 columns for time and frame
assert df.shape[1] == 16*13 + 2 

# merge dfs -> frame time + helmets
merged_df = pd.merge(df[["Frame", "Time"]], df.filter(regex=("Helmet.*")), left_index=True, right_index=True)

# create time col for resampling
merged_df["date"] = pd.TimedeltaIndex(merged_df.Time, unit = "s")

# resampling
no_frame = merged_df.drop("Frame", axis = 1)
no_frame_resampled = no_frame.resample(rule=resample_rule, on = "date").mean()

# splitting each helmet's traj, interpolating, and smooting
roles = get_roles_mapping(experiment = exp, run = run)
col_list = no_frame_resampled.columns.tolist()
dfs_helmets = []
prev_col_name = col_list[0]
time_col = no_frame_resampled["Time"]
for i, column in enumerate(col_list):
    if re.match(".*Y", column) and re.match(".*X",prev_col_name):
        df_targ = no_frame_resampled[[prev_col_name, column]]
        df_targ.columns = ["X", "Y"]
        helmet_n = int(re.findall("\d+", column)[0])
        if helmet_n == 1:
            continue
            
        # interpolation
        df_targ = df_targ.replace(0, np.nan)
        df_targ = df_targ.interpolate()
        
        # average filter
        df_average = df_targ.copy()
        df_average.loc[:, "Time"] = time_col
        df_average["date"] = pd.TimedeltaIndex(time_col, unit = "s")
        df_average = df_average.rolling("500ms", on = "date").mean()
        df_average.loc[:, "Frame"] = np.arange(1, df_average.shape[0] + 1)
        for idx_d, r in enumerate(roles.values()):
            if helmet_n in r:
                idx_dict = idx_d
        df_final =  df_average.assign(Description = list(roles.keys())[idx_dict])
        df_final =  df_final.assign(Person_ID = helmet_n)
        
        df_final = df_final[["Frame", "Time", "Person_ID", "X", "Y", "Description"]]
        dfs_helmets.append(df_final)
    prev_col_name = column


# concatenating and ordering
df_concatenated = pd.concat(dfs_helmets)
df_sorted = df_concatenated.sort_values(by=["Frame", "Person_ID"]).dropna().reset_index(drop=True)

print(f"Data filtered with {df_sorted.shape[0]} data points!")

# split into sub trajs
n_helmets = df_sorted.Person_ID.unique()
sub_trajs = []
for h in n_helmets:
    hel_data = df_sorted[df_sorted.Person_ID == h]
    n_steps = hel_data.shape[0] 
    if n_steps >= (full_traj_len):
        n_chunks = int(n_steps / (full_traj_len))
        chunks = np.array_split(hel_data, n_chunks)
        targ_chunks = list(filter(lambda x : x.shape[0] == (full_traj_len), chunks))   
        sub_trajs.extend(targ_chunks) 
        
print(f"Exporting {len(sub_trajs)} trajectories!")

if not os.path.exists(save_dir):
    print("Save dir doesn't exist. Creating save dir...")
    os.makedirs(save_dir)
    
fn = f"EXP{exp}_RUN_{run}_sub_trajs.pkl"
with open(os.path.join(save_dir, fn), "wb") as f:
    cPickle.dump(sub_trajs, f)

print(f"File {fn} saved in {save_dir}.")