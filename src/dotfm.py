#!/usr/bin/env python3

#==========================
# dotfm - dot file manager
#==========================
# authors: gearsix
# created: 2020-01-15
# updated: 2020-01-23
# notes:

#---------
# IMPORTS
#---------
import sys
import os
import logging
import argparse

#---------
# GLOBALS
#---------
NAME = os.path.basename(__file__)       # program name
USER = os.getenv('USER')                # $USER calling dotfm
ARGS = sys.argv                         # parsed arguments
EDITOR = os.getenv('EDITOR') or 'nano'  # text editor to modify dotfiles with
VERSION = 'v1.0.0'
DOTFILE_LOCATIONS = [                   # recognised dotfile names & locations
    # filename          # location
    ['.bashrc',         '/home/{}/'.format(USER)],
    ['.profile',        '/home/{}/'.format(USER)],
    ['.bash_profile',   '/home/{}/'.format(USER)],
    ['.vim',            '/home/{}/'.format(USER)],
    ['init.vim',        '/home/{}/.config/nvim'.format(USER)],
    ['.tmux.conf',      '/home/{}/'.format(USER)],
    ['user-dirs.dirs',  '/home/{}/.config/'.format(USER)],
]
SOURCE_DOTFILES = [                     # dotfiles that need to be "source"-ed after editing
    '.bashrc',
    '.profile',
    '.bash_profile',
]

#-----------
# FUNCTIONS
#-----------
def error_exit(message):
    LOGGER.error(message)
    print('ERROR!\t| {}'.format(message))
    sys.exit()

def parse_arguments():
    global ARGS
    valid_commands = ['install', 'remove', 'edit', 'install-all']
    
    parser = argparse.ArgumentParser(description='a simple tool to help you manage your dot files, see \"man dotfm\" for more')
    parser.add_argument('cmd', metavar='COMMAND', choices=valid_commands, help='the dotfm COMMAND to execute: {}'.format(valid_commands))
    parser.add_argument('dotfile', metavar='DOTFILE', help='name of the dotfile dotfm will execute COMMAND on, for \"install\" this must be a path to the dotfile to install')
    parser.add_argument('-d', '--debug', action='store_true', help='display debug logs')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    ARGS = parser.parse_args()

def validate_dotfile_path(dotfile, dotfile_path):
    if not os.path.exists(dotfile_path):
        error_exit('DOTFILE \"{}\" ({}) not found'.format(dotfile, dotfile_path))
    if not os.path.isfile(dotfile_path):
        error_exit('DOTFILE \"{}\" ({}) should be a file, not a dir'.format(dotfile, dotfile_path))

def validate_dotfiledir_path(dirname, dotfiledir_path):
    if not os.path.exists(dotfiledir_path):
        error_exist('DOTFILE DIRECTORY \"{}\" ({}) not found'.format(dotfile, dotfiledir_path))
    if not os.path.isdir(dotfiledir_path):
        error_exit('DOTFILE DIRECTORY \"{}\" ({}) is not a directory'.format(dotfile, dotfiledir_path))

def dotfm_install(dotfile):
    LOGGER.info('installing {}...'.format(dotfile))
    
    for dfl in DOTFILE_LOCATIONS:
        name = dfl[0]
        if os.path.basename(dotfile) == name:
            dest = os.path.abspath(os.path.dirname(dfl[1]))
            # make sure path exists
            if not os.path.exists(dest):
                os.system('mkdir -vp {}'.format(dest))
            # check if file already exists
            if os.path.exists('{}/{}'.format(dest, name)):
                LOGGER.warning('{}/{} already exists!'.format(dest, name))
                oca = ''
                while oca == '':
                    oca = input('[o]verwrite/[c]ompare/[a]bort? ')
                    if len(oca) > 0:
                        if oca[0] == 'o':
                            LOGGER.info('overwriting {} with {}'.format(dest, dotfile))
                            os.system('ln -fvs {} {}'.format(dotfile, dest))
                        elif oca[0] == 'c':
                            LOGGER.info('comparing {} to {}/{}'.format(dotfile, dest, name))
                            os.system('diff {} {}/{}'.format(dotfile, dest, name))  # maybe use vimdiff
                            oca = ''
                        elif oca[0] == 'a':
                            LOGGER.info('aborting install')
                            sys.exit()
                        else:
                            oca = ''
                    else:
                        oca = ''
            else:
                os.system('ln -vs {} {}'.format(dotfile, dest))
            # check if file needs to be sourced
            if name in SOURCE_DOTFILES:
                os.system('source {}/{}'.format(dest, name))

def dotfm_installall(dotfile_dir):
    LOGGER.info('installing all dotfiles in {}'.format(dotfile))

    for df in os.listdir(os.path.abspath(dotfile_dir)):
        df = os.path.abspath('{}/{}'.format(dotfile_dir, df))
        LOGGER.debug('found {}'.format(df))
        if os.path.isfile(df):
            dotfm_install(df)
        elif os.path.isdir(df):
            LOGGER.debug('found dir {}')
            dotfm_installall(df)

def dotfm_remove(dotfile):
    LOGGER.info('removing {}...'.format(dotfile))

    for dfl in DOTFILE_LOCATIONS:
        name = dfl[0]
        if os.path.basename(dotfile) == name:
            target = '{}/{}'.format(os.path.abspath(os.path.dirname(dfl[1])), name)
            os.system('rm -v {}'.format(target))

def dotfm_edit(dotfile):
    LOGGER.info('editing {}...'.format(dotfile))

    target = ''
    for dfl in DOTFILE_LOCATIONS:
        name = dfl[0]
        if os.path.basename(dotfile) == name:
            target = '{}/{}'.format(os.path.abspath(os.path.dirname(dfl[1])), name)
            os.system('{} {}'.format(EDITOR, target))

    if target == '':
        error_exit('could not find {} in DOTFILE_LOCATIONS'.format(os.path.basename(dotfile)))

#------
# MAIN
#------
if __name__ == '__main__':
    parse_arguments()
    command = ARGS.cmd
    dotfile = ARGS.dotfile

    if ARGS.debug == True:
        logging.basicConfig(level=logging.DEBUG, format='%(lineno)-4s {} | %(asctime)s | %(levelname)-7s | %(message)s'.format(NAME))
        LOGGER = logging.getLogger(__name__)
        LOGGER.debug('displaying debug logs')
    else:
        logging.basicConfig(level=logging.INFO, format='%(lineno)-4s {} | %(asctime)s | %(levelname)-7s | %(message)s'.format(NAME))
        LOGGER = logging.getLogger(__name__)


    if command == 'install':
        validate_dotfile_path(dotfile, os.path.abspath(dotfile))
        dotfm_install(os.path.abspath(dotfile))
    elif command == 'remove':
        validate_dotfile_path(dotfile)
        dotfm_remove(os.path.abspath(dotfile))
    elif command == 'edit':
        dotfm_edit(os.path.abspath(dotfile))
    elif command == 'install-all':
        validate_dotfiledir_path(dotfile, os.path.abspath(dotfile))
        dotfm_installall(os.path.abspath(dotfile))
