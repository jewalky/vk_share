# vk_share
A script that lets you automatically synchronize and share audio playlists from vk.com

## Prerequisites
- Python 3.x (relatively recent is advised)
- Tornado in pythonpath

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

Once these settings are configured, every new added track will be downloaded
and stored in ./static/music directory.
Removed tracks are removed from the playlist, but left on HDD.