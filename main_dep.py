# -*- coding: utf-8 -*-
import yaml
from datetime import datetime
from parsers import StanfordNLP, BerkeleyNLP, RaspNLP

with open('./config.yaml') as file:
    config_global = yaml.load(file, Loader=yaml.FullLoader)
config = config_global['general']

parsers = [StanfordNLP(), BerkeleyNLP(), RaspNLP()]

for parser in parsers:
    curr_pars = parser
    name_save = curr_pars.name_save
    print('Getting dependencies for {0}'.format(parser))
    date_begin = datetime.now()
    curr_pars.get_dependencies(lines_path=config['raw_sentences'],
                               save_path=config['parsed_sent_template'].format(name_save))
    date_end = datetime.now()
    print('Process began at {0}, ended at {1}'.format(date_begin, date_end))
    print('Process took : {0}'.format(date_end - date_begin))
    print('===')
    curr_pars.write_conll_format(lines_path=config['raw_sentences'],
                                 save_path=config['parsed_sent_conll'].format(name_save))


