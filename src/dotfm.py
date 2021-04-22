#!/usr/bin/env python

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

def writeinstalled():
    with open(INSTALLED_FILE, "w") as dotfm_csv_file:
        dotfm_csv = csv.writer(dotfm_csv_file, lineterminator='\n')
        for dfl in INSTALLED:
            dotfm_csv.writerow(dfl)
        dotfm_csv_file.close()

def isdotfile(dotfile_list, query):
    found = -1
    for d, dfl in enumerate(dotfile_list):
        if query == dfl[0] or query == os.path.basename(dfl[0]):
            found = 0
        for alias in dfl[1:]:
            if query == alias:
                found = d
                break
        if found != -1:
            debug('dotfile {} matches known dotfile alias for {}', alias, dfl[0])
            break

def clearduplicates(dotfile_list, id_index=0, keep_latest=True):
    unique = []
    for d in data:
        for i, u in enumerate(unique):
            if d[id_index] == u[id_index]:
                unique[i] = d # assume later entry = more recent
    return unique

# main/init
def init():
    debug('init: loading dotfile locations')
    if not os.path.exists(INSTALLED_FILE):
        debug(INSTALLED_FILE, 'not found')
        init_createcsv()
    INSTALLED = init_loadcsv(INSTALLED_FILE)
    INSTALLED = clearduplicates(INSTALLED)

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

# main/install
def install(dotfile):
    debug('installing', dotfile)
    known = isdotfile(KNOWN, dotfile)
    location = install_getlocation(known)
    aliases = install_getaliases(known)
    if not os.path.exists(os.path.dirname(location)):
        os.system('mkdir -vp {}'.format(location))
    if os.path.lexists(location):
        install_oca(dotfile, location)
    os.system('ln -vs {} {}'.format(dotfile, location))
    info('appending to installed...')
    dfl = aliases.insert(0, location)
    INSTALLED.append(dfl)
    clearduplicates(INSTALLED)
    info('success - you might need to re-open the terminal to see changes take effect')

def install_getlocation(known_index):
    default = ''
    if known_index != -1:
        default = KNOWN[known_index][0]
    if len(default) > 0 and ARGS.skip == True:
        return default
    location = ''
    while location == '':
        location = input('install location ({})? '.format(
            ('default:', default) if len(default) > 0 else ''))
        if len(location) == 0 and len(default) > 0:
            return default
        elif location.find('~') != -1:
            return location.replace('~', HOME)
        else:
            location = ''

def install_getaliases(known_index):
    default = ''
    if known_index != -1:
        default = KNOWN[known][1:]
    if len(default) > 0 and ARGS.skip == True:
        return default
    aliases = ''
    while aliases == '':
        aliases = input('aliases to call dotfile by (put a space between each alias) ({})? '.format(
            ('default:', default) if len(default) > 0 else ''))
        if len(aliases) > 0:
            return aliases.split(' ')
        elif len(default) > 0:
            return default

def install_oca(dotfile, location):
    oca = ''
    while oca == '':
        oca = input(location 'already exists, [o]verwrite/[c]ompare/[a]bort? ')
        if len(oca) > 0:
            if oca[0] == 'o': # overwrite
                debug('removing', location)
                os.remove(location)
            elif oca[0] == 'c': # compare
                debug('comparing {} to {}'.format(dotfile, location))
                os.system('diff -bys {} {}'.format(dotfile, location))
                oca = ''
            elif oca[0] == 'a': # abort
                debug('aborting install')
                sys.exit()
            else:
                oca = ''
    return oca

# main/update
def update(alias, location):
    debug('updating {} -> {}'.format(alias, location))
    known = isdotfile(INSTALLED, alias)
    if known != -1:
        os.system('ln -isv', location, INSTALLED[known][0])
    else:
        warn(dotfile, 'is unrecognised, installing')
        install(location)

# main/remove
def remove(alias):
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
def edit(dotfile_alias):
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
def list(dotfile_aliases):
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
            install(os.path.abspath(d))
    elif ARGS.cmd == 'update':
        update(ARGS.dotfile[0], ARGS.dotfile[1])
    elif ARGS.cmd == 'remove':
        for d in ARGS.dotfile:
            remove(d)
    elif ARGS.cmd == 'edit':
        for d in ARGS.dotfile:
            edit(d)
    elif ARGS.cmd == 'list':
        list(ARGS.dotfile)
    writeinstalled()
