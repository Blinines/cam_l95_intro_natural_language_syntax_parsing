# -*- coding: utf-8 -*-
import argparse
import yaml
from datetime import datetime
from parsers import StanfordNLP, BerkeleyNLP, RaspNLP

with open('./config.yaml') as file:
    config_global = yaml.load(file, Loader=yaml.FullLoader)
config = config_global['general']

parsers = [StanfordNLP(), BerkeleyNLP(), RaspNLP()]

def run_all(parsers):
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

if __name__=='__main__':
    # Construct the argument parser
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--parser", required=True, help="parser for which we want to parse sentences. " +
                                                          "`benepar`, `stanford` and `rasp` options")
    ap.add_argument("-l", "--lines", required=True, help="path to raw sentences")
    ap.add_argument("-saveall", "--save_all", required=True, help="save path for parsed sentences" + 
                                                                  "in original format")
    ap.add_argument("-saveconll", "--save_conll", required=True, help="save path for parsed sentences" + 
                                                                      "in ConLL-X format")
    
    args = vars(ap.parse_args())
    parser_name_to_class = {'stanford': StanfordNLP(), 'benepar': BerkeleyNLP(), 'rasp': RaspNLP()}

    print('Getting dependencies for {0}'.format(args['parser']))
    parser = parser_name_to_class[args['parser']]
    date_begin = datetime.now()
    parser.get_dependencies(lines_path=args['lines'],
                            save_path=args['save_all'])
    date_end = datetime.now()
    print('Process began at {0}, ended at {1}'.format(date_begin, date_end))
    print('Process took : {0}'.format(date_end - date_begin))
    print('===')
    parser.write_conll_format(args['save_all'],
                              args['save_conll'])


