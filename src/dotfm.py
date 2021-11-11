#!/usr/bin/env python3

#=========================
# dotfm - dotfile manager
#=========================
# authors: gearsix
# created: 2020-01-15
# updated: 2021-09-06

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
ARGS = []
EDITOR = os.getenv('EDITOR') or 'nano'
VERSION = 'v2.2.1'
INSTALLED = []
INSTALLED_FILE = '{}/.local/share/dotfm/installed.csv'.format(HOME)
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
    ['{}/.tmux.conf'.format(HOME), '.tmux.conf', 'tmux.conf'],
    ['{}/.config/user-dirs.dirs'.format(HOME), 'user-dirs.dirs', 'xdg-user-dirs'],
    ['{}/.xinitrc'.format(HOME), '.xinitrc', 'xinitrc'],
    ['{}/.config/rc.conf'.format(HOME), 'rc.conf', 'ranger.conf', 'ranger.cfg'],
    ['{}/.config/neofetch/config'.format(HOME), 'config', 'neofetch.conf', 'neofetch.cfg'],
    ['{}/.config/sway/config'.format(HOME), 'config', 'sway.cfg', 'sway.conf'],
    ['{}/.config/awesome/rc.lua'.format(HOME), 'rc.lua', 'awesomerc'],
    ['{}/.config/i3/config'.format(HOME), 'config', 'i3.conf', 'i3.cfg', 'i3'],
    ['{}/.emacs'.format(HOME), '.emacs', 'emacs'],
    ['{}/.sfeed/sfeedrc'.format(HOME), '.sfeedrc', 'sfeedrc'],
    ['{}/.config/txtnish/config'.format(HOME), 'txtnish', 'txtnish_config'],
]

#-----------
# FUNCTIONS
#-----------
# utilities
def ask(message):
    return input('dotfm | {} '.format(message))

def log(message):
    print('dotfm | {}'.format(message))
    
def debug(message):
    if ARGS.debug == True:
        log(message)
        
def info(message):
    if ARGS.quiet == False:
        log(message)

def warn(message):
    ask('{}, press key to continue'.format(message))

# main
def parseargs():
    valid_commands = ['install', 'in', 'update', 'up', 'link', 'ln', 'remove', 'rm', 'edit', 'ed', 'list', 'ls']
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
        dotfm_csv_writer = csv.writer(dotfm_csv_file, lineterminator='\n')
        for dfl in INSTALLED:
            dotfm_csv_writer.writerow(dfl)
        dotfm_csv_file.close()

def isdotfile(dotfile_list, query):
    query = os.path.basename(query)
    debug('checking for {}'.format(query))
    found = -1
    for d, dfl in enumerate(dotfile_list):
        if query == os.path.basename(dfl[0]) or query in dfl:
            found = d
        if found != -1:
            debug('dotfile {} matches known dotfile alias for {}'.format(query, dfl[0]))
            break
    return found

def clearduplicates(dotfile_list, id_index=0):
    for i, d in enumerate(dotfile_list):
        if len(d) == 0:
            continue
        for j, dd in enumerate(dotfile_list):
            if len(dd) == 0:
                continue
            if j > i and dd[id_index] == d[id_index]:
                dotfile_list.remove(d)
                break

# main/init
def init():
    debug('init...')
    if not os.path.exists(INSTALLED_FILE):
        debug('{} not found'.format(INSTALLED_FILE))
        init_createcsv(INSTALLED_FILE)
    init_loadcsv(INSTALLED_FILE)
    clearduplicates(INSTALLED)
    debug('loaded dotfile list: {}'.format(INSTALLED))

def init_createcsv(default_location):
    location = default_location
    if ARGS.skip == False:
        info('default dotfm csv file location: "{}"'.format(default_location))
        location = ask('dotfm csv file location (enter for default)? ')
        if len(location) == 0:
            location = default_location
        if os.path.exists(location):
            debug('{} already exists'.format(location))
            on = ask('[o]verwrite or [u]se {}? '.format(location))
            if len(on) > 0:
                if on[0] == 'o': # create file at location & write KNOWN[0] to it
                    warn('overwriting {}, all existing data in this file will be lost'.format(location))
                    os.makedirs(os.path.dirname(location), exist_ok=True)
                    dotfm_csv = open(location, "w")
                    for i, dfl in enumerate(KNOWN[0]):
                        dotfm_csv.write(dfl if i == 0 else ',{}'.format(dfl))
                    dotfm_csv.write('\n')
                    dotfm_csv.close()
                elif on[0] == 'u':
                    debug('using pre-existing csv {}'.format(location))
                    sys.exit()

    # create default_location symlink
    if os.path.abspath(location) != os.path.abspath(default_location):
        debug('creating dotfm csv file symlink')
        os.makedirs(os.path.dirname(default_location), exist_ok=True)
        os.system('ln -isv', os.path.abspath(location), default_location)
    else:
        os.makedirs(os.path.dirname(location), exist_ok=True)
        f = open(location, "w")
        f.close()

def init_loadcsv(location):
    dotfm_csv = open(location, "r")
    dotfm_csv_reader = csv.reader(dotfm_csv)
    for dfl in dotfm_csv_reader:
        INSTALLED.append(dfl)
    dotfm_csv.close()

# main/install
def install(dotfile):
    info('installing {}...'.format(dotfile))
    known = isdotfile(KNOWN, dotfile)
    location = install_getlocation(known)
    aliases = install_getaliases(known)
    if not os.path.exists(os.path.dirname(location)):
        os.makedirs(os.path.dirname(location), exist_ok=True)
    if dotfile != location:
        if os.path.lexists(location):
            install_oca(dotfile, location)
        os.system('ln -vs {} {}'.format(dotfile, location))
    debug('appending to {} installed...'.format(location))
    aliases.insert(0, location)
    INSTALLED.append(aliases)
    clearduplicates(INSTALLED)
    info('success - you might need to re-open the terminal to see changes take effect')

def install_getlocation(known_index, msg='install location?'):
    default = ''
    if known_index != -1:
        default = KNOWN[known_index][0]
        info('default install location is "{}"'.format(default))
        msg = 'install location (enter for default):'.format(default)
    if len(default) > 0 and ARGS.skip == True:
        return default
    location = ''
    while location == '':
        location = ask(msg)
        if len(location) == 0 and len(default) > 0:
            return default
        elif location.find('~') != -1:
            return location.replace('~', HOME)
        else:
            location = ''

def install_getaliases(known_index):
    default = ''
    if known_index != -1:
        default = KNOWN[known_index][1:]
        info('default aliases are "{}"'.format(' '.join(default)))
    if len(default) > 0 and ARGS.skip == True:
        return default
    aliases = ''
    while aliases == '':
        aliases = ask('dotfile aliases (enter for default): '.format(
            ('defaults', default) if len(default) > 0 else ''))
        if len(aliases) > 0:
            return aliases.split(' ')
        elif len(default) > 0:
            return default

def install_oca(dotfile, location):
    oca = ''
    while oca == '':
        oca = ask('{} already exists, [o]verwrite/[c]ompare/[a]bort? '.format(location))
        if len(oca) > 0:
            if oca[0] == 'o': # overwrite
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
        os.system('ln -isv {} {}'.format(location, INSTALLED[known][0]))
    else:
        warn('{} is unrecognised, installing'.format(dotfile))
        install(location)

# main/link
def link(dotfile):
    dotfm_dir='~/.dotfiles/'

    if 'DFMDIR' in os.environ:
        dotfm_dir = os.environ('DFMDIR')
    else:
        log('default dotfm dir: "{}"'.format(dotfm_dir))
        d = ask('link to (enter for default)? '.format(dotfm_dir))
        if os.path.exists(d):
            dotfm_dir=d

    dotfm_dir = dotfm_dir.replace('~', HOME)
    os.makedirs(dotfm_dir, exist_ok=True)

    target=os.path.join(dotfm_dir, os.path.basename(dotfile))

    debug('linking {} -> {}'.format(dotfile, target))
    if not os.path.exists(dotfile):
        answer = ask('"{}" does not exist, create [y/n]?'.format(dotfile))
        debug(answer)
        if answer[0] == 'y':
            f = open(dotfile, 'w')
            f.close()
        else:
            return
    if os.path.exists(target):
        answer = install_oca(dotfile, target)
    os.link(dotfile, target)

# main/remove
def remove(dotfile):
    debug('removing {}'.format(dotfile))

    index = isdotfile(INSTALLED, dotfile)
    if index == -1:
        warn('could not find dotfile "{}"'.format(dotfile))
        return
    dotfile = os.path.abspath(INSTALLED[index][0])
    confirm = ''
    while confirm == '':
        confirm = ask('remove "{}", are you sure [y/n]?'.format(dotfile))
    try:
        os.remove(dotfile)
    except OSError as err:
        warn('cannot remove "{}"...\n{}'.format(dotfile, err))
    del INSTALLED[index]
    writeinstalled()

# main/edit
def edit(dotfile):
    debug('editing {}'.format(dotfile))
    index = isdotfile(INSTALLED, dotfile)
    if index == -1:
        if edit_promptinstall(dotfile) == 'y':
            index = isdotfile(INSTALLED, dotfile)
        else:
            return
    target = INSTALLED[index][0]
    os.system('{} {}'.format(EDITOR, target))
    info('You might need to re-open the terminal, or re-execute the relevant dotfile')

def edit_promptinstall(dotfile):
    yn = '-'
    while yn[0] != 'y' and yn[0] != 'n':
        yn = ask('could not find installed dotfile matching "{}", install [y/n]? '.format(dotfile))
        if len(yn) == 0:
            yn = '-'
        if yn[0] == 'y':
            install(install_getlocation(-1, msg='input source path:'))
    return yn[0]

# main/list
def list(dotfiles):
    debug('listing dotfiles: {}'.format(dotfiles))
    if len(dotfiles) == 0:
        os.system('printf "LOCATION,ALIASES...\n$(cat {})" | column -t -s ,'.format(INSTALLED_FILE))
    else:
        data = ''
        for d in dotfiles:
            for i in INSTALLED:
                if d in i:
                    data += '{},'.format(i[0])
                    for alias in i[1:]:
                        data += ',{}'.format(alias)
                    data += '\n'
        os.system('printf "LOCATION,ALIASES...\n{}" | column -t -s ,'.format(data))

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
    if ARGS.cmd == 'install' or ARGS.cmd == 'in':
        for d in ARGS.dotfile:
            install(os.path.abspath(d))
    elif ARGS.cmd == 'update' or ARGS.cmd == 'up':
        if len(ARGS.dotfile) < 2:
            debug('invalid number of arguments')
            info('usage: "dotfm update DOTFILE LOCATION"')
            sys.exit()
        update(ARGS.dotfile[0], ARGS.dotfile[1])
    elif ARGS.cmd == 'link' or ARGS.cmd == 'ln':
        for d in ARGS.dotfile:
            link(d)
    elif ARGS.cmd == 'remove' or ARGS.cmd == 'rm':
        for d in ARGS.dotfile:
            remove(d)
    elif ARGS.cmd == 'edit' or ARGS.cmd == 'ed':
        for d in ARGS.dotfile:
            edit(d)
    elif ARGS.cmd == 'list' or ARGS.cmd == 'ls':
        list(ARGS.dotfile)
    writeinstalled()
