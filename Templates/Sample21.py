# -*- coding: utf-8 -*-
# This file encoding UTF-8 no BOM. このファイルの文字コードはUTF-8 BOM無しです。
import sys
# あなたの環境に合わせて、pyOssフォルダまでのパスを書いてください。￥マークは２つで１文字を表します。
sys.path.insert(0, u"C:\\Games\\Oblivion\\Data\\pyOss")

from pyOssLib.v1_0.MasterlistLib import *
from pyOssLib.v1_0.UserlistLib import *

################################################################################
# マスタリストを作成します。（オブジェクト生成時に渡す方法と、子要素に追加していく方法）
################################################################################
# 出力するファイル名
out1fullpath = u"test_masterlist.txt"
out2fullpath = u"Debug.txt"
out3fullpath = u"DebugSimple.txt"

# マスタリストの枠を作ります。
master = Masterlist()

master.AddChild(
    Group(u"Test01 Group", [
        Block([
            Line(u"TestMod01.esm"),
            Line(u"\\ comment1"),
            Line(u"% {{BASH:Factions}}"),
            Line(u"? test1 comment."),
        ]),
    ]))

master.AddChild(
    Block([
        Line(u"TestMod02.esp"),
        Line(u"\\ comment2"),
    ]))

master.AddChild(
    Group(u"Test02 Group", [
        Group(u"Test03 Group", [
            Block([
                Line(u"TestMod03.esp"),
                Line(u"% {{BASH:Names,Stats,Relev,Delev,Invent,Sound,Factions,Graphics}}"),
                Line(u"? test2 comment."),
            ]),
            Block([
                Line(u"TestMod04.esp"),
                Line(u"% {{BASH:Names,Stats,Relev,Delev,Invent,Sound,Factions,Graphics}}"),
                Line(u"? test3 comment."),
                Line(u"? test4 comment."),
                Line(u"? test5 comment."),
            ]),
        ]),
    ]))

# 作成したマスタリストを保存します。
master.Save(out1fullpath)

# 読み込みしたマスタリストの解析結果をデバッグ出力します。
master.DebugSave(out2fullpath)

# 読み込みしたマスタリストの解析結果をデバッグ出力します。（シンプル版）
master.DebugSimpleSave(out3fullpath)
