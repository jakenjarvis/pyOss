#!/usr/bin/python
# -*- coding: utf-8 -*-
# This file encoding UTF-8 no BOM. このファイルの文字コードはUTF-8 BOM無しです。
################################################################################
__appname__   = "CommonLib"
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

__all__       = [
    "CutBomString",
]

################################################################################
# Import
################################################################################
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import codecs


################################################################################
# Global variable
################################################################################
def CutBomString(linestring):
    """
        *linestring* で指定した文字列の先頭にBOMが存在する場合、BOMを削除した文字列を返却する。
        ファイルの先頭文字列以外でこの関数を使った場合、BOM以外の文字列を削除する可能性があるため、注意が必要です。

        :param string linestring: 対象の文字列
    """
    ret = linestring
    if linestring[:3] == codecs.BOM_UTF8:
        # UTF-8 BOM
        ret = linestring[3:]
    elif linestring[:4] == codecs.BOM_UTF32_LE:
        # UTF-32, little-endian BOM
        ret = linestring[4:]
    elif linestring[:4] == codecs.BOM_UTF32_BE:
        # UTF-32, big-endian BOM
        ret = linestring[4:]
    elif linestring[:4] == "\xFE\xFF\x00\x00":
        # UCS-4, unusual octet order BOM (3412)
        ret = linestring[4:]
    elif linestring[:4] == "\x00\x00\xFF\xFE":
        # UCS-4, unusual octet order BOM (2143)
        ret = linestring[4:]
    elif linestring[:2] == codecs.BOM_UTF16_LE:
        # UTF-16, little endian BOM
        ret = linestring[2:]
    elif linestring[:2] == codecs.BOM_UTF16_BE:
        # UTF-16, big endian BOM
        ret = linestring[2:]
    return ret

if __name__  == "__main__":
    print u"%s Version: %s %s" % (__appname__, __version__, __copyright__)
    print u"%s" % (__license__)

