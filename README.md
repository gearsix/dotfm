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

```
	usage: dotfm [-h] [-d] [-v] [-q] COMMAND DOTFILE...

	a simple tool to help you manage your dot files.

	positional arguments:
	  COMMAND        the dotfm COMMAND to execute: ['install', 'remove', 'edit', 'list']
	  DOTFILE        the target dotfile to execute COMMAND on

	optional arguments:
	  -h, --help     show this help message and exit
	  -d, --debug    display debug logs
	  -v, --version  show program's version number and exit
	  -q, --quiet    tell dotfm to shutup
```

\* Multiple DOTFILE args can be passed

### commands

<details>
	<summary><b>dotfm install DOTFILE...</b> = create a symlink to DOTFILE... at it's install location</summary>

	Multiple DOTFILE args can be passed.

	DOTFILE... should be the filepath of the dotfile to install

	If the basename of DOTFILE is a recognised alias in KNOWN_DOTFILES, then dotfm will install it automatically.

	If the basename of DOTFILE is not a recognised alias in KNOWN_DOTFILES, then dotfm will prompt you for an install location and aliases to recognise the dotfile with

	If a file already exists at the install location of the dotfile, you will be prompted askin whether you want to:
		- [o]verwrite = move the existing file to (existing file location).bak and install the dotfile
		- [c]ompare = print out a diff -y of the two files and return to this prompt
		- [a]bort = abort the dotfm runtime
	
	Feel free to fork this repo and modify KNOWN DOTFILES
</details>

<details>
	<summary><b>dotfm remove DOTFILE...</b> = remove the file at the install location of the installed dotfile with a matching alias</summary>

	This function will rm the file at the install location.

	Multiple DOTFILE args can be passed.
	
	DOTFILE... should be an alias for the dotfile to remove.
	
	DOTFILE... will only be removed if they exist in DOTFM_CSV_FILE (tracks dotfiles installed by dotfm)
	
	Since this is a destructive function (uses rm), you will permenantly lose the file. This should be fine in most cases, however it's always best to check.
</details>

<details>
	<summary><b>dotfm edit DOTFILE...</b> = edit a dotfile</summary>

	Multiple DOTFILE args can be passed.
	
	DOTFILE... should be an alias for the dotfile to remove.
	
	This will simply open the file at the corresponding dotfiles install location
	
	The editor the dotfile is opened in will be whatever the environment variable $EDITOR is set to. If it's not set nano will be used.
</details>

<details>
	<summary><b>dotfm list [DOTFILE...]</b> = list installed dotfiles</summary>

	Multiple or no dotfiles can be specified

	If no DOTFILE... args are passed the all installed dotfiles are listed

	if DOTFILE... args are present, then they should correspond to an alias of an installed dotfile
</details>

### examples

**Note:** For the following examples, _$DOTFILES_ will be used to address the src folder dotfiles are stored in.

- **install a dotfile** - `dotfm install $DOTFILES/bashrc` = will **ln -s** _$DOTFILES/bashrc_ -> _~/.bashrc_
- **remove a dotfile** - `dotfm remove bashrc` = will **rm** _~/.bashrc_
- **edit a dotfile** - `dotfm edit bashrc` = will open _.bashrc_ in _$EDITOR_ or _nano_
- **list all dotfiles** - `dotfm list` = displays a printout of all the dotfles
- **list a specific dotfile** - `dotfm list bashrc` = displays a printout of the bashrc dotfile
	- Alternatively, you could print the files content outside of dotfm like this: `printf "Location,Aliases...\n$(cat ~/.local/share/dotfm/installed.csv)" | column -t -s,`

---

## installing dotfm

Make sure you're in the dotfm directory

- If you **do** plan on modifying dotfm after install: `sudo make link`. This will install the script as a symlink.
- If you **don't** plan on modifying dotfm after install: `sudo make install`. This will copy the script.

### install location

By default the install location of the python script = _/usr/local/bin/dotfm_.

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

- [x] Change `DOTFILE\_LOCATIONS` to use an external config (C)
- [ ] Allow a remote git repo to be used for calling dotfile source (W)
- [ ] Add a double-check to _dotfm remove_(W)
- [x] Follow symlinks to list source file locations too (?)
- [ ] Move the details section above into man pages, probably use txt2man (with pdf conversion) (S)

Commands:
- [x] <s>List dotfile locations (W)</s>
- [ ] Create a dotfile (W)
- [ ] Update dotfile source location (W)
- [ ] Move a dotfile and create a link to it's new location in the original location (S)

---

## authors

- GeaRSiX <gearsix@tuta.io>

