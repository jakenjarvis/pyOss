# -*- coding: utf-8 -*-
# This file encoding UTF-8 no BOM. このファイルの文字コードはUTF-8 BOM無しです。
import sys
# あなたの環境に合わせて、pyOssフォルダまでのパスを書いてください。￥マークは２つで１文字を表します。
sys.path.insert(0, u"C:\\Games\\Oblivion\\Data\\pyOss")

from pyOssLib.v1_0.MasterlistLib import *
from pyOssLib.v1_0.UserlistLib import *

################################################################################
# ユーザーリストを編集します。（オペレーションを追加します。）
#
# マスタリストを編集する目的で、ユーザーリストを組み立てる場合は、この方法は手間がかかるので避けたほうが無難です。（Sample04.pyを参照）
# これとは別に、マスタリストの編集内容を記録し、記録内容からユーザーリストを生成する方法があります。（Sample08.pyを参照）
################################################################################
# 入力するファイル名
infullpath = u"C:\\Games\\Oblivion\\Data\\BOSS\\userlist.txt"

# 出力するファイル名
outfullpath = u"test_userlist.txt"


# ユーザーリストの枠を作ります。
user = Userlist()

# ユーザーリストのファイルを指定して、読み込みます。（このLoadをせずに以下の処理を実行すると、新規作成もできます。その場合はSaveのファイル名は省略できません）
user.Load(infullpath)


# 以下のユーザーリストと同じものを作ります。
# --------------------------------------------------
# // ESMsグループの後ろに新規グループ「JP Group」を作成する。
# ADD: JP Group
# AFTER: ESMs
# 
# // 新しく作った「JP Group」の先頭にJPWikiMod.espを追加する。
# // かつコメントに、JPWikiMod.espがJPWikiModAlt_by_Cytosine.espとは互換性がないことを示す。
# ADD: JPWikiMod.esp
# TOP: JP Group
# APPEND: " JPWikiModAlt_by_Cytosine.esp
# 
# // UOPグループをJPWikiMod.espの後ろに並べる。（ちょっと強引ですがBOSSではできないサンプルということで。）
# OVERRIDE: UOP
# AFTER: JPWikiMod.esp
# --------------------------------------------------


# 操作するには、以下の方法があります。
# --------------------------------------------------
# 空白行を追加します。
#operation1.AddNewBlank()
# コメント行を追加します。
#operation1.AddNewComment(comment)
# ルールを追加します。オペレーションに最初に一つだけ追加できます。
#operation1.AddNewRuleAdd(name)
#operation1.AddNewRuleOverride(name)
#operation1.AddNewRuleFor(name)
# ソートを追加します。オペレーションにルールの後に一つだけ追加できます。
#operation1.AddNewSortBefore(name)
#operation1.AddNewSortAfter(name)
#operation1.AddNewSortTop(name)
#operation1.AddNewSortBottom(name)
# メッセージを追加します。オペレーションにルールかソートの後に複数追加できます。
#operation1.AddNewMessageAppend(name)
#operation1.AddNewMessageReplace(name)
# --------------------------------------------------
# AddNewBlankとAddNewCommentは、必要がなければ使う必要はありません。


# オペレーション１を作成します。
operation1 = UserOperation()
operation1.AddNewComment(u"ESMsグループの後ろに新規グループ「JP Group」を作成する。")
operation1.AddNewRuleAdd(u"JP Group")
operation1.AddNewSortAfter(u"ESMs")
operation1.AddNewBlank()

# オペレーション２を作成します。
operation2 = UserOperation()
operation2.AddNewComment(u"新しく作った「JP Group」の先頭にJPWikiMod.espを追加する。")
operation2.AddNewComment(u"かつコメントに、JPWikiMod.espがJPWikiModAlt_by_Cytosine.espとは互換性がないことを示す。")
operation2.AddNewRuleAdd(u"JPWikiMod.esp")
operation2.AddNewSortTop(u"JP Group")
operation2.AddNewMessageAppend(u"\" JPWikiModAlt_by_Cytosine.esp")    # ダブルクオーテーションを表現するために￥マークを頭につけてます。「\"」で「"」を表すことになります。
operation2.AddNewBlank()

# オペレーション３を作成します。
operation3 = UserOperation()
operation3.AddNewComment(u"UOPグループをJPWikiMod.espの後ろに並べる。（ちょっと強引ですがBOSSではできないサンプルということで。）")
operation3.AddNewRuleOverride(u"UOP")
operation3.AddNewSortAfter(u"JPWikiMod.esp")
operation3.AddNewBlank()


# ユーザーリストにオペレーションを追加します。（読み込んだユーザーリストの後ろに追加されます）
user.AddChild(operation1)
user.AddChild(operation2)
user.AddChild(operation3)


# ユーザーリストを保存する。
# もし、読み込んだユーザーリストを上書きしてしまいたい場合は、
# ファイル名を省略して以下のように書くこともできます。
# user.Save()
# 今回は、サンプルを動かして、勝手に上書きしないように、別のファイルへ保存します。
user.Save(outfullpath)

# 出来上がった反映後のユーザーリストを、元のファイルと比較してみてください。
# WinMerge、Rekisa、DFなどのフリーソフトを使うと簡単に比較できます。




