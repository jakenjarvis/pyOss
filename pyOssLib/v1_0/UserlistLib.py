#!/usr/bin/python
# -*- coding: utf-8 -*-
# This file encoding UTF-8 no BOM. このファイルの文字コードはUTF-8 BOM無しです。
################################################################################
__appname__   = "UserlistLib"
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
    "EnumCommandType",
    "EnumUserAttributeType",
    "UserOperation",
    "UserLine",
    "Userlist",
]

################################################################################
# Import
################################################################################
import sys
import os
import codecs
import re
import copy

reload(sys)
sys.setdefaultencoding('utf-8')

from chardet.universaldetector import UniversalDetector

import CommonLib
from LinkedTreeObject import LinkedTreeObject

################################################################################
# Global variable
################################################################################
# [userlist] ユーザーリスト検出用
regexUslCommand = re.compile(ur"^([A-Za-z]+)\s*[:]\s*(.*)$", re.IGNORECASE)
# [userlist] コメント行検出用
regexUslCommentLine = re.compile(ur"^[/]{2}\s*(.*)$", re.IGNORECASE)


# ESM、ESPファイル検出正規表現（含まれていればOKとする）
regexModsName = re.compile(ur"(\w+(\w|[ ]|[$%'_@!()~-])+)[.](esm|esp)", re.IGNORECASE)


################################################################################
# Class
################################################################################
# ------------------------------------------------------------------------------
# EnumCommandType
# ------------------------------------------------------------------------------
class EnumCommandType(object):
    """
        \ :class:`UserLine`\ クラスの名前格納タイプを表現します。（列挙体ビットフィールド表現クラス）
    """
    # --------------------------------------------------
    # 共通タイプ
    # --------------------------------------------------
    #: 判定できなかった不明な行を表します。
    OTHER     = 0x000000
    #: 空白行を表します。
    BLANK     = 0x000001
    #: コメント行を表します。（コメントのみで構成された行のみ）
    COMMENT   = 0x000002
    # --------------------------------------------------
    # ルールタイプ
    # --------------------------------------------------
    #: ルール行を表します。
    RULE      = 0x010000
    #: ADDルールコマンド行を表します。
    ADD       = 0x011000
    #: OVERRIDEルールコマンド行を表します。
    OVERRIDE  = 0x012000
    #: FORルールコマンド行を表します。
    FOR       = 0x014000
    # --------------------------------------------------
    # ソートタイプ
    # --------------------------------------------------
    #: ソート行を表します。
    SORT      = 0x020000
    #: BEFOREソートコマンド行を表します。
    BEFORE    = 0x020100
    #: AFTERソートコマンド行を表します。
    AFTER     = 0x020200
    #: TOPソートコマンド行を表します。
    TOP       = 0x020400
    #: BOTTOMソートコマンド行を表します。
    BOTTOM    = 0x020800
    # --------------------------------------------------
    # メッセージタイプ
    # --------------------------------------------------
    #: メッセージ行を表します。
    MESSAGE   = 0x040000
    #: APPENDメッセージコマンド行を表します。
    APPEND    = 0x040010
    #: REPLACEメッセージコマンド行を表します。
    REPLACE   = 0x040020
    __slots__ = []

    @staticmethod
    def ToString(linetype):
        ret = u""
        sepa = u""
        if linetype == EnumCommandType.OTHER:
            ret = u"OTHER"
        else:
            if (linetype & EnumCommandType.BLANK) == EnumCommandType.BLANK:
                ret += sepa + u"BLANK"
                sepa = u"|"
            if (linetype & EnumCommandType.COMMENT) == EnumCommandType.COMMENT:
                ret += sepa + u"COMMENT"
                sepa = u"|"

            #if (linetype & EnumCommandType.RULE) == EnumCommandType.RULE:
            #    ret += sepa + u"RULE"
            #    sepa = u"-"

            if (linetype & EnumCommandType.ADD) == EnumCommandType.ADD:
                ret += sepa + u"ADD"
                sepa = u"|"
            if (linetype & EnumCommandType.OVERRIDE) == EnumCommandType.OVERRIDE:
                ret += sepa + u"OVERRIDE"
                sepa = u"|"
            if (linetype & EnumCommandType.FOR) == EnumCommandType.FOR:
                ret += sepa + u"FOR"
                sepa = u"|"

            #if (linetype & EnumCommandType.SORT) == EnumCommandType.SORT:
            #    ret += sepa + u"SORT"
            #    sepa = u"-"

            if (linetype & EnumCommandType.BEFORE) == EnumCommandType.BEFORE:
                ret += sepa + u"BEFORE"
                sepa = u"|"
            if (linetype & EnumCommandType.AFTER) == EnumCommandType.AFTER:
                ret += sepa + u"AFTER"
                sepa = u"|"
            if (linetype & EnumCommandType.TOP) == EnumCommandType.TOP:
                ret += sepa + u"TOP"
                sepa = u"|"
            if (linetype & EnumCommandType.BOTTOM) == EnumCommandType.BOTTOM:
                ret += sepa + u"BOTTOM"
                sepa = u"|"

            #if (linetype & EnumCommandType.MESSAGE) == EnumCommandType.MESSAGE:
            #    ret += sepa + u"MESSAGE"
            #    sepa = u"-"

            if (linetype & EnumCommandType.APPEND) == EnumCommandType.APPEND:
                ret += sepa + u"APPEND"
                sepa = u"|"
            if (linetype & EnumCommandType.REPLACE) == EnumCommandType.REPLACE:
                ret += sepa + u"REPLACE"
                sepa = u"|"
        return ret

# ------------------------------------------------------------------------------
# EnumUserAttributeType
# ------------------------------------------------------------------------------
class EnumUserAttributeType(object):
    """
        \ :class:`UserOperation`\ クラス及び\ :class:`UserLine`\ クラスの属性タイプを表現します。（列挙体ビットフィールド表現クラス）
    """
    #: 空白行及び無効行で構成された範囲であることを表します。
    BLANKONLY   = 0x0000
    #: コマンド行で構成された範囲であることを表します。
    EXISTCOMMAND = 0x0001
    __slots__ = []


# ------------------------------------------------------------------------------
# UserOperation
# ------------------------------------------------------------------------------
class UserOperation(LinkedTreeObject):
    """
       ユーザーオペレーションクラス
        このクラスは、コマンド行のADD、OVERRIDE、FORから始まる複数行で表す１つの操作を表現します。
        ユーザーオペレーションの子要素にはユーザー行オブジェクトのみ内包できるものとします。
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
        rule = self.GetUserLine(EnumCommandType.RULE)
        sort = self.GetUserLine(EnumCommandType.SORT)
        messages = self.GetUserLineAll(EnumCommandType.MESSAGE)
        if rule != None:
            ret += u"%s;" % (rule)
        if sort != None:
            ret += u"%s;" % (sort)
        if messages != None:
            for msg in messages:
                ret += u"%s;" % (msg)
        return ret

    def _onAppendChild(self, leaf):
        if not (isinstance(leaf, UserLine)):
            raise TypeError, "This object can not be added. expected type is UserLine."

        if leaf.IsType(EnumCommandType.RULE):
            if self.IsType(EnumCommandType.RULE):
                raise ValueError, "This object can not be added. In the UserOperation, only one RULE can exist."

        if leaf.IsType(EnumCommandType.SORT):
            if self.IsType(EnumCommandType.SORT):
                raise ValueError, "This object can not be added. In the UserOperation, only one SORT can exist."
            if self.IsType(EnumCommandType.FOR):
                raise ValueError, "This object can not be added. When the RULE is FOR, the SORT cannot be added."

        # 挿入順序に制限を加える
        if leaf.IsType(EnumCommandType.RULE):
            if self.IsType(EnumCommandType.SORT):
                raise ValueError, "This object can not be added. When SORT exists, the RULE cannot be added."
            if self.IsType(EnumCommandType.MESSAGE):
                raise ValueError, "This object can not be added. When MESSAGE exists, the RULE cannot be added."
        if leaf.IsType(EnumCommandType.SORT):
            if self.IsType(EnumCommandType.MESSAGE):
                raise ValueError, "This object can not be added. When MESSAGE exists, the SORT cannot be added."

        return self

    def UserlistOutput(self):
        """
            :rtype: string
            :return: Userlist形式でこのオブジェクトと全ての子要素を出力します。
        """
        return u"".join([u"%s" % (child.UserlistOutput()) for child in self.EachChilds()])

    def GetAttribute(self):
        """
            このオブジェクトの属性を返却します。
            ユーザーオペレーションは、子要素\ :class:`UserLine`\ クラスのオブジェクトを検査し、このオブジェクトの属性を決定します。
            属性決定のルールは\ :meth:`UserLine.GetAttribute`\ を参照してください。

            :rtype: EnumUserAttributeType
            :return: 子要素を含めたこのオブジェクトの属性を返却します。
        """
        ret = EnumUserAttributeType.BLANKONLY
        for child in self.EachChilds():
            ret |= child.GetAttribute()
        return ret

    def IsType(self, linetype):
        """
            このオブジェクトの行格納タイプに指定したタイプが含まれるか判断します。
            これは子要素全ての\ :data:`LineType`\ を論理和した値に対して比較判断します。

            :param EnumCommandType linetype: 比較するEnumCommandTypeの値

            :rtype: bool
            :return: このオブジェクトのタイプが指定したタイプと一致する場合は真を返す。一致しない場合は偽を返す。
        """
        return ((self.GetLineTypes() & linetype) == linetype)

    def IsValid(self):
        """
            このユーザーオペレーションが有効なコマンドとして機能するか判断します。
            これは「ADD、OVERRIDE＋ソート」もしくは「FOR＋メッセージ」の組み合わせが存在するなら有効とみなします。
            BOSSのユーザーリストの記述で禁止されている組み合わせでも「有効」と判断するため注意が必要です。

            :rtype: bool
            :return: このユーザーオペレーションが有効な場合は真を返す。無効な場合は偽を返す。
        """
        ret = False
        if self.GetAttribute() == EnumUserAttributeType.EXISTCOMMAND:
            if self.IsType(EnumCommandType.ADD):
                if self.IsType(EnumCommandType.SORT):
                    ret = True
            elif self.IsType(EnumCommandType.OVERRIDE):
                if self.IsType(EnumCommandType.SORT):
                    ret = True
            elif self.IsType(EnumCommandType.FOR):
                if self.IsType(EnumCommandType.MESSAGE):
                    ret = True
        return ret

    def GetLineTypes(self):
        """
            このオブジェクトの子要素全ての\ :data:`LineType`\ を論理和した値を返却します。

            :rtype: EnumCommandType
            :return: 子要素を含めたこのオブジェクトのEnumCommandTypeを返却します。
        """
        ret = EnumCommandType.OTHER
        for child in self.EachChilds():
            ret |= child.LineType
        return ret

    def GetUserLine(self, commandtype):
        """
            このユーザーオペレーションに *commandtype* で指定したEnumCommandTypeのユーザー行オブジェクトが存在するか検索し、結果を返却します。

            :rtype: UserLineまたはNone
            :return: 最初に一致したUserLineを返却します。該当するUserLineを発見できなかった場合はNoneを返却します。
        """
        return self.FindDataFunc(u"LineType", lambda v: ((v & commandtype) == commandtype))

    def GetUserLineAll(self, commandtype):
        """
            このユーザーオペレーションに *commandtype* で指定したEnumCommandTypeのユーザー行オブジェクトが存在するか **全て** 検索し、結果を返却します。

            :rtype: UserLineのリスト
            :return: 一致した全てのUserLineをリストに列挙して返却します。
             該当するUserLineを発見できなかった場合は空のリストを返却します。
        """
        return self.FindDataAllFunc(u"LineType", lambda v: ((v & commandtype) == commandtype))

    def AddNewBlank(self):
        """
            空白行を追加します。
            これは新規に\ :class:`UserLine`\ クラスのオブジェクトを生成し、子要素に追加します。
        """
        return self.AddChild(UserLine(u""))

    def AddNewComment(self, comment):
        """
            コメント行を追加します。
            これは新規に\ :class:`UserLine`\ クラスのオブジェクトを生成し、子要素に追加します。

            :param string comment: 追加するコメント文字列（コメントの「//」は内部で付与します）
        """
        return self.AddChild(UserLine(u"// %s" % (comment)))

    def AddNewRuleAdd(self, name):
        """
            子要素にルール「ADD:」を新たに追加します。
            これは新規に\ :class:`UserLine`\ クラスのオブジェクトを生成し、子要素に追加します。

            :param string name: 追加する要素の文字列（コマンド文字列は内部で付与します）
        """
        return self.AddChild(UserLine(u"ADD: %s" % (name)))

    def AddNewRuleOverride(self, name):
        """
            子要素にルール「OVERRIDE:」を新たに追加します。
            これは新規に\ :class:`UserLine`\ クラスのオブジェクトを生成し、子要素に追加します。

            :param string name: 追加する要素の文字列（コマンド文字列は内部で付与します）
        """
        return self.AddChild(UserLine(u"OVERRIDE: %s" % (name)))

    def AddNewRuleFor(self, name):
        """
            子要素にルール「FOR:」を新たに追加します。
            これは新規に\ :class:`UserLine`\ クラスのオブジェクトを生成し、子要素に追加します。

            :param string name: 追加する要素の文字列（コマンド文字列は内部で付与します）
        """
        return self.AddChild(UserLine(u"FOR: %s" % (name)))

    def AddNewSortBefore(self, name):
        """
            子要素にソート「BEFORE:」を新たに追加します。
            これは新規に\ :class:`UserLine`\ クラスのオブジェクトを生成し、子要素に追加します。

            :param string name: 追加する要素の文字列（コマンド文字列は内部で付与します）
        """
        return self.AddChild(UserLine(u"BEFORE: %s" % (name)))

    def AddNewSortAfter(self, name):
        """
            子要素にソート「AFTER:」を新たに追加します。
            これは新規に\ :class:`UserLine`\ クラスのオブジェクトを生成し、子要素に追加します。

            :param string name: 追加する要素の文字列（コマンド文字列は内部で付与します）
        """
        return self.AddChild(UserLine(u"AFTER: %s" % (name)))

    def AddNewSortTop(self, name):
        """
            子要素にソート「TOP:」を新たに追加します。
            これは新規に\ :class:`UserLine`\ クラスのオブジェクトを生成し、子要素に追加します。

            :param string name: 追加する要素の文字列（コマンド文字列は内部で付与します）
        """
        return self.AddChild(UserLine(u"TOP: %s" % (name)))

    def AddNewSortBottom(self, name):
        """
            子要素にソート「BOTTOM:」を新たに追加します。
            これは新規に\ :class:`UserLine`\ クラスのオブジェクトを生成し、子要素に追加します。

            :param string name: 追加する要素の文字列（コマンド文字列は内部で付与します）
        """
        return self.AddChild(UserLine(u"BOTTOM: %s" % (name)))

    def AddNewMessageAppend(self, name):
        """
            子要素にメッセージ「APPEND:」を新たに追加します。
            これは新規に\ :class:`UserLine`\ クラスのオブジェクトを生成し、子要素に追加します。

            :param string name: 追加する要素の文字列（コマンド文字列は内部で付与します）
        """
        return self.AddChild(UserLine(u"APPEND: %s" % (name)))

    def AddNewMessageReplace(self, name):
        """
            子要素にメッセージ「REPLACE:」を新たに追加します。
            これは新規に\ :class:`UserLine`\ クラスのオブジェクトを生成し、子要素に追加します。

            :param string name: 追加する要素の文字列（コマンド文字列は内部で付与します）
        """
        return self.AddChild(UserLine(u"REPLACE: %s" % (name)))


# ------------------------------------------------------------------------------
# UserLine
# ------------------------------------------------------------------------------
class UserLine(LinkedTreeObject):
    """
       ユーザー行オブジェクトクラス
        このクラスは、ユーザーリスト内の１行を１つの行オブジェクトとして表現します。
        ユーザー行オブジェクトに子要素を持つことはできません。
    """
    def __init__(self, linestring):
        """
            :param string linestring: このユーザー行オブジェクトに格納する文字列
        """
        LinkedTreeObject.__init__(self)
        # --------------------------------------------------
        # ユーザーリスト行の補正処理
        # --------------------------------------------------
        # 改行、空白の削除
        linestring = linestring.rstrip("\r\n").lstrip().rstrip()

        commentmatch = None

        # 正規表現チェック
        match = regexUslCommand.search(linestring)
        if match != None:
            # ルールの記述方法にマッチした行
            paramcommand = u"%s" % (match.group(1).lstrip().rstrip().upper())
            paramstring = u"%s" % (match.group(2).lstrip().rstrip())

            # 識別できないコマンドの場合はカラにする
            if not paramcommand in [u"ADD",    u"OVERRIDE", u"FOR",
                                    u"BEFORE", u"AFTER",    u"TOP",   u"BOTTOM",
                                    u"APPEND", u"REPLACE"]:
                paramcommand = u""
                paramstring = u""
        else:
            # ルールの記述方法にマッチしなかった行
            paramcommand = u""
            paramstring = u""

            commentmatch = regexUslCommentLine.search(linestring)

        # --------------------------------------------------
        # LineTypeの設定
        # --------------------------------------------------
        linetype = EnumCommandType.OTHER
        if len(linestring) == 0:
            # カラ行はBLANK設定
            linetype |= EnumCommandType.BLANK
        elif commentmatch != None:
            # コメント行
            linetype |= EnumCommandType.COMMENT
            #self.CommentString = u"%s" % (commentmatch.group(1).lstrip().rstrip())
        elif len(paramcommand) == 0:
            linetype |= EnumCommandType.OTHER
        else:
            #: この行がコマンド行だった場合、パラメータの文字列を表します。（\ :meth:`LinkedTreeObject.LinkedTreeObject.Data`\ に保管します。）
            self.ParamString = paramstring

            if paramcommand == u"ADD":
                linetype |= EnumCommandType.ADD
            if paramcommand == u"OVERRIDE":
                linetype |= EnumCommandType.OVERRIDE
            if paramcommand == u"FOR":
                linetype |= EnumCommandType.FOR

            if paramcommand == u"BEFORE":
                linetype |= EnumCommandType.BEFORE
            if paramcommand == u"AFTER":
                linetype |= EnumCommandType.AFTER
            if paramcommand == u"TOP":
                linetype |= EnumCommandType.TOP
            if paramcommand == u"BOTTOM":
                linetype |= EnumCommandType.BOTTOM

            if paramcommand == u"APPEND":
                linetype |= EnumCommandType.APPEND
            if paramcommand == u"REPLACE":
                linetype |= EnumCommandType.REPLACE

        #: この行の定義文字列を表します。（\ :meth:`LinkedTreeObject.LinkedTreeObject.Data`\ に保管します。）
        self.LineString = linestring
        #: この行の行格納タイプを表します。（\ :meth:`LinkedTreeObject.LinkedTreeObject.Data`\ に保管します。）
        self.LineType = linetype

    def __str__(self):
        ret = u"%s{%s}" % (EnumCommandType.ToString(self.LineType), self.LineString)
        return ret

    def _onAppendChild(self, leaf):
        raise SyntaxError, "This object can not be added."

    def _onRemoveChild(self, leaf):
        raise SyntaxError, "This object can not be deleted."

    def UserlistOutput(self):
        """
            :rtype: string
            :return: Userlist形式でこのオブジェクトと全ての子要素を出力します。
        """
        return u"%s\r\n" % (self.LineString)

    def GetAttribute(self):
        """
            このオブジェクトの属性を返却します。
            ユーザー行オブジェクトは、オブジェクト生成時の\ :data:`LineType`\ によって、このオブジェクトの属性を決定します。
            この行にコマンド行が含まれる場合は、EnumUserAttributeType.EXISTCOMMANDを返却します。
            それ以外の場合は、EnumUserAttributeType.BLANKONLYを返却します。

            :rtype: EnumUserAttributeType
            :return: 子要素を含めたこのオブジェクトの属性を返却します。
        """
        ret = EnumUserAttributeType.BLANKONLY
        if self.IsType(EnumCommandType.OTHER):
            ret = EnumUserAttributeType.BLANKONLY           # OTHER   => BLANKONLY
        elif self.IsType(EnumCommandType.BLANK):
            ret = EnumUserAttributeType.BLANKONLY           # BLANK   => BLANKONLY
        elif self.IsType(EnumCommandType.COMMENT):
            ret = EnumUserAttributeType.BLANKONLY           # COMMENT => BLANKONLY
        else:
            ret = EnumUserAttributeType.EXISTCOMMAND
        return ret

    def IsType(self, linetype):
        """
            このオブジェクトの行格納タイプに指定したタイプが含まれるか判断します。

            :param EnumCommandType linetype: 比較するEnumCommandTypeの値

            :rtype: bool
            :return: このオブジェクトのタイプが指定したタイプと一致する場合は真を返す。一致しない場合は偽を返す。
        """
        ret = False
        if linetype == EnumCommandType.OTHER:
            ret = (self.LineType == EnumCommandType.OTHER)
        else:
            ret = ((self.LineType & linetype) == linetype)
        return ret

    def AddChild(self, leaf):
        """ .. warning:: ユーザー行オブジェクトでは、このメソッドを利用できません。呼び出すと例外が発生します。 """
        raise SyntaxError, "This method is not available."

    def DeleteChild(self, leaf):
        """ .. warning:: ユーザー行オブジェクトでは、このメソッドを利用できません。呼び出すと例外が発生します。 """
        raise SyntaxError, "This method is not available."

    def InsertChild(self, index, leaf):
        """ .. warning:: ユーザー行オブジェクトでは、このメソッドを利用できません。呼び出すと例外が発生します。 """
        raise SyntaxError, "This method is not available."

    def InsertChildBefore(self, baseleaf, leaf):
        """ .. warning:: ユーザー行オブジェクトでは、このメソッドを利用できません。呼び出すと例外が発生します。 """
        raise SyntaxError, "This method is not available."

    def InsertChildAfter(self, baseleaf, leaf):
        """ .. warning:: ユーザー行オブジェクトでは、このメソッドを利用できません。呼び出すと例外が発生します。 """
        raise SyntaxError, "This method is not available."

    def Child(self, index):
        """ .. warning:: ユーザー行オブジェクトでは、このメソッドを利用できません。呼び出すと例外が発生します。 """
        raise SyntaxError, "This method is not available."

    def GetChildIndex(self, leaf):
        """ .. warning:: ユーザー行オブジェクトでは、このメソッドを利用できません。呼び出すと例外が発生します。 """
        raise SyntaxError, "This method is not available."

    def GetTopChild(self):
        """ .. warning:: ユーザー行オブジェクトでは、このメソッドを利用できません。呼び出すと例外が発生します。 """
        raise SyntaxError, "This method is not available."

    def GetBottomChild(self):
        """ .. warning:: ユーザー行オブジェクトでは、このメソッドを利用できません。呼び出すと例外が発生します。 """
        raise SyntaxError, "This method is not available."

# ------------------------------------------------------------------------------
# Userlist
# ------------------------------------------------------------------------------
class Userlist(LinkedTreeObject):
    """
       ユーザーリストオブジェクトクラス
        このクラスは、ユーザーリストを表現します。
        ユーザーリストのテキストファイルから行を読み込み、その解析を行います。
    """
    def __init__(self, fullpathfilename = u""):
        """
            :param string fullpathfilename: 読み込むユーザーリストのフルパスファイル名
        """
        LinkedTreeObject.__init__(self)

        self._fullpathfilename = fullpathfilename.lstrip().rstrip()
        self._encoding = "cp1252"

        if len(self._fullpathfilename) != 0:
            self.Load(self._fullpathfilename)

    def __str__(self):
        ret = u"Userlist"
        if len(self._fullpathfilename) != 0:
            ret = u"Userlist:(%s)" % (self._fullpathfilename)
        return ret

    def _onAppendChild(self, leaf):
        if not (isinstance(leaf, UserOperation)):
            raise TypeError, "This object can not be added. expected type is UserOperation."
        return self

    @property
    def FullPathFileName(self):
        """
            :rtype: string
            :return: このユーザーリストオブジェクトに登録されたユーザーリストファイル名を返却します。
        """
        return self._fullpathfilename

    def UserlistOutput(self):
        """
            :rtype: string
            :return: Userlist形式でこのオブジェクトと全ての子要素を出力します。
        """
        return u"".join([u"%s" % (child.UserlistOutput()) for child in self.EachChilds()])

    def UnnecessaryMergeOperations(self):
        """
            無駄なオペレーションをマージして、オペレーションの数を減らします。
            前後に同一MODsに対する操作を行っている場合のみ結合を行い、複数のFOR文に分かれた操作をADDやOVERRIDEにまとめます。
        """
        if self.ChildCount() != 0:
            mergetargetlists = []
            lastparamstring = u""
            lastparenttarget = None
            # マージ対象のリストを作成する。
            for target in self.EachChilds():
                userruleline = target.GetUserLine(EnumCommandType.RULE)
                paramstring = userruleline.ParamString
                mergeparent = False

                linetype = EnumCommandType.OTHER
                if userruleline.IsType(EnumCommandType.ADD):
                    linetype = EnumCommandType.ADD
                    # 必ずマージ元になる。
                    mergeparent = True
                elif userruleline.IsType(EnumCommandType.OVERRIDE):
                    linetype = EnumCommandType.OVERRIDE
                    # 必ずマージ元になる。
                    mergeparent = True
                elif userruleline.IsType(EnumCommandType.FOR):
                    linetype = EnumCommandType.FOR
                    # 直前の名称が異なる場合はFORもマージ元になりえる。
                    if lastparamstring != paramstring:
                        mergeparent = True

                if linetype != EnumCommandType.OTHER:
                    if mergeparent:
                        lastparenttarget = target
                    else:
                        # 直前が同一名称のFORのみマージする。
                        mergetargetlists += [[lastparenttarget, target]]

                lastparamstring = paramstring

            # マージ処理
            for merge in mergetargetlists:
                target = merge[0]
                mergetarget = merge[1]

                # 挿入先の検索。
                firstmessage = None
                lastcommand = None
                for child in target.EachChilds():
                    if child.IsType(EnumCommandType.RULE):
                        lastcommand = child
                    elif child.IsType(EnumCommandType.SORT):
                        lastcommand = child
                    elif child.IsType(EnumCommandType.MESSAGE):
                        lastcommand = child
                        if firstmessage == None:
                            firstmessage = child

                # マージ対象のルールを切り離す。
                self.DeleteChild(mergetarget)

                replaceflg = False
                # 最後の有効行の後ろから、全てのメッセージを挿入する
                messagelists = mergetarget.GetUserLineAll(EnumCommandType.MESSAGE)
                for message in messagelists:
                    if message.IsType(EnumCommandType.REPLACE):
                        # REPLACEは先頭にないと意味がないので、一旦APPENDにする。
                        replaceflg = True
                        mergetarget.DeleteChild(message)
                        newmessage = UserLine(u"APPEND: %s" % (message.ParamString))
                        target.InsertChildAfter(lastcommand, newmessage)
                        # targetにメッセージが存在しないケース用
                        if firstmessage == None:
                            firstmessage = newmessage
                    elif message.IsType(EnumCommandType.APPEND):
                        mergetarget.DeleteChild(message)
                        target.InsertChildAfter(lastcommand, message)
                        # targetにメッセージが存在しないケース用
                        if firstmessage == None:
                            firstmessage = message

                # REPLACEが存在した場合は、最初のメッセージをREPLACEにする。
                # ルールとソートの後に続く最初のメッセージを対象とする。
                if replaceflg:
                    if firstmessage != None:
                        newmessage = UserLine(u"REPLACE: %s" % (firstmessage.ParamString))
                        target.InsertChildAfter(firstmessage, newmessage)
                        target.DeleteChild(firstmessage)
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
            #filemasterlist.write(self.UserlistOutput())
            for object in self.EachRecursion():
                if isinstance(object, UserLine):
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
            指定したファイルからユーザーリストを読み込み、構成を解析します。
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
                # 行オブジェクトの作成
                return UserLine(linestring)
            self.OnCreateLineObject = _onCreateLineObject

        # --------------------------------------------------
        # userlistの読み込みとオブジェクトへの展開
        # --------------------------------------------------
        thisProcedure = self
        thisOperation = UserOperation()
        thisProcedure.AddChild(thisOperation)

        linecount = 0

        fileuserlist = open(self._fullpathfilename, "rU")
        #fileuserlist = codecs.open(self._fullpathfilename, "rU", "shift_jis")
        try:
            for linestring in fileuserlist:
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
                #thisLine = UserLine(linestring)
                param_linecount = copy.copy(linecount)
                thisLine = self.OnCreateLineObject(param_linecount, linestring)
                if not isinstance(thisLine, UserLine):
                    raise SyntaxError, "OnCreateLineObject() is an invalid object to return."

                if thisLine.IsType(EnumCommandType.RULE):
                    # ルール定義の開始に合わせてユーザーオペレーションを作成する。
                    thisOperation = UserOperation()
                    thisProcedure.AddChild(thisOperation)

                # ユーザーオペレーションに行を追加
                thisOperation.AddChild(thisLine)
        finally:
            # ユーザーリストを閉じる
            fileuserlist.close()
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

