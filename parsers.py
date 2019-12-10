# -*- coding: utf-8 -*-
import yaml
import subprocess
from os import listdir
import stanfordnlp
import spacy
import benepar
import StanfordDependencies
from benepar.spacy_plugin import BeneparComponent   
from helpers import get_lines

with open('./config.yaml') as file:
    config_global = yaml.load(file, Loader=yaml.FullLoader)

config_stanford_nlp = config_global['config_stanford_nlp']
config_berkeley_nlp = config_global['config_benepar']
config_general = config_global['general']

""" All the default languages are set to English and parameters + documentation accordingly.
Please refer to the parsers' documentation for the use of another language. """


class StanfordNLP:
    """ 
    End-to-end pipeline for StanfordNLP Parser- English
    config='default'       => Default configuration : includes tokenisation
    config='pre-tokenized' => Option available : input sentence already tokenized 

    Processors summary
    Tokenize - MWT - Lemma - POS Processor - Depparse
    """
    def __init__(self, lang='en', config='default'):
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


class BerkeleyNLP:
    """
    End-to-end pipeline for Berkeley Neural Parser - English
    """
    def __init__(self, lang={'spacy': 'en', 'benepar': 'benepar_en2'}, config=None):
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


class RaspNLP:
    """ End-to-end pipeline for RASP - English (only option available) """
    def __init__(self, script_path='./rasp3os/scripts/'):
        self.script_path = script_path
        self.is_possible = config_general['os'] != 'Windows'
        self.name_save = 'rasp'
    
    def get_dependencies(self, lines_path, save_path):
        if self.is_possible:
            command_line = '{0}rasp.sh -m < {1} > {2}'.format(self.script_path,
                                                            lines_path, save_path)
            subprocess.call(command_line, shell=True)
        else:
            print("RASP not configured for this OS, aborting")
        return self