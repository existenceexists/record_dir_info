#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
.. module:: file_info
   :platform: Windows, Unix, others
   :synopsis: Class that provides information about file.

.. moduleauthor:: František Brožka

Class that provides information about file.

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

import grp
import os
import pwd
import stat

class FileInfo():
	#TODO: put this class into a separate my-project and git repo
	
	def __init__(self, topDir, doComputeHash, hashType, doGetCreationTime=True, doGetLinkTargets=True):
		self.topDir = topDir
		self.doComputeHash = doComputeHash
		self.initHashingProcessor(doComputeHash, hashType)
		self.doGetCreationTime = doGetCreationTime
		self.initCreationTimeProcessor(doGetCreationTime, topDir)
		self.doGetLinkTargets = doGetLinkTargets
		self.initLinkProcessor(doGetLinkTargets)
	
	def initCreationTimeProcessor(self, doGetCreationTime, topDir):
		"""Can be hidden by subclass."""
		self.creationTimeProcessor = None
	
	def initHashingProcessor(self, doComputeHash, hashType):
		"""Can be hidden by subclass."""
		self.hashingProcessor = None
	
	def initLinkProcessor(self, doGetLinkTargets):
		self.linkTargetProcessor = None
	
	def returnUnsetValue(self, *ignoredArgs):
		return None
	
	def getFileHashFromProcessor(self, path):
		return self.returnUnsetValue()
	
	def setPathAndAllInfo(self, path):
		self.setPathAndOnlyStat(path)
		self.setAddinionalInfo()
	
	def setPathAndOnlyStat(self, path):
		self.path = path
		self.osStatResult = os.lstat(path)
		self.st_mode = self.osStatResult.st_mode
		self.creationTime = None
		self.fileHash = None
		self.linkTarget = None
	
	def setAddinionalInfo(self):
		self.creationTime = self.getCreationTimeFromProcessor()
		self.fileHash = self.getFileHashFromProcessor(self.path)
		self.linkTarget = self.getLinkTargetFromProcessor(self.path)
	
	def getFileHash(self):
		return self.fileHash
	
	def getLinkTarget(self):
		return self.linkTarget
	
	def isDirectory(self):
		return bool(stat.S_ISDIR(self.st_mode))
	
	def isRegularFile(self):
		return bool(stat.S_ISREG(self.st_mode))
	
	def isSymbolicLink(self):
		return bool(stat.S_ISLNK(self.st_mode))
	
	def isCharacterSpecialDevice(self):
		return bool(stat.S_ISCHR(self.st_mode))
	
	def isBlockSpecialDevice(self):
		return bool(stat.S_ISBLK(self.st_mode))
	
	def isSocket(self):
		return bool(stat.S_ISSOCK(self.st_mode))
	
	def isFIFO(self):
		return bool(stat.S_ISFIFO(self.st_mode))
	
	def isSocket(self):
		return bool(stat.S_ISSOCK(self.st_mode))
	
	def getInodeNumber(self):
		return self.osStatResult[stat.ST_INO]
	
	def getFileModeNumber(self):
		return self.osStatResult[stat.ST_MODE]
	
	def getSizeBytes(self):
		return self.osStatResult[stat.ST_SIZE]
	
	def getUserID(self):
		return self.osStatResult[stat.ST_UID]
	
	def getUserName(self):
		uid = self.getUserID()
		try:
			userInfo = pwd.getpwuid(uid)
		except KeyError:
			return self.returnUnsetValue()
		return userInfo[0]
	
	def getGroupID(self):
		return self.osStatResult[stat.ST_GID]
	
	def getGroupName(self):
		gid = self.getGroupID()
		try:
			groupInfo = grp.getgrgid(gid)
		except KeyError:
			return self.returnUnsetValue()
		return groupInfo[0]
	
	def getNumberOfLinks(self):
		return self.osStatResult[stat.ST_NLINK]
	
	def getAccessRightsOctal(self):
		return oct(self.st_mode)[-3:]
	
	def getCreationTime(self):
		return self.creationTime
	
	def getCreationTimeFromProcessor(self):
		return self.returnUnsetValue()
	
	def getAccessTime(self):
		return self.osStatResult[stat.ST_ATIME]
	
	def getModificationTime(self):
		return self.osStatResult[stat.ST_MTIME]
	
	def getChangedTime(self):
		"""To be hidden by subclasses if such functionality is available."""
		return self.returnUnsetValue()
	
	def getLinkTargetFromProcessor(self, path):
		"""To be hidden by subclasses if such functionality is available."""
		return self.returnUnsetValue()
	
	def outputFileInfo(self):
		# TODO: delete this method
		# TODO: string=stat+crtime+md5sum
		pass
