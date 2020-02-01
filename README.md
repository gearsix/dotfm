# dotfm - dot file manager
a **really** simple dot file manager.

## contents
1. [overview](#overview)
2. [usage](#usage)
	1. [cheatsheet](#cheatsheet)
	2. [details](#details)
3. [install](#install)
2. [uninstall](#uninstall)
4. [authors](#authors)

## overview
This is a really simple python script I wrote to manage dotfiles. I had a brief look at a few and decided I'd just make my own.

It doesn't do anything complicated, but there's an array near the top of the file (_DOTFILE_LOCATIONS_) that informs _dotfm_ where to install recognised files to. The downside to this tool is that dot files I don't use will need to be manually added to this array by yourself. I'll be adding to it overtime, but feel free to modify it yourself.

---

## usage

### cheatsheet
Keep all your dotfiles in one directory (replace $DOTFILES with this directory name):
- Install a dot file: `dotfm install $DOTFILES/.bashrc` (will **ln -s** _$DOTFILES/.bashrc_ -> _~/.bashrc_)
- Uninstall a dot file: `dotfm remove .bashrc` (will **rm**_~/.bashrc_)
- Edit a dot file: `dotfm edit .bashrc` (will open _.bashrc_ in _$EDITOR_ or _nano_)
- Install all your dotfiles: `dotfm install-all $DOTFILES` (runs **dotfm install** on all files in _$DOTFILES_)

### details
#### _dotfm install DOTFILE_
_DOTFILE_ should be a **path** to the **dotfile to install**.

If the file name of _DOTFILE_ is recognised, it will make sure the directory to install the dotfile to exists and then create a symbolic link at that location to _DOTFILE_.

If a file already exists at the install location, you'll get a prompt asking whether you want to:
- _\[o\]verwrite_ = move the existing file to __(existing file location).bak_ and continue with creating the symbolic link
- _\[c\]ompare_ = print out a _diff_ of the two files
- _\[a\]bort_ = abort the installation

If _DOTFILE_ isn't found in _DOTFILE\_LOCATIONS_, then you'll have to manually add it. This is simple though, just go modify _src/dotfm.py_ and add an element to the array. Make sure to re-install too.

#### _dotfm remove DOTFILE_
_DOTFILE_  should be the **name** of the **dotfile to remove**.

**WARNING!** This will _rm_ the file named _DOTFILE_ from it's install location (found in _DOTFILE\_LOCATIONS_).

#### _dotfm edit DOTFILE_
_DOTFILE_ should be the **name** of the **dotfile to edit**.

This will open the _DOTFILE_ in the editor named in your environment variables as _EDITOR_. If _EDITOR_ is not available as an environment varialbe, then it will open it in _nano_.

The file opened is located at the matching install location found in _DOTFILE\_LOCATIONS_.

#### _dotfm install-all DOTFILE_
_DOTFILE_ should be a **directory path** containing all the **dotfiles to install**

This will recursively run _dotfm install DOTFILE_ on each file found in the specified directory.

### help

```
usage: dotfm [-h] [-d] [-v] COMMAND DOTFILE

a simple tool to help you manage your dot files, see "man dotfm" for more

positional arguments:
  COMMAND        the dotfm COMMAND to execute: ['install', 'remove', 'edit',
                 'install-all']
  DOTFILE        name of the dotfile dotfm will execute COMMAND on, for
                 "install" this must be a path to the dotfile to install

optional arguments:
  -h, --help     show this help message and exit
  -d, --debug    display debug logs
  -v, --version  show program's version number and exit
```

---

## installing dotfm
Just run `sudo make install`

### install location
By default this will install the python script to _/usr/bin/dotfm_.
To change this, just modify _Makefile_ and change the value of _DESTDIR_ to your preferred install location.

---

## uninstall dotfm
Just run `sudo make uninstall`

---

## authors
- GeaRSiX <gearsix@tuta.io>

---
