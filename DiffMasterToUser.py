#!/usr/bin/python
# -*- coding: utf-8 -*-
# This file encoding UTF-8 no BOM. このファイルの文字コードはUTF-8 BOM無しです。
################################################################################
__appname__   = "DiffMasterToUser.py"
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
import difflib

from optparse import OptionParser

from pyOssLib.v1_0.MasterlistLib import *
from pyOssLib.v1_0.UserlistLib import *

################################################################################
# Function
################################################################################
def CreateUuid():
    return unicode(uuid.uuid4())

def GetPreviousGroupSortPoint(findgroup):
    sort = u""
    name = u""
    for target in findgroup.EachPrevious():
        if isinstance(target, Group):
            # 両方に存在するGroupのみ対象にする。
            if target.Data.get(u"GroupUuid", None) != None:
                sort = u"AFTER"
                name = u"%s" % (target.GroupName)
                break
    else:
        # それでも見つからない場合は、親グループのTOPにする。
        sort = u"TOP"
        name = findgroup.Parent().GroupName
    return (sort, name)


def GetPreviousModsSortPoint(findmod):
    sort = u""
    name = u""
    block = findmod.Parent()
    for target in block.EachPrevious():
        if isinstance(target, Block):
            mods = target.GetLine(EnumLineType.MODS)
            if mods != None:
                # 両方に存在するMODのみ対象にする。
                if mods.Data.get(u"ModsUuid", None) != None:
                    sort = u"AFTER"
                    name = u"%s" % (mods.LineString)
                    break
        if isinstance(target, Group):
            # BOSSで操作不能なユーザーリストを作ってしまうのでグループは対称としない。
            ## 両方に存在するGroupのみ対象にする。
            #if target.Data.get(u"GroupUuid", None) != None:
            #    sort = u"AFTER"
            #    name = u"%s" % (target.GroupName)
            #    break
            # グループの場合は、最後のMOD名を抽出する。グループ内にMODが無かった場合は、さらに前を検索する。
            (tmpsort, tmpname) = GetPreviousModsSortPoint(target.GetBottomChild().GetBottomChild())
            if (tmpsort == u"AFTER") and (tmpname != u""):
                sort = u"AFTER"
                name = u"%s" % (tmpname)
                break
    else:
        # それでも見つからない場合は、親グループのTOPにする。
        sort = u"TOP"
        name = block.Parent().GroupName
    return (sort, name)


def IsSameBlock(edit, base):
    ret = False
    editblock = edit.Parent()
    baseblock = base.Parent()
    ret = True
    for editline in editblock.EachChilds():
        if editline.GetAttribute() != EnumAttributeType.BLANKONLY:
            # ブロック内で前後がずれてても存在すれば同じだろうという判断。
            # 新しい要素が追加されている場合も同じと判断しておけば間違いないだろう。
            # 要素を手動で移動したなどの理由で、コマンド行が残ってしまっている場合に、
            # 直前のブロックが「差異あり」と判断してしまうが、これはマスタリスト自体がおかしいのであきらめる。
            baseline = baseblock.FindData(u"LineString", editline.LineString)
            if baseline == None:
                ret = False
                break
    return ret


################################################################################
# Main
################################################################################
if __name__  == "__main__":
    print u"%s Version: %s %s" % (__appname__, __version__, __copyright__)
    print u""

    usage = u"%prog [Options] BASEMASTERLISTFILE EDITMASTERLISTFILE"
    version = u"%s %s" % (u"%prog", __version__)

    parser = OptionParser(usage = usage, version = version)
    parser.add_option("-o", "--output",
                action="store",
                type="string",
                dest="outfilename",
                default="DiffMasterToUser.txt",
                metavar="FILE",
                help="specify an output file")

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

    # 絶対パスの取得
    BaseMasterlistFile = u"%s" % (os.path.abspath(args0))
    EditMasterlistFile = u"%s" % (os.path.abspath(args1))
    OutputFile = u"%s" % (os.path.abspath(outfilename))

    # 入力ファイルの存在チェック
    if not os.path.exists(BaseMasterlistFile):
        parser.error(u"file not exists. \'%s\'" % BaseMasterlistFile)
    if not os.path.exists(EditMasterlistFile):
        parser.error(u"file not exists. \'%s\'" % EditMasterlistFile)
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
            WriteLine(False, True, False, line)
            return
        def FileWriteLine(line):
            WriteLine(False, False, True, line)
            return
        def DebugWriteLine(line):
            WriteLine(True, True, False, line)
            return

        PrintWriteLine(u"Input files:")

        FileWriteLine(u"// --------------------------------------------------")
        FileWriteLine(u"// Output pyOss - DiffMasterToUser.py")

        PrintWriteLine(u"  Base Masterlist : %s" % (BaseMasterlistFile))
        FileWriteLine(u"//  Base Masterlist : %s" % (BaseMasterlistFile))
        # BASEマスタリストの読み込みと解析
        basemasterfile = Masterlist(BaseMasterlistFile)

        PrintWriteLine(u"  Edit Masterlist : %s" % (EditMasterlistFile))
        FileWriteLine(u"//  Edit Masterlist : %s" % (EditMasterlistFile))
        # EDITマスタリストの読み込みと解析
        editmasterfile = Masterlist(EditMasterlistFile)

        PrintWriteLine(u"Output files:")
        PrintWriteLine(u"  %s" % (OutputFile))
        FileWriteLine(u"//  OutputFile      : %s" % (OutputFile))
        FileWriteLine(u"// --------------------------------------------------")

        basemasterfile.ClearRecord()
        basemasterfile.BeginRecord()

        PrintWriteLine(u"--------------------------------------------------")
        PrintWriteLine(u" Processing Group")
        PrintWriteLine(u"--------------------------------------------------")
        PrintWriteLine(u"Getting group information...")

        # グループ名の一覧を取得する。
        editgrouplists = editmasterfile.FindDataAllFunc(u"GroupName", lambda v: (v != None))
        editgroupstrings = [obj.GroupName for obj in editgrouplists]
        basegrouplists = basemasterfile.FindDataAllFunc(u"GroupName", lambda v: (v != None))
        basegroupstrings = [obj.GroupName for obj in basegrouplists]

        # EDIT側のグループ全てにUUIDを割り振る（ユニークなIDになるようにUUIDを使う）
        for editgroup in editgrouplists:
            editgroup.GroupUuid = CreateUuid()

        # グループ名でDIFF差分を抽出する。
        # これによって、同じ行付近にある重複グループも、ある程度同一グループとして判断できる。
        opetargetgroups = []
        matcher = difflib.SequenceMatcher(None, basegroupstrings, editgroupstrings)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes(): 
            DebugWriteLine(("%7s s1[%d:%d] (%s=>%s) s2[%d:%d] (%s=>%s)" % (tag, i1, i2, basegroupstrings[i1], basegroupstrings[i2-1], j1, j2, editgroupstrings[j1], editgroupstrings[j2-1])))
            if tag in ["replace", "insert"]:
                # 動いたか追加されたグループを記録する。
                indexj1 = j1
                for edittargetstring in editgroupstrings[j1:j2]:
                    if edittargetstring == editgrouplists[indexj1].GroupName:
                        opetargetgroups.append(editgrouplists[indexj1])
                        indexj1 += 1
            elif tag == "delete":
                # 移動したものも、deleteになるのであとで検索してなんとかする。
                pass
            elif tag == "equal":
                # 同一グループとして確定する。
                indexi1 = i1
                indexj1 = j1
                for edittargetstring in editgroupstrings[j1:j2]:
                    if basegrouplists[indexi1].GroupName == editgrouplists[indexj1].GroupName:
                        # 同一グループとしてUUIDをコピーする。
                        basegrouplists[indexi1].GroupUuid = editgrouplists[indexj1].GroupUuid
                        indexi1 += 1
                        indexj1 += 1

        PrintWriteLine(u"Searching for the same group...")
        for opreditgroup in opetargetgroups:
            for basegroup in basegrouplists:
                if basegroup.GroupName == opreditgroup.GroupName:
                    if basegroup.Data.get(u"GroupUuid", None) == None:
                        # 同一グループとしてUUIDをコピーする。
                        basegroup.GroupUuid = opreditgroup.GroupUuid
                        # 操作方法をマーク
                        opreditgroup.OperationRule = u"OVERRIDE"
                        break
            else:
                # 見つからなかったら新規追加グループと判断する。
                # 操作方法をマーク
                opreditgroup.OperationRule = u"ADD"

        DebugWriteLine(u"--------------------------------------------------")
        PrintWriteLine(u"Searching for the appropriate groups...")

        for opreditgroup in opetargetgroups:
            (sort, name) = GetPreviousGroupSortPoint(opreditgroup)
            opreditgroup.OperationSort = sort
            opreditgroup.OperationSortName = name

            DebugWriteLine(u"%s: %s %s, %s %s" % (opreditgroup.GroupUuid, opreditgroup.OperationRule ,opreditgroup.GroupName, opreditgroup.OperationSort, opreditgroup.OperationSortName))

            oper = UserOperation()
            if opreditgroup.OperationRule == u"ADD":
                oper.AddNewRuleAdd(opreditgroup.GroupName)
            elif opreditgroup.OperationRule == u"OVERRIDE":
                oper.AddNewRuleOverride(opreditgroup.GroupName)

            if opreditgroup.OperationSort == u"AFTER":
                oper.AddNewSortAfter(opreditgroup.OperationSortName)
            elif opreditgroup.OperationSort == u"TOP":
                oper.AddNewSortTop(opreditgroup.OperationSortName)

            oper.AddNewBlank()
            basemasterfile.Operater(oper)

        PrintWriteLine(u"Generating for userlist commands...")

        proc = basemasterfile.GenerateUserlistFromRecord()
        if proc.ChildCount() >= 1:
            FileWriteLine(u"// 以下にグループに対する操作を出力します。")
            FileWriteLine(u"// ただし、BOSSではグループの追加ができませんのでADDコマンドにご注意下さい。")
            FileWriteLine(u"%s" % (proc.UserlistOutput()))
            FileWriteLine(u"// --------------------------------------------------")
        basemasterfile.ClearRecord()


        PrintWriteLine(u"--------------------------------------------------")
        PrintWriteLine(u" Processing MODs")
        PrintWriteLine(u"--------------------------------------------------")
        PrintWriteLine(u"Getting mods information...")

        # MODs名の一覧を取得する。
        editmodslists = editmasterfile.FindDataAllFunc(u"LineType", lambda v: ((v & EnumLineType.MODS) == EnumLineType.MODS))
        editmodsstrings = [obj.LineString for obj in editmodslists]
        basemodslists = basemasterfile.FindDataAllFunc(u"LineType", lambda v: ((v & EnumLineType.MODS) == EnumLineType.MODS))
        basemodsstrings = [obj.LineString for obj in basemodslists]

        # EDIT側のグループ全てにUUIDを割り振る（ユニークなIDになるようにUUIDを使う）
        for editmods in editmodslists:
            editmods.ModsUuid = CreateUuid()

        # MODs名でDIFF差分を抽出する。
        # これによって、同じ行付近にある重複MODsも、ある程度同一MODsとして判断できる。
        opetargetmods = []
        matcher = difflib.SequenceMatcher(None, basemodsstrings, editmodsstrings)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes(): 
            DebugWriteLine(("%7s s1[%d:%d] (%s=>%s) s2[%d:%d] (%s=>%s)" % (tag, i1, i2, basemodsstrings[i1], basemodsstrings[i2-1], j1, j2, editmodsstrings[j1], editmodsstrings[j2-1])))
            if tag in ["replace", "insert"]:
                # 動いたか追加されたMODsを記録する。
                indexj1 = j1
                for edittargetstring in editmodsstrings[j1:j2]:
                    if edittargetstring == editmodslists[indexj1].LineString:
                        opetargetmods.append(editmodslists[indexj1])
                        indexj1 += 1
            elif tag == "delete":
                # 移動したものも、deleteになるのであとで検索してなんとかする。
                pass
            elif tag == "equal":
                # 同一MODsとして確定する。
                indexi1 = i1
                indexj1 = j1
                for edittargetstring in editmodsstrings[j1:j2]:
                    if basemodslists[indexi1].LineString == editmodslists[indexj1].LineString:
                        # 同一MODsとしてUUIDをコピーする。
                        basemodslists[indexi1].ModsUuid = editmodslists[indexj1].ModsUuid
                        indexi1 += 1
                        indexj1 += 1

        PrintWriteLine(u"Searching for the same mods...")
        for opreditmod in opetargetmods:
            for basemod in basemodslists:
                if basemod.LineString == opreditmod.LineString:
                    if basemod.Data.get(u"ModsUuid", None) == None:
                        # 同一MODsとしてUUIDをコピーする。
                        basemod.ModsUuid = opreditmod.ModsUuid
                        # 操作方法をマーク
                        opreditmod.OperationRule = u"OVERRIDE"
                        break
            else:
                # 見つからなかったら新規追加MODsと判断する。
                # 操作方法をマーク
                opreditmod.OperationRule = u"ADD"

        # --------------------------------------------------
        # MODSのみの実装
        # --------------------------------------------------
        PrintWriteLine(u"The unique ID is allocated in MODs...")
        # FindDataでは検索速度が遅すぎるので、一旦ディクショナリに格納する。
        basehashlists = {}
        for basemod in basemodslists:
            if basemod.Data.get(u"ModsUuid", None) != None:
                basehashlists[basemod.ModsUuid] = basemod

        PrintWriteLine(u"The accompanying information on MODs is inspected...")
        for editmod in editmodslists:
            DebugWriteLine(editmod.LineString)

            #basemod = basemasterfile.FindData(u"ModsUuid", editmod.ModsUuid)
            basemod = basehashlists.get(editmod.ModsUuid, None)
            if basemod != None:
                # BaseにもEditにもあるMods
                if not IsSameBlock(editmod, basemod):
                    # 変更あり

                    # REPLACEが必要か調査する。
                    replaceflg = True
                    for command in basemod.EachNext():
                        if command.IsType(EnumLineType.COMMAND):
                            # コマンド行があればREPLACEが必要と判断する。
                            replaceflg = False

                    # コマンドタイプの行を列挙
                    addlists = []
                    for command in editmod.EachNext():
                        if command.IsType(EnumLineType.COMMAND):
                            addlists += [command]
                    if len(addlists) >= 1:
                        editmod.OperationMessage = []
                        for command in addlists:
                            if not replaceflg:
                                editmod.OperationMessage += [[u"REPLACE", basemod.LineString, command.LineString]]
                                replaceflg = True
                            else:
                                editmod.OperationMessage += [[u"APPEND", basemod.LineString, command.LineString]]

            else:
                # コマンドタイプの行を列挙
                addlists = []
                for command in editmod.EachNext():
                    if command.IsType(EnumLineType.COMMAND):
                        addlists += [command]
                if len(addlists) >= 1:
                    editmod.OperationMessage = []
                    for command in addlists:
                        editmod.OperationMessage += [[u"APPEND", editmod.LineString, command.LineString]]


        DebugWriteLine(u"--------------------------------------------------")
        PrintWriteLine(u"Searching for the appropriate mods...")

        for opreditmod in editmodslists:
            if opreditmod.Data.get(u"OperationRule", None) != None:
                (sort, name) = GetPreviousModsSortPoint(opreditmod)
                opreditmod.OperationSort = sort
                opreditmod.OperationSortName = name

                DebugWriteLine(u"%s: %s %s, %s %s" % (opreditmod.ModsUuid, opreditmod.OperationRule ,opreditmod.LineString, opreditmod.OperationSort, opreditmod.OperationSortName))

                oper = UserOperation()
                if opreditmod.OperationRule == u"ADD":
                    oper.AddNewRuleAdd(opreditmod.LineString)
                elif opreditmod.OperationRule == u"OVERRIDE":
                    oper.AddNewRuleOverride(opreditmod.LineString)

                if opreditmod.OperationSort == u"AFTER":
                    oper.AddNewSortAfter(opreditmod.OperationSortName)
                elif opreditmod.OperationSort == u"TOP":
                    oper.AddNewSortTop(opreditmod.OperationSortName)

                oper.AddNewBlank()
                basemasterfile.Operater(oper)

            operationmessages = opreditmod.Data.get(u"OperationMessage", None)
            if operationmessages != None:
                for message in operationmessages:
                    oper = UserOperation()
                    oper.AddNewRuleFor(message[1])
                    if message[0] == u"REPLACE":
                        oper.AddNewMessageReplace(message[2])
                    elif message[0] == u"APPEND":
                        oper.AddNewMessageAppend(message[2])
                    oper.AddNewBlank()
                    basemasterfile.Operater(oper)

        DebugWriteLine(u"--------------------------------------------------")
        PrintWriteLine(u"Generating for userlist commands...")

        basemasterfile.EndRecord()
        proc = basemasterfile.GenerateUserlistFromRecord()
        FileWriteLine(u"%s" % (proc.UserlistOutput()))

    finally:
        fileoutput.close()

    print u"Completed!"
    print u" Output File : %s" % (OutputFile)

