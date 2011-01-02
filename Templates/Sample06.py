# -*- coding: utf-8 -*-
# This file encoding UTF-8 no BOM. このファイルの文字コードはUTF-8 BOM無しです。
import sys
# あなたの環境に合わせて、pyOssフォルダまでのパスを書いてください。￥マークは２つで１文字を表します。
sys.path.insert(0, u"C:\\Games\\Oblivion\\Data\\pyOss")

from pyOssLib.v1_0.MasterlistLib import *
from pyOssLib.v1_0.UserlistLib import *

################################################################################
# マスタリストを編集します。（新規ユーザーリストや新規グループを使う）
#
# Sample04.pyとSample05.pyを先に見てください。
################################################################################
# 入力するファイル名
infullpath = u"C:\\Games\\Oblivion\\Data\\BOSS\\masterlist.txt"

# 出力するファイル名
outfullpath = u"test_masterlist.txt"


# マスタリストの枠を作り、内部でLoadします。
master = Masterlist(infullpath)

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


# マスタリストに新規グループや新規MODsを追加する方法として、このような方法もあります。
# --------------------------------------------------
# 上記で追加した「JP Group」を検索して、グループオブジェクトを取得する。
#（「GroupName」が「JP Group」の値を格納しているオブジェクトを検索して、最初に見つかったオブジェクトを返却する。見つからない場合はNoneが返却される）
jpgroup = master.FindData(u"GroupName", u"JP Group")
if jpgroup != None:
    # 検索対象が見つかるとNone以外が返却される。

    # 新規グループを作成する。
    newgroup = Group(u"New Group1")
    # 行を格納するブロックを作成します。
    jpwikimodblock = Block()
    # 新しい行を作成する（これはMODsタイプになります）
    jpwikimodline = Line(u"JPWikiMod.esp")
    # ブロックに新しい行を追加します。
    jpwikimodblock.AddChild(jpwikimodline)
    # 「New Group1」に「JPWikiMod.esp」を追加する。（グループ→ブロック→行の関係を維持しなければならない）
    newgroup.AddChildToBottom(jpwikimodblock)

    # 「New Group1」を「JP Group」の中に入れる。
    jpgroup.AddChildToBottom(newgroup)

    # グループにMODやグループを追加する場合、AddChildではなく、AddChildToBottomを使うことに注意しましょう。詳しくはAPIリファレンス参照
# --------------------------------------------------


# 上記は以下のように簡潔に書くことができます。この方法だと、複数のグループとMODsを一気に作成して追加することができます。Sample07.py参照。
# --------------------------------------------------
#jpgroup = master.FindData(u"GroupName", u"JP Group")
#if jpgroup != None:
#    # 検索対象が見つかるとNone以外が返却される。
#
#    # 新規グループを作成する。
#    newgroup = Group(u"New Group1", [
#        Block([Line(u"JPWikiMod.esp")])
#    ])
#    # 「New Group1」を「JP Group」の中に入れる。
#    jpgroup.AddChildToBottom(newgroup)
# --------------------------------------------------


# マスタリストを保存する。
# もし、読み込んだマスタリストを上書きしてしまいたい場合は、
# ファイル名を省略して以下のように書くこともできます。
# master.Save()
# 今回は、サンプルを動かして、勝手に上書きしないように、別のファイルへ保存します。
master.Save(outfullpath)

# 出来上がった反映後のマスタリストを、元のファイルと比較してみてください。
# WinMerge、Rekisa、DFなどのフリーソフトを使うと簡単に比較できます。

