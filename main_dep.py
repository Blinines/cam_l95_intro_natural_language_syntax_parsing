# -*- coding: utf-8 -*-
import yaml
from parsers import StanfordNLP, BerkeleyNLP, RaspNLP

with open('./config.yaml') as file:
    config_global = yaml.load(file, Loader=yaml.FullLoader)
config = config_global['general']

parsers = [StanfordNLP(), BerkeleyNLP(), RaspNLP()]

for parser in parsers:
    curr_pars = parser
    name_save = curr_pars.name_save
    curr_pars.get_dependencies(lines_path=config['raw_sentences'],
                               save_path=config['parsed_sent_template'].format(name_save))
    curr_pars.get_dependencies(lines_path=config['raw_sentences'],
                               save_path=config['parsed_sent_conll'].format(name_save))


