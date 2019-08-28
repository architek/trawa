=====
trawa
=====


Watch directories to trigger transmission downloads.

Trawa is a small python script to monitor watch directories, each having a specific configuration.
Any file dropped in these directories is sent to a transmission instance using rpcxml.

You can define for each directory to watch, a set of rpc parameters to send to transmission. The following example
will watch 2 directories and set a specific download_dir for each of the two categories::

    dirs:
        - watch_path:   /home/lke/torrents/linux/images
          descrip:      Linux images
          rpc_params:
            download_dir:   /downloads/linux_images
        
        - watch_path:   /home/lke/torrents/audio/samples
          descrip:      Audio samples
          rpc_params:
            download_dir:   /mnt/ext4/audio/samples


Only newly created torrent files are watched. Torrent files are never removed.

*Note:* For the complete list of rpc parameters, see `Transmission RPC proto spec <https://github.com/transmission/transmission/wiki/RPC-Protocol-Specification>`.

INSTALL / USE
-------------

Python3 only, untested with Python2.

You can directly install from github provided you have python3 pip::

    pip3 install git+https://github.com/architek/trawa

To run::

    trawa