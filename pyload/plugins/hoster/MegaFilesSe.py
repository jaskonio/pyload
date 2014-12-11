# -*- coding: utf-8 -*-

from pyload.plugins.internal.DeadHoster import DeadHoster, create_getInfo


class MegaFilesSe(DeadHoster):
    __name    = "MegaFilesSe"
    __type    = "hoster"
    __version = "0.02"

    __pattern = r'http://(?:www\.)?megafiles\.se/\w{12}'

    __description = """MegaFiles.se hoster plugin"""
    __license     = "GPLv3"
    __authors     = [("t4skforce", "t4skforce1337[AT]gmail[DOT]com")]


getInfo = create_getInfo(MegaFilesSe)