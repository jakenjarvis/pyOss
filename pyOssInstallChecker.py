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

reload(sys)
sys.setdefaultencoding('utf-8')

################################################################################
# Main
################################################################################
if __name__  == "__main__":
    print u"%s Version: %s %s" % (__appname__, __version__, __copyright__)
    print u""

    iserror = False
    print u"Checking pyOss installation."

    execpath = os.path.dirname(os.path.abspath(__file__))
    print execpath

    # Python Version check
    if sys.version_info[0] != 2 or sys.version_info[1] != 6:
        iserror = True
        print u"The version of Python is not 2.6. There is a possibility that pyOss doesn't operate: %s" % (sys.version_info)

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
            u"pyOssLib",
            u"Templates",
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
            u"v1_0",
            u"__init__.py",
            ]
        ],
        # pyOssLib/v1_0 check
        [ u"../pyOss/pyOssLib/v1_0",
            [
            u"chardet",
            u"__init__.py",
            u"CommonLib.py",
            u"LinkedTreeObject.py",
            u"MasterlistLib.py",
            u"UserlistLib.py",
            ]
        ],
        # pyOssLib/v1_0/chardet check
        [ u"../pyOss/pyOssLib/v1_0/chardet",
            [
            u"docs",
            u"__init__.py",
            u"big5freq.py",
            u"big5prober.py",
            u"chardistribution.py",
            u"charsetgroupprober.py",
            u"charsetprober.py",
            u"codingstatemachine.py",
            u"constants.py",
            u"COPYING",
            u"escprober.py",
            u"escsm.py",
            u"eucjpprober.py",
            u"euckrfreq.py",
            u"euckrprober.py",
            u"euctwfreq.py",
            u"euctwprober.py",
            u"gb2312freq.py",
            u"gb2312prober.py",
            u"hebrewprober.py",
            u"jisfreq.py",
            u"jpcntx.py",
            u"langbulgarianmodel.py",
            u"langcyrillicmodel.py",
            u"langgreekmodel.py",
            u"langhebrewmodel.py",
            u"langhungarianmodel.py",
            u"langthaimodel.py",
            u"latin1prober.py",
            u"mbcharsetprober.py",
            u"mbcsgroupprober.py",
            u"mbcssm.py",
            u"sbcharsetprober.py",
            u"sbcsgroupprober.py",
            u"setup.py",
            u"sjisprober.py",
            u"test.py",
            u"universaldetector.py",
            u"utf8prober.py",
            ]
        ],
    ]

    for check in CheckPaths:
        relativepath = check[0]
        for file in check[1]:
            chkpath = os.path.abspath(os.path.join(execpath, relativepath, file))
            if not os.path.exists(chkpath):
                iserror = True
                print u"%s  can not be found." % (chkpath)

    if not iserror:
        print u"Check pyOss installation is completed successfully."
    else:
        print u"There is an error in the installation of pyOss. Please confirm the above-mentioned content."

