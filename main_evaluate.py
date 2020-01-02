# -*- coding: utf-8 -*-
from io import open
import yaml
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


with open('./config.yaml') as file:
    config_global = yaml.load(file, Loader=yaml.FullLoader)

test = [[None]*(len(config_global['general']['dep_level_0'])+1)]
dep_gold = get_dep_list(data_path=config_global['general']['gold_standard'])
dep_parser = get_dep_list(data_path=config_global['general']['parsed_sent_conll'].format('benepar'))
nb_dep = len(dep_gold)
print(nb_dep, len(dep_parser))