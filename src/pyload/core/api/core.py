# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import os

from future import standard_library

from pyload.utils.fs import availspace, lopen

from ..datatype.init import Permission, StatusInfo
from ..datatype.task import Interaction
from .base import BaseApi
from .init import requireperm

standard_library.install_aliases()


class CoreApi(BaseApi):
    """
    This module provides methods for general interaction with the core,
    like status or progress retrieval.
    """
    @requireperm(Permission.All)
    def get_server_version(self):
        """
        PyLoad Core version.
        """
        return self.__pyload.version

    def is_ws_secure(self):
        # needs to use TLS when either requested or webui is also using
        # encryption
        if not self.__pyload.config.get('ssl', 'activated'):
            return False

        cert = self.__pyload.config.get('ssl', 'cert')
        key = self.__pyload.config.get('ssl', 'key')
        if not os.path.isfile(cert) or not os.path.isfile(key):
            self.__pyload.log.warning(
                self._('SSL key or certificate not found'))
            return False

        return True

    @requireperm(Permission.All)
    def get_status_info(self):
        """
        Some general information about the current status of pyLoad.

        :return: `StatusInfo`
        """
        queue = self.__pyload.files.get_queue_stats()
        total = self.__pyload.files.get_download_stats()

        server_status = StatusInfo(0,
                                   total[0], queue[0],
                                   total[1], queue[1],
                                   self.is_interaction_waiting(
                                       Interaction.All),
                                   not self.__pyload.tsm.pause,
                                   self.__pyload.tsm.pause,
                                   self.__pyload.config.get(
                                       'reconnect', 'activated'),
                                   self.get_quota())

        for file in self.__pyload.tsm.active_downloads():
            server_status.speed += file.get_speed()  # bytes/s

        return server_status

    @requireperm(Permission.All)
    def get_progress_info(self):
        """
        Status of all currently running tasks

        :rtype: list of :class:`ProgressInfo`
        """
        return (self.__pyload.tsm.get_progress_list() +
                self.__pyload.iom.get_progress_list())

    def pause_server(self):
        """
        Pause server: It won't start any new downloads,
        but nothing gets aborted.
        """
        self.__pyload.tsm.pause = True

    def unpause_server(self):
        """
        Unpause server: New Downloads will be started.
        """
        self.__pyload.tsm.pause = False

    def toggle_pause(self):
        """
        Toggle pause state.

        :return: new pause state
        """
        self.__pyload.tsm.pause ^= True
        return self.__pyload.tsm.pause

    def toggle_reconnect(self):
        """
        Toggle reconnect activation.

        :return: new reconnect state
        """
        self.__pyload.config['reconnect']['activated'] ^= True
        return self.__pyload.config.get('reconnect', 'activated')

    def avail_space(self):
        """
        Available free space at download directory in bytes.
        """
        return availspace(self.__pyload.config.get(
            'general', 'storage_folder'))

    def shutdown(self):
        """
        Clean way to quit pyLoad.
        """
        self.__pyload._Core__do_shutdown = True

    def restart(self):
        """
        Restart pyload core.
        """
        self.__pyload._Core__do_restart = True

    def get_log(self, offset=0):
        """
        Returns most recent log entries.

        :param offset: line offset
        :return: List of log entries
        """
        # TODO: Rewrite!
        logfile_folder = self.config.get('log', 'logfile_folder')
        if not logfile_folder:
            logfile_folder = self.__pyload.DEFAULT_LOGDIRNAME
        logfile_name = self.config.get('log', 'logfile_name')
        if not logfile_name:
            logfile_name = self.DEFAULT_LOGFILENAME
        filepath = os.path.join(logfile_folder, logfile_name)
        try:
            with lopen(filepath) as fp:
                lines = fp.readlines()
            if offset >= len(lines):
                return []
            return lines[offset:]
        except Exception:
            return ['No log available']

    # @requireperm(Permission.All)
    # def is_time_download(self):
        # """
        # Checks if pyload will start new downloads according to time in
        # config.

        # :return: bool
        # """
        # start = self.__pyload.config.get('connection', 'start').split(":")
        # end = self.__pyload.config.get('connection', 'end').split(":")
        # return compare_time(start, end)

    # @requireperm(Permission.All)
    # def is_time_reconnect(self):
        # """
        # Checks if pyload will try to make a reconnect

        # :return: bool
        # """
        # start = self.__pyload.config.get('reconnect', 'start').split(":")
        # end = self.__pyload.config.get('reconnect', 'end').split(":")
        # return compare_time(start, end) and
        # self.__pyload.config.get('reconnect', 'activated')
