# -*- coding: utf-8 -*-
# This file encoding UTF-8 no BOM. このファイルの文字コードはUTF-8 BOM無しです。
import sys
# あなたの環境に合わせて、pyOssフォルダまでのパスを書いてください。￥マークは２つで１文字を表します。
sys.path.insert(0, u"C:\\Games\\Oblivion\\Data\\pyOss")

from pyOssLib.v1_0.MasterlistLib import *
from pyOssLib.v1_0.UserlistLib import *

################################################################################
# マスタリストをユーザーリストの内容で更新します。（自作のUpdateUserToMaster.pyを作る）
################################################################################
# 入力するファイル名
in1fullpath = u"C:\\Games\\Oblivion\\Data\\BOSS\\masterlist.txt"
in2fullpath = u"C:\\Games\\Oblivion\\Data\\BOSS\\userlist.txt"

# 出力するファイル名
outfullpath = u"test_masterlist.txt"

# --------------------------------------------------
# マスタリストの枠を作ります。
master = Masterlist()
# マスタリストのファイルを指定して、読み込みます。
master.Load(in1fullpath)
# --------------------------------------------------
# 上記の操作は、以下のように１行で書くこともできます。（内部でLoadが呼び出されます）
# master = Masterlist(in1fullpath)


# --------------------------------------------------
# ユーザーリストの枠を作ります。
user = Userlist()
# ユーザーリストのファイルを指定して、読み込みます。
user.Load(in2fullpath)
# --------------------------------------------------
# 上記の操作は、以下のように１行で書くこともできます。（内部でLoadが呼び出されます）
# user = Userlist(in2fullpath)


# ユーザーリストの内容をマスタリストへ反映する。
master.Operater(user)

# マスタリストを保存する。
# もし、読み込んだマスタリストを上書きしてしまいたい場合は、
# ファイル名を省略して以下のように書くこともできます。
# master.Save()
# 今回は、サンプルを動かして、勝手に上書きしないように、別のファイルへ保存します。
master.Save(outfullpath)

# 出来上がった反映後のマスタリストを、元のファイルと比較してみてください。
# WinMerge、Rekisa、DFなどのフリーソフトを使うと簡単に比較できます。

