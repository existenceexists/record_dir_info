#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
.. module:: hash_file_unix
   :platform: Unix
   :synopsis: Class that provides hash sum for a file on Unix platform.

.. moduleauthor:: František Brožka

Class that provides hash sum for a file on Unix platform.

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

import subprocess

import hash_file

class HashFileUnix(hash_file.HashFile):
	
	def setAttributes(self, hashType="sha1"):
		self.hashingUtility = ''.join((hashType, "sum"))
		subprocess.check_output(['which', self.hashingUtility], stderr=subprocess.PIPE)
	
	def getFileHash(self, path):
		return subprocess.check_output([self.hashingUtility, path], stderr=subprocess.STDOUT).split('  ')[0]

