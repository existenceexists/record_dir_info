#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
.. module:: link_target_unix_utility1
   :platform: Unix
   :synopsis: Class that provides information on a target file path for link file on Unix platform using application readlink.

.. moduleauthor:: František Brožka

Class that provides information on a target file path for link file on Unix platform using application readlink.

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

import link_target

class LinkTargetUnixUtility1(link_target.LinkTarget):
	
	def __init__(self):
		self.CLIUtility = "readlink"
		subprocess.check_output(["which", self.CLIUtility], stderr=subprocess.PIPE)
	
	def getLinkTarget(self, path):
		return subprocess.check_output([self.CLIUtility, path], stderr=subprocess.PIPE).rstrip('\r\n')

