#!/usr/bin/python
# -*- coding: utf-8 -*-
# This file encoding UTF-8 no BOM. このファイルの文字コードはUTF-8 BOM無しです。
################################################################################
__appname__   = "pyOssInstallChecker.py"
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

################################################################################
# Main
################################################################################
if __name__  == "__main__":
    print u"%s Version: %s %s" % (__appname__, __version__, __copyright__)
    print u""

    iserror = False
    print u"pyOssインストール状況を確認します。"

    execpath = os.path.dirname(os.path.abspath(__file__))
    print execpath

    # Python Version check
    if sys.version_info[0] != 2 or sys.version_info[1] != 6:
        iserror = True
        print u"Pythonのバージョンが2.6ではありません。pyOssは正常に動作しない可能性があります。: %s" % (sys.version_info)

    CheckPaths = [
        # Data check
        [ u"../",
            [
            u"pyOss",
            u"BOSS.exe",
            ]
        ],
        # Tools check
        [ u"../pyOss",
            [
            u"MasterlistChecker.py",
            u"MasterlistDownloader.py",
            u"UpdateUserToMaster.py",
            u"DiffMasterToUser.py",
            u"pyOssInstallChecker.py",
            ]
        ],
        # pyOssLib check
        [ u"../pyOss/pyOssLib",
            [
            u"__init__.py",
            u"LinkedTreeObject.py",
            u"MasterlistLib.py",
            u"UserlistLib.py",
            ]
        ],
    ]

    for check in CheckPaths:
        relativepath = check[0]
        for file in check[1]:
            chkpath = os.path.abspath(os.path.join(execpath, relativepath, file))
            if not os.path.exists(chkpath):
                iserror = True
                print u"%s が見つかりません。" % (chkpath)

    if not iserror:
        print u"pyOssのインストール状況の確認が正常に完了しました。"
    else:
        print u"pyOssのインストール状況が異常です。上記の内容を確認して下さい。"

