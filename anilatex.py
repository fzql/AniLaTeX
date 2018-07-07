﻿#!/usr/bin/python
# -*- coding: utf-8 -*-

# Main script.
import argparse
import errno
import os
import subprocess
import re
from shutil import copy2

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

REGEX = {
    'print': r'显示“(.*)”。'
}


def print_latex(string, workspace, filename='temp'):
    """Produce and compile a standalone LaTeX file"""
    preamble = """\\documentclass[preview]{{standalone}}
\\usepackage{{CJK}}
\\begin{{document}}
\\begin{{CJK}}{{UTF8}}{{gbsn}}%
{}
\\end{{CJK}}
\\end{{document}}
"""
    document = preamble.format(string)
    tex_path = os.path.join(workspace, '{}.tex'.format(filename))
    dvi_path = os.path.join(workspace, '{}.dvi'.format(filename))
    png_path = os.path.join(workspace, '{}.png'.format(filename))
    with open(tex_path, 'w', encoding='utf-8') as file:
        file.write(document)
    with open(os.devnull, 'w') as devnull:
        subprocess.run(['latex', tex_path],
            cwd=workspace, stdout=devnull)
        subprocess.run(['dvipng', dvi_path, '-o', png_path, '-D', '600'],
            cwd=workspace, stdout=devnull)


def parse_animath(path):
    """Parses an AniMath file"""
    file_name = os.path.splitext(os.path.basename(path))[0]
    directory = os.path.join(os.path.dirname(path), '{}-ws'.format(file_name))
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    
    with open(path, 'r', encoding='utf-8') as file:
        commands = file.read().splitlines()
        for command in commands:
            match = re.search(REGEX['print'], command)
            if match:
                print_latex(match.group(1), workspace=directory)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A python script to parse AniMath scripts.')
    parser.add_argument('text', nargs='?',
        help='LaTeX document body to write (can leave empty)')
    parser.add_argument('-i', nargs=1,
        help='name of script to be parsed', metavar='input_file', dest='input')
    parser.add_argument('-o',
        help='name of output file', metavar='output_file', dest='output')
    parser.add_argument('--demo', nargs='?', const='hello_world',
        help='name of demo to be executed', metavar='demo_name')
    args = parser.parse_args()

    if args.output is None:
        args.output = 'text'
    
    if args.text is not None:
        directory = os.path.join(PROJECT_DIR, 'demo', 'ws')
        png_path = os.path.join(directory, '{}.png'.format(args.output))
        try:
            os.makedirs(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        print_latex(args.text, directory, filename=args.output)
        copy2(png_path, os.getcwd())
    elif args.demo is not None:
        path = os.path.join(PROJECT_DIR, 'demo', args.demo)
        parse_animath(path)
    elif args.input is not None:
        parse_animath(args.input)
    else:
        parser.print_help()