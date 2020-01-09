# -*- coding: utf-8 -*-
from io import open
import yaml
import argparse
import pandas as pd
import numpy as np
from copy import deepcopy
from helpers import get_elt_to_index

def convert_hierarchy_to_deprel_root(h, deprel_to_root={}, to_add=[]):
    """ Convert hierarchy of typed dependencies to a hashmap
    from dependencies to all its parents """
    for dep in h.keys():
        # adding upper dependencies
        deprel_to_root[dep] = [dep] + to_add
        # adding any additional dependencies
        if h[dep]:
            deprel_to_root = convert_hierarchy_to_deprel_root(h=h[dep], 
                                                              deprel_to_root=deprel_to_root,
                                                              to_add=to_add+[dep])
    
    return deprel_to_root


def get_dep_list(data_path):
    data_file = open(data_path, 'r', encoding='utf-8')
    lines = data_file.readlines()
    lines = [sent.split('\t') for sent in lines]
    dep = []
    for elt in lines:
        if len(elt)==10:
            dep.append(elt[7])
    return dep


def process_spec_col(s):
    info = s.split('/')
    tp, f = info[0], info[1]
    if f[-1] == ',':
        f = f[:-1]
    return int(tp), int(f)


def get_line_info(df, first_col_name, dep, mode='recall'):
    if mode == 'precision':
        return deepcopy(df[df[first_col_name]==dep].values[0][1:])
    else:
        return deepcopy(df[dep].values)


def get_metrics(df, first_col_name, dep_list, dep_to_index, mode='recall'):
    """ Computes precision or recall of a given dependency
    mode in ['precision', 'recall'] 
    Default (arbitrary) recall 
    dep: list of dependency to take into account.
    Basic metric => list of one element, upper level => several elemets"""
    tp, denom = 0, 0
    for dep in dep_list:
        index = dep_to_index[dep]
        line_info = get_line_info(df, first_col_name, dep, mode)
        curr_tp, curr_f = process_spec_col(line_info[index])
        line_info[index] = curr_f
        tp += curr_tp
        denom += np.sum(line_info)

    if np.sum(line_info) + tp != 0:
        return float(tp)/(np.sum(line_info) + tp)
    else:
        return 'N/A'


def get_f1_score(precision, recall):
    if (type(precision)==float) and (type(recall)==float) and (precision+recall!=0): 
        return float(2*precision*recall)/(precision+recall)
    else:
        return 'N/A'


def get_support(df, first_col_name, dep_list, dep_to_index):
    res = 0
    for dep in dep_list:
        index = dep_to_index[dep]
        line_info = deepcopy(df[df[first_col_name]==dep].values[0][1:])
        tp, f = process_spec_col(line_info[index])
        line_info[index] = f
        res += np.sum(line_info) + tp
    return(res)


def display_metrics(df, first_col_name, dep_dict, dep_to_index):
    res = {'precision': [], 'recall': [], 'f1-score': [], 'support': []}
    index_df = []
    for dep, dep_list in dep_dict.items():
        precision = get_metrics(df, first_col_name, dep_list, dep_to_index, mode='precision')
        recall = get_metrics(df, first_col_name, dep_list, dep_to_index, mode='recall')
        f1 = get_f1_score(precision, recall)
        support = get_support(df, first_col_name, dep_list, dep_to_index)
        res['precision'].append(precision)
        res['recall'].append(recall)
        res['f1-score'].append(f1)
        res['support'].append(support)
        index_df.append(dep)
    res_df = pd.DataFrame(data=res, index=index_df)
    return res_df


def round_cols(x):
    if x != 'N/A':
        return round(float(x), 2)
    else:
        return x


def format_df(df, f, cols):
    for col in cols:
        df[col] = df[col].apply(f)
    return df

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

    print('{0} - Dependency metrics - unique relations'.format(args['parser']))
    res_df = display_metrics(df=df, first_col_name=first_col_name, dep_dict=dep_level_0_dict, dep_to_index=dep_to_index)
    res_df = format_df(df=res_df, f=round_cols, cols=['precision', 'recall', 'f1-score'])
    print(res_df)
    print('=====')
    print('{0} - Dependency metrics - grouped relations'.format(args['parser']))
    res_df = display_metrics(df=df, first_col_name=first_col_name, dep_dict=dep_level_upper, dep_to_index=dep_to_index)
    print(res_df)