# -*- coding: utf-8 -*-
import argparse
import yaml
import pandas as pd
from collections import OrderedDict 
from main_evaluate import display_metrics, format_df, round_cols

index_grouped = [2, 6, 8, 13, 17, 18, 21, 28, 36, 39, 45]
indent = [0]*3 + [1]*3 + [0] + [1]*2 + [2]*5 + [3]*3 + [1] + [2] + [3]*2 + [2] + [3]*2 + \
         [0]*5 + [1]*8 + [2]*2 + [1] + [2]*2 + [1]*4 + [2]*2 + [1]*7 + [0]*5


def order_lines(df_unique_latex, df_grouped_latex, index_grouped):
    lines = ['']*len(df_unique_latex + df_grouped_latex)
    for i, line in enumerate(df_grouped_latex):
        lines[index_grouped[i]] = line
    i_unique, i_total = 0, 0
    while i_unique < len(df_unique_latex):
        if lines[i_total] == '':
            lines[i_total] = df_unique_latex[i_unique]
            i_unique += 1
        i_total += 1
    return lines 


def indent_lines(lines, indent):
    indented = []
    for index, line in enumerate(lines):
        indented.append('\\quad '*indent[index] + line)
    return indented 

if __name__=='__main__':
    # Construct the argument parser
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--parser", required=True, help="parser for which we want metrics. " +
                                                          "`benepar`, `stanford` and `rasp` options")
    args = vars(ap.parse_args())

    # Loading the data
    with open('./config.yaml') as file:
        config_global = yaml.load(file, Loader=yaml.FullLoader)
    cols_dep = config_global['general']['dep_level_0']
    first_col_name = config_global['general']['first_col_name']
    dep_level_upper = config_global['general']['dep_level_upper']

    dep_to_index, dep_level_0_dict = {}, {}
    for index, dep in enumerate(cols_dep):
        dep_to_index[dep] = index
        dep_level_0_dict[dep] = [dep]
    
    df = pd.read_excel(config_global['general']['analysis_path'], 
                       sheet_name=config_global['general']['sheet_names'][args['parser']])
    df = df[[first_col_name] + cols_dep].fillna(0)

    # Dependency metrics - unique relations
    df_unique = display_metrics(df=df, first_col_name=first_col_name, dep_dict=dep_level_0_dict, dep_to_index=dep_to_index)
    df_unique = format_df(df=df_unique, f=round_cols, cols=['precision', 'recall', 'f1-score'])
    df_unique_latex = df_unique.to_latex().split('\n')
    df_unique_values = df_unique_latex[4:-3]
    
    # Dependency metrics - grouped relations
    df_grouped = display_metrics(df=df, first_col_name=first_col_name, dep_dict=dep_level_upper, dep_to_index=dep_to_index)
    df_grouped = format_df(df=df_grouped, f=round_cols, cols=['precision', 'recall', 'f1-score'])
    df_grouped_latex = df_grouped.to_latex().split('\n')
    df_grouped_values = df_grouped_latex[4:-3]

    lines = order_lines(df_unique_latex=df_unique_values, df_grouped_latex=df_grouped_values,
                        index_grouped=index_grouped)
    lines = indent_lines(lines=lines, indent=indent)
    lines = df_unique_latex[:4] + lines + df_unique_latex[-3:-1]
    print('\n'.join(lines))
    