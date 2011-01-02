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
outfullpath = u"test_masterlist.txt"

# マスタリストの枠を作ります。
master = Masterlist()

# --------------------------------------------------
master.AddChild(
    Block([
        Line(u"\\ Sample01_masterlist.txt"),
        Line(u"\\ create by pyOss"),
        Line(u""),
    ]))

master.AddChild(
    Group(u"JP Mod Group", [
        Block([
            Line(u"JPWikiMod.esp"),
            Line(u"? 他のMODへの影響が大きいので、安全を考えてここ（先頭の方）に移動しました。"),
        ]),
        Block([
            Line(u"JPWikiModAlt_by_Cytosine.esp"),
            Line(u"? これを入れた場合は JPWikiMod.esp はロードしないこと。"),
        ]),
    ]))

# カンマ区切りの最後の要素の後ろにあるカンマは、Pythonの場合はあってもなくても正しく判断してくれます。（カラの要素ができたりしない）
# なので、「[1,2,3,]」と「[1,2,3]」は同じです。「かぎ括弧[]」の詳細はPythonの言語仕様の「リスト」を調べてみてください。
# AddChildに渡せるのは一つのオブジェクトだけなので、上記の場合は、２つのAddChildをまとめることはできません。
# --------------------------------------------------



# 上記の追加と下記の追加は、まったく同じ処理です。
# --------------------------------------------------
# ヘッダ部分のコメントを作ります。
headerblock = Block()
headerblock.AddChild(Line(u"\\ Sample01_masterlist.txt"))
headerblock.AddChild(Line(u"\\ create by pyOss"))
headerblock.AddChild(Line(u""))
# ヘッダをマスタリストへ追加します。
master.AddChild(headerblock)

# 新しいグループ「JP Mod Group」を作ります。
jpmodgroup = Group(u"JP Mod Group")

# JPWikiMod.espを追加するためにブロックを用意します。
jpwikimodblock = Block()
jpwikimodblock.AddChild(Line(u"JPWikiMod.esp"))
jpwikimodblock.AddChild(Line(u"? 他のMODへの影響が大きいので、安全を考えてここ（先頭の方）に移動しました。"))
# グループにBlockを追加します。
jpmodgroup.AddChildToBottom(jpwikimodblock)

# JPWikiModAlt_by_Cytosine.espを追加するためにブロックを用意します。
jpwikimodalt_by_cytosineblock = Block()
jpwikimodalt_by_cytosineblock.AddChild(Line(u"JPWikiModAlt_by_Cytosine.esp"))
jpwikimodalt_by_cytosineblock.AddChild(Line(u"? これを入れた場合は JPWikiMod.esp はロードしないこと。"))
# グループにBlockを追加します。
jpmodgroup.AddChildToBottom(jpwikimodalt_by_cytosineblock)

# 「JP Mod Group」グループをマスタリストへ追加します。
master.AddChild(jpmodgroup)
# --------------------------------------------------
# グループにMODやグループを追加する場合、AddChildではなく、AddChildToBottomを使うことに注意しましょう。詳しくはAPIリファレンス参照




# 作成したマスタリストを保存します。
master.Save(outfullpath)

