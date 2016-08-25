# vk_share
A script that lets you automatically synchronize and share audio playlists from vk.com

## Configuration file
For this script to function correctly, a configuration file is required.
The default name for this file is vsh.cfg, but you can specify different
filename with -cfg filename.

Example contents are as follows:

```
[vk]
login=test@gmail.com
password=blablabla
source=163837192
```

Where login and passwords are your vk.com login and password, and source
is an user (positive) or group (negative) ID to fetch the playlist from.
