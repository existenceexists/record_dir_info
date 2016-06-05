#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
.. module:: file_info_windows
   :platform: Windows
   :synopsis: Class that provides information about file on Windows platform.

.. moduleauthor:: František Brožka

Class that provides information about file on Windows platform.

"""

u"""
    Copyright 2016 František Brožka

    This file is part of RecordDirInfo.

    RecordDirInfo is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    RecordDirInfo is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with RecordDirInfo.  If not, see <http://www.gnu.org/licenses/>.

"""

import file_info

class FileInfoWindows(file_info.FileInfo):
	
	def getCreationTime(self):
		return self.osStatResult[stat.ST_CTIME]
	
	def getChangedTime(self):
		return self.returnUnsetValue()
