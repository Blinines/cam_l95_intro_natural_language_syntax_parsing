# -*- coding: utf-8 -*-
from io import open
import yaml
import argparse
import pandas as pd
import numpy as np
from copy import deepcopy
from helpers import get_elt_to_index


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

    if denom + tp != 0:
        return float(tp)/(denom + tp)
    else:
        return 'N/A'


def get_f1_score(precision, recall):
    if (type(precision)==float) and (type(recall)==float) and (precision+recall!=0): 
        return float(2*precision*recall)/(precision+recall)
    else:
        return 'N/A'


def get_support(df, first_col_name, dep_list, dep_to_index):
    # tp, fn, fp
    # nb_gold = tp+fn
    # nb_parser = tp+fp
    tp, fn, fp = 0, 0, 0
    for dep in dep_list:
        index = dep_to_index[dep]
        line_info_gold = deepcopy(df[df[first_col_name]==dep].values[0][1:])
        line_info_parser = deepcopy(df[dep].values)

        curr_tp, curr_fp = process_spec_col(line_info_gold[index])
        line_info_gold[index] = curr_fp

        tp += curr_tp
        fp += np.sum(line_info_gold)

        _, curr_fn = process_spec_col(line_info_parser[index])
        line_info_parser[index] = curr_fn
        fn += np.sum(line_info_parser) 
    return(tp, fn, fp)


def display_metrics(df, first_col_name, dep_dict, dep_to_index):
    res = {'precision': [], 'recall': [], 'f1-score': [], 'tp': [], 'fn': [], 'fp': []}
    index_df = []
    for dep, dep_list in dep_dict.items():
        precision = get_metrics(df, first_col_name, dep_list, dep_to_index, mode='precision')
        recall = get_metrics(df, first_col_name, dep_list, dep_to_index, mode='recall')
        f1 = get_f1_score(precision, recall)
        tp, fn, fp = get_support(df, first_col_name, dep_list, dep_to_index)
        res['precision'].append(precision)
        res['recall'].append(recall)
        res['f1-score'].append(f1)
        res['tp'].append(tp)
        res['fn'].append(fn)
        res['fp'].append(fp)
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


def macro_avg(df, col):
    """ col in ['precision', 'recall']"""
    values = df[col].values
    sum, nb = 0, 0
    for elt in values:
            if elt != 'N/A':
                sum += float(elt)
                nb += 1
    return round(sum/nb, 2)


def micro_avg(df, col):
    """ col in ['precision', 'recall']"""
    tp = df['tp'].values
    if col == 'precision':
        f = df['fp'].values
    else:
        f = df['fn'].values
    
    num, denum = 0, 0
    for index, value in enumerate(tp):
        num += value
        denum += value + f[index]
    return round(float(num)/denum, 2)
    

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
    res_df_unique = display_metrics(df=df, first_col_name=first_col_name, dep_dict=dep_level_0_dict, dep_to_index=dep_to_index)
    res_df_unique = format_df(df=res_df_unique, f=round_cols, cols=['precision', 'recall', 'f1-score'])
    #print(res_df_unique[['precision', 'recall', 'f1-score']])
    print(res_df_unique)
    print('=====')

    print('{0} - Dependency metrics - grouped relations'.format(args['parser']))
    res_df_grouped = display_metrics(df=df, first_col_name=first_col_name, dep_dict=dep_level_upper, dep_to_index=dep_to_index)
    res_df_grouped = format_df(df=res_df_grouped, f=round_cols, cols=['precision', 'recall', 'f1-score'])
    #print(res_df_grouped[['precision', 'recall', 'f1-score']])
    print(res_df_grouped)
    print('=====')

    print('{0} - Macro and micro average'.format(args['parser']))
    df_avg = pd.concat([res_df_unique, res_df_grouped])
    macro_precision, macro_recall = macro_avg(df=df_avg, col='precision'), macro_avg(df=df_avg, col='recall')
    micro_precision, micro_recall = micro_avg(df=df_avg, col='precision'), micro_avg(df=df_avg, col='recall')
    print('Macro average - precision : {0}'.format(macro_precision))
    print('Macro average - recall    : {0}'.format(macro_recall))
    print('Macro average - F1        : {0}'.format(round(2./((1./macro_precision) + (1./macro_recall)), 2)))
    print('Micro average - precision : {0}'.format(micro_precision))
    print('Micro average - recall    : {0}'.format(micro_recall))
    print('Micro average - F1        : {0}'.format(round(2./((1./micro_precision) + (1./micro_recall)), 2)))