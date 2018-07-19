Todo:
[X] Add convenience scripts to block and unblock from console.
[X] An automated switch could replace the HostsFile Object and make this
    script work for linux as well.
[X] Read in the hosts from an external config file.
[ ] Make function to install cronjob.
[ ] Add a comment to the hosts file, that these parts were added using
    this script
[ ] The lines-Abstraction made sense along the way but it broke. Could it
    be improved?
[ ] Separate CLI from Program
[ ] Introduce a TEST Object
[ ] Implement Selective Unblocking. Sometimes
    I just really needed AMAZON.com
[ ] Introduce a Windows / Posix object, for post processing, e.g. flush dns
[ ] Flush DNS after update:
    > ipconfig /flushdns
[ ] I started procedural, moved to yegor style, and now it's quite
    procedural again. Could this be even more yegor style?
