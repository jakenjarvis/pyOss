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
out1fullpath = u"test_masterlist.txt"

# マスタリストの枠を作ります。
master = Masterlist()
# マスタリストのファイルを指定して、読み込みます。
master.Load(infullpath)

# 空のマスタリストを作成します。こちらはロードせずに使います。
master2 = Masterlist()


# UOPグループを検索します。最初に見つかったグループオブジェクトがuopにセットされます。
uop = master.FindData(u"GroupName", u"UOP")

# --------------------------------------------------
# UOPグループのクローン（コピー）を作成します。ここではUOPの中に存在するブロックや行を全てコピーしてます。
# これによって、masterにつながっているUOPグループとは別に、新しいどこにもつながってないUOPのツリーができあがります。
newuop = uop.Clone(True)
# 空のマスタリストに新しく作ったUOPを追加します。（CloneでUOPにぶら下がっているもの全てをコピーしているので、そのまま全部追加されます）
master2.AddChild(newuop)
# --------------------------------------------------


# --------------------------------------------------
# 今回の場合は、masterに変更を加えても最終的にmasterを保存していないので、
# 以下のようにmasterから切り離してから、master2へ追加することもできます。
# どのオブジェクトも、一つのツリーにしか存在できないことに注意が必要です。
#（uopをDeleteChildせずにAddChildしようとするとエラーになります）
#
# UOPグループの親にあたるオブジェクトを取得します。
#uopparent = uop.Parent()
# UOPグループをツリーから切り離します。
#uopparent.DeleteChild(uop)
# 空のマスタリストに切り離したUOPを追加します。
#master2.AddChild(uop)
# --------------------------------------------------



# 新しく作ったマスタリストを保存する。（UOPグループだけ存在するマスタリストになります）
master2.Save(out1fullpath)
