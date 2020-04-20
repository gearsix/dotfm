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
VERSION = 'v1.0.2'
DOTFILE_LOCATIONS = [   # recognised dotfile names & locations
    # filename aliases                  # location
    [['bashrc', '.bashrc'],                 '/home/{}/.bashrc'.format(USER)],
    [['profile', '.profile'],               '/home/{}/.profile'.format(USER)],
    [['bash_profile', '.bash_profile'],     '/home/{}/.bash_profile'.format(USER)],
    [['vimrc'],                             '/home/{}/.vimrc'.format(USER)],
    [['nvimrc'],                            '/home/{}/.config/nvim/init.vim'.format(USER)],
    [['tmux.conf', 'tmux.cfg'],             '/home/{}/.tmux.conf'.format(USER)],
    [['rc.conf', 'ranger.cfg'],             '/home/{}/.config/ranger/rc.conf'.format(USER)],
    [['user-dirs.dirs', 'xdg-user-dirs'],   '/home/{}/.config/user-dirs.dirs'.format(USER)],
    [['ssh_config', 'ssh.cfg'],             '/home/{}/.ssh/config'.format(USER)]
]

#-----------
# FUNCTIONS
#-----------
def error_exit(message):
    LOGGER.error(message)
    sys.exit()

def parse_arguments():
    global ARGS
    valid_commands = ['install', 'remove', 'edit', 'install-all', 'list']
    
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
    
    found = False
    for dfl in DOTFILE_LOCATIONS:
        if found == True:
            break
        for name in dfl[0]:
            if os.path.basename(dotfile) == name:
                found = True
                dest = os.path.abspath(dfl[1])
                # make sure path exists
                if not os.path.exists(os.path.dirname(dest)):
                    os.system('mkdir -vp {}'.format(dest))
                # check if file already exists
                if os.path.lexists(dest):
                    LOGGER.warning('{} already exists!'.format(dest))
                    oca = ''
                    while oca == '':
                        oca = input('[o]verwrite/[c]ompare/[a]bort? ')
                        if len(oca) > 0:
                            if oca[0] == 'o':
                                LOGGER.info('overwriting {} with {}'.format(dest, dotfile))
                                LOGGER.info('backup {} -> {}.bak'.format(dest, dest))
                                os.system('mv {} {}.bak'.format(dest, dest))
                                LOGGER.info('linking {} -> {}'.format(dest, dotfile)) 
                                os.system('ln -s {} {}'.format(dotfile, dest))
                            elif oca[0] == 'c':
                                LOGGER.info('comparing {} to {}'.format(dotfile, dest))
                                os.system('diff -y {} {}'.format(dotfile, dest))  # maybe use vimdiff
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
                break

    # check for unrecognised dotfile
    if found == False:
        error_exit('dotfile basename not recognised ({})!\nmake sure that the dotfile name and location to install to exist in \"DOTFILE_LOCATIONS\" (see src/dotfm.py)'.format(os.path.basename(dotfile)))
    else:
        LOGGER.info('success - you might need to re-open the terminal to see changes take effect')

def dotfm_installall(dotfile_dir):
    LOGGER.info('installing all dotfiles in {}'.format(dotfile_dir))

    for df in os.listdir(os.path.abspath(dotfile_dir)):
        df = os.path.abspath('{}/{}'.format(dotfile_dir, df))
        if os.path.isfile(df):
            LOGGER.debug('found {}, installing...'.format(df))
            dotfm_install(df)
        elif os.path.isdir(df):
            LOGGER.debug('found dir {}')
            dotfm_installall(df)

def dotfm_remove(dotfile):
    LOGGER.info('removing {}...'.format(dotfile))

    found = False
    for dfl in DOTFILE_LOCATIONS:
        if found == True:
            break
        for name in dfl[0]:
            if os.path.basename(dotfile) == name:
                found = True
                target = '{}'.format(os.path.abspath(dfl[1]), name)
                os.system('rm -v {}'.format(target))
                break

def dotfm_edit(dotfile):
    LOGGER.info('editing {}...'.format(dotfile))

    found = False
    target = ''
    for dfl in DOTFILE_LOCATIONS:
        if found == True:
            break
        for name in dfl[0]:
            if os.path.basename(dotfile) == name:
                found = True
                target = '{}'.format(os.path.abspath(dfl[1]))
                os.system('{} {}'.format(EDITOR, target))
                LOGGER.info('success - you might need to re-open the terminal to see changes take effect')
                break

    if target == '':
        error_exit('could not find {} in DOTFILE_LOCATIONS'.format(os.path.basename(dotfile)))

def dotfm_list(dotfile):
    LOGGER.info('listing dotfm files')

    found = False
    for dfl in DOTFILE_LOCATIONS:
        # list all dotfile locations
        if dotfile == 'all':
            dfln = '"' + '", "'.join(dfl[0]) + '"'
            LOGGER.info('\t{} -> {}'.format(dfln.ljust(35), dfl[1]))#'", "'.join(dfl[0]).ljust(40), dfl[1]))
        # list specific dotfile location
        else:
            if found == True:
                break
            for name in dfl[0]:
                if dotfile == name:
                    found = True
                    dfln = '"' + '", "'.join(dfl[0]) + '"'
                    LOGGER.info('\t{} -> {}'.format(dfln.ljust(35), dfl[1]))
                    break

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
    elif command == 'list':
        dotfm_list(dotfile)

