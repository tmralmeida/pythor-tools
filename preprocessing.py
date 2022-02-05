import pandas as pd
import re
import numpy as np
import _pickle as cPickle
from typing import List
import os
import random

class Preprocessor():
    def __init__(self, curr_exp, curr_run, cfg) -> None:
        data_cfg = cfg["data"]
        params_cfg = cfg["parameters"]
        self.exp = curr_exp
        self.run = curr_run
        self.path = os.path.join(data_cfg["path"], f"Exp_{self.exp}_run_{self.run}_6D.tsv")
        self.save_dir = os.path.join(data_cfg["save_dir"], "raw")
        
        self.res_rule = params_cfg["resample_rule"]
        self.avg_window = params_cfg["average_window"]
        obs_len = params_cfg["obs_len"]
        pred_len = params_cfg["pred_len"]
        self.full_len = obs_len + pred_len
        
        
        
    def __loading(self) -> pd.DataFrame:
        # initial df
        df = pd.read_csv(self.path, sep = "\t", header = 10).dropna(axis = 1)
        
        # changing column names
        col_list = df.columns.tolist()[1:]
        new_columns = [df.columns.tolist()[0]]
        prev_col_name = col_list[0]
        for column in col_list:
            if re.match("Y.*", column) and re.match("Helmet.*",prev_col_name):
                new_columns.append(prev_col_name + " Y")
            else:
                new_columns.append(column)
            prev_col_name = column.split(" ")[0]
        df.columns = new_columns
        # Checking if all data:
        # * 13 rigid bodies
        # * 16 coordinates
        # * 2 columns for time and frame
        assert df.shape[1] == 16*13 + 2 
        return df
    
    
    def __get_rolesmap(self):
        if self.exp == 1:
            if self.run== 1:
                n_groups = 2
                visitors_group1 = [6,7,5] 
                visitors_group2 = [8,2,4]
            elif self.run== 2:
                n_groups = 2
                visitors_group1 = [2,6,7,5] 
                visitors_group2 = [8, 4]
            elif self.run== 3:
                n_groups = 3
                visitors_group1 = [6,7,8]
                visitors_group2 = [4,5]
                visitors_group3 = [2]
            elif self.run== 4:
                n_groups = 2
                visitors_group1 = [2, 4, 5, 7, 8]
                visitors_group2 = [6]
            
            workers_utility = [3]
            workers_lab = [9]

        elif self.exp == 2:
            if self.run== 1:
                n_groups = 2
                visitors_group1 = [4,5,6] 
                visitors_group2 = [3,7,9]
            elif self.run== 2:
                n_groups = 2
                visitors_group1 = [3,5,6,9] 
                visitors_group2 = [7, 4]
            elif self.run== 3:
                n_groups = 3
                visitors_group1 = [5,7,9]
                visitors_group2 = [4,6]
                visitors_group3 = [3]
            elif self.run== 4:
                n_groups = 2
                visitors_group1 = [3,5,6,7,9]
                visitors_group2 = [4]
            elif self.run== 5:
                n_groups = 3
                visitors_group1 = [3, 6]
                visitors_group2 = [4, 9]
                visitors_group3 = [5, 7]
            
            workers_utility = [2]
            workers_lab = [8]
            
        elif self.exp == 3:
            if self.run== 1:
                n_groups = 2
                visitors_group1 = [2,3,8] 
                visitors_group2 = [6,7,9]
            elif self.run== 2:
                n_groups = 2
                visitors_group1 = [2,8,9] 
                visitors_group2 = [3,6,7]
            elif self.run== 3:
                n_groups = 3
                visitors_group1 = [2,3,7]
                visitors_group2 = [8,9]
                visitors_group3 = [6]
            elif self.run== 4:
                n_groups = 2
                visitors_group1 = [2,3,6,7,9]
                visitors_group2 = [8]
            
            workers_utility = [5]
            workers_lab = [4]
        
        inspector = [10]

        roles = {
            "VISITOR" : visitors_group1 + visitors_group2 if n_groups == 2 else visitors_group1 + visitors_group2 + visitors_group3,
            "WORKER" : workers_lab + workers_utility,
            "inspector" : inspector,
        }
        return roles
    
    
    def __splitting_helms(self, df : pd.DataFrame) -> pd.DataFrame:
        roles = self.__get_rolesmap()
        col_list = df.columns.tolist()
        dfs_helmets = []
        prev_col_name = col_list[0]
        time_col = df["Time"]
        for column in col_list:
            if re.match(".*Y", column) and re.match(".*X",prev_col_name):
                df_targ = df[[prev_col_name, column]]
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
        return df_sorted
    
    
    def __extract_subtrajs(self, df : pd.DataFrame) -> List[pd.DataFrame]:
        n_helmets = df.Person_ID.unique()
        sub_trajs = []
        for h in n_helmets:
            hel_data = df[df.Person_ID == h]
            n_steps = hel_data.shape[0] 
            if n_steps >= (self.full_len):
                n_chunks = int(n_steps / (self.full_len))
                chunks = np.array_split(hel_data, n_chunks)
                targ_chunks = list(filter(lambda x : x.shape[0] == (self.full_len), chunks))   
                sub_trajs.extend(targ_chunks)
        return sub_trajs
    
    
    def preprocessing(self) -> List[pd.DataFrame]:
        df = self.__loading()
        # merge dfs -> frame time + helmets
        merged_df = pd.merge(df[["Frame", "Time"]], df.filter(regex=("Helmet.*")), left_index=True, right_index=True)

        # create time col for resampling
        merged_df["date"] = pd.TimedeltaIndex(merged_df.Time, unit = "s")
        
        # resampling
        no_frame = merged_df.drop("Frame", axis = 1)
        no_frame_resampled = no_frame.resample(rule=self.res_rule, on = "date").mean()
        
        # splitting helmets and ordering
        ordered_df = self.__splitting_helms(no_frame_resampled)
        print(f"Data filtered with {ordered_df.shape[0]} data points!")
        
        # split into sub trajs
        sub_trajs = self.__extract_subtrajs(ordered_df)
        return sub_trajs
    
    
    def save_files(self, sub_trajs : List[pd.DataFrame]) -> None:
        print(f"Exporting {len(sub_trajs)} trajectories!")
        if not os.path.exists(self.save_dir):
            print("Save dir doesn't exist. Creating save dir...")
            os.makedirs(self.save_dir)
            
        fn = f"EXP{self.exp}_RUN_{self.run}_sub_trajs.pkl"
        with open(os.path.join(self.save_dir, fn), "wb") as f:
            cPickle.dump(sub_trajs, f)

        print(f"File {fn} saved in {self.save_dir}.")
        
        
        
class Splitter():
    def __init__(self, cfg) -> None:
        split_cfg = cfg["split"]
        self.saved_dir = os.path.join(cfg["data"]["save_dir"], "raw")
        self.save_dir = split_cfg["save_dir"]
        self.train_ratio = split_cfg["train_ratio"]
        self.val_ratio = split_cfg["val_ratio"]
        self.test_set = split_cfg["test_set"]
        if not self.test_set:
            self.sets = ["train", "val"]
            assert self.train_ratio + self.val_ratio == 1, "train_ratio and val_ratio should sum up to 1"
        else:
            self.sets = ["train", "val", "test"]
            assert self.train_ratio + self.val_ratio <= 0.90, "a test set should be at lest 0.10 of your data"
            
    def split(self):
        
        files = os.listdir(self.saved_dir)
        all_trajs = []
        for f in files:
            path = os.path.join(self.saved_dir, f)
            with open(path, "rb") as f:
                trajectories = cPickle.load(f)
            all_trajs.extend(trajectories)
        random.Random(1).shuffle(all_trajs)
        full_set_len = len(all_trajs)
        n_train_trajs = int(self.train_ratio * full_set_len)
        n_val_trajs =  int(self.val_ratio * full_set_len)
        train_set = all_trajs[:n_train_trajs]
        dataset = {}
        dataset["train"] = train_set
        
        if self.test_set:
            val_set = all_trajs[n_train_trajs : n_train_trajs + n_val_trajs]
            test_set = all_trajs[n_train_trajs + n_val_trajs:]
            assert len(train_set) + len(val_set) + len(test_set) == full_set_len, "You are not using all trajectories"
            dataset["val"] = val_set
            dataset["test"] = test_set
        else:
            val_set = all_trajs[n_train_trajs :]
            assert len(train_set) + len(val_set) == full_set_len, "You are not using all trajectories"
            dataset["val"] = val_set
            
        if not os.path.exists(self.save_dir):
            print("Save dir doesn't exist. Creating save dir...")
            os.makedirs(self.save_dir)
        
        for ns, set_ in dataset.items():
            print(f"Saving {ns} set with {len(set_)} trajectories")
            with open(os.path.join(self.save_dir, ns + "pkl"), "wb") as f:
                cPickle.dump(set_, f)

        
        
        
    