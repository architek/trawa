# -*- coding: utf-8 -*-
"""Torrent Watcher."""
import sys
import logging
import pathlib
import yaml
import datetime
import inotify_simple
import transmissionrpc


class TorrentWatcher:
    def __init__(self, conf_name, log_level):
        logging.basicConfig(
            stream=sys.stdout,
            level=log_level,
            format='%(message)s')
        self.log = logging.getLogger(__name__)
        self.inotify = None
        self.wds = {}
        self.conf = {}
        self.read_conf(conf_name)

    def start(self):
        self.log.debug("Starting TorrentWatcher")
        self.inotify = inotify_simple.INotify()
        self.set_watches(self.conf['dirs'])
        try:
            self.loop()
        except KeyboardInterrupt:
            self.log.info("\nExited")

    def loop(self):
        self.log.debug("Waiting")
        while True:
            for event in self.inotify.read():
                for flag in inotify_simple.flags.from_mask(event.mask):
                    self.log.debug("%s", flag)
                path = pathlib.Path(self.wds[event.wd])
                filename = path / event.name
                path = str(path)
                conf_dir = [e for e in self.conf['dirs']
                            if e['watch_path'].rstrip("/" "\\") == path][0]
                if not filename.match(conf_dir['file_mask']):
                    self.log.debug("Ignoring %s", str(filename))
                    continue
                server = self.conf['rpc_server']
                self.rpc_add_torrent(server['ip'], server['port'],
                                     server['username'], server['password'],
                                     str(filename), **conf_dir['rpc_params'])

    def rpc_add_torrent(self, ip, port, user, password, torrent_uri, **kwargs):
        self.log.info(
            "%s : Sending %s to %s with params %s",
            datetime.datetime.now(),
            torrent_uri,
            ip,
            kwargs)
        try:
            tc = transmissionrpc.Client(ip, port, user, password)
            tc.add_torrent(torrent_uri, **kwargs)
        except (transmissionrpc.error.TransmissionError, transmissionrpc.error.HTTPHandlerError) as exc:
            self.log.error(
                "Couldn't add torrent %s to %s@%s:%s: %s",
                torrent_uri,
                user,
                ip,
                port,
                exc)

    def read_conf(self, name):
        self.log.debug("Reading conf [%s]", name)
        try:
            with open(name, 'r') as stream:
                self.conf = yaml.load(stream, Loader=yaml.BaseLoader)
        except FileNotFoundError:
            self.log.critical("File %s not found!", name)
            exit(1)
        except yaml.YAMLError as exc:
            self.log.critical("YAML error %s", exc)
            exit(1)
        for d in self.conf['dirs']:
            d.setdefault('file_mask', '*')

    def set_watches(self, dirs, flags=inotify_simple.flags.CLOSE_WRITE |
                    inotify_simple.flags.MOVED_TO):
        self.wds = {}
        for mdir in dirs:
            descrip = mdir['descrip']
            watch_path = mdir['watch_path']
            file_mask = mdir['file_mask']
            rpc_params = mdir['rpc_params']
            try:
                wd = self.inotify.add_watch(watch_path, flags)
                self.log.info(
                    "%s : %s/%s -> %s",
                    descrip,
                    watch_path,
                    file_mask,
                    rpc_params)
                self.wds[wd] = watch_path
            except FileNotFoundError:
                self.log.warning(
                    "Path \"%s\" not found! Ignoring", watch_path)
        if not self.wds:
            self.log.warning("Nothing to do!")
            exit(0)
