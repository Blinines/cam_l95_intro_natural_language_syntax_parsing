# -*- coding: utf-8 -*-

def get_lines(lines_path):
    lines = []
    with open(lines_path, encoding='utf8') as fp:
        for _, line in enumerate(fp):
            lines.append(line[:-1])
    return lines