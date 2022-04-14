#!/usr/bin/env python3

import argparse
import os
import subprocess
import yaml
import sys
import re
import json

# Arguments section
parser = argparse.ArgumentParser()
parser.add_argument('template', help='yaml template describing the project',
    default='template.yaml')
parser.add_argument('--dst-dir', help='the destination directory', default='.')

# Logger class
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

# Template keys
class TemplateKey:
    DevDependencies = 'DevDependencies'
    Dependencies = 'Dependencies'
    ProjectDirs = 'ProjectDirs'
    GitIgnore = 'GitIgnore'
    TsConfig = 'TsConfig'
    Eslint = 'Eslint'
    EslintIgnore = 'EslintIgnore'

# NPM class
class Npm:
    @staticmethod
    def install(module, dev=False, batch=False):
        commands = ['npm', 'install']
        if dev:
            commands += ['--save-dev']
     
        if batch:
            commands += module
        else:
            commands += [module]

        cmd = ' '.join(commands)
        Log.info('install', f'running {cmd} in {os.getcwd()}')
        subprocess.check_call(cmd, shell=True)

    @staticmethod
    def init(fast_init=True):
        cmd = ' '.join(['npm', 'init']
            + ['-y'] if fast_init else [])
        Log.info('init', f'running {cmd} in {os.getcwd()}')
        subprocess.check_call(cmd, shell=True)

    @staticmethod
    def exec(option):
        cmd = f'npx {option}'
        Log.info('npx', f'running {cmd} in {os.getcwd()}')
        subprocess.check_call(cmd, shell=True)

def comment_remover(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " "
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)

def init_project(args):
    Log.info('Template', f'opening {args.template}')
    try:
        with open(args.template, 'r') as template:
            config = yaml.safe_load(template)
    except:
        Log.die('Template', f'There was an error opening {args.template}')

    
    os.makedirs(args.dst_dir, exist_ok=True)
    os.chdir(args.dst_dir)
    Log.info('Initialization', 'running npm init')
    Npm.init()
        
    if TemplateKey.DevDependencies in config.keys():
        Npm.install(config[TemplateKey.DevDependencies], dev=True, batch=True)

    if TemplateKey.Dependencies in config.keys():
        Npm.install(config[TemplateKey.Dependencies], batch=True)

    if 'tsc' in config.get(TemplateKey.DevDependencies, []):
        Npm.exec('tsc --init')
        if TemplateKey.TsConfig in config.keys():
            with open('tsconfig.json') as ts_config:
                json_data = comment_remover(ts_config.read())
            
            data = json.loads(json_data)

            Log.info('TSConfig', f'{config[TemplateKey.TsConfig]}') 
            for key, value in config[TemplateKey.TsConfig].items():
                    data['compilerOptions'][key] = value
                
            with open('tsconfig.json', 'w') as ts_config:
                ts_config.write(json.dumps(data))

    if TemplateKey.Eslint in config.keys():
        with open('.eslintrc.yaml', 'w') as eslint:
            eslint.write(yaml.dump(config[TemplateKey.Eslint]))
    
    if TemplateKey.EslintIgnore in config.keys():
        with open('.eslintignore', 'w') as eslint_ignore:
            for line in config[TemplateKey.EslintIgnore]:
                eslint_ignore.write(line + '\n')   
    
    if TemplateKey.ProjectDirs in config.keys():
        Log.info('Creating directories', f"{config['ProjectDirs']}")
        for dir in config[TemplateKey.ProjectDirs]:
            path = os.path.normpath(os.path.normcase(dir))
            os.makedirs(path, exist_ok=True)
    
    if TemplateKey.GitIgnore in config.keys():
        Log.info('git', 'creating .gitignore')
        with open('.gitignore', 'w') as git_ign:
            for line in config[TemplateKey.GitIgnore]:
                git_ign.write(line + '\n')


if __name__ == '__main__':
    init_project(parser.parse_args())

