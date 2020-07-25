#!/usr/bin/env python3

#==========================
# dotfm - dot file manager
#==========================
# authors: gearsix
# created: 2020-01-15
# updated: 2020-07-20
# notes:
# TODO:
#   - add handling for duplicate alias names (provide user choice)
#   - make KNOWN_DOTFILES more exhaustive
#   - on installing unknown dotfile, add the option to send request to authors to add it to KNOWN_DOTFILES

#---------
# IMPORTS
#---------
# std
import sys
import os
import csv
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
DOTFM_CSV_FILE = '/home/{}/.config/dotfm/installed.csv'.format(USER)
KNOWN_DOTFILES = [ # dotfiles that dotfm knows by default
    # location                                          # aliases
    ['/home/{}/.config/dotfm/{}'.format(USER, os.path.basename(DOTFM_CSV_FILE)),   os.path.basename(DOTFM_CSV_FILE), 'dotfm'],
    ['/home/{}/.bashrc'.format(USER),                   '.bashrc', 'bashrc'],
    ['/home/{}/.profile'.format(USER),                  '.profile', 'profile'],
    ['/home/{}/.bash_profile'.format(USER),             '.bash_profile', 'bash_profile'],
    ['/home/{}/.ssh/config'.format(USER),               'ssh_config'],
    ['/home/{}/.vimrc'.format(USER),                    '.vimrc', 'vimrc'],
    ['/home/{}/.config/nvim/init.vim'.format(USER),     'init.vim', 'nvimrc'],
    ['/home/{}/.tmux.conf'.format(USER),                'tmux.conf', 'tmux.conf'],
    ['/home/{}/.config/rc.conf'.format(USER),           'rc.conf', 'ranger.conf'],
    ['/home/{}/.config/user-dirs.dirs'.format(USER),    'user-dirs.dirs', 'xdg-user-dirs'],
]
INSTALLED_DOTFILES = [] # appended to during dotfm_init

#-----------
# FUNCTIONS
#-----------
def error_exit(message):
    LOGGER.error(message)
    sys.exit()

def parse_arguments():
    global ARGS
    valid_commands = ['install', 'remove', 'edit', 'install-all', 'list']
    
    parser = argparse.ArgumentParser(description='a simple tool to help you manage your dot files, see \"man dotfm\" for more.')
    parser.add_argument('cmd', metavar='COMMAND', choices=valid_commands, help='the dotfm COMMAND to execute: {}'.format(valid_commands))
    parser.add_argument('dotfile', metavar='DOTFILE', help='the target dotfile to execute COMMAND on')
    parser.add_argument('-d', '--debug', action='store_true', help='display debug logs')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    ARGS = parser.parse_args()

def dotfm_init():
    """ If DOTFM_CSV_FILE does not exist, create it. If it does, load it's values into KNOWN_DOTFILES
        Will prompt the user where they want the file to be created at,
        if that location does not match DOTFM_CSV_FILE, DOTFM_CSV_FILE 
        will be a symbolic link to that location.

        @param LOGGER = A logger to use the .debug, .warning and .info functions of
    """
    
    LOGGER.debug('loading dotfile locations...')

    if not os.path.exists(DOTFM_CSV_FILE):
        LOGGER.warning('dotfile_locations not found')

        # get location to create dotfm.csv at
        location = -1
        while location == -1:
            location = input('where would you like to store the dotfm config (default: {})? '.format(DOTFM_CSV_FILE))
            # prompt user to overwrite existing dotfm.csv file
            if len(location) > 0 and os.path.exists(location):
                yn = ''
                while yn == '':
                    yn = input('{} already exists, overwrite (y/n)? '.format(location))
                    if yn[0] == 'y':
                        LOGGER.info('overwriting {}'.format(location))
                    elif yn[0] == 'n':
                        LOGGER.info('{} already exists, using default location ({})'.format(DOTFILE_LOCATION))
                        location = DOTFM_CSV_FILE
                    else:
                        yn = ''
            # use default location
            elif len(location) == 0:
                location = DOTFM_CSV_FILE
            # ask again
            else:
                location = -1

        # write dotfm dotfile to csv
        dotfm_csv = open(location, "w")
        for i, dfl in enumerate(KNOWN_DOTFILES[0]):
            if i == 0:
                dotfm_csv.write(dfl)
            else:
                dotfm_csv.write(',{}'.format(dfl))
        dotfm_csv.write('\n')
        dotfm_csv.close()

        # create dotfm.csv symbolic link
        os.system('mkdir -p {}'.format(os.path.dirname(DOTFM_CSV_FILE)))
        if os.path.abspath(location) != DOTFM_CSV_FILE:
            os.system('ln -fsv {} {}'.format(os.path.abspath(location), DOTFM_CSV_FILE))

        # append to INSTALLED_DOTFILES
        INSTALLED_DOTFILES.append(KNOWN_DOTFILES[0])
    else: # load existing values into INSTALLED_DOTFILES
        dotfm_csv = open(DOTFM_CSV_FILE, "r")
        dotfm_csv_reader = csv.reader(dotfm_csv)
        for dfl in dotfm_csv_reader:
            INSTALLED_DOTFILES.append(dfl)
        dotfm_csv.close()

def dotfm_install(dotfile):
    """ check "KNOWN_DOTFILES" to see if an alias matches "dotfile" basename, if it does create a
        symbolic link from "dotfile" to the matching "KNOWN_DOTFILES" location (index 0).

        If file at matching "KNOWN_DOTFILES" location exists, prompt user to overwrite it.

        @param dotfile = filepath to the dotfile to install
    """

    LOGGER.info('installing {}...'.format(dotfile))

    # check if dotfile matches an alias in KNOWN_DOTFILES
    found = False
    for dfl in KNOWN_DOTFILES:
        if found == True:
            break
        for alias in dfl[1:]:
            if os.path.basename(dotfile) == alias: # compare dotfile base file name
                found = True
                # make sure dotfile dir exists
                dest = os.path.abspath(dfl[0])
                if not os.path.exists(os.path.dirname(dest)):
                    os.system('mkdir -vp {}'.format(dest))
                # check if file already exists and prompt for action if it does
                if os.path.lexists(dest):
                    LOGGER.warning('{} already exists!'.format(dest))
                    oca = ''
                    while oca == '':
                        oca = input('[o]verwrite/[c]ompare/[a]bort? ')
                        if oca[0] == 'o': # overwrite existing file
                            LOGGER.info('overwriting {} with {}'.format(dest, dotfile))
                            LOGGER.info('backup {} -> {}.bak'.format(dest, dest))
                            os.system('mv {} {}.bak'.format(dest, dest))
                            LOGGER.info('linking {} -> {}'.format(dest, dotfile)) 
                            os.system('ln -s {} {}'.format(dotfile, dest))
                        elif oca[0] == 'c': # print diff between existing file & dotfile
                            LOGGER.info('comparing {} to {}'.format(dotfile, dest))
                            os.system('diff -y {} {}'.format(dotfile, dest))  # maybe use vimdiff ?
                            oca = ''
                        elif oca[0] == 'a': # abort install
                            LOGGER.info('aborting install')
                            sys.exit()
                        else:
                            oca = ''
                # create symbolic link to dotfile
                else:
                    os.system('ln -vs {} {}'.format(dotfile, dest))
                # append to DOTFILE_CSV_FILE and INSTALLED_DOTFILES
                LOGGER.info('appending to installed dotfiles...')
                with open(DOTFM_CSV_FILE, "a") as dotfm_csv_file:
                    dotfm_csv = csv.writer(dotfm_csv_file)
                    dotfm_csv.writerow(dfl)
                    dotfm_csv_file.close()
                INSTALLED_DOTFILES.append(dfl)
                break

    # handle unrecognised dotfile alias
    if found == False:
        LOGGER.info('dotfile not known by dotfm ({})'.format(os.path.basename(dotfile)))
        path = ''
        while path == '':
            path = input('where should dotfm install "{}" (e.g. /home/{}/.bashrc)? '.format(dotfile, USER))
            aliases = input('what aliases would you like to assign to this dotfile (e.g. .bashrc bashrc brc): ')
            dfl = aliases.split(' ')
            dfl.insert(0, path)
            KNOWN_DOTFILES.append(dfl) # will be forgotten at the end of runtime
            dotfm_install(dotfile)
    else:
        LOGGER.info('success - you might need to re-open the terminal to see changes take effect')

def dotfm_remove(alias):
    """remove a dotfile (from it's known location) and remove it from DOTFM_CSV_FILE
    
        @param alias = an alias matching the known aliases of the dotfile to remove
    """
    LOGGER.info('removing {}...'.format(dotfile))

    found = -1
    for i, dfl in enumerate(INSTALLED_DOTFILES):
        if alias in dfl:
            found = i
            break

    if found != -1:
        # remove dotfile
        target = '{}'.format(os.path.abspath(dfl[0]))
        os.system('rm -v {}'.format(target))
        # remove from installed
        del INSTALLED_DOTFILES[found]
        with open(DOTFM_CSV_FILE, 'w') as dotfm_file:
            dotfm_csv = csv.writer(dotfm_file)
            dotfm_csv.writerows(INSTALLED_DOTFILES)
            dotfm_file.close()

def dotfm_edit(dotfile_alias):
    """ open dotfile with alias matching "dotfm_alias" in EDITOR
        @param dotfile_alias = an alias of the dotfile to open
    """
    LOGGER.info('editing {}...'.format(dotfile))

    target = ''
    for dfl in INSTALLED_DOTFILES:
        if dotfile in dfl:
            target = '{}'.format(dfl[0])
            os.system('{} {}'.format(EDITOR, target))
            LOGGER.info('success - you might need to re-open the terminal to see changes take effect')
            break

    if target == '':
        error_exit('could not find alias {} in installed.csv'.format(os.path.basename(dotfile)))

def dotfm_list(dotfile):
    LOGGER.info('listing dotfm files')

    found = False
    LOGGER.info('\t{} Location'.format('Aliases...'.ljust(35)))
    for dfl in INSTALLED_DOTFILES:
        # list all dotfile locations
        if dotfile == 'all':
            dfln = '"' + '", "'.join(dfl[1:]) + '"'
            LOGGER.info('\t{} {} -> {}'.format(dfln.ljust(35), dfl[0], os.path.realpath(dfl[0])))
        # list specific dotfile location
        else:
            for name in dfl:
                if dotfile == name:
                    found = True
                    dfln = '"' + '", "'.join(dfl[1:]) + '"'
                    LOGGER.info('\t{} {} -> {}'.format(dfln.ljust(35), dfl[0], os.path.realpath(dfl[0])))
                    break

#------
# MAIN
#------
if __name__ == '__main__':
    # parse args
    parse_arguments()
    command = ARGS.cmd
    dotfile = ARGS.dotfile

    # init LOGGER
    log_lvl = logging.INFO
    log_fmt = '%(lineno)-4s {} | %(asctime)s | %(levelname)-7s | %(message)s'.format(NAME)
    if ARGS.debug == True:
        LOGGER.debug('displaying debug logs')
        log_lvl = logging.DEBUG
    logging.basicConfig(level=log_lvl, format=log_fmt)
    LOGGER = logging.getLogger(__name__)

    # load dotfile locations
    dotfm_init()

    # run command
    if command == 'install':
        dotfm_install(os.path.abspath(dotfile))
    elif command == 'remove':
        dotfm_remove(dotfile)
    elif command == 'edit':
        dotfm_edit(dotfile)
    elif command == 'list':
        dotfm_list(dotfile)

