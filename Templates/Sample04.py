# -*- coding: utf-8 -*-
# This file encoding UTF-8 no BOM. このファイルの文字コードはUTF-8 BOM無しです。
import sys
# あなたの環境に合わせて、pyOssフォルダまでのパスを書いてください。￥マークは２つで１文字を表します。
sys.path.insert(0, u"C:\\Games\\Oblivion\\Data\\pyOss")

from pyOssLib.v1_0.MasterlistLib import *
from pyOssLib.v1_0.UserlistLib import *

################################################################################
# マスタリストを編集します。
################################################################################
# 入力するファイル名
infullpath = u"C:\\Games\\Oblivion\\Data\\BOSS\\masterlist.txt"

# 出力するファイル名
outfullpath = u"test_masterlist.txt"


# マスタリストの枠を作り、内部でLoadします。
master = Masterlist(infullpath)


# 操作するには、以下の方法があります。
# --------------------------------------------------
# 既に存在するMODsやグループを移動する場合に使います。
# 指定した名称が存在しない場合は例外が発生するので注意が必要です）
#master.MoveBefore(srcname, basename)
#master.MoveAfter(srcname, basename)
#master.MoveTop(srcname, basename)
#master.MoveBottom(srcname, basename)

# マスタリストに存在しないMODsやグループを新しく追加する場合に使います。
# 存在チェックを行わないので、重複しても気にせず追加するので注意が必要です）
#master.InsertBefore(newobject, basename)
#master.InsertAfter(newobject, basename)
#master.InsertTop(newobject, basename)
#master.InsertBottom(newobject, basename)

# 存在するMODsにメッセージを追加、または入れ替えする場合に使います。
#master.AppendLine(newlinestring, basename)
#master.ReplaceLine(newlinestring, basename)

# マスタリストに存在する場合は、Move系と同じように移動し、存在しない場合はInsert系と同じように追加します。
# （内部で存在チェック後にMoveかInsertのどちらかを呼び出します）
#master.ReplaceBefore(newobjectorname, basename)
#master.ReplaceAfter(newobjectorname, basename)
#master.ReplaceTop(newobjectorname, basename)
#master.ReplaceBottom(newobjectorname, basename)
# --------------------------------------------------

# 今回は試しに、UOPをESMsの前に移動してみます。（見やすいように先頭のほうを操作していますが、本来BOSSでは「禁止された移動」ですので注意してください）
master.MoveBefore(u"UOP", u"ESMs")


# お試し用
#master.ReplaceBefore(u"UOP", u"ESMs")
#master.InsertBefore(u"new group", u"ESMs")
#master.ReplaceBefore(u"new group", u"ESMs")


# マスタリストを保存する。
# もし、読み込んだマスタリストを上書きしてしまいたい場合は、
# ファイル名を省略して以下のように書くこともできます。
# master.Save()
# 今回は、サンプルを動かして、勝手に上書きしないように、別のファイルへ保存します。
master.Save(outfullpath)

# 出来上がった反映後のマスタリストを、元のファイルと比較してみてください。
# WinMerge、Rekisa、DFなどのフリーソフトを使うと簡単に比較できます。

