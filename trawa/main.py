# -*- coding: utf-8 -*-
"""Torrent Watcher."""
import sys
import yaml
import pathlib
import logging
import inotify_simple
import transmissionrpc


class TorrentWatcher:
    def __init__(self, conf_name, log_level):
        logging.basicConfig(stream=sys.stdout, level=log_level, format='%(message)s')
        self.log = logging.getLogger(__name__)
        self.read_conf(conf_name)

    def start(self):
        self.log.info("Starting")
        self.inotify = inotify_simple.INotify()
        self.set_watches(self.conf['dirs'])
        try:
            self.loop()
        except KeyboardInterrupt:
            self.log.info("\nExited")

    def loop(self):
        self.log.info("Waiting")
        while True:
            for event in self.inotify.read():
                for flag in inotify_simple.flags.from_mask(event.mask):
                    self.log.debug("{}s".format(flag))
                path = pathlib.Path(self.wds[event.wd])
                filename = path / event.name
                conf_dir = [e for e in self.conf['dirs']
                            if e['watch_path'] == str(path)][0]
                server = self.conf['rpc_server']
                self.rpc_add_torrent(server['ip'], server['port'], server['username'], server['password'],
                                     str(filename), **conf_dir['rpc_params'])

    def rpc_add_torrent(self, ip, port, user, password, torrent_uri, **kwargs):
        self.log.info("Sending {} to {} with params {}".format(
            torrent_uri, ip, kwargs))
        try:
            tc = transmissionrpc.Client(ip, port, user, password)
            tc.add_torrent(torrent_uri, **kwargs)
        except (transmissionrpc.error.TransmissionError, transmissionrpc.error.HTTPHandlerError) as exc:
            self.log.error("Couldn't add torrent {} to {}@{}:{}: {}".format(torrent_uri, user, ip, port, exc))

    def read_conf(self, name):
        self.log.debug("Reading conf [{}]".format(name))
        try:
            with open(name, 'r') as stream:
                    self.conf = yaml.load(stream, Loader=yaml.BaseLoader)
        except FileNotFoundError:
            self.log.critical("File {} not found!".format(name))
            exit(1)
        except yaml.YAMLError as exc:
            self.log.critical("YAML error {}".format(exc))
            exit(1)

    def set_watches(self, dirs, flags=inotify_simple.flags.CLOSE_WRITE):
        self.wds = {}
        for dir in dirs:
            descrip = dir['descrip']
            watch_path = dir['watch_path']
            rpc_params = dir['rpc_params']
            try:
                wd = self.inotify.add_watch(watch_path, flags)
                self.log.info("{} : {} -> {}".format(descrip, watch_path, rpc_params))
                self.wds[wd] = watch_path
            except FileNotFoundError:
                self.log.warning("Path \"{}\" not found! Ignoring".format(watch_path))
        if not self.wds:
            self.log.warning("Nothing to do!")
            exit(0)
