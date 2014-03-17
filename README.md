# Alfred App Install
Install your downloaded Mac OS X Applications right from [Alfred 2][].

## Description
**Alfred App Install** searches through your `~/Downloads` folder and lists installable Objects like `.app` or `.dmg` in Alfred, sorted by *most-recent downloaded*. Upon selection, it will automatically install it to your `/Applications/` folder.

## How to use
The script will run through the supplied paths and list all supported filetypes, sorted by most-recently-downloaded, so that new applications will be on top. It will then install (copy) all `.app`s to your `/Applications/` folder, **overwriting** any existing app (think of 'upgrade'). Depending on your pressed modifier, it will then delete the source.


The search path and installation path setting can be configured inside the Workflow (see: [Settings](#Settings)).

#### As Keyword:
* Simply type `install` into Alfred
* Select the Download and install with `Enter` (using `CMD-Enter` will 
  delete the Download after successful installation)
  
![](http://f.lc3dyr.de/dmginstall-v1.0-01.png)
  
* You can filter the list of results by entering a substring after the keyword

![](http://f.lc3dyr.de/dmginstall-v1.0-02.png)


#### As File-Action:
* Select a supported File in Alfred
* type `install`

![](http://f.lc3dyr.de/dmginstall-v1.0-03.png)

## Supported Filetypes
App Install will find and install the following files:

* Disk Images `.dmg`:
    - Will automatically mount and unmount the Image, installing all `.app` and `.pkg`s inside.
* Archives `.zip`:
    - Will extract the zip to a temporary location and install all `.app` and `.pkg`s inside. If the zip **does not** contain any installable files, the zip will **not** be extracted.
* OS X Installation Packages `.pkg`:
	- Will open the Graphical Installer
* Individual Applications `.app`:
    - Will copy them to `/Applications/`
* Alfred Workflows `.alfredworkflow`:
    - Will open the Workflow in Alfred

## How to install
Download the [workflow][]. If you want to develop or build the workflow yourself, clone this repository.

## Settings
**Alfred App Install** currently lags a direct configuration through Alfred, but some of the settings can be easily changed inside the workflow.

#### Search Path
To edit the search path, i.e. the locations where this script looks for installable files, you need to modify the **Script Filter**. In the Edit-Dialogue you should see the following code:

```
from alfred import list_installables

PATHS = [
	'~/Downloads',
]

list_installables(query="{query}", paths=PATHS)
```

To add for example `~/Desktop` as a path, you simply need to add him into the list like this:

```
from alfred import list_installables

PATHS = [
	'~/Downloads',
	'~/Desktop',
]

list_installables(query="{query}", paths=PATHS)
```

Please don't forget the comma at the end of the line and the single-quotes around the path.

#### Installation Prefix
To change the installation path (prefix) you need to modify **both** **Run Script** Actions. (One of the Actions is for normal (`Enter`), the other one for (`CMD+Enter`))

```
from alfred import install

install(query="{query}", prefix='/Applications/', overrite=True, remove=False)
```

To set a new install location, simply change the value of `prefix='/Applications/'` to something else, for example `prefix='/Users/NAME/Applications/'` to install to your own User Directory (substitute `NAME` for your username).

Please be aware, that the Prefix is only used for `.app`s, `.pkg`s will install to the location specified in the opening dialogue.



## Changelog
### Current Version
* v1.0:
	- Complete Rewrite
		- Now uses an individual library for the installation (`install.py`)
		- New Icon by [metalcabana][meta]
	- Bugfix: Symbolic Links inside `.app`s should now be preserved during 
installation.
	- Feature: Filter results by entering a substring after the keyword
 
### Earlier Versions
* v0.4:
    - Ability to install .pkg-Files
    - Ability to find and install Alfred.Workflows
    - Some bug fixes
* v0.3:
    - Fix Symlinkproblem in Zipfiles
    - Add ability to delete Download after install (by pressing 
      &#x2318;-&#x21A9;)
* v0.2:
    - Add ability to install from `*.zip`-Files
    - Show all possible matches instead of only one<br/>(This is still sorted by most-recent)
* v0.1:
    - Initial Release
    
## Support and Contribution
If you find a Bug or if you have a feature request (i.e. additional filetypes) please open an issue on [Github](https://github.com/laerador/dmginstall).

## License and Credits
This workflow is inspired by the Alfred v1 Extension from [Christian 
Schlensker](https://github.com/wordofchristian/Install-DMG), but written completely new. It uses the [alp][]-Python 
Environment for Alfred and the [send2trash](https://pypi.python.org/pypi/Send2Trash) Module. The Icon was designed by [metalcabana on deviantart][meta].

**Alfred App Install**, including `install.py` and `alfred.py` are licensed under the Simplified BSD License (see `LICENSE`).



[meta]: http://metalcabana.deviantart.com/art/Installer-Flurry-Icon-273338470 "Installer Flurry Icons"
[Alfred 2]: http://www.alfredapp.com/ "Alfred v2 - Productivity Application for OS X"
[alp]: https://github.com/phyllisstein/alp
[workflow]: http://l.lc3dyr.de/dmginstallflow
