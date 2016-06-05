#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
.. module:: crtime_ext4_inode_unix_utility1
   :platform: Unix
   :synopsis: Class that provides creeation time information for a file on Unix platform on ext4 filesystem using application debugfs.

.. moduleauthor:: František Brožka

Class that provides creeation time information for a file on Unix platform on ext4 filesystem using application debugfs.

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

import re
import subprocess
import time

import crtime_ext4_inode

class CrtimeExt4InodeUnixUtility1(crtime_ext4_inode.CrtimeExt4Inode):
	
	def __init__(self, deviceName):
		try:
			self.CLIUtility = "debugfs"
			subprocess.check_output(["which", self.CLIUtility], stderr=subprocess.PIPE)
		except subprocess.CalledProcessError:
			self.CLIUtility = "/sbin/debugfs"
			subprocess.check_output(["which", self.CLIUtility], stderr=subprocess.PIPE)
		self.deviceName = deviceName
	
	def getCreationTime(self, inodeNumber):
		s = "stat <" + str(inodeNumber) + ">"
		output = subprocess.check_output([self.CLIUtility, "-R", s, self.deviceName], stderr=subprocess.PIPE)
		crtime = None
		for line in output.split('\n'):
			if re.match("crtime.*", line):
				s = line.split(' -- ')[1]
				try:
					t = time.strptime(s)
				except ValueError:
					crtime = None
				else:
					crtime = int(time.mktime(t))
				break
		return crtime
