# App Install
Install your downloaded Applications right from [Alfred][]

## How it works
DMG Install searches through your ~/Downloads-folder for the newest `.dmg`- and 
`.zip`-File, mounts it, copies all Apps to /Application and unmounts the Volume.

## How to use
#### As Keyword:
* Simply type `install` into Alfred
* Select the Download and install with `Enter` (Selecting &#x2318;-&#x21A9; will 
  delete the Download afterwards)

![](http://f.lc3dyr.de/dmginstall-1.png)


#### As File-Action:
* Select an `.dmg`-File in Alfred
* type `install`

![](http://f.lc3dyr.de/dmginstall-2.png)

## How to install
Clone this repository to your Mac or simply download and open the [workflow][].

## Changelog
* v0.3:
    - Fix Symlinkproblem in Zipfiles
    - Add ability to delete Download after install (by pressing 
      &#x2318;-&#x21A9;)
* v0.2:
    - Add ability to install from `*.zip`-Files
    - Show all possible matches instead of only one<br/>(This is still sorted by most-recent)
* v0.1:
    - Initial Release

## Credits
This workflow is inspired by the Alfred v1 Extension from [Christian 
Schlensker](https://github.com/wordofchristian/Install-DMG), translated from 
Ruby to Python and Updated as a Alfred v2 Workflow. It uses the [alp][]-Python 
Environment for Alfred.




[Alfred]: http://www.alfredapp.com/ "Alfred v2 - Productivity Application for OS X"
[alp]: https://github.com/phyllisstein/alp
[workflow]: http://l.lc3dyr.de/dmginstallflow
