import pandas as pd
from src.config import FEATURES_CSV_DIR


class LatexGenerator:

    def __init__(self, df_unique_final, df_all_final, approach_list, map_list, output_oracle_list):
        self.df_unique_GA_final = df_unique_final[[name for name in df_unique_final.columns if "GA" in name]]
        self.df_unique_pairwise_final = df_unique_final[[name for name in df_unique_final.columns if "T-way" in name]]
        self.df_unique_ConfVD_final = df_unique_final[[name for name in df_unique_final.columns if "ConfVD" in name]]
        self.df_all_GA_final = df_all_final[[name for name in df_all_final.columns if "GA" in name]]
        self.df_all_pairwise_final = df_all_final[[name for name in df_all_final.columns if "T-way" in name]]
        self.df_all_ConfVD_final = df_all_final[[name for name in df_all_final.columns if "ConfVD" in name]]

        self.df_unique_final = df_unique_final
        self.df_all_final = df_all_final

        self.approach_list = approach_list
        self.map_list = map_list
        self.output_oracle_list = output_oracle_list



    def start_write(self):
        with open(f"{FEATURES_CSV_DIR}/latex.txt", "w") as f:
            self.write_all(f)
            self.write_all_elim(f)


    def write_all(self, f):
        f.write("all ads/GA_pairwise_ConfVD\n")
        for index, row in self.df_unique_final.iterrows():
            f.write("\\textbf{" + self.output_oracle_list[index] + "}")
            write_str = ""
            pair = []
            for a_num in row:
                pair.append(a_num)
                if len(pair) == 3:
                    # find the max value
                    max_value = max(pair)
                    for i in range(3):
                        if pair[i] == max_value and max_value != 0:
                            pair[i] = "\\textbf{" + str(pair[i]) + "}"
                    # if pair[0] > pair[1]:
                    #     pair[0] = "\\textbf{" + str(pair[0]) + "}"
                    # elif pair[0] < pair[1]:
                    #     pair[1] = "\\textbf{" + str(pair[1]) + "}"
                    # write_str += f" & {pair[0]} & {pair[1]}"
                    write_str += f" & {pair[0]} & {pair[1]} & {pair[2]}"
                    pair = []
            f.write(f"{write_str}\\\\ \n")
        f.write("\\textbf{Improv. (\%)}")
        write_str = ""
        unique_total_row = self.df_unique_final.iloc[-1]
        for e1, e2, e3 in zip(unique_total_row[0::3], unique_total_row[1::3], unique_total_row[2::3]):
            improvement1 = round((e1 - e2) / e2 * 100, 2)
            improvement2 = round((e1 - e3) / e3 * 100, 2)
            write_str += " & - & " + str(improvement1) + " & " + str(improvement2)

        # for e1, e2 in zip(unique_total_row[0::2], unique_total_row[1::2]):
        #     improvement = round((e1 - e2) / e2 * 100, 2)
        #     write_str += " & \multicolumn{2}{c}{\\textbf{" + str(improvement) + "\%}}"
        f.write(f"{write_str}\\\\ \n")
        f.write("\n\n\n\n")

    def write_all_elim(self, f):
        df_elim = pd.DataFrame()
        # for testing_approach in ["GA", "T-way"]:
        for testing_approach in ["GA", "T-way", "ConfVD"]:

            df_elim[f"{testing_approach}_All"] = self.df_all_final[
                [name for name in self.df_all_final.columns if testing_approach in name]].sum(axis=1)
            df_elim[f"{testing_approach}_Unique"] = self.df_unique_final[
                [name for name in self.df_unique_final.columns if testing_approach in name]].sum(axis=1)
            df_elim[f"{testing_approach}_Elim."] = (
                    (1 - df_elim[f"{testing_approach}_Unique"] / df_elim[f"{testing_approach}_All"]) * 100).round(2)

        f.write("elim all by testing\n")
        for idx in df_elim.index:
            f.write("\\textbf{" + self.output_oracle_list[idx] + "} ")
            write_str = ""
            for col in df_elim.columns:
                value = str(df_elim.loc[idx, col])
                if "Elim." in col:
                    if value != "nan":
                        write_item = format(df_elim.loc[idx, col], ".2f") + "\%"
                    else:
                        write_item = "/"
                else:
                    write_item = value
                write_str += f"& {write_item} "
            f.write(f"{write_str}\\\\ \n")
        f.write("\n\n\n\n")


###########################################
    def write_ga_elim(self, f):
        df_ga_elim = pd.DataFrame()
        for approach_name in self.approach_list:
            df_ga_elim[f"{approach_name}_All"] = self.df_all_GA_final[
                [name for name in self.df_all_GA_final.columns if approach_name in name]].sum(axis=1)
            df_ga_elim[f"{approach_name}_Unique"] = self.df_unique_GA_final[
                [name for name in self.df_unique_GA_final.columns if approach_name in name]].sum(axis=1)
            df_ga_elim[f"{approach_name}_Elim."] = (
                    (1 - df_ga_elim[f"{approach_name}_Unique"] / df_ga_elim[f"{approach_name}_All"]) * 100).round(2)

        f.write("elim ga by ads\n")
        for idx in df_ga_elim.index:
            f.write("\\textbf{" + self.output_oracle_list[idx] + "} ")
            write_str = ""
            for col in df_ga_elim.columns:
                value = str(df_ga_elim.loc[idx, col])
                if "Elim." in col:
                    if value != "nan":
                        write_item = format(df_ga_elim.loc[idx, col], ".2f") + "\%"
                    else:
                        write_item = "/"
                else:
                    write_item = value
                write_str += f"& {write_item} "
            f.write(f"{write_str}\\\\ \n")
        f.write("\n\n\n\n")

    def write_pairwise_elim(self, f):
        df_pairwise_elim = pd.DataFrame()
        for approach_name in self.approach_list:
            df_pairwise_elim[f"{approach_name}_All"] = self.df_all_pairwise_final[
                [name for name in self.df_all_pairwise_final.columns if approach_name in name]].sum(axis=1)
            df_pairwise_elim[f"{approach_name}_Unique"] = self.df_unique_pairwise_final[
                [name for name in self.df_unique_pairwise_final.columns if approach_name in name]].sum(axis=1)
            df_pairwise_elim[f"{approach_name}_Elim."] = (
                    (1 - df_pairwise_elim[f"{approach_name}_Unique"] / df_pairwise_elim[
                        f"{approach_name}_All"]) * 100).round(2)

        f.write("elim pairwise by ads\n")
        for idx in df_pairwise_elim.index:
            f.write("\\textbf{" + self.output_oracle_list[idx] + "} ")
            write_str = ""
            for col in df_pairwise_elim.columns:
                value = str(df_pairwise_elim.loc[idx, col])
                if "Elim." in col:
                    if value != "nan":
                        write_item = format(df_pairwise_elim.loc[idx, col], ".2f") + "\%"
                    else:
                        write_item = "/"
                else:
                    write_item = value
                write_str += f"& {write_item} "
            f.write(f"{write_str}\\\\ \n")
        f.write("\n\n\n\n")

    def write_ga_map(self, f):
        dr_ga_map = pd.DataFrame()
        for approach_name in self.approach_list:
            temp_df = self.df_unique_GA_final[
                [name for name in self.df_unique_GA_final.columns if approach_name in name]]
            dr_ga_map = pd.concat([dr_ga_map, temp_df], axis=1)

        f.write("by ga map\n")
        for index, row in dr_ga_map.iterrows():
            f.write("\\textbf{" + self.output_oracle_list[index] + "}")
            write_str = ""
            for a_num in row:
                write_str += f" & {a_num}"
            f.write(f"{write_str}\\\\ \n")
        f.write("\n\n\n\n")

    def write_map_ga_pairwise(self, f):
        df_map_ga_pairwise = pd.DataFrame()
        for map_name in self.map_list:
            temp1_df = self.df_unique_GA_final[
                [name for name in self.df_unique_GA_final.columns if map_name in name]].sum(axis=1)
            temp2_df = self.df_unique_pairwise_final[
                [name for name in self.df_unique_pairwise_final.columns if map_name in name]].sum(axis=1)
            df_map_ga_pairwise = pd.concat([df_map_ga_pairwise, temp1_df, temp2_df], axis=1)

        f.write("by map ga_pairwise\n")
        for index, row in df_map_ga_pairwise.iterrows():
            f.write("\\textbf{" + self.output_oracle_list[index] + "}")
            write_str = ""
            pair = []
            for a_num in row:
                pair.append(a_num)
                if len(pair) == 2:
                    if pair[0] > pair[1]:
                        pair[0] = "\\textbf{" + str(pair[0]) + "}"
                    elif pair[0] < pair[1]:
                        pair[1] = "\\textbf{" + str(pair[1]) + "}"
                    write_str += f" & {pair[0]} & {pair[1]}"
                    pair = []
            f.write(f"{write_str}\\\\ \n")
        f.write("\n\n\n\n")

    def write_ads_ga_pairwise(self, f):
        df_ads_ga_pairwise = pd.DataFrame()
        for approach_name in self.approach_list:
            temp1_df = self.df_unique_GA_final[
                [name for name in self.df_unique_GA_final.columns if approach_name in name]].sum(
                axis=1)
            temp2_df = self.df_unique_pairwise_final[
                [name for name in self.df_unique_pairwise_final.columns if approach_name in name]].sum(axis=1)
            df_ads_ga_pairwise = pd.concat([df_ads_ga_pairwise, temp1_df, temp2_df], axis=1)

        f.write("by ads ga_pairwise\n")
        for index, row in df_ads_ga_pairwise.iterrows():
            f.write("\\textbf{" + self.output_oracle_list[index] + "}")
            write_str = ""
            pair = []
            for a_num in row:
                pair.append(a_num)
                if len(pair) == 2:
                    if pair[0] > pair[1]:
                        pair[0] = "\\textbf{" + str(pair[0]) + "}"
                    elif pair[0] < pair[1]:
                        pair[1] = "\\textbf{" + str(pair[1]) + "}"
                    write_str += f" & {pair[0]} & {pair[1]}"
                    pair = []
            f.write(f"{write_str}\\\\ \n")
        f.write("\n\n\n\n")


