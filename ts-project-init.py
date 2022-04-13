#!/usr/bin/env python3

import argparse
import os
import subprocess
import yaml
import sys

parser = argparse.ArgumentParser()
parser.add_argument('template', help='yaml template describing the project',
    default='template.yaml')

class AnsiColor:
    Black = '\u001b[30m'
    Red = '\u001b[31m'
    Green = '\u001b[32m'
    Yellow = '\u001b[33m'
    Blue = '\u001b[34m'
    Magenta = '\u001b[35m'
    Cyan = '\u001b[36m'
    White = '\u001b[37m'
    Reset = '\u001b[0m'

class Log:
    @staticmethod
    def info(name, msg):
        print(f'{AnsiColor.Cyan}[{name}] {msg}{AnsiColor.Reset}')

    @staticmethod
    def warn(name, msg):
        print(f'{AnsiColor.Yellow}[{name}] {msg}{AnsiColor.Reset}')

    @staticmethod
    def die(name, msg):
        sys.exit(f'{AnsiColor.Red}[{name}] {msg}{AnsiColor.Reset}')

class Npm:
    @staticmethod
    def install(module, dev=False, batch=False):
        commands = ['npm', 'install']
        if dev:
            commands += ['--save-dev']
     
        commands += [module] if not batch else module


        cmd = ' '.join(commands)
        Log.info('build', f'running {cmd} in {os.getcwd()}')
        subprocess.check_call(cmd, shell=True)

    @staticmethod
    def init(fast_init=True):
        cmd = ' '.join(['npm', 'init']
            + ['-y'] if fast_init else [])
        Log.info('build', f'running {cmd} in {os.getcwd()}')
        subprocess.check_call(cmd, shell=True)


def init_project(args):
    Log.info('Initialization', 'running npm init')
    Npm.init()
    with open(args.template, 'r') as template:
        config = yaml.safe_load(template)
    
    Log.info('Dev deps', 'installing dev deps')
    dev_deps = [dev_dep for dev_dep in config['DevDependencies']]
    Npm.install(dev_deps, dev=True, batch=True)
    
    Log.info('Creating directories', f"{config['ProjectDirs']}")
    for dir in config['ProjectDirs']:
        norm = os.path.normpath(dir)
        os.makedirs(norm, exist_ok=True)
    
    if 'GitIgnore' in config.keys():
        Log.info('git', 'creating .gitignore')
        with open('.gitignore', 'w') as git_ign:
            git_ign.writelines(config['GitIgnore'])


if __name__ == '__main__':
    init_project(parser.parse_args())

