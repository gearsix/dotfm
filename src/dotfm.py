#!/usr/bin/env python3

#==========================
# dotfm - dot file manager
#==========================
# authors: gearsix
# created: 2020-01-15
# updated: 2020-07-26
# notes:
# TODO:
#   - add handling for duplicate alias names (provide user choice)
#   - add the option to submit unknown dotfiles to authors (to be appended to KNOWN_DOTFILES)
#   - add option to install from remote urls
#   - add function to modify dotfile aliases

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
HOME = os.getenv('HOME')                # $HOME (where user's dotfiles are stored)
USER = os.getenv('USER')                # $USER calling dotfm
ARGS = sys.argv                         # parsed arguments
EDITOR = os.getenv('EDITOR') or 'nano'  # text editor to modify dotfiles with
VERSION = 'v2.0.0'
DOTFM_CSV_FILE = '/home/{}/.local/dotfm/installed.csv'.format(USER)
KNOWN_DOTFILES = [ # dotfiles that dotfm knows by default (install location, aliases...)
    [DOTFM_CSV_FILE, 'dotfm', 'dotfm.csv'],
    # bashrc
    ['{}/.bashrc'.format(HOME), '.bashrc', 'bashrc'],
    ['{}/.bash_profile'.format(HOME), '.bash_profile', 'bash_profile'],
    ['{}/.profile'.format(HOME), '.profile', 'profile'],
    # zshell
    ['{}/.zshrc'.format(HOME), '.zshrc', 'zshrc'],
    ['{}/.zprofile'.format(HOME), '.zprofile', 'zprofile'],
    ['{}/.zshenv'.format(HOME), '.zshenv', 'zshenv'],
    # ssh
    ['{}/.ssh/config'.format(HOME), 'ssh_config'],
    # vim
    ['{}/.vimrc'.format(HOME), '.vimrc', 'vimrc'],
    # neovim
    ['{}/.config/nvim/init.vim'.format(HOME), 'init.vim', 'nvimrc'],
    # git
    ['{}/.gitconfig'.format(HOME), '.gitconfig', 'gitconfig'],
    ['{}/.gitmessage'.format(HOME), '.gitmessage', 'gitmessage'],
    ['{}/.gitignore'.format(HOME), '.gitignore', 'gitignore'],
    # ruby
    ['{}/.gemrc'.format(HOME), '.gemrc', 'gemrc'],
    # tmux
    ['{}/.tmux.conf'.format(HOME), 'tmux.conf', 'tmux.conf'],
    # xdg 
    ['{}/.config/user-dirs.dirs'.format(HOME), 'user-dirs.dirs', 'xdg-user-dirs'],
    ['{}/.xinitrc'.format(HOME), '.xinitrc', 'xinitrc'],
    # ranger
    ['{}/.config/rc.conf'.format(HOME), 'rc.conf', 'ranger.conf', 'ranger.cfg'],
    # neofetch
    ['{}/.config/neofetch/config'.format(HOME), 'config', 'neofetch.conf', 'neofetch.cfg'],
    # sway
    ['{}/.config/sway/config'.format(HOME), 'config', 'sway.cfg', 'sway.conf'],
    # awesome
    ['{}/.config/awesome/rc.lua'.format(HOME), 'rc.lua', 'awesomerc'],
    # i3
    ['{}/.config/i3/config'.format(HOME), 'config', 'i3.conf', 'i3.cfg', 'i3'],
    # emacs
    ['{}/.emacs'.format(HOME), '.emacs', 'emacs'],
    # misc
    ['{}/.inputrc'.format(HOME), '.inputrc', 'inputrc']
]
INSTALLED_DOTFILES = [] # appended to during dotfm_init

#-----------
# FUNCTIONS
#-----------
def log_info(info):
    if ARGS.quiet == False:
        LOGGER.info(info)

def error_exit(message):
    LOGGER.error(message)
    sys.exit()

def parse_arguments():
    global ARGS
    valid_commands = ['install', 'remove', 'edit', 'install-all', 'list']
    
    parser = argparse.ArgumentParser(description='a simple tool to help you manage your dot files, see \"man dotfm\" for more.')
    parser.add_argument('cmd', metavar='COMMAND', choices=valid_commands, help='the dotfm COMMAND to execute: {}'.format(valid_commands))
    parser.add_argument('dotfile', metavar='DOTFILE', nargs=argparse.REMAINDER, help='the target dotfile to execute COMMAND on')
    parser.add_argument('-d', '--debug', action='store_true', help='display debug logs')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(VERSION))
    parser.add_argument('-q', '--quiet', action='store_true', help='tell dotfm to shutup')
    ARGS = parser.parse_args()

def dotfm_init():
    """ If DOTFM_CSV_FILE does not exist, create it. If it does, load it's values into KNOWN_DOTFILES
        Will prompt the user where they want the file to be created at,
        if that location does not match DOTFM_CSV_FILE, DOTFM_CSV_FILE 
        will be a symbolic link to that location.
    """
    LOGGER.debug('loading dotfile locations...')

    if not os.path.exists(DOTFM_CSV_FILE):
        LOGGER.warning('{} not found'.format(DOTFM_CSV_FILE))

        # get location to create dotfm.csv at
        location = -1
        while location == -1:
            location = input('where would you like to store the dotfm csv file (default: {})? '.format(DOTFM_CSV_FILE))
            # prompt user to overwrite existing dotfm.csv file
            if len(location) > 0 and os.path.exists(location):
                yn = ''
                while yn == '':
                    yn = input('{} already exists, overwrite (y/n)? '.format(location))
                    if yn[0] == 'y':
                        log_info('overwriting {}'.format(location))
                    elif yn[0] == 'n':
                        log_info('{} already exists, using default location ({})'.format(DOTFILE_LOCATION))
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
        log_info('creating dotfm_csv_file at {}'.format(location))
        os.system('mkdir -p {}'.format(os.path.dirname(location)))
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
    log_info('installing {}...'.format(dotfile))

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
                            log_info('overwriting {} with {}'.format(dest, dotfile))
                            log_info('backup {} -> {}.bak'.format(dest, dest))
                            os.system('mv {} {}.bak'.format(dest, dest))
                            log_info('linking {} -> {}'.format(dest, dotfile)) 
                            os.system('ln -s {} {}'.format(dotfile, dest))
                        elif oca[0] == 'c': # print diff between existing file & dotfile
                            log_info('comparing {} to {}'.format(dotfile, dest))
                            os.system('diff -y {} {}'.format(dotfile, dest))  # maybe use vimdiff ?
                            oca = ''
                        elif oca[0] == 'a': # abort install
                            log_info('aborting install')
                            sys.exit()
                        else:
                            oca = ''
                # create symbolic link to dotfile
                else:
                    os.system('ln -vs {} {}'.format(dotfile, dest))
                # append to DOTFILE_CSV_FILE and INSTALLED_DOTFILES
                log_info('appending to installed dotfiles...')
                with open(DOTFM_CSV_FILE, "a") as dotfm_csv_file:
                    dotfm_csv = csv.writer(dotfm_csv_file)
                    dotfm_csv.writerow(dfl)
                    dotfm_csv_file.close()
                INSTALLED_DOTFILES.append(dfl)
                break

    # handle unrecognised dotfile alias
    if found == False:
        log_info('dotfile not known by dotfm ({})'.format(os.path.basename(dotfile)))
        path = ''
        while path == '':
            path = input('where should dotfm install "{}" (e.g. /home/{}/.bashrc)? '.format(dotfile, USER))
            aliases = input('what aliases would you like to assign to this dotfile (e.g. .bashrc bashrc brc): ')
            dfl = aliases.split(' ')
            dfl.insert(0, path)
            KNOWN_DOTFILES.append(dfl) # will be forgotten at the end of runtime
            dotfm_install(dotfile)
    else:
        log_info('success - you might need to re-open the terminal to see changes take effect')

def dotfm_remove(alias):
    """remove a dotfile (from it's known location) and remove it from DOTFM_CSV_FILE
    
        @param alias = an alias matching the known aliases of the dotfile to remove
    """
    log_info('removing {}...'.format(dotfile))

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
    log_info('editing {}...'.format(dotfile))

    target = ''
    for dfl in INSTALLED_DOTFILES:
        if dotfile in dfl:
            target = '{}'.format(dfl[0])
            os.system('{} {}'.format(EDITOR, target))
            log_info('success - you might need to re-open the terminal to see changes take effect')
            break
        for name in dfl[0]:
            if os.path.basename(dotfile) == name:
                found = True
                target = '{}'.format(os.path.abspath(dfl[1]))
                log_info('found {}'.format(target))
                os.system('{} {}'.format(EDITOR, target))
                log_info('success - you might need to re-open the terminal to see changes take effect')
                break

    if target == '':
        error_exit('could not find alias {} in installed.csv'.format(os.path.basename(dotfile)))

def dotfm_list(dotfiles):
    """ list specified dotfile aliases and install location (displays all if none are specified)
        @param dotfiles = an array of dotfile aliases to list, if len == 0 then all will be printed
    """
    log_info('listing dotfm files: {}'.format('all' if len(dotfiles) == 0 else dotfiles))

    found = False
    printout = [ # string arr, 1 elem for each row
        '\t{} | Location'.format('Aliases...'.ljust(35)),
        '\t----------------------------------------------------------------------------',
    ]

    # list all dotfiles
    if len(dotfiles) == 0:
        for dfl in INSTALLED_DOTFILES:
            aliases = ('"'+'", "'.join(dfl[1:])+'"')
            location = dfl[0]
            if os.path.realpath(dfl[0]) != location:
                location += ' -> {}'.format(os.path.realpath(dfl[0]))
            printout.append('\t{} | {}'.format(aliases.ljust(35), location))
    # list specified dotfiles
    else:
        for dotfile in dotfiles:
            for dfl in INSTALLED_DOTFILES:
                if dotfile in dfl:
                    aliases = ('"'+'", "'.join(dfl[1:])+'"')
                    location = dfl[0]
                    if os.path.realpath(dfl[0]) != location:
                        location += ' -> {}'.format(os.path.realpath(dfl[0]))
                    printout.append('\t{} | {}'.format(aliases.ljust(35), location))
                    break

    for p in printout:
        print(p)

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
        for d in dotfile:
            dotfm_install(os.path.abspath(d))
    elif command == 'remove':
        for d in dotfile:
            dotfm_remove(d)
    elif command == 'edit':
        for d in dotfile:
            dotfm_edit(d)
    elif command == 'list':
        dotfm_list(dotfile)

