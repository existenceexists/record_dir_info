#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
.. module:: record_dir_info
   :platform: Windows, Unix, others
   :synopsis: The main class of the application.

.. moduleauthor:: František Brožka

The main class of the application.
Initializes instances of other classes of the application.

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

import argparse
import codecs
import logging
import os
import re
import socket
import sys
import string
import time

import file_info
import file_info_unix
import file_info_windows

class RecordDirInfo():
	
	def __init__(self):
		self.appName = "RecordDirInfo"
		self.appVersion = "1.0.0"
		# set values
		self.formatSequencePath = "%p"
		self.formatSequenceInodeNumber = "%i"
		self.formatSequenceFileModeNumber = "%M"
		self.formatSequenceFileType = "%F"
		self.formatSequenceSizeInBytes = "%s"
		self.formatSequenceAccessRightsOctal = "%a"
		self.formatSequenceUserId = "%u"
		self.formatSequenceUserName = "%U"
		self.formatSequenceGroupId = "%g"
		self.formatSequenceGroupName = "%G"
		self.formatSequenceNumberLinks = "%L"
		self.formatSequenceCreationTime = "%W"
		self.formatSequenceLastChangeTime = "%Z"
		self.formatSequenceLastAccessTime = "%X"
		self.formatSequenceLastModificationTime = "%Y"
		self.formatSequenceHash = "%H"
		self.formatSequenceLinkTarget = "%T"
		self.formattingSequencesAndPositions = ((self.formatSequencePath, 0), (self.formatSequenceInodeNumber, 1), (self.formatSequenceFileModeNumber, 2), (self.formatSequenceFileType, 3), (self.formatSequenceSizeInBytes, 4), (self.formatSequenceAccessRightsOctal, 5), (self.formatSequenceUserId, 6), (self.formatSequenceUserName, 7), (self.formatSequenceGroupId, 8), (self.formatSequenceGroupName, 9), (self.formatSequenceNumberLinks, 10), (self.formatSequenceCreationTime, 11), (self.formatSequenceLastChangeTime, 12), (self.formatSequenceLastModificationTime, 13), (self.formatSequenceLastAccessTime, 14), (self.formatSequenceHash, 15), (self.formatSequenceLinkTarget, 16))
		self.defaultTimeFormatSequence = '%s'
		self.regularFileSymbol = "f"
		self.directorySymbol = "d"
		self.symbolicLinkSymbol = "l"
		self.blockSpecialDeviceSymbol = "b"
		self.characterSpecialDeviceSymbol = "c"
		self.socketSymbol = "s"
		self.FIFOSymbol = "p"
		self.fileTypesSymbols = [self.regularFileSymbol, self.directorySymbol, self.symbolicLinkSymbol, self.blockSpecialDeviceSymbol, self.characterSpecialDeviceSymbol, self.socketSymbol, self.FIFOSymbol]
		self.defaultEncoding = 'utf-8'
		self.doLog = True
		self.loggingLevel = logging.DEBUG
		self.loggingFormat = '%(asctime)s:%(levelname)s:%(message)s', 
		# set default values, these values can be changed with setAttributes() or setAttribute()
		self.setChangeableDefaultAttributes()
		# set values derived from previous attributes
		self.defaultFormat = self.fieldDelimiter.join([s[0] for s in self.formattingSequencesAndPositions])
		# decide correct file info class
		if os.name == 'posix':
			self.fileInfoProcessorClass = file_info_unix.FileInfoUnix
		elif os.name == 'nt':
			self.fileInfoProcessorClass = file_info_windows.FileInfoWindows
		else:
			self.fileInfoProcessorClass = file_info.FileInfo
	
	def setChangeableDefaultAttributes(self):
		# set default values, these values can be changed with setAttributes() or setAttribute()
		self.quoteChars="\"\"\""
		self.fieldDelimiter = ";"
		self.commentChars = "#"
		self.hashType = "sha1"
		self.unsetValueSymbol = "-"
		self.customFormat = None
		self.doUseCustomFormat = False
		self.customTimeFormat = None
		self._formatTime = self.convertIntToUnicode
		self.doOutputHash = True
		self.doGetCreationTime = True
		self.doGetLinkTargets = True
		self.fileTypesToOutput = None
		
	def setTopDir(self, topDir):
		self.topDir = topDir
		self.fileInfoProcessor = self.fileInfoProcessorClass(topDir, doComputeHash=self.doOutputHash, hashType=self.hashType, doGetCreationTime=self.doGetCreationTime, doGetLinkTargets=self.doGetLinkTargets)
	
	def resetChangeableAttributes(self, doOutputAbsolutePaths=None, doQuotePaths=None, hashType=None, fieldDelimiter=None, commentChars=None, quoteChars=None , customFormat=None, customTimeFormat=None, fileTypesToOutput=None):
		self.setChangeableDefaultAttributes()
		if not hashType is None:
			self.hashType = hashType
		if not commentChars is None:
			self.commentChars = commentChars
		if not quoteChars is None:
			self.quoteChars = quoteChars
		if not fieldDelimiter is None:
			self.fieldDelimiter = fieldDelimiter
		self.quotePathCallback = self.returnValueUnchanged
		if not doQuotePaths is None and doQuotePaths is True:
			self.quotePathCallback = self.quotePath
		if not customFormat is None:
			self.customFormat = customFormat
			self.doUseCustomFormat = True
			if not re.search(self.formatSequenceHash, self.customFormat):
				self.doOutputHash = False
			if not re.search(self.formatSequenceCreationTime, self.customFormat):
				self.doGetCreationTime = False
			if not re.search(self.formatSequenceLinkTarget, self.customFormat):
				self.doGetLinkTargets = False
		if not customTimeFormat is None:
			self.customTimeFormat = customTimeFormat
			self._formatTime = self.formatTimeCustom
		if fileTypesToOutput == self.fileTypesSymbols:
			fileTypesToOutput = None
		if not fileTypesToOutput is None:
			self.fileTypesToOutput = fileTypesToOutput
			if not self.regularFileSymbol in fileTypesToOutput:
				self.doOutputHash = False
			if not self.symbolicLinkSymbol in fileTypesToOutput:
				self.doGetLinkTargets = False
	
	def setAttribute(self, attributeName, attributeValue):
		if not hasattr(self, attributeName):
			raise AttributeError(''.join(("instance '", self.__name__, "' of class '", type(self).__name__, "' has no attribute '", attributeName, "'")))
		setattr(self, attributeName, attributeValue)
	
	def parseCommandLineArguments(self):
		"""initialize argparse.ArgumentParser and add command line arguments to it and return the initialized instance"""
		parser = argparse.ArgumentParser(description="Fanda\'s script to record information about directory (called here \"top directory\" or \"top dir\") and it\'s content. Recommended usage: 1) If you have unix system file structure and you want to record your whole filesystem structure, it is recommended to run this script in two steps as follows: sudo recorddirinfo --absolute-paths --quoted-paths --time-format '%Y-%m-%d_%H-%M-%S_%Z' --top-dir '/home/' $(date +'%Y-%m-%d_%H-%M-%S_%Z')._home_ ; sudo recorddirinfo --absolute-paths --quoted-paths --format '%p;%i;%M;%F;%s;%a;%u;%U;%g;%G;%L;%W;%Z;%Y;%X;;%T' --time-format '%Y-%m-%d_%H-%M-%S_%Z' --exclude-regex '/home/.*' --top-dir / $(date +'%Y-%m-%d_%H-%M-%S_%Z').__all__-excluding-_home_ ;  The reason for this is that at the noted second run of the script, hash values of files are not generated and recorded by the script as it is hard for some system files to get hash values.  2) If you run this script on a unix system and you want to record all info including time of birth, run this script as superuser e.g. run it with sudo: sudo recorddirinfo --top-dir / - ")
		parser.add_argument('-a', '--absolute-paths', help='Top dirs command line arguments will be converted to absolute paths before being processed and checked against regular expression patterns to be excluded.', action='store_true', required=False)
		parser.add_argument('-u', '--quoted-paths', help=string.replace(''.join(('If given the paths in the output file will be quoted, i.e. surrounded with  \'', self.quoteChars, '\'.')), '%', '%%'), action='store_true', required=False)
		parser.add_argument('-i', '--field-delimiter', help='Delimiter that will delimit fields in the output, output file. Defaults to \';\'. If --format is given this option is ignored.', default=u';', type=unicode, required=False)
		parser.add_argument('-e', '--exclude-regex', help='Regular expression to exclude paths from being processed and outputed. Can be given multiple times. E.g. to exclude of directory foo/bar/ (and all it\'s content) but not foo/barbar/ give --exclude-regex \'foo/bar$\'. Recognized regular expression patterns info can be found on https://docs.python.org/2.7/library/re.html. If --absolute-paths is given the regex is checked against absolute paths.', metavar='REGEX', type=unicode, action='append', required=False)
		parser.add_argument('-s', '--hash-type', help='Specify hash algorithm to be used for computing hash value of regular files. Defaults to \'sha1\'.', default=u'sha1', type=unicode, required=False)
		parser.add_argument('-f', '--format', help=string.replace(''.join(('Specify custom format to be used as outputed record line for each path under top directory. Default format is \'', self.defaultFormat, '\'. Format sequences are similar to the ones specified for the option --format of the GNU stat utility. The valid format sequences are: %p .. path, quoted if --quoted-paths given ; %i .. inode number ; %M .. file mode integer number (missing in GNU stat) ; %F .. file type (one of f (regular file), d (directory), l (symbolic link), c (character special device), b (block special device), i (FIFO), s (socket)), %s .. total size (in bytes) ; %a .. access rights in octal ; %u .. user ID of owner ; %U .. user name of owner, this may be an incorrect name e.g. if top dir is on a mounted device originally comming from another computer while the user id exists on both computers etc. ; %g .. group ID of owner ; %G .. group name of owner, this may be an incorrect name e.g. if top dir is on a mounted device originally comming from another computer while the group id exists on both computers etc. ; %L .. number of links (missing in GNU stat) ; %W .. time  of  file birth, seconds since Epoch ; %Z .. time of last change, seconds since Epoch ; %Y .. time of last modification, seconds since Epoch ; %X .. time of last access, seconds since Epoch ; %H .. hash value as computed by an external hashing utility')), '%', '%%'), type=unicode, required=False)
		parser.add_argument('-t', '--time-format', help=string.replace(''.join(('Specify custom time format to be used as outputed timestamps in record lines for each time information. Default format is \'', self.defaultTimeFormatSequence, '\'. Format sequences are similar to the ones specified for the option --format of the GNU date utility. The valid format sequences can be found in python manual for the module time on https://docs.python.org/2.7/library/time.html#time.strftime and additionally also the sequene \'', self.defaultTimeFormatSequence, '\' can be given as seconds since epoch (on Unix it is seconds since 1970-01-01 00:00:00 UTC)')), '%', '%%'), type=unicode, required=False)
		parser.add_argument('-y', '--file-type', help='If given, only info for paths of the given type will be outputed. Can be given multiple times (of course with different values). If given with value already given, then the repetition is ignored.', type=unicode, action='append', choices=self.fileTypesSymbols, required=False)
		parser.add_argument('-c', '--continue-from', help='Continue from path. If --absolute-paths is given it is converted to absolute paths and then checked against absolute paths of top dir(s). (TODO-?: currently not: ?If --absolute-paths is given, this should be absolute path?). Can be combined with --file-append.', metavar='PATH', type=unicode, required=False)
		parser.add_argument('-p', '--file-append', help='Append output to existing file <output-file> instead of creating a new file. Can be combined with --continue-from', action='store_true', required=False)
		parser.add_argument('-q', '--quiet', help='Supress warnings and error messages and other messages produced by the script.', action='store_true', required=False) # TODO: implement --quiet
		parser.add_argument('-d', '--top-dir', help='Path to top directory that will be searched by the script. Can be given multiple times.', type=str, action='append', required=True)
		parser.add_argument('output_file_path', help='Path to output file. Give \'-\' if you want to print to stdout in terminal, in such case also consider using the option "-q, --quiet". TODO-check.', metavar='<output-file>', type=unicode) # adding "required=True" produces "TypeError: 'required' is an invalid argument for positionals"
		self.arguments = parser.parse_args()
	
	def checkCommandLineArguments(self):
		# check if output file exists:
		if self.arguments.output_file_path == "-":
			pass
		elif os.path.exists(self.arguments.output_file_path):
			if not self.arguments.file_append:
				raise Exception(''.join(("Error. The output file '", self.arguments.output_file_path, "' already exists."))) # TODO: define my own subclass of Exception ?
		# if --file-append given, output file should exist:
		if self.arguments.file_append:
			if not os.path.exists(self.arguments.output_file_path):
				raise Exception(''.join(("Error. The output file '", self.arguments.output_file_path, "' does not exist and argument --file-append given so the file should exist."))) # TODO: define my own subclass of Exception ?
		for i, topDir in enumerate(self.arguments.top_dir):
			self.arguments.top_dir[i] = self.stripTrailingSlash(topDir)
		if not self.arguments.continue_from is None:
			self.arguments.continue_from = self.stripTrailingSlash(self.arguments.continue_from)
		# make the list file_type filled with unique values and in particular order
		if not self.arguments.file_type is None:
			l = list(self.fileTypesSymbols)
			for t in self.fileTypesSymbols:
				if t not in self.arguments.file_type:
					l.remove(t)
			self.arguments.file_type = l
	
	def recordingCreationInfo(self):
		loggedUserName = os.getenv("USER")
		if not os.getenv("SUDO_USER") is None:
			loggedUserName = os.getenv("SUDO_USER")
		return ''.join((self.commentChars, " created on ", time.strftime("%Y-%m-%d_%H-%M-%S_%Z", time.localtime()), " by user ", os.getenv("USER"), " on ", loggedUserName, '@', socket.gethostname(), " by application ", self.appName, " version ", self.appVersion))
	
	def recordingFieldsInfo(self):
		if self.doUseCustomFormat:
			f = self.arguments.format
		else:
			f = self.defaultFormat
		return ''.join((self.commentChars, " record line format: \"\"\"", f, "\"\"\""))
	
	def recordingTopDirInfo(self, topDir):
		return ''.join((self.commentChars, "--- --top-dir \"\"\"", os.path.abspath(topDir), "\"\"\":"))
	
	def commandInfo(self):
		return ''.join((self.commentChars, " script run with arguments: \"\"\"", ' '.join(sys.argv), "\"\"\""))
	
	def startOfRecordingInfo(self):
		return ''.join((self.commentChars, " --- --- start of recording"))
	
	def recordingFinishedInfo(self):
		return ''.join((self.commentChars, " recording finished at ", time.strftime("%Y-%m-%d_%H-%M-%S_%Z", time.localtime())))
	
	def endOfRecordingInfo(self):
		return ''.join((self.commentChars, " --- --- end of recording (recording finished succesfully)"))
	
	def returnValueUnchanged(self, value):
		return value
	
	def returnUnsetValueSymbol(self):
		return self.unsetValueSymbol
	
	def quotePath(self, path):
		return ''.join((self.quoteChars, path, self.quoteChars))
	
	def formatTimeCustom(self, seconds):
		if seconds == self.unsetValueSymbol:
			return seconds
		f = string.replace(self.customTimeFormat, '%Z', 'UTC')
		f = string.replace(f, self.defaultTimeFormatSequence, unicode(seconds))
		return time.strftime(f, time.gmtime(float(seconds)))
	
	def returnJustUnicodeValue(self, fileName):
		if type(fileName) == unicode:
			return fileName
		else:
			return unicode(fileName, self.defaultEncoding, errors='replace')
	
	def convertIntToUnicode(self, number):
		return unicode(number)
	
	def stripTrailingSlash(self, path):
		# get rid of a trailing slash if not root dir:
		if path[-1] == os.sep:
			pathSplitted = list(os.path.splitdrive(path))
			if not (pathSplitted[1] == os.sep or pathSplitted[1] == os.sep + os.sep):
				# if not root dir
				pathSplitted[1] = pathSplitted[1].rstrip(os.sep)
			path = u''.join((pathSplitted[0], pathSplitted[1]))
		return path
	
	def getFileTypeSymbol(self):
		if self.fileInfoProcessor.isRegularFile():
			return self.regularFileSymbol
		elif self.fileInfoProcessor.isDirectory():
			return self.directorySymbol
		elif self.fileInfoProcessor.isSymbolicLink():
			return self.symbolicLinkSymbol
		elif self.fileInfoProcessor.isCharacterSpecialDevice():
			return self.characterSpecialDeviceSymbol
		elif self.fileInfoProcessor.isBlockSpecialDevice():
			return self.blockSpecialDeviceSymbol
		elif self.fileInfoProcessor.isFIFO():
			return self.FIFOSymbol
		elif self.fileInfoProcessor.isSocket():
			return self.socketSymbol
		else:
			return self.returnUnsetValueSymbol()
	
	def getUserName(self):
		name = self.fileInfoProcessor.getUserName()
		if name is None:
			return self.returnUnsetValueSymbol()
		else:
			return name
	
	def getGroupName(self):
		name = self.fileInfoProcessor.getGroupName()
		if name is None:
			return self.returnUnsetValueSymbol()
		else:
			return name
	
	def getFileHash(self):
		if self.doOutputHash:
			h = self.fileInfoProcessor.getFileHash()
			if h is None:
				return self.returnUnsetValueSymbol()
			else:
				return h
		else:
			return self.returnUnsetValueSymbol()
	
	def getCreationTime(self):
		creationTime = self.fileInfoProcessor.getCreationTime()
		if creationTime is None:
			return self.returnUnsetValueSymbol()
		else:
			return creationTime
	
	def getLinkTarget(self):
		linkTarget = self.fileInfoProcessor.getLinkTarget()
		if linkTarget is None:
			return self.returnUnsetValueSymbol()
		else:
			return self.quotePathCallback(self.returnJustUnicodeValue(linkTarget))
	
	def log(self, message):
		# TODO: use module logging to output into terminal and log file, see logging HOWTO
		pass
	
	def createInfo(self, path):
		if self.pathSetSuccessfully:
			return (self.quotePathCallback(self.returnJustUnicodeValue(path)), 
				unicode(self.fileInfoProcessor.getInodeNumber()), 
				unicode(self.fileInfoProcessor.getFileModeNumber()), 
				self.getFileTypeSymbol(), 
				unicode(self.fileInfoProcessor.getSizeBytes()), 
				self.fileInfoProcessor.getAccessRightsOctal(), 
				unicode(self.fileInfoProcessor.getUserID()), 
				self.getUserName(), 
				unicode(self.fileInfoProcessor.getGroupID()), 
				self.getGroupName(), 
				unicode(self.fileInfoProcessor.getNumberOfLinks()), 
				self._formatTime(self.getCreationTime()), 
				self._formatTime(self.fileInfoProcessor.getChangedTime()), 
				self._formatTime(self.fileInfoProcessor.getModificationTime()), 
				self._formatTime(self.fileInfoProcessor.getAccessTime()), 
				self.getFileHash(), 
				self.getLinkTarget())
		else:
			return self.createEmptyInfo(path)
	
	def createEmptyInfo(self, path):
		return (self.quotePathCallback(path), 
			self.returnUnsetValueSymbol(), 
			self.returnUnsetValueSymbol(), 
			self.returnUnsetValueSymbol(), 
			self.returnUnsetValueSymbol(), 
			self.returnUnsetValueSymbol(), 
			self.returnUnsetValueSymbol(), 
			self.returnUnsetValueSymbol(), 
			self.returnUnsetValueSymbol(), 
			self.returnUnsetValueSymbol(), 
			self.returnUnsetValueSymbol(), 
			self.returnUnsetValueSymbol(), 
			self.returnUnsetValueSymbol(), 
			self.returnUnsetValueSymbol(), 
			self.returnUnsetValueSymbol(), 
			self.returnUnsetValueSymbol(), 
			self.returnUnsetValueSymbol())
	
	def createRecordLine(self, info):
		return self.fieldDelimiter.join(info)
	
	def createRecordLineCustomFormat(self, info):
		f = self.customFormat
		for symbol, i in self.formattingSequencesAndPositions:
			f = string.replace(f, symbol, info[i])
		return f
	
	def writeLineToTerminal(self, line):
		sys.stdout.write(line)
		sys.stdout.write(os.linesep)
		sys.stdout.flush()
	
	def writeLineToFile(self, line):
		self.outputFile.write(''.join((line, '\n'))) # don't use os.linesep, see http://stackoverflow.com/questions/6159900/correct-way-to-write-line-to-file-in-python
	
	def setPath(self, topDir, continueFromPath=None):
		"""Returns True if the path and it's info should be outputed, False otherwise"""
		try:
			self.fileInfoProcessor.setPathAndOnlyStat(topDir)
		except OSError:
			self.pathSetSuccessfully = False
		else:
			self.pathSetSuccessfully = True
		if not self.fileTypesToOutput is None:
			symbol = self.getFileTypeSymbol()
			if not symbol in self.fileTypesToOutput:
				return False
		if continueFromPath:
			return False
		else:
			self.fileInfoProcessor.setAddinionalInfo()
			return True
	
	def recordTopDir(self, topDir, writeCallback, formattingCallback, doOutputAbsolutePaths, pathExludeRegexes, continueFromPath=None):
		writeCallback(self.recordingTopDirInfo(topDir))
		topDir = self.stripTrailingSlash(topDir)
		if doOutputAbsolutePaths:
			topDir = os.path.abspath(topDir)
		if not type(topDir) == unicode:
			d = topDir
			try:
				topDir = unicode(d, encoding=self.defaultEncoding, errors='strict')
			except UnicodeDecodeError:
				topDir = d
		self.setTopDir(topDir)
		if not continueFromPath is None:
			if not type(continueFromPath) == unicode:
				p = continueFromPath
				try:
					continueFromPath = unicode(p, encoding=self.defaultEncoding, errors='strict')
				except UnicodeDecodeError:
					continueFromPath = p
			continueFromPath = self.stripTrailingSlash(continueFromPath)
			if doOutputAbsolutePaths:
				continueFromPath = os.path.abspath(continueFromPath)
			if not os.path.exists(continueFromPath):
				continueFromPath = None
		if not continueFromPath is None:
			if os.path.isabs(continueFromPath):
				continueFromPath = list(os.path.splitdrive(continueFromPath))
				continueFromPath.extend(continueFromPath.pop(1).split(os.sep))
				c = list(continueFromPath)
				for i in range(1, len(c)):
					if c[i] in (u"", ""):
						continueFromPath.remove(c[i])
			else:
				continueFromPath = continueFromPath.split(os.sep)
			if os.path.isabs(topDir):
				t = list(os.path.splitdrive(topDir))
				t.extend(t.pop(1).split(os.sep))
				tl = list(t)
				for i in range(1, len(tl)):
					if tl[i] in (u"", ""):
						t.remove(tl[i])
			else:
				t = t.split(os.sep)
			c = list(continueFromPath)
			lengthT = len(t) - 1
			for i in range(len(t)):
				if t[i] != c[i]:
					continueFromPath = None
					break
				if i < lengthT:
					continueFromPath[0] = os.sep.join((continueFromPath[0], continueFromPath.pop(1)))
		if self.setPath(topDir, continueFromPath):
			writeCallback(formattingCallback(self.createInfo(topDir)))
		self.walkTree(topDir, writeCallback, formattingCallback, pathExludeRegexes=pathExludeRegexes, continueFromPath=continueFromPath)
	
	def walkTree(self, topDir, writeCallback, formattingCallback, pathExludeRegexes, continueFromPath=None):
		"""
		recursively descend the directory tree rooted at top,
		calling the callback function for each file
		
		based on "example" on https://docs.python.org/2/library/stat.html
		based on "example" on https://docs.python.org/2/library/os.html#os.walk
		"""
		# TODO: implement sorting functions that will e.g. sort names alphabetically and descend into directories before recording files in the parent directory etc.
		dirs = []
		try:
			names = sorted(os.listdir(topDir), key=self.returnJustUnicodeValue)
		except OSError:
			return
		if continueFromPath:
			for f in names:
				if f == continueFromPath[1]:
					names = names[names.index(f):]
					continueFromPath[0] = os.path.join(continueFromPath[0], continueFromPath[1])
					continueFromPath.pop(1)
					if len(continueFromPath) == 1:
						# found final path to be continued-from
						continueFromPath.pop(0)
						names = names[1:]
					break
		for f in names:
			if not type(f) == unicode:
				# if this value returned by os.listdir is not unicode then non utf-8 characters are in the name
				# so we cannot stat or further process the path so just write it without any stat info and don't recurse into it if directory
				if type(topDir) == unicode:
					topDir = topDir.encode(self.defaultEncoding)
			path = os.path.join(topDir, f)
			doExcludePath = False
			if not pathExludeRegexes is None:
				for r in pathExludeRegexes:
					if re.search(r, path):
						doExcludePath = True
						break
			if doExcludePath:
				continue
			if self.setPath(path, continueFromPath):
				writeCallback(formattingCallback(self.createInfo(path)))
			if self.fileInfoProcessor.isDirectory():
				dirs.append(path)
		for d in dirs:
			self.walkTree(d, writeCallback, formattingCallback, pathExludeRegexes, continueFromPath)
	
	def recordTopDirs(self, topDirs, writeCallback, formattingCallback, doOutputAbsolutePaths, pathExludeRegexes, continueFromPath=None):
		writeCallback(self.startOfRecordingInfo())
		writeCallback(self.recordingCreationInfo())
		writeCallback(self.commandInfo())
		writeCallback(self.recordingFieldsInfo())
		for topDir in topDirs:
			self.recordTopDir(topDir, writeCallback=writeCallback, formattingCallback=formattingCallback, doOutputAbsolutePaths=doOutputAbsolutePaths, pathExludeRegexes=pathExludeRegexes, continueFromPath=continueFromPath)
		writeCallback(self.recordingFinishedInfo())
		writeCallback(self.endOfRecordingInfo())
	
	def recordDirs(self, topDirs, outputFilePath, doOutputAbsolutePaths=False, pathExludeRegexes=None, appendToFile=None, continueFromPath=None):
		if appendToFile is True:
			mode = 'ab'
		else:
			mode = 'wb'
		if self.doUseCustomFormat:
			formattingCallback = self.createRecordLineCustomFormat
		else:
			formattingCallback = self.createRecordLine
		if outputFilePath == "-":
			self.recordTopDirs(topDirs, writeCallback=self.writeLineToTerminal, formattingCallback=formattingCallback, doOutputAbsolutePaths=doOutputAbsolutePaths, pathExludeRegexes=pathExludeRegexes, continueFromPath=continueFromPath)
		else:
			with codecs.open(outputFilePath, encoding=self.defaultEncoding, mode=mode) as self.outputFile:
				self.recordTopDirs(topDirs, writeCallback=self.writeLineToFile, formattingCallback=formattingCallback, doOutputAbsolutePaths=doOutputAbsolutePaths, pathExludeRegexes=pathExludeRegexes, continueFromPath=continueFromPath)
	
	# --------- section: the main function, run it
	
	def run(self):
		"""Main function of the script. Parse command line arguments, check them, read input csv file correct it and write the corrected csv rows into output csv file."""
		self.parseCommandLineArguments()
		self.checkCommandLineArguments()
		self.resetChangeableAttributes(doOutputAbsolutePaths=self.arguments.absolute_paths, doQuotePaths=self.arguments.quoted_paths, hashType=self.arguments.hash_type, fieldDelimiter=self.arguments.field_delimiter, customFormat=self.arguments.format, customTimeFormat=self.arguments.time_format, fileTypesToOutput=self.arguments.file_type)
		self.log("******* Script starting. *******")
		self.recordDirs(topDirs=self.arguments.top_dir, outputFilePath=self.arguments.output_file_path, doOutputAbsolutePaths=self.arguments.absolute_paths, pathExludeRegexes=self.arguments.exclude_regex, appendToFile=self.arguments.file_append, continueFromPath=self.arguments.continue_from)
		self.log("******* Script finished succesfully. *******")

