#!/usr/bin/python
# -*- coding: utf-8 -*-
# This file encoding UTF-8 no BOM. このファイルの文字コードはUTF-8 BOM無しです。
################################################################################
__appname__   = "UpdateUserToMaster.py"
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
import codecs
import re

reload(sys)
sys.setdefaultencoding('utf-8')

import uuid

from optparse import OptionParser

from pyOssLib.v1_0.MasterlistLib import *
from pyOssLib.v1_0.UserlistLib import *

################################################################################
# Main
################################################################################
if __name__  == "__main__":
    print u"%s Version: %s %s" % (__appname__, __version__, __copyright__)
    print u""

    usage = u"%prog [Options] MASTERLISTFILE USERLISTFILE"
    version = u"%s %s" % (u"%prog", __version__)

    parser = OptionParser(usage = usage, version = version)

    parser.add_option("-o", "--output",
                action="store",
                type="string",
                dest="outfilename",
                default="",
                metavar="FILE",
                help="specify an output file. default=MASTERLISTFILE")

    parser.add_option("", "--outenc",
                action="store",
                type="string",
                dest="outputencoding",
                default="",
                help="specify an output file encoding. default=Encoding of MASTERLISTFILE")

    parser.add_option("-d", "--debug",
                action="store_true",
                dest="debug",
                default=False,
                help="debug output")

    # オプションの解析
    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.error(u"incorrect number of arguments")

    args0 = u"%s" % (args[0])
    args1 = u"%s" % (args[1])
    outfilename = u"%s" % (options.outfilename)
    outputencoding = u"%s" % (options.outputencoding)

    # 絶対パスの取得
    MasterlistFile = u"%s" % (os.path.abspath(args0))
    UserlistFile = u"%s" % (os.path.abspath(args1))

    if len(outfilename) != 0:
        OutputFile = u"%s" % (os.path.abspath(outfilename))
    else:
        OutputFile = MasterlistFile

    # 入力ファイルの存在チェック
    if not os.path.exists(MasterlistFile):
        parser.error(u"file not exists. \'%s\'" % MasterlistFile)
    if not os.path.exists(UserlistFile):
        parser.error(u"file not exists. \'%s\'" % UserlistFile)

    # マスタリストの読み込みと解析
    masterfile = Masterlist(MasterlistFile)
    # ユーザーリストの読み込みと解析
    userfile = Userlist(UserlistFile)

    # ユーザーリストの内容をマスタリストへ反映する。
    masterfile.Operater(userfile)

    # マスタリストを保存する。
    if len(outputencoding) == 0:
        outputencoding = masterfile.Encoding
    masterfile.Save(OutputFile, outputencoding)

