# -*- coding: utf-8 -*-
import yaml
from collections import defaultdict
import subprocess
from os import listdir
import stanfordnlp
import spacy
import benepar
import StanfordDependencies
from benepar.spacy_plugin import BeneparComponent   
from helpers import get_lines, get_rasp_structure, get_sent_info

with open('./config.yaml') as file:
    config_global = yaml.load(file, Loader=yaml.FullLoader)

config_stanford_nlp = config_global['config_stanford_nlp']
config_berkeley_nlp = config_global['config_benepar']
config_general = config_global['general']
sentences = config_general['sentences']

""" All the default languages are set to English and parameters + documentation accordingly.
Please refer to the parsers' documentation for the use of another language. """

class Parser:
    def __init__(self):
        self.sd_equivalent = defaultdict(lambda: '')  # parser => sd
        self.parser_equivalent = defaultdict(lambda: '')  # sd => parser
        self.sd_equivalent['ncsubj'] = 'nsubj'
        self.sd_equivalent['cmod'] = 'rcmod'

    def get_line_info(self, line):
        """ From ConLL format returns list with main info : index, form, head, deprel (in this order) """
        info = line.split('\t')
        return info[:2] + info[6:8]

    def compare_parsing(self, lines_gold, lines_parser):
        identical = defaultdict(int)
        need_manual = []
        if len(lines_gold) != len(lines_parser):
            print('Gold and parser do not have the same tokens -- cannot perform comparison')
            print('')
        else:
            for index, line in enumerate(lines_gold):
                info_gold, info_parser = self.get_line_info(line), self.get_line_info(lines_parser[index])
                if info_gold[2] == info_parser[2]:  # Same head
                    deprel_parser = info_parser[3].split(':')
                    index = 1 if len(deprel_parser)==2 else 0
                    if deprel_parser[index] == info_gold[3]:
                        identical[info_gold[3]] += 1
                    elif self.sd_equivalent[deprel_parser[index]] == info_gold[3]:
                        identical[info_gold[3]] += 1
                    elif deprel_parser[index] == self.parser_equivalent[info_gold[3]]:
                        identical[info_gold[3]] += 1
                    else:
                        need_manual.append((info_gold, info_parser))
                else:
                    need_manual.append((info_gold, info_parser))

            # Printing all results
            print('Total number of dependency relations: {0}'.format(len(lines_gold)))
            deprel = list(identical.keys())
            for elt in deprel:
                print('Successfully identified {0}: {1}'.format(elt, identical[elt]))
            print('')
            print('To be checked manually')
            for elt in need_manual:
                print('{0}\t{1}'.format(elt[0], elt[1]))
        
        return self


class StanfordNLP(Parser):
    """ 
    End-to-end pipeline for StanfordNLP Parser- English
    config='default'       => Default configuration : includes tokenisation
    config='pre-tokenized' => Option available : input sentence already tokenized 

    Processors summary
    Tokenize - MWT - Lemma - POS Processor - Depparse
    """
    def __init__(self, lang='en', config='default'):
        super().__init__()
        # Downloads the language models for the neural pipeline if never installed before
        if 'stanfordnlp_resources' not in listdir('./'):
            stanfordnlp.download('en')
        # Initialize pipeline
        self.nlp = stanfordnlp.Pipeline(**config_stanford_nlp[config])
        self.name_save = 'stanfordnlp'

    
    def get_dependencies(self, lines_path, save_path):
        f = open(save_path, 'w+')
        lines = get_lines(lines_path=lines_path)

        for line in lines:
            f.write(line + '\n')
            f.write('\n')
            doc = self.nlp(line)
            for sent in doc.sentences:
                for word in sent.words:
                    f.write('text: {0}\tlemma: {1}\tupos: {2}\txpos: {3}\tfeats: {4}\tgovernor: {5}\tdependency_relation: {6} \n'
                            .format(word.text, word.lemma, word.upos, word.xpos, word.feats,
                                    word.governor, word.dependency_relation))
                f.write('\n')
            f.write('======')
        f.close()

        return self
    
    def write_conll_format(self, lines_path, save_path, parsed_path=None):
        f = open(save_path, 'w+')
        lines = get_lines(lines_path=lines_path)

        for index, line in enumerate(lines):
            f.write('# sent_id = sent-{0} \n'.format(index+1))
            f.write('# text = {0} \n'.format(line))
            doc = self.nlp(line)
            for sent in doc.sentences:
                for i, word in enumerate(sent.words):
                    f.write('{0}\t{1}\t_\t_\t_\t_\t{2}\t{3}\t_\t_\n'
                            .format(i+1, word.text, word.governor, word.dependency_relation))
                f.write('\n')
        f.close()
        return self


class BerkeleyNLP(Parser):
    """
    End-to-end pipeline for Berkeley Neural Parser - English
    """
    def __init__(self, lang={'spacy': 'en', 'benepar': 'benepar_en2'}, config=None):
        super().__init__()
        self.download = False
        # Checking if NLTK sentence and word tokenizers should be downloaded
        if not config_berkeley_nlp['benepar_sent_word_tok_downloaded']:
            spacy.load(lang['spacy'])
            config_global['config_benepar']['benepar_sent_word_tok_downloaded'] = True
            self.download = True
        # Checking if parsing model should be downloaded
        if not config_berkeley_nlp['parsing_model_downloaded']:
            benepar.download(lang['benepar'])
            config_global['config_benepar']['parsing_model_downloaded'] = True
            self.download = True
        # Updating yaml file if necessary
        if self.download:
            with open("./config.yaml", "w") as f:
                yaml.dump(config_global, f)
        
        self.nlp = spacy.load(lang['spacy'])
        self.nlp.add_pipe(BeneparComponent(lang['benepar']))
        self.sd = StanfordDependencies.get_instance(backend='subprocess')  # to convert trees
        self.name_save = 'benepar'

    def get_dependencies(self, lines_path, save_path):
        f = open(save_path, 'w+')
        lines = get_lines(lines_path=lines_path)

        for line in lines:
            f.write(line + '\n')
            doc = self.nlp(line)
            for sent in list(doc.sents):
                dependency = self.sd.convert_tree(sent._.parse_string)
                for token in dependency:
                    f.write('index: {0}\tform: {1}\tcpos: {2}\tpos: {3}\thead: {4}\tdeprel: {5} \n'
                            .format(token.index, token.form, token.cpos, token.pos, token.head,
                                    token.deprel))
            f.write('\n')
            f.write('======')
        
        f.close()
        return self
    
    def write_conll_format(self, lines_path, save_path, parsed_path=None):
        f = open(save_path, 'w+')
        lines = get_lines(lines_path=lines_path)

        for index, line in enumerate(lines):
            f.write('# sent_id = sent-{0} \n'.format(index+1))
            f.write('# text = {0} \n'.format(line))
            doc = self.nlp(line)
            for sent in list(doc.sents):
                dependency = self.sd.convert_tree(sent._.parse_string)
                for token in dependency:
                    f.write('{0}\t{1}\t_\t_\t_\t_\t{2}\t{3}\t_\t_\n'
                            .format(token.index, token.form, token.head, token.deprel))
            f.write('\n')
        f.close()
        return self


class RaspNLP(Parser):
    """ End-to-end pipeline for RASP - English (only option available) """
    def __init__(self, script_path='./rasp3os/scripts/'):
        super().__init__()
        self.script_path = script_path
        self.is_possible = config_general['os'] != 'Windows'
        self.name_save = 'rasp'
        self.parser_equivalent['nn'] = 'ncmod'
        self.parser_equivalent['prt'] = 'iobj'
        self.parser_equivalent['amod'] = 'ncmod'
        self.parser_equivalent['advmod'] = 'ncmod'
        self.parser_equivalent['pobj'] = 'dobj'
    
    def get_dependencies(self, lines_path, save_path):
        if self.is_possible:
            command_line = '{0}rasp.sh -m < {1} > {2}'.format(self.script_path,
                                                            lines_path, save_path)
            subprocess.call(command_line, shell=True)
        else:
            print("RASP not configured for this OS, aborting")
        return self
    
    def write_conll_format(self, parsed_path, save_path, lines_path=None, spec_to_sent=False):
        # Converting output of RASP algorithm on Linux into conll format.
        # If output was transferred into Windows system, can be done.
        f = open(save_path, 'w+', encoding='utf-8')
        try:
            rasp_file = open(parsed_path, 'r', encoding='utf-8')
        except Exception as e:
            print('RASP file does not exist. Aborting.')
            return
        lines = rasp_file.readlines()
        sent_begin, dep_begin, block_end = get_rasp_structure(lines=lines)
        nb_sent = len(sent_begin)

        if not spec_to_sent:  # General case, sentences detected are described one by one
            for i in range(nb_sent):
                f.write('# sent_id = sent-{0} \n'.format(i+1))
                class_words = get_sent_info(lines=lines, index_sent=sent_begin[i],
                                            index_dep=dep_begin[i], index_block=block_end[i])
                for word in class_words:
                    if word.head is not None:
                        f.write('{0}\t{1}\t_\t_\t_\t_\t{2}\t{3}\t_\t_\n'
                                .format(word.index + 1, word.form, word.head + 1, word.deprel))
                    else:
                        f.write('{0}\t{1}\t_\t_\t_\t_\t{2}\t{3}\t_\t_\n'
                                .format(word.index + 1, word.form, word.head, word.deprel))
                f.write('\n')
        
        else:  # Case specific to the 10 sentences chosent for the project. Aim = looking like gold standards.
            sent_id = [1, 2, 3, 4, 5, 5, 6, 7, 8, 8, 9, 10]
            for i in range(nb_sent):
                if i not in [5, 9]:
                    f.write('# sent_id = sent-{0} \n'.format(sent_id[i]))
                    f.write('# text = {0} \n'.format(sentences[i+1]))
                class_words = get_sent_info(lines=lines, index_sent=sent_begin[i],
                                            index_dep=dep_begin[i], index_block=block_end[i])
                for word in class_words:
                    if word.head is not None:
                        f.write('{0}\t{1}\t_\t_\t_\t_\t{2}\t{3}\t_\t_\n'
                                .format(word.index + 1, word.form, word.head + 1, word.deprel))
                    else:
                        f.write('{0}\t{1}\t_\t_\t_\t_\t{2}\t{3}\t_\t_\n'
                                .format(word.index + 1, word.form, word.head, word.deprel))
                if i not in [4, 8]:
                    f.write('\n')
        f.close()
        return self