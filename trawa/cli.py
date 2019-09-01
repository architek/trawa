#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Console script for trawa."""
import sys
import click
import logging
from trawa.main import TorrentWatcher
from trawa import __version__


@click.command()
@click.option('--config', default='trawa.yaml',
              help='config file (default trawa.yaml)')
@click.option('--quiet/--no-quiet', help='Quiet  mode(default False)')
@click.option('--verbose/--no-verbose', help='Show events (default False)')
def main(config, quiet, verbose):
    """Monitor directories for torrents"""
    print("Starting trawa version {}".format(__version__))
    tw = TorrentWatcher(conf_name=config,
                        log_level=logging.WARNING if quiet
                        else logging.DEBUG if verbose
                        else logging.INFO)
    tw.start()
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
