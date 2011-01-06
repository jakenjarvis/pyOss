This readme is made by the machine translation.


Introduction
================================================================================
pyOss is 'Python BOSS Support Software'.
This is tools and libraries, for 'The Elder Scrolls IV: Oblivion' and 'Better Oblivion Sorting Software - BOSS'.
masterlist.txt and userlist.txt can be easily edited with Python scripts.

pyOss doesn't sort MODs. The text file is edited(masterlist.txt and userlist.txt).
However, The operation that cannot be done in BOSS is possible in pyOss.


Rule and sort.
+----------+---------+----------+----------+--------+--------+
| RULE     |         | SORT     |          | BOSS   | pyOss  |
+==========+=========+==========+==========+========+========+
| OVERRIDE | [GROUP] |  BEFORE  | [GROUP]  |   Yes  |   Yes  |
+----------+---------+----------+----------+--------+--------+
| OVERRIDE | [GROUP] |  BEFORE  | [MODs ]  |   No   |   Yes  |
+----------+---------+----------+----------+--------+--------+
| OVERRIDE | [MODs ] |  BEFORE  | [GROUP]  |   No   |   Yes  |
+----------+---------+----------+----------+--------+--------+
| OVERRIDE | [MODs ] |  BEFORE  | [MODs ]  |   Yes  |   Yes  |
+----------+---------+----------+----------+--------+--------+
| OVERRIDE | [GROUP] |  AFTER   | [GROUP]  |   Yes  |   Yes  |
+----------+---------+----------+----------+--------+--------+
| OVERRIDE | [GROUP] |  AFTER   | [MODs ]  |   No   |   Yes  |
+----------+---------+----------+----------+--------+--------+
| OVERRIDE | [MODs ] |  AFTER   | [GROUP]  |   No   |   Yes  |
+----------+---------+----------+----------+--------+--------+
| OVERRIDE | [MODs ] |  AFTER   | [MODs ]  |   Yes  |   Yes  |
+----------+---------+----------+----------+--------+--------+
| OVERRIDE | [GROUP] |  TOP     | [GROUP]  |   No   |   Yes  |
+----------+---------+----------+----------+--------+--------+
| OVERRIDE | [GROUP] |  TOP     | [MODs ]  |   No   |   Yes  |
+----------+---------+----------+----------+--------+--------+
| OVERRIDE | [MODs ] |  TOP     | [GROUP]  |   Yes  |   Yes  |
+----------+---------+----------+----------+--------+--------+
| OVERRIDE | [MODs ] |  TOP     | [MODs ]  |   No   |   Yes  |
+----------+---------+----------+----------+--------+--------+
| OVERRIDE | [GROUP] |  BOTTOM  | [GROUP]  |   No   |   Yes  |
+----------+---------+----------+----------+--------+--------+
| OVERRIDE | [GROUP] |  BOTTOM  | [MODs ]  |   No   |   Yes  |
+----------+---------+----------+----------+--------+--------+
| OVERRIDE | [MODs ] |  BOTTOM  | [GROUP]  |   Yes  |   Yes  |
+----------+---------+----------+----------+--------+--------+
| OVERRIDE | [MODs ] |  BOTTOM  | [MODs ]  |   No   |   Yes  |
+----------+---------+----------+----------+--------+--------+
| ADD      | [GROUP] |  BEFORE  | [GROUP]  |   No   |   Yes  |
+----------+---------+----------+----------+--------+--------+
| ADD      | [GROUP] |  BEFORE  | [MODs ]  |   No   |   Yes  |
+----------+---------+----------+----------+--------+--------+
| ADD      | [MODs ] |  BEFORE  | [GROUP]  |   No   |   Yes  |
+----------+---------+----------+----------+--------+--------+
| ADD      | [MODs ] |  BEFORE  | [MODs ]  |   Yes  |   Yes  |
+----------+---------+----------+----------+--------+--------+
| ADD      | [GROUP] |  AFTER   | [GROUP]  |   No   |   Yes  |
+----------+---------+----------+----------+--------+--------+
| ADD      | [GROUP] |  AFTER   | [MODs ]  |   No   |   Yes  |
+----------+---------+----------+----------+--------+--------+
| ADD      | [MODs ] |  AFTER   | [GROUP]  |   No   |   Yes  |
+----------+---------+----------+----------+--------+--------+
| ADD      | [MODs ] |  AFTER   | [MODs ]  |   Yes  |   Yes  |
+----------+---------+----------+----------+--------+--------+
| ADD      | [GROUP] |  TOP     | [GROUP]  |   No   |   Yes  |
+----------+---------+----------+----------+--------+--------+
| ADD      | [GROUP] |  TOP     | [MODs ]  |   No   |   Yes  |
+----------+---------+----------+----------+--------+--------+
| ADD      | [MODs ] |  TOP     | [GROUP]  |   Yes  |   Yes  |
+----------+---------+----------+----------+--------+--------+
| ADD      | [MODs ] |  TOP     | [MODs ]  |   No   |   Yes  |
+----------+---------+----------+----------+--------+--------+
| ADD      | [GROUP] |  BOTTOM  | [GROUP]  |   No   |   Yes  |
+----------+---------+----------+----------+--------+--------+
| ADD      | [GROUP] |  BOTTOM  | [MODs ]  |   No   |   Yes  |
+----------+---------+----------+----------+--------+--------+
| ADD      | [MODs ] |  BOTTOM  | [GROUP]  |   Yes  |   Yes  |
+----------+---------+----------+----------+--------+--------+
| ADD      | [MODs ] |  BOTTOM  | [MODs ]  |   No   |   Yes  |
+----------+---------+----------+----------+--------+--------+

Rule and message.
+----------+---------+----------+----------+--------+--------+
| RULE     |         | MESSAGE  |          | BOSS   | pyOss  |
+==========+=========+==========+==========+========+========+
| FOR      | [GROUP] |  APPEND  | [GROUP]  |   --   |   --   |
+----------+---------+----------+----------+--------+--------+
| FOR      | [GROUP] |  APPEND  | [MODs ]  |   --   |   --   |
+----------+---------+----------+----------+--------+--------+
| FOR      | [MODs ] |  APPEND  | [GROUP]  |   --   |   --   |
+----------+---------+----------+----------+--------+--------+
| FOR      | [MODs ] |  APPEND  | [MODs ]  |   Yes  |   Yes  |
+----------+---------+----------+----------+--------+--------+
| FOR      | [GROUP] |  REPLACE | [GROUP]  |   --   |   --   |
+----------+---------+----------+----------+--------+--------+
| FOR      | [GROUP] |  REPLACE | [MODs ]  |   --   |   --   |
+----------+---------+----------+----------+--------+--------+
| FOR      | [MODs ] |  REPLACE | [GROUP]  |   --   |   --   |
+----------+---------+----------+----------+--------+--------+
| FOR      | [MODs ] |  REPLACE | [MODs ]  |   Yes  |   Yes  |
+----------+---------+----------+----------+--------+--------+



Requirements
================================================================================
Python2.6



Installation
================================================================================
1. Python2.6 installed.(Wrye_Python_03a-22368.exe is desirable.)

2. Set the path environment variable.
    add python folder
        ;C:\Python26;C:\Python26\Scripts;

3. Oblivion's Data folder to copy. (pyOss)
    exist files as follows:
        C:\Games\Oblivion\Oblivion.exe
        C:\Games\Oblivion\Data\Oblivion.esm
        C:\Games\Oblivion\Data\BOSS.exe
        C:\Games\Oblivion\Data\pyOss
        C:\Games\Oblivion\Data\pyOss\pyOssLib
        C:\Games\Oblivion\Data\pyOss\pyOssLib\v1_0



pyOss tools
================================================================================
Help parameter '-h' option.

* MasterlistChecker.py
    If the format of masterlist.txt is checked, and abnormality is found, the problem part is output to the file.

    Usage: MasterlistChecker.py [Options] MASTERLISTFILE

* MasterlistDownloader.py
    The latest version of masterlist.txt is downloaded.

    Usage: MasterlistDownloader.py [Options]

* UpdateUserToMaster.py
    This actually applies content of definition of userlist.txt to masterlist.txt, and rewrites the masterlist. (Or, the output is also possible to another file.)

    Usage: UpdateUserToMaster.py [Options] MASTERLISTFILE USERLISTFILE

* DiffMasterToUser.py
    The difference of two masterlists is extracted, and the difference is output to the file by "Form of the userlist".
    This is a supplementary tool to do help that makes the userlist since BOSS1.6.
    It is assumed to compare before the masterlist is edited after it edits it.

    Usage: DiffMasterToUser.py [Options] BASEMASTERLISTFILE EDITMASTERLISTFILE



Example
================================================================================
* UpdateUserToMaster.py

    masterlist.txt
    --------------------------------------------------
    ---(Omission)---
    --------------------------------------------------

    userlist.txt
    --------------------------------------------------
    ADD: JP Group
    AFTER: ESMs

    ADD: JPWikiMod.esp
    TOP: JP Group
    APPEND: " JPWikiModAlt_by_Cytosine.esp

    OVERRIDE: UOP
    AFTER: JPWikiMod.esp
    --------------------------------------------------

    > UpdateUserToMaster.py masterlist.txt userlist.txt -o masterlist2.txt

    masterlist2.txt
    --------------------------------------------------
    \BeginGroup\: ESMs
    ---(Omission)---
    \EndGroup\\
    \BeginGroup\: JP Group
    JPWikiMod.esp
    " JPWikiModAlt_by_Cytosine.esp
    \BeginGroup\: UOP
    ---(Omission)---
    \EndGroup\\
    \EndGroup\\
    --------------------------------------------------


* DiffMasterToUser.py

    masterlist1.txt
    --------------------------------------------------
    \BeginGroup\: ESMs
    \----
    Oblivion.esm
    ? Masterlist Information: $Revision$, $Date$, $LastChangedBy$
    SoVvM.esm
    MERP Data.esm
    MiddleEarth.esm
    \EndGroup\\
    --------------------------------------------------

    masterlist2.txt
    --------------------------------------------------
    \BeginGroup\: ESMs
    \----
    Oblivion.esm
    ? Masterlist Information: $Revision$, $Date$, $LastChangedBy$
    Oblivion_1.1.esm
    ? A modding esm - do not use in game, deactivate.
    Oblivion_SI.esm
    ? A modding esm - do not use in game, deactivate.
    SoVvM.esm
    MERP Data.esm
    MiddleEarth.esm
    \EndGroup\\
    --------------------------------------------------

    > DiffMasterToUser.py masterlist1.txt masterlist2.txt -o diffuserlist.txt

    diffuserlist.txt
    --------------------------------------------------
    ADD: Oblivion_1.1.esm
    AFTER: Oblivion.esm
    APPEND: ? A modding esm - do not use in game, deactivate.

    ADD: Oblivion_SI.esm
    AFTER: Oblivion_1.1.esm
    APPEND: ? A modding esm - do not use in game, deactivate.
    --------------------------------------------------



Python Script Libraries "pyOssLib"
================================================================================
The sample script is prepared. Please refer to pyOss\Templates folder.

Example1
    Example1.py
    --------------------------------------------------
    #---(Omission)---
    masterfile = Masterlist(u"masterlist.txt")
    masterfile.InsertAfter(u"JP Group", u"ESMs")
    masterfile.InsertTop(u"JPWikiMod.esp", u"JP Group")
    masterfile.AppendLine(u"\" JPWikiModAlt_by_Cytosine.esp", u"JPWikiMod.esp")
    masterfile.MoveAfter(u"UOP", u"JPWikiMod.esp")
    masterfile.Save()
    --------------------------------------------------

Example2
    Example2.py
    --------------------------------------------------
    #---(Omission)---
    masterfile = Masterlist(u"masterlist.txt")
    userfile = Userlist(u"userlist.txt")
    masterfile.Operater(userfile)
    masterfile.Save()
    --------------------------------------------------



Manual
================================================================================
There is no English manual. Only in this readme.

A Japanese manual is here. Someone please translate....
http://pyoss.limewebs.com/



License
================================================================================
GNU General Public License v3

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



Using Libraries
================================================================================
Universal Encoding Detector
chardet-2.0.1 for Python 2, released 2009-11-10
http://chardet.feedparser.org/



Acknowledgment
================================================================================
Oblivion all over the world now believe that the player is using, 'Better Oblivion Sorting Software - BOSS' thanks to all the team.
Moreover, we wish to express our gratitude to the Bethesda Softworks Co. that produces the great game named Oblivion.
On this occasion, the people of you and the MOD producers who are contributing to Japanese localization also give a reward.
It would be greatly appreciated if your work is reduced even a little by this tool.

Thanks!
