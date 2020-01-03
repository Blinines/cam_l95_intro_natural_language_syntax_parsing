# -*- coding: utf-8 -*-
import re

class Word:
    def __init__(self, index, form, head=None, deprel=None):
        self.index = index
        if (len(form)==2) and (form[0]=='\\'):
            self.form = form[1]
        else:
            self.form = form
        self.head = head
        self.deprel = deprel

    def set_head(self, head):
        self.head = head

    def set_deprel(self, deprel):
        self.deprel = deprel

def get_lines(lines_path):
    lines = []
    with open(lines_path, encoding='utf8') as fp:
        for _, line in enumerate(fp):
            lines.append(line[:-1])
    return lines

def get_elt_to_index(l):
    res = {}
    for index, elt in l:
        res[elt] = index
    return res

def get_rasp_structure(lines):
    # Findind beginning of sentences, dependency relation within sentences and end of each sentence
    sent_begin, dep_begin, block_end = [], [], []
    index = 0
    while index < len(lines):
        if lines[index] == 'gr-list: 1\n':
            sent_begin.append(index-1)
            dep_begin.append(index+1)
            index += 1
        elif lines[index] == '\n':
            block_end.append(index)
            index += 2
        else:
            index +=1
    
    return sent_begin, dep_begin, block_end

def get_words_sent(lines, index):
    # Getting words in order from the sentence line
    right_part = ' |;| '.join(lines[index].split(';')[:-1])
    raw_words_draft = [elt for elt in right_part[2:-5].split('|') if elt != ' ' ]
    raw_words = []
    for elt in raw_words_draft:
        pot_words = elt.split(' ')
        raw_words += [word for word in pot_words if word != '']
    class_words = [Word(index, form) for index, form in enumerate(raw_words)]
    return class_words

def get_dep_info(line):
    # Getting dependency info in exploitable format for a given line
    info_line = [elt for elt in line[2:-2].split('|') if elt not in ['', ' ', ' _ ', ' _']]
    dep_info = [info_line[0]]
    for elt in info_line[1:]:
        if ':' in elt:
            dep_info.append(elt.split(':')[1].split('_')[0])
        else:  # complementary info on dep relation
            dep_info[0] = dep_info[0] + ':{0}'.format(elt)
    return dep_info

def get_sent_info(lines, index_sent, index_dep, index_block):
    class_words = get_words_sent(lines=lines, index=index_sent)
    for line in lines[index_dep:index_block]:
        dep_info = get_dep_info(line=line)
        index_dep = int(dep_info[-1])
        class_words[index_dep].set_head(int(dep_info[1]))
        class_words[index_dep].set_deprel(dep_info[0])
    return class_words


