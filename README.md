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

---

## usage
There's an array near the top of the file (`DOTFILE_LOCATIONS`) that informs _dotfm_ of alias names for calling a dotfile and where to install that dotfile. Feel free to modify this array to your liking.

### cheatsheet
**Note:** For the following examples, _$DOTFILES_ will be used to address the src folder dotfiles are stored in.

- **Install** a dotfile: `dotfm install $DOTFILES/bashrc` (will **ln -s** _$DOTFILES/bashrc_ -> _~/.bashrc_)
- **Uninstall** a dotfile: `dotfm remove bashrc` (will **rm** _~/.bashrc_)
- **Edit** a dotfile: `dotfm edit bashrc` (will open _.bashrc_ in _$EDITOR_ or _nano_)
- **Install all** your dotfiles: `dotfm install-all $DOTFILES` (runs **dotfm install** on all files in _$DOTFILES_)
- **List** your dotfm dotfile aliases and their location: `dotfm list $DOTFILE`

### details
#### DOTFILE\_LOCATIONS

_DOTFILE\_LOCATIONS_ is a multi-dimensional array near the top of _src/dotfm.py_ (under _GLOBALS_). Think of this array as your _config file_ for now.

**It's important this array has the correct values for dotfm to work.**

Each element of it is an array with _two values_: `[['dotfile_alias', ...], 'dotfile_install_path']`

- **[dotfile\_alias, ...]** = An array of names you'd like to use to call this dotfile (at least one value should match the dotfile's name in your $DOTFILE repo)
- **dotfile\_install\_path** = Filepath of where the dotfile should install to (include filename, e.g. `'/home/{}/.bashrc'.format(USER)`)
  
#### dotfm install DOTFILE\_PATH
_DOTFILE_ should be **path** of the **dotfile to install**.

**If the base name of _DOTFILE_ is recognised**, _dotfm_ will make sure the directory to install the dotfile to exists and then create a symbolic link at that location to _DOTFILE_.
If a file already exists at the install location, you'll get a prompt asking whether you want to:

- _\[o\]verwrite_ = move the existing file to _(existing file location).bak_ and force create the symbolic link
- _\[c\]ompare_ = print out a _diff_ of the two files and return to these options
- _\[a\]bort_ = abort the installation

**If the base name of _DOTFILE_ isn't found** in the alias lists in _DOTFILE\_LOCATIONS_, then the install will abort. You'll have to manually add your dotfile to _DOTFILE_LOCATIONS_ or modify it's aliases to include yours. Make sure to re-install afterwards.

#### dotfm remove DOTFILE\_NAME
_DOTFILE_  should be the **name** of the **dotfile to remove**.

**WARNING!** This will _rm_ the file named _DOTFILE_ from it's install location (found in _DOTFILE\_LOCATIONS_).

_This is a destructive function and you will **permenantly lose the file**._ This should be fine in most cases if you installed the file with _dotfm_ as it will only rm the symlink to your source dotfile, It's always best to make sure you check though. 

#### dotfm edit DOTFILE\_NAME
_DOTFILE_ should be the **name** of the **dotfile to edit**.

This will open the _DOTFILE_ in the editor set in your environment variables as _EDITOR_. If _EDITOR_ is not set, then it will open it in _nano_.

The file opened is located at the matching install location found in _DOTFILE\_LOCATIONS_.

#### dotfm install-all DOTFILE\_DIR
_DOTFILE_DIR_ should be a **directory path** containing the source files of all the **dotfiles to install**

This will recursively run _dotfm install DOTFILE_ on each file found in the specified directory.

#### _dotfm list DOTFILE\_NAME_
Useful if you've forgotten the alias names of your dotfiles or if you've forgotten where they're kept.

_DOTFILE\_NAME_ can be **all** to **list all known** dotfiles, otherwise it should be the **name** of the **dotfile to list**.

### help

	usage: dotfm [-h] [-d] [-v] COMMAND DOTFILE
	
	a simple tool to help you manage your dot files, see "man dotfm" for more
	
	positional arguments:
	  COMMAND        the dotfm COMMAND to execute: ['install', 'remove', 'edit',
	                 'install-all', 'list']
	  DOTFILE        name of the dotfile dotfm will execute COMMAND on, for
	                 "install" this must be a path to the dotfile to install
	
	optional arguments:
	  -h, --help     show this help message and exit
	  -d, --debug    display debug logs
	  -v, --version  show program's version number and exit

---

## installing dotfm
- If you **do** plan on modifying _DOTFILE\_LOCATIONS_ after install _dotfm_ (recommended): `sudo make link`. This will install the script as a symlink.
- If you **don't** plan on modifying _DOTFILE\_LOCATIONS_ after installing _dotfm_: `sudo make install`. This will copy the script.

### install location
By default this will install the python script to _/usr/bin/local/dotfm_.

To change this, just modify _Makefile_ and change the value of _DESTDIR_ to your preferred install location.

---

## uninstall dotfm
Just run `sudo make uninstall` while in the same directory as the _Makefile_.

---

## TODO
Development on this project isn't a massive priority for me. Currently things are getting added as I need them.

**Legend**

_[x] = done; [~] = in-progress; [-] = won't do; [ ] = not started;_

_(W) = Will do; (S) = Should do; (C) = Could do;_

- [ ] Change `DOTFILE\_LOCATIONS` to use an external config (C)
- [ ] Allow a remote git repo to be used for calling dotfile source (W)
- [ ] Add a double-check to _dotfm remove_(W)
- [ ] Follow symlinks to list source file locations too (?)
- [ ] Move the details section above into man pages (with pdf conversion) (S)

Commands:
- [x] <s>List dotfile locations (W)</s>
- [ ] Create a dotfile (W)
- [ ] Update dotfile source location (W)
- [ ] Move a dotfile and create a link to it's new location in the original location (S)

---

## authors
- GeaRSiX <gearsix@tuta.io>

