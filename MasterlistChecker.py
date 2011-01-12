#!/usr/bin/python
# -*- coding: utf-8 -*-
# This file encoding UTF-8 no BOM. このファイルの文字コードはUTF-8 BOM無しです。
################################################################################
__appname__   = "MasterlistChecker.py"
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
# Global variable
################################################################################
# [masterlist] ESM、ESPファイル検出正規表現（「>」と「<」は、ファイルとして認識させる）
regexMods = re.compile(ur"^([><]?)([^><\\%?*:\"$^]{1}[^\\><:\"/|?*]*[.](esm|esp))\s*.*$", re.IGNORECASE)
# [masterlist] コメントorコマンド行検出正規表現
regexCommand = re.compile(ur"^([><]?)([\\%?*:\"$^]{1})\s*(.*)$")
# [masterlist] グループ開始検出正規表現 \BeginGroup\: Post BSA
regexBeginGroup = re.compile(ur"^\\BeginGroup\\:(.*)", re.IGNORECASE)
# [masterlist] グループ終了検出正規表現 \EndGroup\\
regexEndGroup = re.compile(ur"^\\EndGroup\\\\", re.IGNORECASE)

# [masterlist補正用] BASH定義っぽい行検出正規表現
regexExBash = re.compile(ur"^([{]{2}BASH[:]\S+[}]{2}.*)$", re.IGNORECASE)
# [masterlist補正用] コメント間違いっぽい行検出正規表現
regexExComment = re.compile(ur"^/\s*(.*)")
# [masterlist補正用] ESM,ESPっぽい行検出正規表現
regexExMods1 = re.compile(ur"^(\w+(\w|[ ]|[$%'_@!()~-])+)\s*$")


regexWarnings = re.compile(ur"""
    ^([><]?)
    ([^><\\%?*:\"$^]{1})
    ([a-zA-Z0-9_() .\[\]#!+,%&'-])+
    (?!
        (
        \s{2,}
        |[_() .\[\]#!+,%&'-]{2,}
        )
    )[.](esm|esp)$
    """, re.IGNORECASE | re.VERBOSE)


################################################################################
# Function
################################################################################
def CreateUuid():
    return unicode(uuid.uuid4())


################################################################################
# Main
################################################################################
if __name__  == "__main__":
    print u"%s Version: %s %s" % (__appname__, __version__, __copyright__)
    print u""

    usage = u"%prog [Options] MASTERLISTFILE"
    version = u"%s %s" % (u"%prog", __version__)

    parser = OptionParser(usage = usage, version = version)
    parser.add_option("-o", "--output",
                action="store",
                type="string",
                dest="outfilename",
                default="MasterlistChecker.txt",
                metavar="FILE",
                help="specify an output file")

    parser.add_option("-d", "--debug",
                action="store_true",
                dest="debug",
                default=False,
                help="debug output")

    # オプションの解析
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error(u"incorrect number of arguments")

    args0 = unicode(args[0], "shift-jis")
    outfilename = unicode(options.outfilename, "shift-jis")

    # 絶対パスの取得
    MasterlistFile = u"%s" % (os.path.abspath(args0))
    OutputFile = u"%s" % (os.path.abspath(outfilename))

    # 入力ファイルの存在チェック
    if not os.path.exists(MasterlistFile):
        parser.error(u"file not exists. \'%s\'" % MasterlistFile)

    # 出力ファイルが存在していたら削除する
    if os.path.exists(OutputFile):
        os.remove(OutputFile)

    # 出力開始
    fileoutput = codecs.open(OutputFile, "wU", "utf-8-sig")
    try:
        # 適当に出力用ファンクション作成
        def WriteLine(debug = False, screen = True, file = True, line = u""):
            if debug:
                if options.debug:
                    # 出力する
                    if screen:
                        print u"%s" % (line)
                    if file:
                        fileoutput.write(u"%s\r\n" % (line))
                else:
                    # 出力しない
                    pass
            else:
                if screen:
                    print u"%s" % (line)
                if file:
                    fileoutput.write(u"%s\r\n" % (line))
            return

        def PrintWriteLine(line):
            WriteLine(False, False, True, line)
            return
        def DebugWriteLine(line):
            WriteLine(True, True, True, line)
            return

        PrintWriteLine(u"--------------------------------------------------")
        PrintWriteLine(u"Output pyOss - MasterlistChecker.py")
        PrintWriteLine(u"Input files:")
        PrintWriteLine(u" Masterlist : %s" % (MasterlistFile))
        PrintWriteLine(u"Output files:")
        PrintWriteLine(u" OutputFile : %s" % (OutputFile))
        PrintWriteLine(u"--------------------------------------------------")

        SkipLines = []

        StackErrors = {}
        def AddStackErrors(count, error, message):
            if not error in StackErrors:
                StackErrors[error] = []
            StackErrors[error] += [[count, message]]

        # --------------------------------------------------
        # 
        # --------------------------------------------------
        masterfile = Masterlist()

        def _onEncodingError(linecount, linestring, encoding):
            message = u"Can not be displayed : %s" % (encoding)
            AddStackErrors(linecount, u"A01 UNICODE encoding error!", message)
            return
        masterfile.OnEncodingErrorFromSave = _onEncodingError
        masterfile.OnDecodingErrorFromLoad = _onEncodingError

        def _onCreateLineObject(linecount, linestring):
            lineobject = Line(linestring)
            lineobject.LineCount = linecount

            linestring = lineobject.LineString

            if lineobject.IsType(EnumLineType.OTHER):
                matchEx = [regexExBash.search(linestring)
                        ,regexExComment.search(linestring)
                        ,regexExMods1.search(linestring)]
                if matchEx[0] is not None:
                    # Bashタグを書いたが、先頭の％を書き忘れちゃった感で一杯の行
                    # 先頭に％を付け足す。
                    linecorrectionstring = u"%"

                    AddStackErrors(linecount, u"A02 Typographical errors!", u"%s => %s" % (linecorrectionstring, linestring))
                elif matchEx[1] is not None:
                    # コメントを書いたが、「＼バックスラッシュ」と「／スラッシュ」を間違えた感で一杯の行
                    # ￥マークに書き換える。（英語圏では￥マークは＼バックスラッシュに置き換えられる）
                    linecorrectionstring = u"\\"
                    AddStackErrors(linecount, u"A02 Typographical errors!", u"%s => %s" % (linecorrectionstring, linestring))
                elif matchEx[2] is not None:
                    # 拡張子を書き忘れた感で一杯の行
                    # espとみなす。（少なくともピリオドがない行はESPファイルと思われる。）
                    # 今のところesmではミスなさそう。
                    linecorrectionstring = u".esp"
                    AddStackErrors(linecount, u"A02 Typographical errors!", u"%s => %s" % (linecorrectionstring, linestring))
                else:
                    if len(linestring) != 0:
                        AddStackErrors(linecount, u"A03 Format unknown error!", u"%s" % (linestring))

            if lineobject.IsType(EnumLineType.MODS):
                match2 = regexWarnings.search(linestring)
                if match2 == None:
                    pass
                    #AddStackErrors(linecount, u"A04 Warning! Please check if this is correct.", u"%s" % (linestring))

            return lineobject
        masterfile.OnCreateLineObject = _onCreateLineObject

        loadingflg = False
        try:
            masterfile.Load(MasterlistFile)
            loadingflg = True
        except BaseException as ex:
            AddStackErrors(0, u"A05 Load error!", unicode(ex))
            PrintWriteLine(u"--------------------------------------------------")
            PrintWriteLine(u"Could not run some checks!!!!")
            PrintWriteLine(u"--------------------------------------------------")

        if loadingflg:
            AddStackErrors(0, u"A00 Encoding Information", masterfile.Encoding)
            GroupLists = {}
            ModsLists = {}

            for object in masterfile.EachRecursion():
                if isinstance(object, Line):
                    if object.IsType(EnumLineType.MODS):
                        if object.LineString in ModsLists:
                            ModsLists[object.LineString] += [object]
                        else:
                            ModsLists[object.LineString] = [object]

                        if object.GetParentGroup().GroupName == None:
                            AddStackErrors(object.LineCount, u"B01 Warning! There are lines that do not belong to the group.", u"%s" % (object.LineString))

                elif isinstance(object, Block):
                    pass

                elif isinstance(object, Group):
                    if object.GroupName in GroupLists:
                        GroupLists[object.GroupName] += [object]
                    else:
                        GroupLists[object.GroupName] = [object]

            for key, value in GroupLists.iteritems():
                if len(value) >= 2:
                    for group in value:
                        linecount = group.GetTopChild().GetTopChild().LineCount
                        AddStackErrors(linecount, u"B02 Duplicate groups error!", u"%s" % (group.GroupName))

            for key, value in ModsLists.iteritems():
                if len(value) >= 2:
                    for mods in value:
                        AddStackErrors(mods.LineCount, u"B03 Duplicate mods error!", u"%s" % (mods.LineString))

        # --------------------------------------------------
        # エラーの出力
        # --------------------------------------------------
        for errorkey in sorted(StackErrors):
            errorvalue = StackErrors[errorkey]
            PrintWriteLine(u"--------------------------------------------------")
            PrintWriteLine(errorkey)
            PrintWriteLine(u"--------------------------------------------------")
            for error in errorvalue:
                PrintWriteLine(u"%8d: %s" % (error[0], error[1]))

    finally:
        fileoutput.close()

    print u"Completed!"
    print u" Output File : %s" % (OutputFile)

