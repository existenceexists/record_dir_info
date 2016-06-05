#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
.. module:: file_info_unix
   :platform: Unix
   :synopsis: Class that provides information about file on Unix platform.

.. moduleauthor:: František Brožka

Class that provides information about file on Unix platform.

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

import os
import subprocess
import stat

import crtime_ext4_inode_unix_utility1
import file_info
import hash_file_unix
import link_target_unix_utility1

class FileInfoUnix(file_info.FileInfo):
	
	def initCreationTimeProcessor(self, doGetCreationTime, topDir):
		# now find out what filesystem the top directory is in so we can decide if we can obtain creation time, if top dir is on ext4 filesystem then we can obtain crtime
		self.creationTimeProcessor = None
		self._getCreationTime = self.returnUnsetValue
		if not doGetCreationTime:
			return
		filesystemType = self.getFilesystemType(topDir)
		if filesystemType == 'ext4': # TODO: find out other (unix and other) filesystems that have "crtime" and that is obtainable by my script that is using debugfs
			if os.getenv("USER") == 'root':
				try:
					self.creationTimeProcessor = crtime_ext4_inode_unix_utility1.CrtimeExt4InodeUnixUtility1(self.getDeviceName(topDir))
					self._getCreationTime = self.creationTimeProcessor.getCreationTime
				except subprocess.CalledProcessError:
					# TODO: log warning "either debugfs or interpreter ruby/python.....  was not found on your system, therefore creation time will not be outputed/recorded for any file"  or raise an Exception and terminate application
					pass
			else:
				pass # TODO: log warning "script is not executed with root privileges for dir topDir therefore creation time will not be outputed"
		else:
			pass # TODO: log warning "getting creation time for filesystem type the directory topDir is on is not implemented or the filesystem type does not support creation time therefore creation time will not be outputed"
	
	def initHashingProcessor(self, doComputeHash, hashType):
		if doComputeHash and not hashType is None:
			try:
				self.hashingProcessor = hash_file_unix.HashFileUnix(hashType)
			except subprocess.CalledProcessError:
				self.hashingProcessor = None
				# TODO: log warning "hashing utility ..... was not found on your system, therefore hash will not be computed and outputed/recorded for any file"  or raise an Exception and terminate application
		else:
			self.hashingProcessor = None
	
	def initLinkProcessor(self, doGetLinkTargets):
		self.linkTargetProcessor = None
		self._getLinkTarget = self.returnUnsetValue
		if doGetLinkTargets:
			try:
				self.linkTargetProcessor = link_target_unix_utility1.LinkTargetUnixUtility1()
			except subprocess.CalledProcessError:
				self.linkTargetProcessor = None
				# TODO: log warning 
			else:
				self._getLinkTarget = self.linkTargetProcessor.getLinkTarget
	
	def getCreationTimeFromProcessor(self):
		try:
			return self._getCreationTime(self.getInodeNumber())
		except subprocess.CalledProcessError as e:
			return self.returnUnsetValue()
	
	def getFilesystemType(self, path):
		filesystemType = None
		p = subprocess.Popen(["df", "-T", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		if p.wait() == 0:
			filesystemType = p.stdout.read().split('\n')[1].split()[1]
		return filesystemType
	
	def getDeviceName(self, path):
		deviceName = None
		p = subprocess.Popen(["df", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		if p.wait() == 0:
			deviceName = p.stdout.read().split('\n')[1].split()[0]
		return deviceName

	def getChangedTime(self):
		return self.osStatResult[stat.ST_CTIME]
	
	def getFileHashFromProcessor(self, path):
		if self.doComputeHash and self.isRegularFile():
			try:
				return self.hashingProcessor.getFileHash(path)
			except subprocess.CalledProcessError:
				return self.returnUnsetValue()
		else:
			return self.returnUnsetValue()
	
	def getLinkTargetFromProcessor(self, path):
		try:
			return self._getLinkTarget(path)
		except subprocess.CalledProcessError:
			return self.returnUnsetValue()
