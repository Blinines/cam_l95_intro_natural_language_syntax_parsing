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


def get_metrics(df, first_col_name, dep, index, mode='recall'):
    """ Computes precision or recall of a given dependency
    mode in ['precision', 'recall'] 
    Default (arbitrary) recall """
    if mode == 'precision':
        line_info = deepcopy(df[df[first_col_name]==dep].values[0][1:])
    else:
        line_info = deepcopy(df[dep].values)
    
    tp, f = process_spec_col(line_info[index])
    line_info[index] = f

    if np.sum(line_info) + tp != 0:
        return float(tp)/(np.sum(line_info) + tp)
    else:
        return 'N/A'


def get_f1_score(precision, recall):
    if (type(precision)==float) and (type(recall)==float) and (precision+recall!=0): 
        return float(2*precision*recall)/(precision+recall)
    else:
        return 'N/A'


def get_support(df, first_col_name, dep, index):
    line_info = deepcopy(df[df[first_col_name]==dep].values[0][1:])
    tp, f = process_spec_col(line_info[index])
    line_info[index] = f
    return(np.sum(line_info) + tp)


def display_metrics(df, first_col_name, cols_dep):
    res = {'precision': [], 'recall': [], 'f1-score': [], 'support': []}
    for index, dep in enumerate(cols_dep[1:]):
        precision = get_metrics(df, first_col_name, dep, index, mode='precision')
        recall = get_metrics(df, first_col_name, dep, index, mode='recall')
        f1 = get_f1_score(precision, recall)
        support = get_support(df, first_col_name, dep, index)
        res['precision'].append(precision)
        res['recall'].append(recall)
        res['f1-score'].append(f1)
        res['support'].append(support)
    res_df = pd.DataFrame(data=res, index=cols_dep[1:])
    print(res_df)


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
    cols_dep = [first_col_name] + cols_dep
    
    df = pd.read_excel(config_global['general']['analysis_path'], 
                       sheet_name=config_global['general']['sheet_names'][args['parser']])
    df = df[cols_dep].fillna(0)

    display_metrics(df=df, first_col_name=first_col_name, cols_dep=cols_dep)
    