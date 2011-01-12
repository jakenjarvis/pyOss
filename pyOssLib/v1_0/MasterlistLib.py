#!/usr/bin/python
# -*- coding: utf-8 -*-
# This file encoding UTF-8 no BOM. このファイルの文字コードはUTF-8 BOM無しです。
################################################################################
__appname__   = "MasterlistLib"
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
    "EnumLineType",
    "EnumAttributeType",
    "Group",
    "Block",
    "Line",
    "Masterlist",
]

################################################################################
# Import
################################################################################
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import codecs
import re
import copy

from chardet.universaldetector import UniversalDetector

import CommonLib
from LinkedTreeObject import LinkedTreeObject

from UserlistLib import EnumCommandType
from UserlistLib import EnumUserAttributeType
from UserlistLib import UserOperation
from UserlistLib import UserLine
from UserlistLib import Userlist


################################################################################
# Global variable
################################################################################
# [masterlist] ESM、ESPファイル検出正規表現（「>」と「<」は、ファイルとして認識させる）
regexMods = re.compile(ur"^([><]?)([^><\\%?*:\"$^]{1}[^\\><:\"/|?*]*[.](esm|esp))\s*.*$", re.IGNORECASE)
# [masterlist] コメントorコマンド行検出正規表現
regexCommand = re.compile(ur"^([><]?)([\\%?*:\"$^]{1}(?!(BeginGroup|EndGroup)))\s*(.*)$")
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

# レコード判定用
regexRecord = re.compile(ur"^(((Move|Insert)(Before|After|Top|Bottom))|(AppendLine|ReplaceLine))From(MODs|Group)To(MODs|Group)$")


################################################################################
# Class
################################################################################
# ------------------------------------------------------------------------------
# EnumLineType
# ------------------------------------------------------------------------------
class EnumLineType(object):
    """
        \ :class:`Line`\ クラスの行格納タイプを表現します。（列挙体ビットフィールド表現クラス）
    """
    #: 判定できなかった不明な行を表します。
    OTHER                   = 0x000000
    #: 空白行を表します。
    BLANK                   = 0x000001
    #: コメント行を表します。開始行が\\マークで始まる行を表します。
    SILENTCOMMENT           = 0x000002

    #: コマンド行を表します。*マークや%、?などの開始行が含まれます。（BeginGroup、EndGroupも対象となります。\\マークのSILENTCOMMENTは含まれません。）
    COMMAND                 = 0x004000
    COMMAND_BASHEDPATCH     = 0x004010 # %
    COMMAND_COMMENT         = 0x004020 # ?
    COMMAND_FCOM            = 0x004040 # *
    COMMAND_REQUIREMENT     = 0x004080 # :
    COMMAND_INCOMPATIBILITY = 0x004100 # "
    COMMAND_OOO             = 0x004200 # $
    COMMAND_BETTERCITIES    = 0x004400 # ^

    #: グループの開始行を表します。
    BEGINGROUP              = 0x006100
    #: グループの終了行を表します。
    ENDGROUP                = 0x006200

    #: MODファイル名指定を表します。（ESM、ESPファイル名）
    MODS                    = 0x008000
    MODS_ESM                = 0x008010 # esm
    MODS_ESP                = 0x008020 # esp

    # FCOMインストール条件
    FCOM_ISINSTALLED        = 0x110000 # >
    FCOM_ISNOTINSTALLED     = 0x120000 # <
    __slots__ = []

    @staticmethod
    def ToString(linetype):
        """
            :param linetype: ビットフィールドの合計値
            :rtype: 文字列
            :return: ビットフィールドの合計値から文字列を生成して返却します。区切り記号に「|」が使われます。
        """
        ret = u""
        sepa = u""
        if linetype == EnumLineType.OTHER:
            ret = u"OTHER"
        else:
            # あんまり細かい表示はしない。
            if (linetype & EnumLineType.BLANK) == EnumLineType.BLANK:
                ret += sepa + u"BLANK"
                sepa = u"|"
            if (linetype & EnumLineType.SILENTCOMMENT) == EnumLineType.SILENTCOMMENT:
                ret += sepa + u"SILENTCOMMENT"
                sepa = u"|"
            if (linetype & EnumLineType.COMMAND) == EnumLineType.COMMAND:
                ret += sepa + u"COMMAND"
                sepa = u"|"
            if (linetype & EnumLineType.BEGINGROUP) == EnumLineType.BEGINGROUP:
                ret += sepa + u"BEGINGROUP"
                sepa = u"|"
            if (linetype & EnumLineType.ENDGROUP) == EnumLineType.ENDGROUP:
                ret += sepa + u"ENDGROUP"
                sepa = u"|"
            if (linetype & EnumLineType.MODS) == EnumLineType.MODS:
                ret += sepa + u"MODS"
                sepa = u"|"
        return ret

# ------------------------------------------------------------------------------
# EnumAttributeType
# ------------------------------------------------------------------------------
class EnumAttributeType(object):
    """
        \ :class:`Group`\ クラス及び\ :class:`Block`\ クラスの属性タイプを表現します。（列挙体ビットフィールド表現クラス）
    """
    #: 空白行のみで構成された範囲であることを表します。
    BLANKONLY   = 0x0000
    #: 空白行又はコマンド行のみで構成された範囲であることを表します。
    COMMANDONLY = 0x0001
    #: ESM、ESPを含む行で構成された範囲であることを表します。
    EXISTMODS   = 0x0002
    __slots__ = []

# ------------------------------------------------------------------------------
# Group
# ------------------------------------------------------------------------------
class Group(LinkedTreeObject):
    """
       グループオブジェクトクラス
        このクラスは、BeginGroupからEndGroupまでのグループを表現します。
        グループの子要素にはグループ及びブロックを内包できるものとします。
    """
    def __init__(self, name = u"", childs = None, createdefault = True):
        """
            :param string name: このグループの名前
            :param LinkedTreeObject[] childs: 子要素に追加するLinkedTreeObjectのリスト
            :param bool createdefault: このグループにBeginGroupとEndGroupの定義行を生成して追加します。
             デフォルトはTrueです。通常はこのパラメータを変更する必要はありません。
        """
        LinkedTreeObject.__init__(self)
        #: このグループの名前を表します。（\ :meth:`LinkedTreeObject.LinkedTreeObject.Data`\ に保管します。）
        self.GroupName = name

        if childs != None:
            if not (isinstance(childs, list)):
                raise TypeError, "expected type is list."
            for child in childs:
                self.AddChild(child)

        # childs指定でBeginGroupとEndGroupが挿入されている場合を考慮し、childsを入れてから処理を行う。
        if createdefault:
            # BeginGroupのチェック
            beginfindflg = False
            findchild = self.GetTopChild()
            while findchild is not None:
                if isinstance(findchild, Group):
                    findchild = None
                elif isinstance(findchild, Block):
                    beginline = findchild.FindDataFunc(u"LineType", lambda v: ((v & EnumLineType.BEGINGROUP) == EnumLineType.BEGINGROUP))
                    if beginline != None:
                        if beginline.BeginGroupName != self.GroupName:
                            # 存在するが、グループ名が異なる場合は、入れ替える。
                            newbeginline = Line(ur"\BeginGroup\: %s" % (self.GroupName))
                            targetblock = beginline.Parent()
                            targetblock.ReplaceChild(beginline, newbeginline)
                        beginfindflg = True
                        break
                    else:
                        findchild = findchild.Next()

            if not beginfindflg:
                biginblock = Block([Line(ur"\BeginGroup\: %s" % (self.GroupName))])
                if self.ChildCount() != 0:
                    self.InsertChildBefore(self.GetTopChild(), biginblock)
                else:
                    self.AddChild(biginblock)

            # EndGroupのチェック
            endfindflg = False
            findchild = self.GetBottomChild()
            while findchild is not None:
                if isinstance(findchild, Group):
                    findchild = None
                elif isinstance(findchild, Block):
                    endline = findchild.FindDataFunc(u"LineType", lambda v: ((v & EnumLineType.ENDGROUP) == EnumLineType.ENDGROUP))
                    if endline != None:
                        endfindflg = True
                        break
                    else:
                        findchild = findchild.Previous()

            if not endfindflg:
                endblock = Block([Line(ur"\EndGroup\\")])
                self.AddChild(endblock)

    def __str__(self):
        ret = u"%s" % (self.GroupName)
        return ret

    def _onAppendChild(self, leaf):
        if not (isinstance(leaf, Group) or isinstance(leaf, Block)):
            raise TypeError, "This object can not be added. expected Group or Block."
        return self

    def MasterlistOutput(self):
        """
            :rtype: string
            :return: Masterlist形式でこのオブジェクトと全ての子要素を出力します。
        """
        return u"".join([u"%s" % (child.MasterlistOutput()) for child in self.EachChilds()])

    def GetAttribute(self):
        """
            このオブジェクトの属性を返却します。
            グループオブジェクトは、子要素にかかわらず、常にEnumAttributeType.EXISTMODSを返却します。

            :rtype: EnumAttributeType
            :return: 子要素を含めたこのオブジェクトの属性を返却します。
        """
        ret = EnumAttributeType.EXISTMODS
        return ret

    def _getWasteBlock(self):
        """
            このオブジェクトの子要素から全ての不要なブロックを返却します。
            不要なブロックの決定ルールは\ :meth:`Block._getWasteBlock`\ を参照してください。

            :rtype: LinkedTreeObject[]
            :return: 不要なブロックをリストに列挙して返却します。
        """
        ret = []
        for child in self.EachChilds():
            ret += child._getWasteBlock()
        return ret

    def _getTopBaseChild(self):
        """
            このグループの子要素から ESM、ESPが存在するできるだけ **先頭** のブロックを返却します。
            グループの子要素にESM、ESPが存在しない場合は、空のブロックを追加し、そのブロックを返却する場合があります。
            （これは基準となるブロックを返却し、前後にブロックを挿入できるように考慮したものです。
            そのため、グループの先頭と末尾にはBeginGroup及びEndGroupのコマンド行が存在していることを想定しています）

            :rtype: LinkedTreeObject（\ :class:`Block`\ オブジェクト、又は、\ :class:`Group`\ オブジェクト）
            :return: 該当するLinkedTreeObject
        """
        ret = None
        topchild = self.GetTopChild()
        for child in topchild.EachNext():
            attribute = child.GetAttribute()
            if attribute == EnumAttributeType.EXISTMODS:
                ret = child
                break
        else:
            if self.ChildCount() <= 2:
                ret = Block() # dummy block
                self.InsertChildAfter(topchild, ret)
            else:
                ret = topchild.Next()
        return ret

    def _getBottomBaseChild(self):
        """
            このグループの子要素から ESM、ESPが存在するできるだけ **末尾** のブロックを返却します。
            グループの子要素にESM、ESPが存在しない場合は、空のブロックを追加し、そのブロックを返却する場合があります。
            （これは基準となるブロックを返却し、前後にブロックを挿入できるように考慮したものです。
            そのため、グループの先頭と末尾にはBeginGroup及びEndGroupのコマンド行が存在していることを想定しています）

            :rtype: LinkedTreeObject（\ :class:`Block`\ オブジェクト、又は、\ :class:`Group`\ オブジェクト）
            :return: 該当するLinkedTreeObject
        """
        ret = None
        bottomchild = self.GetBottomChild()
        for child in bottomchild.EachPrevious():
            attribute = child.GetAttribute()
            if attribute == EnumAttributeType.EXISTMODS:
                ret = child
                break
        else:
            if self.ChildCount() <= 2:
                ret = Block() # dummy block
                self.InsertChildBefore(bottomchild, ret)
            else:
                ret = bottomchild.Previous()
        return ret

    def AddChildToTop(self, leaf):
        """
            このオブジェクトの子要素に *leaf* で指定したLinkedTreeObjectを追加します。
            追加する要素は常に先頭（ **BeginGroup行の直後** ）に付け加えられます。このメソッドは「グループにMODs又はグループを追加する」場合に使用します。

            「グループにMODsを追加する」ことと、「グループオブジェクトに子要素を追加する」ことは別の意味です。
            通常の\ :meth:`LinkedTreeObject.LinkedTreeObject.AddChild`\ を使って子要素を追加することは、「グループオブジェクトに子要素を追加する」ということでしかありません。
            そのため、通常のAddChildでの操作は、EndGroup行よりも後ろに子要素が追加されます。
            グループにMODsを追加する場合、この動作はグループに追加したことにはならず、見落としやすい不具合になる場合がありますので注意が必要です。

            このメソッドを使用すると、グループ内の行を検索し、BeginGroup行を見つけてから、挿入処理を行います。
            このとき、関連する要素の親子・兄弟のリンク状態、深さなどは、子要素を含めて再帰的に再設定されます。

            :param LinkedTreeObject leaf: 追加対象のLinkedTreeObject
        """
        self.InsertChildBefore(self._getTopBaseChild(), leaf)
        return self

    def AddChildToBottom(self, leaf):
        """
            このオブジェクトの子要素に *leaf* で指定したLinkedTreeObjectを追加します。
            追加する要素は常に末尾（ **EndGroup行の直前** ）に付け加えられます。このメソッドは「グループにMODs又はグループを追加する」場合に使用します。

            「グループにMODsを追加する」ことと、「グループオブジェクトに子要素を追加する」ことは別の意味です。
            通常の\ :meth:`LinkedTreeObject.LinkedTreeObject.AddChild`\ を使って子要素を追加することは、「グループオブジェクトに子要素を追加する」ということでしかありません。
            そのため、通常のAddChildでの操作は、EndGroup行よりも後ろに子要素が追加されます。
            グループにMODsを追加する場合、この動作はグループに追加したことにはならず、見落としやすい不具合になる場合がありますので注意が必要です。

            このメソッドを使用すると、グループ内の行を検索し、EndGroup行を見つけてから、挿入処理を行います。
            このとき、関連する要素の親子・兄弟のリンク状態、深さなどは、子要素を含めて再帰的に再設定されます。

            :param LinkedTreeObject leaf: 追加対象のLinkedTreeObject
        """
        self.InsertChildAfter(self._getBottomBaseChild(), leaf)
        return self

# ------------------------------------------------------------------------------
# Block
# ------------------------------------------------------------------------------
class Block(LinkedTreeObject):
    """
       ブロックオブジェクトクラス
        このクラスは、ESM、ESPから始まる複数行をひとまとめにしたものをブロックとして表現します。
        また、ESM、ESPファイル名、BeginGroup及びEndGroupでブロックを切り替えます。
        マスタリスト内を編集する際の *最小単位* となります。
        ブロックの子要素には行オブジェクトのみ内包できるものとします。
    """
    def __init__(self, childs = None):
        """
            :param LinkedTreeObject[] childs: 子要素に追加するLinkedTreeObjectのリスト
        """
        LinkedTreeObject.__init__(self)

        if childs != None:
            if not (isinstance(childs, list)):
                raise TypeError, "expected type is list."
            for child in childs:
                self.AddChild(child)

    def __str__(self):
        ret = u""
        return ret

    def _onAppendChild(self, leaf):
        if not (isinstance(leaf, Line)):
            raise TypeError, "This object can not be added. expected type is Line."

        if self.GetAttribute() == EnumAttributeType.EXISTMODS:
            if leaf.GetAttribute() == EnumAttributeType.EXISTMODS:
                raise ValueError, "This object can not be added. In the block, ESM and ESP can exist only one."
        return self

    def MasterlistOutput(self):
        """
            :rtype: string
            :return: Masterlist形式でこのオブジェクトと全ての子要素を出力します。
        """
        return u"".join([u"%s" % (child.MasterlistOutput()) for child in self.EachChilds()])

    def GetAttribute(self):
        """
            このオブジェクトの属性を返却します。
            ブロックオブジェクトは、子要素\ :class:`Line`\ クラスのオブジェクトを検査し、このオブジェクトの属性を決定します。
            属性決定のルールは\ :meth:`Line.GetAttribute`\ を参照してください。

            :rtype: EnumAttributeType
            :return: 子要素を含めたこのオブジェクトの属性を返却します。
        """
        ret = EnumAttributeType.BLANKONLY
        for child in self.EachChilds():
            attribute = child.GetAttribute()
            if attribute == EnumAttributeType.COMMANDONLY:
                ret = EnumAttributeType.COMMANDONLY
            elif attribute == EnumAttributeType.EXISTMODS:
                #commit
                ret = EnumAttributeType.EXISTMODS
                break
        return ret

    def GetLine(self, linetype):
        """
            このブロックに *linetype* で指定したEnumLineTypeの行オブジェクトが存在するか検索し、結果を返却します。

            :rtype: LineまたはNone
            :return: 最初に一致したLineを返却します。該当するLineを発見できなかった場合はNoneを返却します。
        """
        return self.FindDataFunc(u"LineType", lambda v: ((v & linetype) == linetype))

    def GetLineAll(self, linetype):
        """
            このブロックに *linetype* で指定したEnumLineTypeの行オブジェクトが存在するか **全て** 検索し、結果を返却します。

            :rtype: Lineのリスト
            :return: 一致した全てのLineをリストに列挙して返却します。
             該当するLineを発見できなかった場合は空のリストを返却します。
        """
        return self.FindDataAllFunc(u"LineType", lambda v: ((v & linetype) == linetype))

    def _getWasteBlock(self):
        """
            このオブジェクト、及び、全ての子要素から不要なブロックを返却します。
            ブロックに子要素が存在しない場合は、不要なブロックとして判断します。

            :rtype: LinkedTreeObject[]
            :return: 不要なブロックをリストに列挙して返却します。
        """
        ret = []
        if self.ChildCount() == 0:
            ret += [self]
        else:
            for child in self.EachChilds():
                if not isinstance(child, Line):
                    ret += child._getWasteBlock()
        return ret


# ------------------------------------------------------------------------------
# Line
# ------------------------------------------------------------------------------
class Line(LinkedTreeObject):
    """
       行オブジェクトクラス
        このクラスは、マスタリスト内の１行を１つの行オブジェクトとして表現します。
        行オブジェクトに子要素を持つことはできません。
    """
    def __init__(self, linestring, correction = False):
        """
            :param string linestring: この行オブジェクトに格納する文字列
            :param bool correction: *linestring* で指定した文字列に補正処理を行うか指定します。デフォルトはFalseです。
        """
        LinkedTreeObject.__init__(self)
        # --------------------------------------------------
        # マスタリスト行の補正処理
        # --------------------------------------------------
        # 改行、空白の削除
        linestring = linestring.rstrip("\r\n").lstrip().rstrip()

        # 正規表現チェック
        match = [regexBeginGroup.search(linestring)
                ,regexEndGroup.search(linestring)
                ,regexMods.search(linestring)
                ,regexCommand.search(linestring)]

        if correction:
            if match == [None, None, None, None]:
                # 基本的に上記４つの正規表現のどれかに必ずヒットするはずだが、
                # 想定外の行文字列が存在している場合がある。（マスタリストのミスと思われる）
                # そこで、直せそうな行はそれっぽく修正する。修正内容があっているかどうかは不明。
                matchEx = [regexExBash.search(linestring)
                        ,regexExComment.search(linestring)
                        ,regexExMods1.search(linestring)]
                if matchEx[0] is not None:
                    # Bashタグを書いたが、先頭の％を書き忘れちゃった感で一杯の行
                    # 先頭に％を付け足す。
                    linestring = u"%% %s" % (matchEx[0].group(1))
                    # 正規表現結果書き換え
                    match[3] = regexCommand.search(linestring)
                elif matchEx[1] is not None:
                    # コメントを書いたが、「＼バックスラッシュ」と「／スラッシュ」を間違えた感で一杯の行
                    # ￥マークに書き換える。（英語圏では￥マークは＼バックスラッシュに置き換えられる）
                    linestring = u"\\ %s" % (matchEx[1].group(1))
                    # 正規表現結果書き換え
                    match[3] = regexCommand.search(linestring)
                elif matchEx[2] is not None:
                    # 拡張子を書き忘れた感で一杯の行
                    # espとみなす。（少なくともピリオドがない行はESPファイルと思われる。）
                    # 今のところesmではミスなさそう。
                    linestring = u"%s.esp" % (matchEx[2].group(1))
                    # 正規表現結果書き換え
                    match[2] = regexMods.search(linestring)

        # --------------------------------------------------
        # LineTypeの設定
        # --------------------------------------------------
        flaglists = {
                u">"   : EnumLineType.FCOM_ISINSTALLED,
                u"<"   : EnumLineType.FCOM_ISNOTINSTALLED,

                u"%"   : EnumLineType.COMMAND_BASHEDPATCH,
                u"?"   : EnumLineType.COMMAND_COMMENT,
                u"*"   : EnumLineType.COMMAND_FCOM,
                u":"   : EnumLineType.COMMAND_REQUIREMENT,
                u"\""  : EnumLineType.COMMAND_INCOMPATIBILITY,
                u"$"   : EnumLineType.COMMAND_OOO,
                u"^"   : EnumLineType.COMMAND_BETTERCITIES,

                u"ESM" : EnumLineType.MODS_ESM,
                u"ESP" : EnumLineType.MODS_ESP,
            }

        linetype = EnumLineType.OTHER
        begingroupname = None
        if len(linestring) == 0:
            # カラ行はBLANK設定
            linetype |= EnumLineType.BLANK

        if match[0] is not None:
            linetype |= EnumLineType.BEGINGROUP
            #: この行がBEGINGROUPの指定だった場合、グループ名を表します。（\ :meth:`LinkedTreeObject.LinkedTreeObject.Data`\ に保管します。）
            self.BeginGroupName = u"%s" % (match[0].group(1).lstrip().rstrip())

        if match[1] is not None:
            linetype |= EnumLineType.ENDGROUP

        if match[2] is not None:
            fcom_command   = u"%s" % (match[2].group(1).lstrip().rstrip())
            modsname       = u"%s" % (match[2].group(2).lstrip().rstrip())
            modstype       = u"%s" % (match[2].group(3).lstrip().rstrip().upper())

            if fcom_command in flaglists:
                linetype |= flaglists[fcom_command]

            if modstype in flaglists:
                linetype |= flaglists[modstype]

            linetype |= EnumLineType.MODS

        if match[3] is not None:
            fcom_command   = u"%s" % (match[3].group(1).lstrip().rstrip())
            commandtype    = u"%s" % (match[3].group(2).lstrip().rstrip())
            commandmessage = u"%s" % (match[3].group(4).lstrip().rstrip())

            if fcom_command in flaglists:
                linetype |= flaglists[fcom_command]

            if commandtype in flaglists:
                linetype |= flaglists[commandtype]

            if commandtype == u"\\":
                linetype |= EnumLineType.SILENTCOMMENT
            else:
                linetype |= EnumLineType.COMMAND

        #: この行の定義文字列を表します。（\ :meth:`LinkedTreeObject.LinkedTreeObject.Data`\ に保管します。）
        self.LineString = linestring
        #: この行の行格納タイプを表します。（\ :meth:`LinkedTreeObject.LinkedTreeObject.Data`\ に保管します。）
        self.LineType = linetype

    def __str__(self):
        ret = u"(%s)%s" % (EnumLineType.ToString(self.LineType), self.LineString)
        return ret

    def _onAppendChild(self, leaf):
        raise SyntaxError, "This object can not be added."

    def _onRemoveChild(self, leaf):
        raise SyntaxError, "This object can not be deleted."

    def MasterlistOutput(self):
        """
            :rtype: string
            :return: Masterlist形式でこのオブジェクトと全ての子要素を出力します。
        """
        return u"%s\r\n" % (self.LineString)

    def GetAttribute(self):
        """
            このオブジェクトの属性を返却します。
            行オブジェクトは、オブジェクト生成時の\ :data:`LineType`\ によって、このオブジェクトの属性を決定します。
            この行にESM、ESPファイルの定義が含まれる場合はEnumAttributeType.EXISTMODSを返却します。
            ESM、ESPファイルを含まず、コマンド行が含まれる場合は、EnumAttributeType.COMMANDONLYを返却します。
            それ以外の場合は、EnumAttributeType.BLANKONLYを返却します。

            :rtype: EnumAttributeType
            :return: 子要素を含めたこのオブジェクトの属性を返却します。
        """
        ret = EnumAttributeType.BLANKONLY
        if self.IsType(EnumLineType.COMMAND):
            ret = EnumAttributeType.COMMANDONLY # COMMAND => COMMANDONLY
        elif self.IsType(EnumLineType.MODS):
            ret = EnumAttributeType.EXISTMODS   # MODS    => EXISTMODS
        return ret

    def IsType(self, linetype):
        """
            このオブジェクトの行格納タイプに指定したタイプが含まれるか判断します。

            :param EnumLineType linetype: 比較するEnumLineTypeの値

            :rtype: bool
            :return: このオブジェクトのタイプが指定したタイプと一致する場合は真を返す。一致しない場合は偽を返す。
        """
        ret = False
        if linetype == EnumLineType.OTHER:
            ret = (self.LineType == EnumLineType.OTHER)
        else:
            ret = ((self.LineType & linetype) == linetype)
        return ret

    def GetParentGroup(self):
        """
            このオブジェクトの親を辿り、最初に見つかったグループオブジェクトを返却します。

            :rtype: LinkedTreeObject（\ :class:`Group`\ オブジェクト）
            :return: この行オブジェクトが所属するグループオブジェクト
        """
        ret = None
        for parent in self.EachParent():
            if isinstance(parent, Group):
                ret = parent
                break
        return ret

    def AddChild(self, leaf):
        """ .. warning:: 行オブジェクトでは、このメソッドを利用できません。呼び出すと例外が発生します。 """
        raise SyntaxError, "This method is not available."

    def DeleteChild(self, leaf):
        """ .. warning:: 行オブジェクトでは、このメソッドを利用できません。呼び出すと例外が発生します。 """
        raise SyntaxError, "This method is not available."

    def InsertChild(self, index, leaf):
        """ .. warning:: 行オブジェクトでは、このメソッドを利用できません。呼び出すと例外が発生します。 """
        raise SyntaxError, "This method is not available."

    def InsertChildBefore(self, baseleaf, leaf):
        """ .. warning:: 行オブジェクトでは、このメソッドを利用できません。呼び出すと例外が発生します。 """
        raise SyntaxError, "This method is not available."

    def InsertChildAfter(self, baseleaf, leaf):
        """ .. warning:: 行オブジェクトでは、このメソッドを利用できません。呼び出すと例外が発生します。 """
        raise SyntaxError, "This method is not available."

    def Child(self, index):
        """ .. warning:: 行オブジェクトでは、このメソッドを利用できません。呼び出すと例外が発生します。 """
        raise SyntaxError, "This method is not available."

    def GetChildIndex(self, leaf):
        """ .. warning:: 行オブジェクトでは、このメソッドを利用できません。呼び出すと例外が発生します。 """
        raise SyntaxError, "This method is not available."

    def GetTopChild(self):
        """ .. warning:: 行オブジェクトでは、このメソッドを利用できません。呼び出すと例外が発生します。 """
        raise SyntaxError, "This method is not available."

    def GetBottomChild(self):
        """ .. warning:: 行オブジェクトでは、このメソッドを利用できません。呼び出すと例外が発生します。 """
        raise SyntaxError, "This method is not available."


# ------------------------------------------------------------------------------
# Masterlist
# ------------------------------------------------------------------------------
class Masterlist(Group):
    """
       マスタリストオブジェクトクラス
        このクラスは、マスタリストを表現します。
        マスタリストのテキストファイルから行を読み込み、その解析を行います。
    """
    def __init__(self, fullpathfilename = u""):
        """
            :param string fullpathfilename: 読み込むマスタリストのフルパスファイル名
        """
        Group.__init__(self, None, None, False)

        self._fullpathfilename = fullpathfilename.lstrip().rstrip()
        self._encoding = "utf-8-sig"
        self._recording = False
        self._archiverecord = []

        if len(self._fullpathfilename) != 0:
            self.Load(self._fullpathfilename)

    def __str__(self):
        ret = u"Masterlist"
        if len(self._fullpathfilename) != 0:
            ret = u"Masterlist:(%s)" % (self._fullpathfilename)
        return ret

    def _onAppendChild(self, leaf):
        if not (isinstance(leaf, Group) or isinstance(leaf, Block)):
            raise TypeError, "This object can not be added. expected Group or Block."
        return self

    @property
    def FullPathFileName(self):
        """
            :rtype: string
            :return: このマスタリストオブジェクトに登録されたマスタリストファイル名を返却します。
        """
        return self._fullpathfilename

    @property
    def Encoding(self):
        """
            :rtype: string
            :return: このマスタリストに登録されたエンコーディング文字列を返却します。これは \ :meth:`Load`\ 及び \ :meth:`Save`\ メソッドで最後に指定したエンコーディングを返却します。
        """
        return self._encoding

    def AddChildToTop(self, leaf):
        """ .. warning:: マスタリストオブジェクトでは、このメソッドを利用できません。呼び出すと例外が発生します。 """
        raise SyntaxError, "This method is not available."

    def AddChildToBottom(self, leaf):
        """ .. warning:: マスタリストオブジェクトでは、このメソッドを利用できません。呼び出すと例外が発生します。 """
        raise SyntaxError, "This method is not available."

    def IsGroupName(self, name):
        """
            このマスタリストに *name* で指定した名前のグループが存在するか検索し、結果を返却します。

            :param string name: 検索対象のグループ名
            :rtype: bool
            :return: グループが存在する場合は真を返却します。存在しない場合は偽を返却します。
        """
        ret = False
        if self.FindData(u"GroupName", name) != None:
            ret = True
        return ret

    def IsLineName(self, linestring):
        """
            このマスタリストに *linestring* で指定した文字列と一致する行が存在するか検索し、結果を返却します。

            :param string linestring: 検索対象の文字列
            :rtype: bool
            :return: 文字列が存在する場合は真を返却します。存在しない場合は偽を返却します。
        """
        ret = False
        if self.FindData(u"LineString", linestring) != None:
            ret = True
        return ret

    def _findNameOfGroup(self, name):
        """
            グループ名を再帰的に最上位グループから検索します。
            見つからなかった場合は、Noneを返却します。
        """
        return self.FindData(u"GroupName", name)

    def _findNameOfLine(self, name):
        """
            行文字列を再帰的に最上位グループから検索します。
            見つからなかった場合は、Noneを返却します。
        """
        return self.FindData(u"LineString", name)

    def _findNameOfTarget(self, name):
        """
            名称を最上位グループから検索します。グループ名に存在した場合はグループを返却します。
            グループに存在しなかった場合は行文字列を検索します。
            行文字列にも見つからなかった場合は、Noneを返却します。
        """
        ret = None
        if (isinstance(name, str)) or (isinstance(name, unicode)):
            group = self._findNameOfGroup(name)
            if group != None:
                ret = group
            else:
                line = self._findNameOfLine(name)
                if line != None:
                    ret = line.Parent()
        return ret

    def _findTargetOfName(self, target):
        """
            渡されたオブジェクトの文字列を返却します。
            *target* に渡されたオブジェクトによって動作を切り替えます。
            行オブジェクト、ブロックの場合は、MODsの行を取得し名称を返却します。グループの場合は、グループ名を返却します。
            該当する文字列が存在しない場合は、空の文字列を返却します。
        """
        ret = u""
        if (isinstance(target, str)) or (isinstance(target, unicode)):
            ret = u"%s" % (target)
        elif isinstance(target, Line):
            ret = u"%s" % (target.LineString)
        elif isinstance(target, Block):
            findmod = target.GetLine(EnumLineType.MODS)
            ret = u"%s" % (findmod.LineString)
        elif isinstance(target, Group):
            ret = u"%s" % (target.GroupName)
        return ret

    def _createOfTarget(self, target):
        """
            渡されたオブジェクトから行オブジェクトを生成して返却します。
            *target* に渡されたオブジェクトによって動作を切り替えます。
            行オブジェクトの場合は、MODsの行をブロックに格納して返却します。ブロック、グループの場合は、そのまま返却します。
            文字列の場合は、文字列を判定し、MODs名らしい名前の場合は行文字列として扱います。それ以外の場合はグループ名として扱います。
        """
        ret = None
        if (isinstance(target, str)) or (isinstance(target, unicode)):
            match = regexMods.search(target)
            if match is not None:
                # 行文字列と判断する。
                ret = Block([Line(target)])
            else:
                # グループ名と判断する。
                ret = Group(target)
        elif isinstance(target, Line):
            ret = Block([target])
        elif isinstance(target, Block):
            ret = target
        elif isinstance(target, Group):
            ret = target
        return ret

    def _cushionGroup(self, target):
        """
            渡されたオブジェクトの親グループを返却します。
            *target* に渡されたオブジェクトによって動作を切り替えます。
            渡されたオブジェクトがグループの場合は、そのまま返却します。
        """
        ret = None
        if isinstance(target, Line):
            ret = target.GetParentGroup()
        elif isinstance(target, Block):
            ret = target.Parent()
        elif isinstance(target, Group):
            ret = target
        return ret

    def _replaceSwitchingOfTarget(self, target):
        """
            渡されたオブジェクトを元に、MoveすべきかInsertすべきか判定し、対象となるオブジェクトを返却します。
            内部でself._findNameOfTarget及びself._createOfTargetを呼び出します。
            *target* に渡されたオブジェクトによって動作を切り替えます。
        """
        move = True
        targetobject = None
        targetname = self._findTargetOfName(target)
        if len(targetname) != 0:
            targetobject = self._findNameOfTarget(targetname)
            if targetobject == None:
                # 存在しなければ、Insertと判断しオブジェクトの生成を行う。
                targetobject = self._createOfTarget(target)
                move = False
        return (move, targetobject)


    def _moveBefore(self, param1, param1target, param2, param2target):
        """
            MoveBeforeの処理を行います。
        """
        param1target.Parent().DeleteChild(param1target)
        param2target.Parent().InsertChildBefore(param2target, param1target)
        self._onOperationRecord(u"MoveBefore", param1, param1target, param2, param2target)
        return self

    def _moveAfter(self, param1, param1target, param2, param2target):
        """
            MoveAfterの処理を行います。
        """
        param1target.Parent().DeleteChild(param1target)
        param2target.Parent().InsertChildAfter(param2target, param1target)
        self._onOperationRecord(u"MoveAfter", param1, param1target, param2, param2target)
        return self

    def _moveTop(self, param1, param1target, param2, param2target):
        """
            MoveTopの処理を行います。
        """
        param1target.Parent().DeleteChild(param1target)
        self._cushionGroup(param2target).InsertChildBefore(self._cushionGroup(param2target)._getTopBaseChild(), param1target)
        self._onOperationRecord(u"MoveTop", param1, param1target, param2, param2target)
        return self

    def _moveBottom(self, param1, param1target, param2, param2target):
        """
            MoveBottomの処理を行います。
        """
        param1target.Parent().DeleteChild(param1target)
        self._cushionGroup(param2target).InsertChildAfter(self._cushionGroup(param2target)._getBottomBaseChild(), param1target)
        self._onOperationRecord(u"MoveBottom", param1, param1target, param2, param2target)
        return self

    def _insertBefore(self, param1, param1target, param2, param2target):
        """
            InsertBeforeの処理を行います。
        """
        param2target.Parent().InsertChildBefore(param2target, param1target)
        self._onOperationRecord(u"InsertBefore", param1, param1target, param2, param2target)
        return self

    def _insertAfter(self, param1, param1target, param2, param2target):
        """
            InsertAfterの処理を行います。
        """
        param2target.Parent().InsertChildAfter(param2target, param1target)
        self._onOperationRecord(u"InsertAfter", param1, param1target, param2, param2target)
        return self

    def _insertTop(self, param1, param1target, param2, param2target):
        """
            InsertTopの処理を行います。
        """
        self._cushionGroup(param2target).InsertChildBefore(self._cushionGroup(param2target)._getTopBaseChild(), param1target)
        self._onOperationRecord(u"InsertTop", param1, param1target, param2, param2target)
        return self

    def _insertBottom(self, param1, param1target, param2, param2target):
        """
            InsertBottomの処理を行います。
        """
        self._cushionGroup(param2target).InsertChildAfter(self._cushionGroup(param2target)._getBottomBaseChild(), param1target)
        self._onOperationRecord(u"InsertBottom", param1, param1target, param2, param2target)
        return self

    def _appendLine(self, param1, param1target, param2, param2target):
        """
            AppendLineの処理を行います。
        """
        param2target.AddChild(param1target)
        self._onOperationRecord(u"AppendLine", param1, param1target, param2, param2target)
        return self

    def _replaceLine(self, param1, param1target, param2, param2target):
        """
            ReplaceLineの処理を行います。
        """
        deleteblock = []
        for line in param2target.EachChilds():
            if not line.IsType(EnumLineType.MODS):
                deleteblock += [line]
        for line in deleteblock:
            param2target.DeleteChild(line)
        param2target.AddChild(param1target)
        self._onOperationRecord(u"ReplaceLine", param1, param1target, param2, param2target)
        return self


    def MoveBefore(self, srcname, basename):
        """
            *srcname* で指定した名称のオブジェクトを、 *basename* で指定した名称のオブジェクトの **前** に移動します。
            これは、ユーザーリストの「OVERRIDE - BEFORE」の操作に該当します。

            :param string srcname: 移動対象の名称
            :param string basename: 移動先のソート基準の名称
        """
        srctarget = self._findNameOfTarget(srcname)
        if srctarget == None:
            raise KeyError, "The specified name is not found: %s" % (srcname)
        basetarget = self._findNameOfTarget(basename)
        if basetarget == None:
            raise KeyError, "The specified name is not found: %s" % (basename)
        self._moveBefore(srcname, srctarget, basename, basetarget)
        return self

    def MoveAfter(self, srcname, basename):
        """
            *srcname* で指定した名称のオブジェクトを、 *basename* で指定した名称のオブジェクトの **後** に移動します。
            これは、ユーザーリストの「OVERRIDE - AFTER」の操作に該当します。

            :param string srcname: 移動対象の名称
            :param string basename: 移動先のソート基準の名称
        """
        srctarget = self._findNameOfTarget(srcname)
        if srctarget == None:
            raise KeyError, "The specified name is not found: %s" % (srcname)
        basetarget = self._findNameOfTarget(basename)
        if basetarget == None:
            raise KeyError, "The specified name is not found: %s" % (basename)
        self._moveAfter(srcname, srctarget, basename, basetarget)
        return self

    def MoveTop(self, srcname, basename):
        """
            *srcname* で指定した名称のオブジェクトを、 *basename* で指定した名称のオブジェクトの **グループ先頭** に移動します。
            これは、ユーザーリストの「OVERRIDE - TOP」の操作に該当します。

            :param string srcname: 移動対象の名称
            :param string basename: 移動先のソート基準の名称
        """
        srctarget = self._findNameOfTarget(srcname)
        if srctarget == None:
            raise KeyError, "The specified name is not found: %s" % (srcname)
        basetarget = self._findNameOfTarget(basename)
        if basetarget == None:
            raise KeyError, "The specified name is not found: %s" % (basename)
        self._moveTop(srcname, srctarget, basename, basetarget)
        return self

    def MoveBottom(self, srcname, basename):
        """
            *srcname* で指定した名称のオブジェクトを、 *basename* で指定した名称のオブジェクトの **グループ末尾** に移動します。
            これは、ユーザーリストの「OVERRIDE - BOTTOM」の操作に該当します。

            :param string srcname: 移動対象の名称
            :param string basename: 移動先のソート基準の名称
        """
        srctarget = self._findNameOfTarget(srcname)
        if srctarget == None:
            raise KeyError, "The specified name is not found: %s" % (srcname)
        basetarget = self._findNameOfTarget(basename)
        if basetarget == None:
            raise KeyError, "The specified name is not found: %s" % (basename)
        self._moveBottom(srcname, srctarget, basename, basetarget)
        return self

    def InsertBefore(self, newobject, basename):
        """
            *newobject* で指定したオブジェクトを、 *basename* で指定した名称のオブジェクトの **前** に移動します。
            これは、ユーザーリストの「ADD - BEFORE」の操作に該当します。
            *newobject* には名称またはグループ、ブロック、行オブジェクトを指定できます。
            名称を指定した場合、行文字列からMODsと判定できた場合はMODs、それ以外の場合はグループとして扱います。
            明示的にMODsかグループかを指定したい場合はオブジェクトを指定して下さい。

            :param (string,Group,Block,Line) newobject: 挿入対象の名称又はオブジェクト
            :param string basename: 移動先のソート基準の名称
        """
        srctarget = self._createOfTarget(newobject)
        if srctarget == None:
            raise TypeError, "expected str, unicode, Line, Block or Group."
        basetarget = self._findNameOfTarget(basename)
        if basetarget == None:
            raise KeyError, "The specified name is not found: %s" % (basename)
        self._insertBefore(newobject, srctarget, basename, basetarget)
        return self

    def InsertAfter(self, newobject, basename):
        """
            *newobject* で指定したオブジェクトを、 *basename* で指定した名称のオブジェクトの **後** に移動します。
            これは、ユーザーリストの「ADD - AFTER」の操作に該当します。
            *newobject* には名称またはグループ、ブロック、行オブジェクトを指定できます。
            名称を指定した場合、行文字列からMODsと判定できた場合はMODs、それ以外の場合はグループとして扱います。
            明示的にMODsかグループかを指定したい場合はオブジェクトを指定して下さい。

            :param (string,Group,Block,Line) newobject: 挿入対象の名称又はオブジェクト
            :param string basename: 移動先のソート基準の名称
        """
        srctarget = self._createOfTarget(newobject)
        if srctarget == None:
            raise TypeError, "expected str, unicode, Line, Block or Group."
        basetarget = self._findNameOfTarget(basename)
        if basetarget == None:
            raise KeyError, "The specified name is not found: %s" % (basename)
        self._insertAfter(newobject, srctarget, basename, basetarget)
        return self

    def InsertTop(self, newobject, basename):
        """
            *newobject* で指定したオブジェクトを、 *basename* で指定した名称のオブジェクトの **グループ先頭** に移動します。
            これは、ユーザーリストの「ADD - TOP」の操作に該当します。
            *newobject* には名称またはグループ、ブロック、行オブジェクトを指定できます。
            名称を指定した場合、行文字列からMODsと判定できた場合はMODs、それ以外の場合はグループとして扱います。
            明示的にMODsかグループかを指定したい場合はオブジェクトを指定して下さい。

            :param (string,Group,Block,Line) newobject: 挿入対象の名称又はオブジェクト
            :param string basename: 移動先のソート基準の名称
        """
        srctarget = self._createOfTarget(newobject)
        if srctarget == None:
            raise TypeError, "expected str, unicode, Line, Block or Group."
        basetarget = self._findNameOfTarget(basename)
        if basetarget == None:
            raise KeyError, "The specified name is not found: %s" % (basename)
        self._insertTop(newobject, srctarget, basename, basetarget)
        return self

    def InsertBottom(self, newobject, basename):
        """
            *newobject* で指定したオブジェクトを、 *basename* で指定した名称のオブジェクトの **グループ末尾** に移動します。
            これは、ユーザーリストの「ADD - BOTTOM」の操作に該当します。
            *newobject* には名称またはグループ、ブロック、行オブジェクトを指定できます。
            名称を指定した場合、行文字列からMODsと判定できた場合はMODs、それ以外の場合はグループとして扱います。
            明示的にMODsかグループかを指定したい場合はオブジェクトを指定して下さい。

            :param (string,Group,Block,Line) newobject: 挿入対象の名称又はオブジェクト
            :param string basename: 移動先のソート基準の名称
        """
        srctarget = self._createOfTarget(newobject)
        if srctarget == None:
            raise TypeError, "expected str, unicode, Line, Block or Group."
        basetarget = self._findNameOfTarget(basename)
        if basetarget == None:
            raise KeyError, "The specified name is not found: %s" % (basename)
        self._insertBottom(newobject, srctarget, basename, basetarget)
        return self

    def AppendLine(self, newlinestring, basename):
        """
            *newlinestring* で指定した行文字列を、 *basename* で指定した名称のオブジェクトにメッセージを **追加** します。
            これは、ユーザーリストの「FOR - APPEND」の操作に該当します。

            :param string newlinestring: 挿入対象の名称
            :param string basename: 移動先のソート基準の名称
        """
        basetarget = self._findNameOfTarget(basename)
        if basetarget == None:
            raise KeyError, "The specified name is not found: %s" % (basename)
        newline = Line(newlinestring)
        self._appendLine(newlinestring, newline, basename, basetarget)
        return self

    def ReplaceLine(self, newlinestring, basename):
        """
            *newlinestring* で指定した行文字列を、 *basename* で指定した名称のオブジェクトのメッセージを **置換** します。
            これは、ユーザーリストの「FOR - REPLACE」の操作に該当します。

            :param string newlinestring: 挿入対象の名称
            :param string basename: 移動先のソート基準の名称
        """
        basetarget = self._findNameOfTarget(basename)
        if basetarget == None:
            raise KeyError, "The specified name is not found: %s" % (basename)
        newline = Line(newlinestring)
        self._replaceLine(newlinestring, newline, basename, basetarget)
        return self


    def ReplaceBefore(self, newobjectorname, basename):
        """
            *newobjectorname* で指定したオブジェクトを、 *basename* で指定した名称のオブジェクトの **前** に **移動又は挿入** します。
            これは、既にマスタリストに *newobjectorname* で指定したオブジェクトが存在する場合は、
            ユーザーリストの「OVERRIDE - BEFORE」の操作を行い、存在しない場合は、「ADD - BEFORE」の操作を行います。
            *newobjectorname* には名称またはグループ、ブロック、行オブジェクトを指定できます。
            名称を指定した場合、行文字列からMODsと判定できた場合はMODs、それ以外の場合はグループとして扱います。
            明示的にMODsかグループかを指定したい場合はオブジェクトを指定して下さい。

            :param (string,Group,Block,Line) newobjectorname: 挿入対象の名称又はオブジェクト
            :param string basename: 移動先のソート基準の名称
        """
        (move, srctarget) = self._replaceSwitchingOfTarget(newobjectorname)
        if srctarget == None:
            raise KeyError, "Invalid target was supplied."
        basetarget = self._findNameOfTarget(basename)
        if basetarget == None:
            raise KeyError, "The specified name is not found: %s" % (basename)
        if move:
            self._moveBefore(newobjectorname, srctarget, basename, basetarget)
        else:
            self._insertBefore(newobjectorname, srctarget, basename, basetarget)
        return self

    def ReplaceAfter(self, newobjectorname, basename):
        """
            *newobjectorname* で指定したオブジェクトを、 *basename* で指定した名称のオブジェクトの **後** に **移動又は挿入** します。
            これは、既にマスタリストに *newobjectorname* で指定したオブジェクトが存在する場合は、
            ユーザーリストの「OVERRIDE - AFTER」の操作を行い、存在しない場合は、「ADD - AFTER」の操作を行います。
            *newobjectorname* には名称またはグループ、ブロック、行オブジェクトを指定できます。
            名称を指定した場合、行文字列からMODsと判定できた場合はMODs、それ以外の場合はグループとして扱います。
            明示的にMODsかグループかを指定したい場合はオブジェクトを指定して下さい。

            :param (string,Group,Block,Line) newobjectorname: 挿入対象の名称又はオブジェクト
            :param string basename: 移動先のソート基準の名称
        """
        (move, srctarget) = self._replaceSwitchingOfTarget(newobjectorname)
        if srctarget == None:
            raise KeyError, "Invalid target was supplied."
        basetarget = self._findNameOfTarget(basename)
        if basetarget == None:
            raise KeyError, "The specified name is not found: %s" % (basename)
        if move:
            self._moveAfter(newobjectorname, srctarget, basename, basetarget)
        else:
            self._insertAfter(newobjectorname, srctarget, basename, basetarget)
        return self

    def ReplaceTop(self, newobjectorname, basename):
        """
            *newobjectorname* で指定したオブジェクトを、 *basename* で指定した名称のオブジェクトの **グループ先頭** に **移動又は挿入** します。
            これは、既にマスタリストに *newobjectorname* で指定したオブジェクトが存在する場合は、
            ユーザーリストの「OVERRIDE - TOP」の操作を行い、存在しない場合は、「ADD - TOP」の操作を行います。
            *newobjectorname* には名称またはグループ、ブロック、行オブジェクトを指定できます。
            名称を指定した場合、行文字列からMODsと判定できた場合はMODs、それ以外の場合はグループとして扱います。
            明示的にMODsかグループかを指定したい場合はオブジェクトを指定して下さい。

            :param (string,Group,Block,Line) newobjectorname: 挿入対象の名称又はオブジェクト
            :param string basename: 移動先のソート基準の名称
        """
        (move, srctarget) = self._replaceSwitchingOfTarget(newobjectorname)
        if srctarget == None:
            raise KeyError, "Invalid target was supplied."
        basetarget = self._findNameOfTarget(basename)
        if basetarget == None:
            raise KeyError, "The specified name is not found: %s" % (basename)
        if move:
            self._moveTop(newobjectorname, srctarget, basename, basetarget)
        else:
            self._insertTop(newobjectorname, srctarget, basename, basetarget)
        return self

    def ReplaceBottom(self, newobjectorname, basename):
        """
            *newobjectorname* で指定したオブジェクトを、 *basename* で指定した名称のオブジェクトの **グループ末尾** に **移動又は挿入** します。
            これは、既にマスタリストに *newobjectorname* で指定したオブジェクトが存在する場合は、
            ユーザーリストの「OVERRIDE - BOTTOM」の操作を行い、存在しない場合は、「ADD - BOTTOM」の操作を行います。
            *newobjectorname* には名称またはグループ、ブロック、行オブジェクトを指定できます。
            名称を指定した場合、行文字列からMODsと判定できた場合はMODs、それ以外の場合はグループとして扱います。
            明示的にMODsかグループかを指定したい場合はオブジェクトを指定して下さい。

            :param (string,Group,Block,Line) newobjectorname: 挿入対象の名称又はオブジェクト
            :param string basename: 移動先のソート基準の名称
        """
        (move, srctarget) = self._replaceSwitchingOfTarget(newobjectorname)
        if srctarget == None:
            raise KeyError, "Invalid target was supplied."
        basetarget = self._findNameOfTarget(basename)
        if basetarget == None:
            raise KeyError, "The specified name is not found: %s" % (basename)
        if move:
            self._moveBottom(newobjectorname, srctarget, basename, basetarget)
        else:
            self._insertBottom(newobjectorname, srctarget, basename, basetarget)
        return self



    def _onOperationRecord(self, operationname, param1, param1target, param2, param2target):
        """
            マスタリストの操作を行った場合に、呼び出されます。
            これは、操作した内容を記録するために用意されています。

            :param string operationname: 操作の名称
            :param (string,Group,Block,Line) param1: 操作のパラメータ１（文字列及びオブジェクト）
            :param string param1target: パラメータ１のオブジェクト
            :param (string,Group,Block,Line) param2: 操作のパラメータ２（文字列及びオブジェクト）
            :param string param2target: パラメータ２のオブジェクト
        """
        if self._recording:
            # 記録中なら実行する。
            param1type = u""
            if isinstance(param1target, Line):
                param1type = u"MODs"
            elif isinstance(param1target, Block):
                param1type = u"MODs"
            elif isinstance(param1target, Group):
                param1type = u"Group"

            param2type = u""
            if isinstance(param2target, Line):
                param2type = u"MODs"
            elif isinstance(param2target, Block):
                param2type = u"MODs"
            elif isinstance(param2target, Group):
                param2type = u"Group"

            recordstring = u"%sFrom%sTo%s" % (operationname, param1type, param2type)
            param1string = self._findTargetOfName(param1)
            param2string = self._findTargetOfName(param2)

            self._archiverecord += [
                    {
                    u"Record" : recordstring,
                    u"Param1" : param1string,
                    u"Param2" : param2string
                    }
                ]
        return self

    def ClearRecord(self):
        """
            操作記録した内容を全て破棄します。
            詳しくは \ :meth:`BeginRecord`\  を参照して下さい。
        """
        self._archiverecord = []
        return self

    def BeginRecord(self):
        """
            操作記録を開始します。
            BeginRecordを呼び出した後に、マスタリストへの操作を行った場合、内部に操作記録を残します。
            この操作記録から、 \ :meth:`GenerateUserlistFromRecord`\ を使ってユーザーリスト定義を作ることができます。

            記録するマスタリストへの操作は、以下の操作が該当します。
            「 \ :meth:`MoveBefore`\ \ :meth:`MoveAfter`\ \ :meth:`MoveTop`\ \ :meth:`MoveBottom`\ 」
            「 \ :meth:`InsertBefore`\ \ :meth:`InsertAfter`\ \ :meth:`InsertTop`\ \ :meth:`InsertBottom`\ 」
            「 \ :meth:`AppendLine`\ \ :meth:`ReplaceLine`\ 」

            また、内部でInsertかMoveのどちらかに切り替えるReplace文も該当します。（実際に内部で実行した操作が記録されます。）
            「 \ :meth:`ReplaceBefore`\ \ :meth:`ReplaceAfter`\ \ :meth:`ReplaceTop`\ \ :meth:`ReplaceBottom`\ 」

            また、ユーザーリスト操作による「 \ :meth:`Operater`\ 」による変更も該当します。
            ただし、この場合はGenerateUserlistFromRecordで生成されるユーザーリスト定義は、Operaterに渡した定義と必ずしも一致するとは限りません。
            （特にコメント行や改行などの定義は定義生成時に、除外されるでしょう。）

            上記以外の、\ :meth:`LinkedTreeObject.LinkedTreeObject.AddChild`\ などのオブジェクト操作にて追加した場合は、記録されません。

            操作記録の終了を行う場合は、「 \ :meth:`EndRecord`\ 」を呼び出します。
            また、記録した操作内容を破棄する場合は、「 \ :meth:`ClearRecord`\ 」を呼び出します。
        """
        self._recording = True
        return self

    def EndRecord(self):
        """
            操作記録を終了します。
            詳しくは \ :meth:`BeginRecord`\  を参照して下さい。
        """
        self._recording = False
        return self

    def GenerateUserlistFromRecord(self):
        """
            操作記録によって記録した内容を元に、ユーザーリスト定義を生成します。（「ADD、OVERRIDE、FOR」などを使った構文）
            操作方法を意識しない限り、BOSSでは動作しない記述が吐き出されますので注意が必要です。（特にグループの操作）
            pyOssLibでは、GenerateUserlistFromRecordの出力は全てそのまま操作可能です。

            操作記録について詳しくは \ :meth:`BeginRecord`\ を参照して下さい。
            生成したユーザーリスト定義は \ :class:`UserlistLib.Userlist`\ クラスオブジェクトとして返却します。

            :rtype: UserlistLib.Userlist
            :return: 生成したユーザーリストクラスのオブジェクト
        """
        ret = None

        procedure = Userlist()
        for record in self._archiverecord:
            recordstring = record.get(u"Record", u"")
            param1string = record.get(u"Param1", u"")
            param2string = record.get(u"Param2", u"")

            match = regexRecord.search(recordstring)
            if match != None:
                command    = u"%s" % (match.group(1))
                rule       = u"%s" % (match.group(3))
                sort       = u"%s" % (match.group(4))
                param1type = u"%s" % (match.group(6))
                param2type = u"%s" % (match.group(7))

                operation = UserOperation()

                if command == u"AppendLine":
                    # ルール
                    operation.AddNewRuleFor(param2string)
                    # メッセージ
                    operation.AddNewMessageAppend(param1string)
                elif command == u"ReplaceLine":
                    # ルール
                    operation.AddNewRuleFor(param2string)
                    # メッセージ
                    operation.AddNewMessageReplace(param1string)
                else:
                    # ルール
                    if rule == u"Move":
                        operation.AddNewRuleOverride(param1string)
                    elif rule == u"Insert":
                        operation.AddNewRuleAdd(param1string)
                        #if param1type == u"Group":
                        #    operation.AddNewRuleAddGroup(param1string)
                        #elif param1type == u"MODs":
                        #    operation.AddNewRuleAdd(param1string)
                    # ソート
                    if sort == u"Before":
                        operation.AddNewSortBefore(param2string)
                    elif sort == u"After":
                        operation.AddNewSortAfter(param2string)
                    elif sort == u"Top":
                        operation.AddNewSortTop(param2string)
                    elif sort == u"Bottom":
                        operation.AddNewSortBottom(param2string)
                procedure.AddChild(operation)

        procedure.UnnecessaryMergeOperations()

        for operation in procedure.EachChilds():
            operation.AddNewBlank()

        ret = procedure
        return ret

    def _operaterUserOperation(self, operation):
        """
            ユーザーオペレーションオブジェクトを元にマスタリストの操作を行います。
        """
        if not operation.IsValid():
            raise ValueError, "Specified operation can not be performed."

        ruletypestring = u""
        ruleparam = None
        sortparam = None
        if operation.IsType(EnumCommandType.ADD):
            ruletypestring = u"Insert"
            ruleparamstring = operation.GetUserLine(EnumCommandType.RULE).ParamString
            match = regexMods.search(ruleparamstring)
            if match is not None:
                # 行文字列と判断する。
                ruleparam = Line(ruleparamstring)
            else:
                # グループ名と判断する。
                ruleparam = Group(ruleparamstring)
            sortparam = operation.GetUserLine(EnumCommandType.SORT).ParamString
        elif operation.IsType(EnumCommandType.OVERRIDE):
            ruletypestring = u"Move"
            ruleparam = operation.GetUserLine(EnumCommandType.RULE).ParamString
            sortparam = operation.GetUserLine(EnumCommandType.SORT).ParamString
        elif operation.IsType(EnumCommandType.FOR):
            ruletypestring = u""
            ruleparam = operation.GetUserLine(EnumCommandType.RULE).ParamString
            sortparam = None

        sorttypestring = u""
        if operation.IsType(EnumCommandType.BEFORE):
            sorttypestring = u"Before"
        elif operation.IsType(EnumCommandType.AFTER):
            sorttypestring = u"After"
        elif operation.IsType(EnumCommandType.TOP):
            sorttypestring = u"Top"
        elif operation.IsType(EnumCommandType.BOTTOM):
            sorttypestring = u"Bottom"

        funclists = [
            u"MoveBefore",
            u"MoveAfter",
            u"MoveTop",
            u"MoveBottom",
            u"InsertBefore",
            u"InsertAfter",
            u"InsertTop",
            u"InsertBottom",
            ]
        funcname = u"%s%s" % (ruletypestring, sorttypestring)
        if funcname in funclists:
            func = getattr(self, funcname)
            func(ruleparam, sortparam)

        messageobjects = operation.GetUserLineAll(EnumCommandType.MESSAGE)
        for messageobj in messageobjects:
            messageparam1 = messageobj.ParamString
            messageparam2 = self._findTargetOfName(ruleparam)
            if messageobj.IsType(EnumCommandType.APPEND):
                self.AppendLine(messageparam1, messageparam2)
            elif messageobj.IsType(EnumCommandType.REPLACE):
                self.ReplaceLine(messageparam1, messageparam2)
        return self

    def _operaterUserlist(self, userlist):
        """
            ユーザーリストオブジェクトを元にマスタリストの操作を行います。
        """
        for operation in userlist.EachChilds():
            if operation.IsValid():
                try:
                    self._operaterUserOperation(operation)
                except BaseException as ex:
                    print u"%s\r\n  %s" % (ex, operation)
        return self

    def Operater(self, operation):
        """
            *operation* で指定したオブジェクトを元にマスタリストの操作を行います。
            *operation* にはユーザーリストオブジェクト、または、ユーザーオペレーションオブジェクトを指定できます。
            このとき渡されたオブジェクトがユーザーリストオブジェクトの場合、その中の有効な操作のみ実行され、無効な操作は無視されます。（実際の操作の段階で例外が発生した場合は、次のオペレーションを処理します）
            渡されたオブジェクトがユーザーオペレーションオブジェクトの場合、無効な操作を実行しようとすると例外を発生します。
            操作が有効か無効かの判断は、\ :meth:`UserlistLib.UserOperation.IsValid`\ で判断します。

            引数に渡すことが可能なオブジェクトについては、それぞれ「 \ :class:`UserlistLib.Userlist`\ \ :class:`UserlistLib.UserOperation`\ 」を参照して下さい。

            :param (UserOperation,Userlist) operation: ユーザーリスト操作情報を持つオブジェクト
        """
        if isinstance(operation, UserOperation):
            self._operaterUserOperation(operation)
        elif isinstance(operation, Userlist):
            self._operaterUserlist(operation)
        else:
            raise TypeError, "Specified operation can not be performed. expected UserOperation or Userlist."
        return self


    def Save(self, fullpathfilename = u"", encoding=None):
        """
            現在の状態を指定したファイルに保存します。
            ファイル名の指定を省略した場合は、最後にLoad又はSaveしたファイルに保存します。

            :param string fullpathfilename: 保存するファイル名
            :param string encoding: ファイルのエンコーディング（公式は「Windows-1252:'cp1252'」又は「UTF-8 BOM有:'utf-8-sig'」）
        """
        if len(fullpathfilename) != 0:
            self._fullpathfilename = fullpathfilename.lstrip().rstrip()
        if len(self._fullpathfilename) == 0:
            raise IOError, "Invalid filename."
        if os.path.exists(self._fullpathfilename):
            os.remove(self._fullpathfilename)

        # 行データのない不要なゴミブロックを削除する。
        for waste in self._getWasteBlock():
            waste.Parent().DeleteChild(waste)

        # エンコーディング判定
        if encoding is not None:
            self._encoding = encoding
        #print u"Save encoding: %s" % (self._encoding)

        # --------------------------------------------------
        # エンコードエラー時の処理定義
        # --------------------------------------------------
        if getattr(self, "OnEncodingErrorFromSave", None) == None:
            def _onEncodingErrorFromSave(linestring, linecount, encoding):
                # コマンドプロンプトはcp932(shift-jisのMicrosoft拡張)で表示するため、暗黙の文字コード変換が行われる。
                # そのため、linestringをprintすると、cp932に存在しない文字は表示できずにエラーになってしまう。
                # これは回避不能なので、表示しない動作をデフォルトとする。
                print u"UNICODE(%s) encoding error! skip line: %s" % (encoding, linecount)
                return
            self.OnEncodingErrorFromSave = _onEncodingErrorFromSave

        linecount = 0

        filemasterlist = codecs.open(self._fullpathfilename, "wU", self._encoding)
        try:
            #filemasterlist.write(self.MasterlistOutput())
            for object in self.EachRecursion():
                if isinstance(object, Line):
                    linecount += 1
                    linestring = u""
                    # --------------------------------------------------
                    # Encodingの変換に失敗する文字が使われている場合は削除する。
                    # --------------------------------------------------
                    try:
                        temp = object.LineString.encode(self._encoding)
                        linestring = object.LineString
                    except UnicodeEncodeError:
                        param_linestring = copy.copy(linestring)
                        param_linecount = copy.copy(linecount)
                        param_encoding = copy.copy(self._encoding)
                        self.OnEncodingErrorFromSave(param_linestring, param_linecount, param_encoding)
                        linestring = u""
                    linestring = u"%s\r\n" % (linestring)
                    filemasterlist.write(linestring)
        finally:
            filemasterlist.close()
        return self

    def Load(self, fullpathfilename = u"", encoding=None):
        """
            指定したファイルからマスタリストを読み込み、構成を解析します。
            ファイル名の指定を省略した場合は、最後にLoad又はSaveしたファイルから読み込みます。
            *encoding* にエンコーディング文字を指定すると、指定したコードで読み込みます。省略した場合は自動判定します。

            :param string fullpathfilename: 読み込むファイル名
            :param string encoding: ファイルのエンコーディング（公式は「Windows-1252:'cp1252'」又は「UTF-8 BOM有:'utf-8-sig'」）
        """
        if len(fullpathfilename) != 0:
            self._fullpathfilename = fullpathfilename.lstrip().rstrip()
        if len(self._fullpathfilename) == 0:
            raise IOError, "Invalid filename."
        if not os.path.exists(self._fullpathfilename):
            raise IOError, "No such file."

        if self.ChildCount() != 0:
            # もし子供が追加されていたら、全て削除する。
            for child in self.EachChilds():
                self.DeleteChild(child)

        # --------------------------------------------------
        # エンコーディング判定
        # --------------------------------------------------
        if encoding is None:
            detector = UniversalDetector()
            detector.reset()
            for line in file(self._fullpathfilename, 'rb'):
                detector.feed(line)
                if detector.done:
                    break
            detector.close()
            encoding = detector.result["encoding"]
        self._encoding = encoding
        #print u"Load encoding: %s" % (self._encoding)

        # --------------------------------------------------
        # デコードエラー時の処理定義
        # --------------------------------------------------
        if getattr(self, "OnDecodingErrorFromLoad", None) == None:
            def _onDecodingErrorFromLoad(linecount, linestring, encoding):
                # コマンドプロンプトはcp932(shift-jisのMicrosoft拡張)で表示するため、暗黙の文字コード変換が行われる。
                # そのため、linestringをprintすると、cp932に存在しない文字は表示できずにエラーになってしまう。
                # これは回避不能なので、表示しない動作をデフォルトとする。
                print u"UNICODE(%s) decoding error! skip line: %s" % (encoding, linecount)
                return None
            self.OnDecodingErrorFromLoad = _onDecodingErrorFromLoad

        # --------------------------------------------------
        # 行オブジェクト生成時の処理定義
        # --------------------------------------------------
        if getattr(self, "OnCreateLineObject", None) == None:
            def _onCreateLineObject(linecount, linestring):
                # 行オブジェクトの作成（行補正機能を有効にする）
                return Line(linestring, True)
            self.OnCreateLineObject = _onCreateLineObject

        # --------------------------------------------------
        # masterlistの読み込みとオブジェクトへの展開
        # --------------------------------------------------
        thisGroup = self
        thisBlock = Block()
        thisGroup.AddChild(thisBlock)

        countbegingroup = 0
        countendgroup = 0
        linecount = 0

        filemasterlist = open(self._fullpathfilename, "rU")
        #filemasterlist = codecs.open(self._fullpathfilename, "rU", "shift_jis")
        try:
            for linestring in filemasterlist:
                if linecount == 0:
                    linestring = CommonLib.CutBomString(linestring)
                linecount += 1
                # --------------------------------------------------
                # Encodingの変換に失敗する文字が使われている場合は削除する。
                # --------------------------------------------------
                try:
                    linestring = u"%s" % (unicode(linestring, self._encoding).encode("utf-8"))
                except UnicodeDecodeError:
                    param_linecount = copy.copy(linecount)
                    param_linestring = copy.copy(linestring)
                    param_encoding = copy.copy(self._encoding)
                    linestring = self.OnDecodingErrorFromLoad(param_linecount, param_linestring, param_encoding)
                    if (isinstance(linestring, str)) or (isinstance(linestring, unicode)):
                        try:
                            linestring = u"%s" % (unicode(linestring, self._encoding).encode("utf-8"))
                        except UnicodeDecodeError:
                            linestring = u""
                    else:
                        linestring = u""

                # 行オブジェクトの作成
                #thisLine = Line(linestring, True)
                param_linecount = copy.copy(linecount)
                thisLine = self.OnCreateLineObject(param_linecount, linestring)
                if not isinstance(thisLine, Line):
                    raise SyntaxError, "OnCreateLineObject() is an invalid object to return."

                if thisLine.IsType(EnumLineType.BEGINGROUP):
                    countbegingroup += 1
                    # グループとブロックを作成して紐付ける
                    newGroup = Group(thisLine.BeginGroupName, None, False)

                    thisGroup.AddChild(newGroup)

                    thisBlock = Block()
                    newGroup.AddChild(thisBlock)

                    thisGroup = newGroup

                if thisLine.IsType(EnumLineType.MODS):
                    # ブロックを作成して紐付ける
                    thisBlock = Block()
                    thisGroup.AddChild(thisBlock)

                if thisLine.IsType(EnumLineType.ENDGROUP):
                    countendgroup += 1
                    if countbegingroup < countendgroup:
                        raise SyntaxError, "The group does not match the beginning and end."
                    # ブロックを作成して紐付ける
                    thisBlock = Block()
                    thisGroup.AddChild(thisBlock)

                # ブロックに行を追加
                thisBlock.AddChild(thisLine)

                if thisLine.IsType(EnumLineType.ENDGROUP):
                    # グループを親に戻し、ブロックを作成して紐付ける
                    if thisGroup.Parent() is None:
                        raise SyntaxError, "The group does not match the beginning and end."

                    thisGroup = thisGroup.Parent()
                    # ここで作ったブロックは、結局、使われなくなるケースが
                    # 発生するが、これは後で消すことにする。
                    thisBlock = Block()
                    thisGroup.AddChild(thisBlock)

            if countbegingroup != countendgroup:
                raise SyntaxError, "The group does not match the beginning and end."

        finally:
            # マスタリストを閉じる
            filemasterlist.close()

        # 行データのない不要なゴミブロックを削除する。
        for waste in self._getWasteBlock():
            waste.Parent().DeleteChild(waste)
        return self

    def DebugSave(self, fullpath):
        """
            指定したファイルへデバッグ情報を出力します。
            デバッグ出力には\ :meth:`LinkedTreeObject.LinkedTreeObject.DebugOutput`\ を使用します。

            :param string fullpath: 保存するファイル名
        """
        if os.path.exists(fullpath):
            os.remove(fullpath)
        filedebug = codecs.open(fullpath, "wU", "utf-8-sig")
        try:
            filedebug.write(self.DebugOutput())
        finally:
            filedebug.close()
        return self

    def DebugSimpleSave(self, fullpath):
        """
            指定したファイルへシンプルなデバッグ情報を出力します。
            デバッグ出力には\ :meth:`LinkedTreeObject.LinkedTreeObject.DebugSimpleOutput`\ を使用します。

            :param string fullpath: 保存するファイル名
        """
        if os.path.exists(fullpath):
            os.remove(fullpath)
        filedebug = codecs.open(fullpath, "wU", "utf-8-sig")
        try:
            filedebug.write(self.DebugSimpleOutput())
        finally:
            filedebug.close()
        return self


if __name__  == "__main__":
    print u"%s Version: %s %s" % (__appname__, __version__, __copyright__)
    print u"%s" % (__license__)

