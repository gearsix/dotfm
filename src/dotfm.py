#!/usr/bin/env python3

#=========================
# dotfm - dotfile manager
#=========================
# authors: gearsix
# created: 2020-01-15
# updated: 2021-04-22

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
NAME = os.path.basename(__file__)
HOME = os.getenv('HOME')
USER = os.getenv('USER')
ARGS = []
EDITOR = os.getenv('EDITOR') or 'nano'
VERSION = 'v2.2.0'
INSTALLED = []
INSTALLED_FILE = '/home/{}/.local/share/dotfm/installed.csv'.format(USER)
KNOWN = [ # dotfiles that dotfm knows by default
    # install location, aliases...
    [INSTALLED_FILE, 'dotfm'],
    ['{}/.bashrc'.format(HOME), '.bashrc', 'bashrc'],
    ['{}/.bash_profile'.format(HOME), '.bash_profile', 'bash_profile'],
    ['{}/.profile'.format(HOME), '.profile', 'profile'],
    ['{}/.zshrc'.format(HOME), '.zshrc', 'zshrc'],
    ['{}/.zprofile'.format(HOME), '.zprofile', 'zprofile'],
    ['{}/.zshenv'.format(HOME), '.zshenv', 'zshenv'],
    ['{}/.ssh/config'.format(HOME), 'ssh_config'],
    ['{}/.vimrc'.format(HOME), '.vimrc', 'vimrc'],
    ['{}/.config/nvim/init.vim'.format(HOME), 'init.vim', 'nvimrc'],
    ['{}/.gitconfig'.format(HOME), '.gitconfig', 'gitconfig'],
    ['{}/.gitmessage'.format(HOME), '.gitmessage', 'gitmessage'],
    ['{}/.gitignore'.format(HOME), '.gitignore', 'gitignore'],
    ['{}/.gemrc'.format(HOME), '.gemrc', 'gemrc'],
    ['{}/.tmux.conf'.format(HOME), 'tmux.conf', 'tmux.conf'],
    ['{}/.config/user-dirs.dirs'.format(HOME), 'user-dirs.dirs', 'xdg-user-dirs'],
    ['{}/.xinitrc'.format(HOME), '.xinitrc', 'xinitrc'],
    ['{}/.config/rc.conf'.format(HOME), 'rc.conf', 'ranger.conf', 'ranger.cfg'],
    ['{}/.config/neofetch/config'.format(HOME), 'config', 'neofetch.conf', 'neofetch.cfg'],
    ['{}/.config/sway/config'.format(HOME), 'config', 'sway.cfg', 'sway.conf'],
    ['{}/.config/awesome/rc.lua'.format(HOME), 'rc.lua', 'awesomerc'],
    ['{}/.config/i3/config'.format(HOME), 'config', 'i3.conf', 'i3.cfg', 'i3'],
    ['{}/.emacs'.format(HOME), '.emacs', 'emacs'],
    ['{}/.inputrc'.format(HOME), '.inputrc', 'inputrc'],
    ['{}/.sfeed'.format(HOME), '.sfeedrc', 'sfeedrc'],
]

#-----------
# FUNCTIONS
#-----------
# utilities
def debug(message):
    if ARGS.debug == True:
        print(message)

def info(message):
    if ARGS.quiet == False:
        print(message)

def warn(message):
    input('{}, press enter to continue.'.format(message))

def fatal(message):
    print(message)
    sys.exit()

# main
def parseargs():
    valid_commands = ['install', 'update', 'remove', 'edit', 'list']
    parser = argparse.ArgumentParser(description='a simple tool to help you manage your dotfile symlinks.')
    # OPTIONS
    parser.add_argument('-s', '--skip', action='store_true',
            help='skip any user prompts and use default values where possible')
    parser.add_argument('-d', '--debug', action='store_true',
            help='display debug logs')
    parser.add_argument('-v', '--version', action='version',
            version='%(prog)s {}'.format(VERSION))
    parser.add_argument('-q', '--quiet', action='store_true',
            help='mute dotfm info logs')
    # POSITIONAL
    parser.add_argument('cmd', metavar='COMMAND', choices=valid_commands,
            help='the dotfm COMMAND to execute: {}'.format(valid_commands))
    parser.add_argument('dotfile', metavar='DOTFILE', nargs=argparse.REMAINDER,
            help='the target dotfile to execute COMMAND on')
    return parser.parse_args()

# main/init
def init():
    debug('init: loading dotfile locations')
    if not os.path.exists(INSTALLED_FILE):
        debug(INSTALLED_FILE, 'not found')
        init_createcsv()
    INSTALLED = init_loadcsv(INSTALLED_FILE)
    INSTALLED = init_cleandups(INSTALLED, 0)

def init_createcsv(default_location):
    location = default_location
    if ARGS.skip == False:
        location = input('dotfm csv file location (default: {})? '.format(default_location))
        if len(location) == 0:
            location = default_location
        if os.path.exists(location):
            debug(location, 'already exists')
            on = input('[o]verwrite or [u]se {}? '.format(location))
            if len(on) > 0:
                if on[0] == 'o': # create file at location & write KNOWN[0] to it
                    warn('overwriting {}, all existing data in this file will be lost')
                    os.system('mkdir -p', os.path.dirname(location))
                    dotfm_csv = open(location, "w")
                    for i, dfl in enumerate(KNOWN[0]):
                        dotfm_csv.write(dfl if i == 0 else ',{}'.format(dfl))
                    dotfm_csv.write('\n')
                    dotfm_csv.close()
                elif on[0] == 'u':
                    debug('', location)
                    sys.exit()
    # create default_location symlink
    if os.path.abspath(location) != os.path.abspath(default_location):
        debug('creating dotfm csv file symlink')
        os.system('mkdir -p', os.path.dirname(default_location))
        os.system('ln -isv', os.path.abspath(location), default_location)

def init_loadcsv(location):
    data = []
    dotfm_csv = csv.reader(open(location, "r"))
    for dfl in dotfm_csv:
        data.append(dfl)
    dotfm_csv.close()
    return data

def init_cleandups(data, id_index):
    unique = []
    for d in data:
        for i, u in enumerate(unique):
            if d[id_index] == u[id_index]:
                unique[i] = d # assume later entry = more recent
    return unique

# main/install
def dotfm_install(dotfile_source):
    """ Check "KNOWN" to see if an alias matches "dotfile" basename,
        if it does create a symbolic link from "dotfile" to the matching
        "KNOWN" location (index 0).

        If file at matching "KNOWN" location exists, prompt user to
        overwrite it.

        @param dotfile = filepath to the dotfile to install
    """
    log_info('installing {}...'.format(dotfile_source))

    # check if dotfile matches an alias in KNOWN
    found = -1
    for d, dfl in enumerate(KNOWN):
        for a, alias in enumerate(dfl[1:]):
            if os.path.basename(dotfile_source) == alias:
                found = d

    # prompt for location
    dest = ''
    if found != -1:
        dest = os.path.abspath(KNOWN[found][0])
    if len(dest) == 0 or ARGS.skip == False:
        default = dest
        dest = ''
        while dest == '':
            dest = input('install location ({})? '.format('default: {}'.format(default) if len(default) > 0 else ''))
            if len(dest) == 0 and len(default) > 0:
                dest = default
            elif dest.find('~') != -1:
                dest = dest.replace('~', HOME)
    # prompt for aliases
    aliases = []
    if found != -1:
        aliases = KNOWN[found][1:]
    if len(aliases) == 0 or ARGS.skip == False:
        default = aliases
        aliases = []
        while len(aliases) == 0:
            inp = input('aliases to call dotfile by ({})? '.format('default: {}'.format(default) if len(default) > 0 else ''))
            if len(inp) > 0:
                aliases = inp.split(' ')
            elif len(default) > 0:
                aliases = default
    # make sure dotfile dir exists
    if not os.path.exists(os.path.dirname(dest)):
        os.system('mkdir -vp {}'.format(dest))
    # check if file already exists and prompt for action if it does
    if os.path.lexists(dest):
        oca = ''
        while oca == '':
            oca = input('{} already exists, [o]verwrite/[c]ompare/[a]bort? '.format(dest))
            if oca[0] == 'o': # overwrite existing file
                log_info('overwriting {}'.format(dest))
                os.system('rm {}'.format(dest))
            elif oca[0] == 'c': # print diff between existing file & dotfile
                log_info('comparing {} to {}'.format(dotfile_source, dest))
                os.system('diff -bys {} {}'.format(dotfile_source, dest))  # use vimdiff ?
                oca = ''
            elif oca[0] == 'a': # abort install
                log_info('aborting install')
                sys.exit()
            else:
                oca = ''
    # create symbolic link to dotfile
    os.system('ln -vs {} {}'.format(dotfile_source, dest))
    # append to DOTFILE_CSV_FILE and INSTALLED
    log_info('appending to installed dotfiles...')
    dfl = aliases
    dfl.insert(0, dest)
    with open(INSTALLED_FILE, "a") as dotfm_csv_file:
        dotfm_csv = csv.writer(dotfm_csv_file, lineterminator='\n')
        dotfm_csv.writerow(dfl)
        dotfm_csv_file.close()
    INSTALLED.append(dfl)

    log_info('success - you might need to re-open the terminal to see changes take effect')

# main/update
def dotfm_update(dotfile_alias, new_source):
    """ Update the source location that the dotfile symlink of an already
        installed dotfile points to. If the dotfile_alias does not exist in
        INSTALLED_FILE, dotfm_install is called instead.

        @param alias = an alias matching the known aliases of the dotfile to
        update
        @param new_source = the new filepath to point the dotfile symlink to
    """

    log_info('updating {} -> {}...'.format(dotfile_alias, new_source))

    found = -1
    for i, dfl in enumerate(INSTALLED):
        if dotfile_alias in dfl:
            found = i
            break

    if found != -1:
        # stat new_source
        if os.path.exists(new_source):
            os.system('ln -isv {} {}'.format(new_source, dfl[0]))
        else:
            log_info('{} does not exist'.format(new_source))
    else:
        log_info('could not find dotfile matching alias "{}"'.format(
            dotfile_alias))

# main/remove
def dotfm_remove(alias):
    """ Remove a dotfile (from it's known location) and remove it from
        INSTALLED_FILE
    
        @param alias = an alias matching the known aliases of the dotfile to
        remove
    """
    log_info('removing {}...'.format(alias))

    found = -1
    for i, dfl in enumerate(INSTALLED):
        if alias in dfl:
            found = i
            break

    if found != -1:
        # remove dotfile
        target = '{}'.format(os.path.abspath(dfl[0]))
        os.system('rm -iv {}'.format(target))
        # remove from installed
        del INSTALLED[found]
        with open(INSTALLED_FILE, 'w') as dotfm_file:
            dotfm_csv = csv.writer(dotfm_file)
            dotfm_csv.writerows(INSTALLED)
            dotfm_file.close()
    else:
        log_info('could not find dotfile matching alias "{}"'.format(alias))

# main/edit
def dotfm_edit(dotfile_alias):
    """ Open dotfile with alias matching "dotfm_alias" in EDITOR
        @param dotfile_alias = an alias of the dotfile to open
    """
    log_info('editing {}...'.format(dotfile_alias))

    target = ''
    for dfl in INSTALLED:
        if dotfile_alias in dfl:
            target = '{}'.format(dfl[0])
            os.system('{} {}'.format(EDITOR, target))
            log_info('success - you might need to re-open the terminal to '\
                    'see changes take effect')
            break
        for name in dfl[0]:
            if os.path.basename(dotfile_alias) == name:
                found = True
                target = '{}'.format(os.path.abspath(dfl[1]))
                log_info('found {}'.format(target))
                os.system('{} {}'.format(EDITOR, target))
                log_info('success - you might need to re-open the terminal '\
                        'to see changes take effect')
                break

    if target == '':
        error_exit('could not find alias {} in installed.csv'.format(
            os.path.basename(dotfile_alias)))

# main/list
def dotfm_list(dotfile_aliases):
    """ List specified dotfile aliases and install location (displays all if
        none are specified).
        @param dotfile_aliases = an array of dotfile aliases to list, if
        len == 0 then all will be printed.
    """
    log_info('listing dotfm files: {}'.format(
        'all' if len(dotfile_aliases) == 0 else dotfile_aliases))

    if len(dotfile_aliases) == 0:
        os.system('printf "LOCATION,ALIASES...\n$(cat {})" | ' \
                'column -t -s,'.format(INSTALLED_FILE))
    else:
        dotfiles = ''
        for alias in dotfile_aliases:
            for dfl in INSTALLED:
                if alias in dfl:
                    dotfiles += dfl[0]
                    for i, a in enumerate(dfl[1:]):
                        dotfiles += ',{}'.format(a)
                        if i == len(dfl[1:]) - 1:
                            dotfiles += '\n'
        os.system('printf "LOCATIOn,ALIASES...\n{}" | ' \
                'column -t -s,'.format(dotfiles))

#------
# MAIN
#------
if __name__ == '__main__':
    ARGS = parseargs()
    if ARGS.debug == True:
        debug('printing debug logs')
    if ARGS.quiet == True:
        debug('muting info logs')

    init()
    if ARGS.cmd == 'install':
        for d in ARGS.dotfile:
            dotfm_install(os.path.abspath(d))
    elif ARGS.cmd == 'update':
        dotfm_update(ARGS.dotfile[0], ARGS.dotfile[1])
    elif ARGS.cmd == 'remove':
        for d in ARGS.dotfile:
            dotfm_remove(d)
    elif ARGS.cmd == 'edit':
        for d in ARGS.dotfile:
            dotfm_edit(d)
    elif ARGS.cmd == 'list':
        dotfm_list(ARGS.dotfile)

