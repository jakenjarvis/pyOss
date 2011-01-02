# -*- coding: utf-8 -*-
# This file encoding UTF-8 no BOM. このファイルの文字コードはUTF-8 BOM無しです。
import sys
# あなたの環境に合わせて、pyOssフォルダまでのパスを書いてください。￥マークは２つで１文字を表します。
sys.path.insert(0, u"C:\\Games\\Oblivion\\Data\\pyOss")

from pyOssLib.v1_0.MasterlistLib import *
from pyOssLib.v1_0.UserlistLib import *

################################################################################
# マスタリストの編集を記録して、ユーザーリストを作成します。
#
# Sample06.pyを先に見てください。
################################################################################
# 入力するファイル名
infullpath = u"C:\\Games\\Oblivion\\Data\\BOSS\\masterlist.txt"

# 出力するファイル名
outfullpath = u"test_userlist.txt"


# マスタリストの枠を作り、内部でLoadします。
master = Masterlist(infullpath)

# 記録内容の初期化
master.ClearRecord()
# 記録開始
master.BeginRecord()


# マスタリストを直接操作します。
# --------------------------------------------------
# 今回は試しに、UOPをESMsの前に移動してみます。（見やすいように先頭のほうを操作していますが、本来BOSSでは「禁止された移動」ですので注意してください）
master.MoveBefore(u"UOP", u"ESMs")
# --------------------------------------------------

# マスタリストをユーザーオペレーションを使って操作します。
# --------------------------------------------------
# オペレーション１を作成します。これは実質「master.InsertBefore(u"JP Group", u"ESMs")」と同じです。
operation1 = UserOperation()
operation1.AddNewComment(u"このコメントは使われません。") #
operation1.AddNewRuleAdd(u"JP Group")
operation1.AddNewSortBefore(u"ESMs")
operation1.AddNewBlank()                                  #この場合ブランク行やコメント行は効果がありません。（これはあくまでユーザーリストへの効果のみです）

# ユーザーオペレーションを直接Operaterで処理すれば、その内容をマスタリストへ更新できます。
# また、このように、上記MoveBeforeを使ったマスタリストへの更新等と、Operaterの更新を混ぜて使うことも可能です。
master.Operater(operation1)
# --------------------------------------------------


# 記録終了
master.EndRecord()
# 記録内容からユーザーリストを生成します。
user = master.GenerateUserlistFromRecord()


# ユーザーリストを保存する。
user.Save(outfullpath)


# 生成したユーザーリストの内容を確認すると、MoveBeforeの操作とOperaterの操作の両方が反映されていることがわかります。
# ただし、UserOperationのコメント行やブランク行は反映されません。（これは操作の結果から記録をおこしているためです）

