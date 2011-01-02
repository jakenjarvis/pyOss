# -*- coding: utf-8 -*-
# This file encoding UTF-8 no BOM. このファイルの文字コードはUTF-8 BOM無しです。
import sys
# あなたの環境に合わせて、pyOssフォルダまでのパスを書いてください。￥マークは２つで１文字を表します。
sys.path.insert(0, u"C:\\Games\\Oblivion\\Data\\pyOss")

from pyOssLib.v1_0.MasterlistLib import *
from pyOssLib.v1_0.UserlistLib import *

################################################################################
# マスタリストを読み込み、デバッグ出力します。
################################################################################
# 入力するファイル名
infullpath = u"C:\\Games\\Oblivion\\Data\\BOSS\\masterlist.txt"

# 出力するファイル名
out1fullpath = u"Debug.txt"
out2fullpath = u"DebugSimple.txt"


# マスタリストの枠を作ります。
master = Masterlist()

# マスタリストのファイルを指定して、読み込みます。
master.Load(infullpath)

# 読み込みしたマスタリストの解析結果をデバッグ出力します。
master.DebugSave(out1fullpath)

# 読み込みしたマスタリストの解析結果をデバッグ出力します。（シンプル版）
master.DebugSimpleSave(out2fullpath)

