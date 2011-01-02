#!/usr/bin/python
# -*- coding: utf-8 -*-
# This file encoding UTF-8 no BOM. このファイルの文字コードはUTF-8 BOM無しです。
################################################################################
__appname__   = "LinkedTreeObject"
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
    "LinkedTreeObject"
]

################################################################################
# Import
################################################################################
import sys
import copy

################################################################################
# Class
################################################################################
# ------------------------------------------------------------------------------
# MetaCloneable
# ------------------------------------------------------------------------------
class MetaCloneable(type):
    """
        オブジェクトのコピーを行うために、copy.copy()又はcopy.deepcopy()を呼び出すと、
        内部でインスタンスを生成し、生成したクラスのインスタンスメンバの__init__()を呼び出します。
        __init__()が引数なし、または省略可能な引数のみの場合は、正常にインスタンスの生成が行われますが、
        __init__()の引数に必須項目がある場合、「TypeError: __init__() takes exactly 2 arguments (1 given)」のようなエラーになります。
        このメタクラスは、コピー処理中の__init__()を呼び出さないようにすることで、これを回避します。
        初期化処理がない変わりに、コピー処理後に「__cloneinit__()」が定義されている場合はこれを呼び出します。
    """
    _initdisable = False
    #def __new__(cls, name, bases, dict):
    #    print "MetaCloneable.__new__ " + name
    #    return type.__new__(cls, name, bases, dict)
    #def __init__(cls, name, bases, dict):
    #    print "MetaCloneable.__init__ " + name

    def __call__(cls, *args, **kwargs):
        #print "MetaCloneable.__call__"
        # ここで指定したクラスのインスタンスが生成されます。
        instances = cls.__new__(cls, *args, **kwargs)
        # 通常はインスタンス生成後に__init__を呼び出すが、コピー処理中は呼び出さない。
        if not MetaCloneable._initdisable:
            cls.__init__(instances, *args, **kwargs)
        return instances

    def _callcloneinit(cls, instances):
        #print "MetaCloneable._callcloneinit"
        cloneinit = getattr(instances, "__cloneinit__", None)
        if cloneinit != None:
            # __cloneinit__()メソッドが定義されているなら呼び出す。
            cls.__cloneinit__(instances)

    def copy(cls, target):
        #print "MetaCloneable.copy"
        MetaCloneable._initdisable = True
        ret = copy.copy(target)
        MetaCloneable._initdisable = False
        MetaCloneable._callcloneinit(cls, ret)
        return ret

    def deepcopy(cls, target):
        #print "MetaCloneable.deepcopy"
        MetaCloneable._initdisable = True
        ret = copy.deepcopy(target)
        MetaCloneable._initdisable = False
        MetaCloneable._callcloneinit(cls, ret)
        return ret

# ex)呼ばれる順序
# MetaCloneable.__call__
# Group.__init__
# LinkedTreeObject.__init__
# LinkedTreeObject.Clone
# MetaCloneable.deepcopy
# MetaCloneable.callcloneinit
# LinkedTreeObject.__cloneinit__


# ------------------------------------------------------------------------------
# LinkedTreeObject
# ------------------------------------------------------------------------------
class LinkedTreeObject(object):
    """
       ツリー状にリンク状態を維持するオブジェクトクラス
        このクラスを使うと、オブジェクト同士をリンク（親子・兄弟関係を維持）した状態で、
        要素の追加削除を管理することができます。
    """
    # MEMO: Python3では動かないかも。class LinkedTreeObject(object, metaclass=MetaCloneable):になるかな？
    __metaclass__ = MetaCloneable   # メタクラスの指定

    def __init__(self):
        self._data = {}             # このクラスで扱うデータ以外をすべてここに保持します。
        self._depth = 0             # 階層の深さ
        self._linkParent = None     # 親オブジェクトへのリンク
        self._linkChilds = []       # 子オブジェクトへのリンク（リスト）
        self._linkPrevious = None   # 前オブジェクトへのリンク
        self._linkNext = None       # 後オブジェクトへのリンク

    def __cloneinit__(self):        # call MetaCloneable._callcloneinit()
        # これは、__copy__及び__deepcopy__メソッドの後（複製後）に呼び出されます。
        # not init self._data
        self._depth = 0
        self._linkParent = None
        self._linkChilds = []
        self._linkPrevious = None
        self._linkNext = None

    def __getattr__(self, attr):
        if attr in self._defaultAttr():
            return self.__dict__[attr]
        else:
            # _defaultAttr()に登録していないメンバはDataを参照します。
            return self.__dict__["_data"][attr]

    def __setattr__(self, attr, value):
        if attr in self._defaultAttr():
            self.__dict__[attr] = value
        else:
            # _defaultAttr()に登録していないメンバはDataを参照します。
            self.__dict__["_data"][attr] = value

    def __delattr__(self, attr):
        if attr in self._defaultAttr():
            raise AttributeError
        else:
            # _defaultAttr()に登録していないメンバはDataを参照します。
            del self.__dict__["_data"][attr]

    def __copy__(self):
        # 新しいインスタンスを生成してDataプロパティをシャローコピーします。
        # _defaultAttr()に登録しているメンバはコピーしません。
        ret = self.__class__()
        ret._data = self._data.copy()
        return ret

    def __deepcopy__(self, memo):
        # 新しいインスタンスを生成してDataプロパティをディープコピーします。
        # _defaultAttr()に登録しているメンバはコピーしません。
        ret = self.__class__()
        memo[id(self)] = ret
        ret._data = copy.deepcopy(self._data, memo)
        return ret

    @property
    def Data(self):
        """
            このクラスオブジェクトに追加されたメンバーはすべてディクショナリ型で、ここに格納されます。
            これは、LinkedTreeObjectクラスから派生したクラスでメンバーを追加した場合にも
            LinkedTreeObjectクラス内で識別できるようにするための処置です。（FindData系メソッドにて内部使用）
        """
        return self._data

    def Clone(self, childs=False, deep=False):
        """
            このオブジェクトのクローンを生成します。
            *childs* がFalseの場合、このオブジェクトのみクローンを生成します。Trueの場合、このオブジェクトを最上位の親として、再帰的に全ての子要素のクローンを生成し、新しい親子関係を構築します。
            *deep* がFalseの場合、Dataプロパティの値をシャローコピーします。Trueの場合、Dataプロパティの値をディープコピーします。

            :param bool childs: 子要素クローンフラグ
            :param bool deep: ディープコピーフラグ
            :rtype: LinkedTreeObject
            :return: 新しく生成したクローンのインスタンスオブジェクトを返却します。
        """
        ret = None
        if deep:
            #ret = copy.deepcopy(self)
            ret = MetaCloneable.deepcopy(self.__class__, self)
        else:
            #ret = copy.copy(self)
            ret = MetaCloneable.copy(self.__class__, self)
        if childs:
            for leaf in self._linkChilds:
                newchild = leaf.Clone(childs, deep)
                ret.AddChild(newchild)
        return ret

    def _defaultAttr(self):
        # このクラスで使用するメンバ名の一覧を返却します。
        # ここに記載したメンバ以外は全てDataへ格納します。
        return ["_data", "_depth", "_linkParent", "_linkChilds", "_linkPrevious", "_linkNext"]

    def _setLinkedPrevious(self, leaf):
        # このオブジェクトと前のオブジェクトをリンクまたはリンク解除します。
        if leaf != None:
            self._linkPrevious = leaf
            self._linkPrevious._linkNext = self
        else:
            if self._linkPrevious != None:
                self._linkPrevious._linkNext = None
            self._linkPrevious = None
        return self

    def _setLinkedNext(self, leaf):
        # このオブジェクトと後のオブジェクトをリンクまたはリンク解除します。
        if leaf != None:
            self._linkNext = leaf
            self._linkNext._linkPrevious = self
        else:
            if self._linkNext != None:
                self._linkNext._linkPrevious = None
            self._linkNext = None
        return self

    def _setLinkedChildDepth(self, depth):
        # このオブジェクトの子要素全ての深さを再帰的に設定します。
        self._depth = depth
        for leaf in self._linkChilds:
            leaf._setLinkedChildDepth(self._depth + 1)
        return self

    def _onAppendChild(self, leaf):
        """
            このメソッドは、LinkedTreeObjectで子要素を **追加** しようとしたときに呼び出します。
            LinkedTreeObjectクラスから派生したクラスで、オーバーライドすることを前提にしています。
            子要素を追加したタイミングで派生クラス側で処理を行う必要がある場合にオーバーライドしてください。
        """
        return self

    def _onRemoveChild(self, leaf):
        """
            このメソッドは、LinkedTreeObjectで子要素を **削除** しようとしたときに呼び出します。
            LinkedTreeObjectクラスから派生したクラスで、オーバーライドすることを前提にしています。
            子要素を追加したタイミングで派生クラス側で処理を行う必要がある場合にオーバーライドしてください。
        """
        return self

    def FindData(self, name, value):
        """
            このオブジェクト及び子要素から、 *name* で指定した名前で保持しているデータを対象に
            *value* で指定した値を保持するLinkedTreeObjectを検索します。
            *name* で指定したメンバ名が存在しない場合は、検索対象から除外します。
            （\ :meth:`FindDataFunc`\ の *func* に「lambda v: (v == value)」を指定した場合と同等です）

            :param string name: 検索対象のメンバ名
            :param string value: 検索対象の値
            :rtype: LinkedTreeObjectまたはNone
            :return: 指定したメンバ名で保持している値を検索し、最初に一致したLinkedTreeObjectを返却します。
             該当するLinkedTreeObjectを発見できなかった場合はNoneを返却します。
        """
        func = lambda v: (v == value)
        return self.FindDataFunc(name, func)

    def FindDataFunc(self, name, func):
        """
            このオブジェクト及び子要素から、 *name* で指定した名前で保持しているデータを対象にLinkedTreeObjectを検索します。
            *name* で指定したメンバ名が存在しない場合は、検索対象から除外します。
            *func* に比較するためのメソッドを指定する必要があります。
            （通常の比較で判断できる場合は、\ :meth:`FindData`\ を使用してください。）

            :param string name: 検索対象のメンバ名
            :param function(v) func: 比較処理を行いbool値を返却するメソッド
            :rtype: LinkedTreeObjectまたはNone
            :return: 指定したメンバ名で保持している値を検索し、最初に一致したLinkedTreeObjectを返却します。
             該当するLinkedTreeObjectを発見できなかった場合はNoneを返却します。
        """
        ret = None
        if name in self._data:
            if func(self._data[name]):
                ret = self
        if ret == None:
            for leaf in self._linkChilds:
                temp = leaf.FindDataFunc(name, func)
                if temp != None:
                    ret = temp
                    break
        return ret

    def FindDataAll(self, name, value):
        """
            このオブジェクト及び子要素から、 *name* で指定した名前で保持しているデータを対象に
            *value* で指定した値を保持するLinkedTreeObjectを **全て** 検索します。
            *name* で指定したメンバ名が存在しない場合は、検索対象から除外します。
            （\ :meth:`FindDataAllFunc`\ の *func* に「lambda v: (v == value)」を指定した場合と同等です）

            :param string name: 検索対象のメンバ名
            :param string value: 検索対象の値
            :rtype: LinkedTreeObjectのリスト
            :return: 指定したメンバ名で保持している値を検索し、一致した全てのLinkedTreeObjectをリストに列挙して返却します。
             該当するLinkedTreeObjectを発見できなかった場合は空のリストを返却します。
        """
        func = lambda v: (v == value)
        return self.FindDataAllFunc(name, func)

    def FindDataAllFunc(self, name, func):
        """
            このオブジェクト及び子要素から、 *name* で指定した名前で保持しているデータを対象にLinkedTreeObjectを **全て** 検索します。
            *name* で指定したメンバ名が存在しない場合は、検索対象から除外します。
            *func* に比較するためのメソッドを指定する必要があります。
            （通常の比較で判断できる場合は、\ :meth:`FindDataAll`\ を使用してください。）

            :param string name: 検索対象のメンバ名
            :param function(v) func: 比較処理を行いbool値を返却するメソッド
            :rtype: LinkedTreeObjectのリスト
            :return: 指定したメンバ名で保持している値を検索し、一致した全てのLinkedTreeObjectをリストに列挙して返却します。
             該当するLinkedTreeObjectを発見できなかった場合は空のリストを返却します。
        """
        ret = []
        if name in self._data:
            if func(self._data[name]):
                ret.append(self)
        for leaf in self._linkChilds:
            ret += leaf.FindDataAllFunc(name, func)
        return ret

    def Parent(self):
        """
            このオブジェクトの親にあたるLinkedTreeObjectを返却します。

            :rtype: LinkedTreeObjectまたはNone
            :return: このオブジェクトに親が存在する場合、LinkedTreeObjectを返却します。
             オブジェクトが存在しない場合、Noneを返却します。
        """
        return self._linkParent

    def Child(self, index):
        """
            このオブジェクトの子にあたるLinkedTreeObjectから指定した *index* にあたるオブジェクトを返却します。
            \ :meth:`AddChild`\ で追加された順番に0からインデックスが割り当てられます。
            通常のリスト同様、-1を指定することで、最後の要素にアクセスできます。

            :param integer index: 子要素へのインデックス
            :rtype: LinkedTreeObject
            :return: このオブジェクトに親が存在する場合、LinkedTreeObjectを返却します。
             オブジェクトが存在しない場合、例外が発生します。
        """
        return self._linkChilds[index]

    def Previous(self):
        """
            このオブジェクトの前にあたるLinkedTreeObjectを返却します。

            :rtype: LinkedTreeObjectまたはNone
            :return: このオブジェクトの親からみて、同じ階層の前にオブジェクトが存在する場合、LinkedTreeObjectを返却します。
             オブジェクトが存在しない場合、Noneを返却します。
        """
        return self._linkPrevious

    def Next(self):
        """
            このオブジェクトの後にあたるLinkedTreeObjectを返却します。

            :rtype: LinkedTreeObjectまたはNone
            :return: このオブジェクトの親からみて、同じ階層の後にオブジェクトが存在する場合、LinkedTreeObjectを返却します。
             オブジェクトが存在しない場合、Noneを返却します。
        """
        return self._linkNext

    def Index(self):
        """
            親からみたときのこのオブジェクトのインデックスを返却します。

            :rtype: インデックス値
            :return: このオブジェクトの親からみたときの子要素としてのインデックスを返却します。
             これは「self.Parent().GetChildIndex(self)」と同等です。
        """
        return self._linkParent.GetChildIndex(self)

    def Count(self):
        """
            このオブジェクトの子要素全ての要素数を返却します。これは再帰的に最下層までカウントします。
            このオブジェクトに直接紐付く子要素の数だけ取得したい場合は\ :meth:`ChildCount`\ を使用してください。

            :rtype: カウント数
            :return: このオブジェクトの子要素から全ての要素数を返却します。
        """
        ret = 1
        for child in self._linkChilds:
            ret += child.Count()
        return ret

    def ChildCount(self):
        """
            このオブジェクトに直接紐付く子要素の数を返却します。
            このオブジェクトの子要素に紐付く子要素まで再帰的にカウントした数を取得したい場合は\ :meth:`Count`\ を使用してください。

            :rtype: カウント数
            :return: このオブジェクトの子要素に直接紐付く要素数を返却します。
        """
        return len(self._linkChilds)

    def GetChildIndex(self, leaf):
        """
            このオブジェクトの子要素から *leaf* で指定したLinkedTreeObjectを検索し、該当するインデックスを返却します。
            このメソッドは、直接紐付く子要素のみ検索します。

            :param LinkedTreeObject leaf: 検索対象のLinkedTreeObject
            :rtype: インデックス値
            :return: 指定したLinkedTreeObjectが存在した場合、インデックス値を返却します。
             該当するLinkedTreeObjectを発見できなかった場合は、例外が発生します。
        """
        return self._linkChilds.index(leaf)

    def GetTopChild(self):
        """
            このオブジェクトの子要素から **先頭** に存在するLinkedTreeObjectを返却します。

            :rtype: LinkedTreeObjectまたはNone
            :return: 子要素が存在しない場合はNoneを返却します。
        """
        ret = None
        if self.ChildCount() != 0:
            ret = self._linkChilds[0]
        return ret

    def GetBottomChild(self):
        """
            このオブジェクトの子要素から **末尾** に存在するLinkedTreeObjectを返却します。

            :rtype: LinkedTreeObjectまたはNone
            :return: 子要素が存在しない場合はNoneを返却します。
        """
        ret = None
        if self.ChildCount() != 0:
            ret = self._linkChilds[-1]
        return ret

    def AddChild(self, leaf):
        """
            このオブジェクトの子要素に *leaf* で指定したLinkedTreeObjectを追加します。
            追加する要素は常に末尾に付け加えられます。
            このとき、関連する要素の親子・兄弟のリンク状態、深さなどは、子要素を含めて再帰的に再設定されます。

            :param LinkedTreeObject leaf: 追加対象のLinkedTreeObject
        """
        if not isinstance(leaf, LinkedTreeObject):
            raise TypeError, "expected type is LinkedTreeObject."
        if leaf._linkParent != None:
            raise ValueError, "This object is already associated."
        self._onAppendChild(leaf)
        leaf._linkParent = self
        leaf._setLinkedChildDepth(self._depth + 1)
        leaf._setLinkedPrevious(self.GetBottomChild())
        leaf._setLinkedNext(None)
        self._linkChilds.append(leaf)
        return self

    def DeleteChild(self, leaf):
        """
            このオブジェクトの子要素から *leaf* で指定したLinkedTreeObjectを削除します。
            これはリンク状態を削除するだけで、オブジェクト自体が破棄されるわけではありません。
            このとき、関連する要素の親子・兄弟のリンク状態、深さなどは、子要素を含めて再帰的に再設定されます。

            このメソッドはEachChildsなどを使ってループ処理中に呼び出すと、予期せぬ問題が発生する可能性があります。
            ツリー構造をループしながら連続してDeleteChildを呼び出す必要がある場合は、一度、削除対象をリストに格納し、
            削除対象リストのループで処理するようにしてください。

            :param LinkedTreeObject leaf: 削除対象のLinkedTreeObject
        """
        if not isinstance(leaf, LinkedTreeObject):
            raise TypeError, "expected type is LinkedTreeObject."
        if leaf._linkParent is not self:
            raise ValueError, "This object is already associated."
        if not leaf in self._linkChilds:
            raise KeyError, "Invalid target was supplied."
        self._onRemoveChild(leaf)
        prev = leaf._linkPrevious
        next = leaf._linkNext
        leaf._linkParent = None
        leaf._setLinkedChildDepth(0)
        leaf._setLinkedPrevious(None)
        leaf._setLinkedNext(None)
        if next != None:
            next._setLinkedPrevious(prev)
        if prev != None:
            prev._setLinkedNext(next)
        self._linkChilds.remove(leaf)
        return self

    def InsertChild(self, index, leaf):
        """
            このオブジェクトの子要素に *leaf* で指定したLinkedTreeObjectを *index* の位置へ挿入します。
            このとき、関連する要素の親子・兄弟のリンク状態、深さなどは、子要素を含めて再帰的に再設定されます。

            :param LinkedTreeObject leaf: 挿入対象のLinkedTreeObject
        """
        baseleaf = self._linkChilds[index]
        self.InsertChildBefore(baseleaf, leaf)
        return self

    def InsertChildBefore(self, baseleaf, leaf):
        """
            このオブジェクトの子要素に *leaf* で指定したLinkedTreeObjectを *baseleaf* で指定した
            LinkedTreeObjectの **前** へ挿入します。
            このとき、関連する要素の親子・兄弟のリンク状態、深さなどは、子要素を含めて再帰的に再設定されます。

            :param LinkedTreeObject baseleaf: 挿入位置を特定するLinkedTreeObject
            :param LinkedTreeObject leaf: 挿入対象のLinkedTreeObject
        """
        if not isinstance(leaf, LinkedTreeObject):
            raise TypeError, "expected type is LinkedTreeObject."
        if leaf._linkParent != None:
            raise ValueError, "This object is already associated."
        if not baseleaf in self._linkChilds:
            raise KeyError, "Invalid target was supplied."
        self._onAppendChild(leaf)
        leaf._linkParent = self
        leaf._setLinkedChildDepth(self._depth + 1)
        prev = baseleaf._linkPrevious
        if prev != None:
            prev._setLinkedNext(leaf)
        if leaf != None:
            leaf._setLinkedNext(baseleaf)
        self._linkChilds.insert(self.GetChildIndex(baseleaf), leaf)
        return self

    def InsertChildAfter(self, baseleaf, leaf):
        """
            このオブジェクトの子要素に *leaf* で指定したLinkedTreeObjectを *baseleaf* で指定した
            LinkedTreeObjectの **後** へ挿入します。
            このとき、関連する要素の親子・兄弟のリンク状態、深さなどは、子要素を含めて再帰的に再設定されます。

            :param LinkedTreeObject baseleaf: 挿入位置を特定するLinkedTreeObject
            :param LinkedTreeObject leaf: 挿入対象のLinkedTreeObject
        """
        if not isinstance(leaf, LinkedTreeObject):
            raise TypeError, "expected type is LinkedTreeObject."
        if leaf._linkParent != None:
            raise ValueError, "This object is already associated."
        if not baseleaf in self._linkChilds:
            raise KeyError, "Invalid target was supplied."
        self._onAppendChild(leaf)
        leaf._linkParent = self
        leaf._setLinkedChildDepth(self._depth + 1)
        next = baseleaf._linkNext
        if next != None:
            next._setLinkedPrevious(leaf)
        if leaf != None:
            leaf._setLinkedPrevious(baseleaf)
        self._linkChilds.insert(self.GetChildIndex(baseleaf) + 1, leaf)
        return self

    def ReplaceChild(self, targetleaf, leaf):
        """
            このオブジェクトの子要素に *leaf* で指定したLinkedTreeObjectを *targetleaf* で指定したLinkedTreeObjectと入れ替えます。
            このとき、 *targetleaf* は、子要素を含めてツリーから切り離されます。
            これは、 *leaf* をInsertChildBeforeした後に *targetleaf* をDeleteChildした動作と同じです。
            このとき、関連する要素の親子・兄弟のリンク状態、深さなどは、子要素を含めて再帰的に再設定されます。

            :param LinkedTreeObject targetleaf: 挿入位置を特定するLinkedTreeObject。これはDeleteChildされます。
            :param LinkedTreeObject leaf: 挿入対象のLinkedTreeObject
        """
        self.InsertChildBefore(targetleaf, leaf)
        self.DeleteChild(targetleaf)
        return self

    def EachParent(self):
        """
            親を辿るジェネレータイテレータを返却します。
            最初の要素にはこのオブジェクトは含まれません。
        """
        target = self._linkParent
        while target is not None:
            yield target
            target = target._linkParent

    def EachChilds(self):
        """
            子要素を辿るイテレータオブジェクトを返却します。
            最初の要素は、先頭の子要素から返却します。
        """
        return iter(self._linkChilds)

    def EachNext(self):
        """
            後を辿るジェネレータイテレータを返却します。
            最初の要素にはこのオブジェクトは含まれません。
        """
        target = self._linkNext
        while target is not None:
            yield target
            target = target._linkNext

    def EachPrevious(self):
        """
            前を辿るジェネレータイテレータを返却します。
            最初の要素にはこのオブジェクトは含まれません。
        """
        target = self._linkPrevious
        while target is not None:
            yield target
            target = target._linkPrevious

    def EachRecursion(self):
        """
            子要素を再帰的に辿るジェネレータイテレータを返却します。
            最初の要素は、先頭の子要素から最下層へ向かって返却します。
            これを使うことにより、全ての子要素を列挙することができます。
        """
        for child in self._linkChilds:
            yield child
            for grandson in child.EachRecursion():
                yield grandson

    def DebugOutput(self):
        """
            デバッグ出力を返却します。再帰的に子を辿るため、大量の文字列を返却します。
            この出力から親子・兄弟のリンク状態が判断できます。
        """
        indent = (u"\t" * self._depth)
        ret = u""
        ret += u"%s----------\r\n" % (indent)
        ret += u"%sID      = %s(%s)\r\n" % (indent, unicode(id(self)), self.__class__.__name__)
        ret += u"%sData    = %s\r\n" % (indent, unicode(self._data))
        ret += u"%sDepth   = %s\r\n" % (indent, unicode(self._depth))
        if self._linkParent == None:
            ret += u"%sParent  = %s\r\n" % (indent, unicode(None))
        else:
            ret += u"%sParent  = %s(%s)\r\n" % (indent, unicode(id(self._linkParent)), self._linkParent.__class__.__name__)
        if self._linkPrevious == None:
            ret += u"%sPrevious= %s\r\n" % (indent, unicode(None))
        else:
            ret += u"%sPrevious= %s(%s)\r\n" % (indent, unicode(id(self._linkPrevious)), self._linkPrevious.__class__.__name__)
        if self._linkNext == None:
            ret += u"%sNext    = %s\r\n" % (indent, unicode(None))
        else:
            ret += u"%sNext    = %s(%s)\r\n" % (indent, unicode(id(self._linkNext)), self._linkNext.__class__.__name__)
        if self.ChildCount() == 0:
            ret += u"%sChilds ={(%s)}\r\n"  % (indent, unicode(len(self._linkChilds)))
        else:
            ret += u"%sChilds ={(%s)\r\n"  % (indent, unicode(len(self._linkChilds)))
            ret += u"".join([u"%s" % (child.DebugOutput()) for child in self._linkChilds])
            ret += u"%s        }\r\n"  % (indent)
        return ret

    def DebugSimpleOutput(self):
        """
            シンプルなデバッグ出力を返却します。再帰的に子を辿るため、大量の文字列を返却します。
            この出力から親子・兄弟の階層構造が判断できます。
        """
        indent = (u"  " * self._depth)
        ret = u""
        #ret += u"%s%s(%s)=%s\r\n" % (indent, self.__class__.__name__, unicode(id(self)), unicode(self._data))
        ret += u"%s%s(%s)=%s\r\n" % (indent, self.__class__.__name__, unicode(id(self)), unicode(self))
        if self.ChildCount() != 0:
            ret += u"".join([u"%s" % (child.DebugSimpleOutput()) for child in self._linkChilds])
        return ret


if __name__  == "__main__":
    print u"%s Version: %s %s" % (__appname__, __version__, __copyright__)
    print u"%s" % (__license__)

