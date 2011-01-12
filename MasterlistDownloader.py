#!/usr/bin/python
# -*- coding: utf-8 -*-
# This file encoding UTF-8 no BOM. このファイルの文字コードはUTF-8 BOM無しです。
################################################################################
__appname__   = "MasterlistDownloader.py"
__author__    = "Jaken<Jaken.Jarvis@gmail.com>"
__copyright__ = "Copyright 2010, Jaken"
__license__   = """
GNU General Public License v3

This file is part of pyOss.
Copyright (C) 2010 Jaken.(jaken.jarvis@gmail.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
__version__   = "1.0.0"
__credits__   = [
  '"Jaken" <Jaken.Jarvis@gmail.com>',
]

################################################################################
# Import
################################################################################
import sys
import os
import urllib

reload(sys)
sys.setdefaultencoding('utf-8')

from optparse import OptionParser

################################################################################
# Global variable
################################################################################

oblivion_masterlist = u"http://better-oblivion-sorting-software.googlecode.com/svn/data/boss-oblivion/masterlist.txt"
fallout_masterlist = u"http://better-oblivion-sorting-software.googlecode.com/svn/data/boss-fallout/masterlist.txt"
nehrim_masterlist = u"http://better-oblivion-sorting-software.googlecode.com/svn/data/boss-nehrim/masterlist.txt"
falloutnv_masterlist = u"http://better-oblivion-sorting-software.googlecode.com/svn/data/boss-fallout-nv/masterlist.txt"

gameslists = {
        "Oblivion" : oblivion_masterlist,
        "Fallout3" : fallout_masterlist,
        "Nehrim" : nehrim_masterlist,
        "Fallout3NV" : falloutnv_masterlist
    }

################################################################################
# Main
################################################################################
if __name__  == "__main__":
    print u"%s Version: %s %s" % (__appname__, __version__, __copyright__)
    print u""

    usage = u"%prog [Options]"
    version = u"%s %s" % (u"%prog", __version__)

    parser = OptionParser(usage = usage, version = version)
    parser.add_option("-o", "--output",
                action="store",
                type="string",
                dest="masterlistname",
                default="masterlist.txt",
                metavar="FILE",
                help="specify an output file")

    parser.add_option("-g", "--game",
                type="choice",
                choices=gameslists.keys(),
                dest="game",
                default="Oblivion",
                metavar="GAME",
                help="Download Masterlist game type. valid values are: 'Oblivion', 'Nehrim', 'Fallout3', and 'Fallout3NV'")

    parser.add_option("-d", "--debug",
                action="store_true",
                dest="debug",
                default=False,
                help="debug output")

    # オプションの解析
    (options, args) = parser.parse_args()

    if len(args) != 0:
        parser.error(u"incorrect number of arguments")
    if not options.game in gameslists:
        parser.error(u"invalid option for 'game' parameter")

    downloadurl = gameslists[options.game]

    # 絶対パスの取得
    masterlistname = options.masterlistname
    MasterlistFile = u"%s" % (os.path.abspath(masterlistname))

    # ダウンロード
    urllib.urlretrieve(downloadurl, MasterlistFile)

