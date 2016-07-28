#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
.. module:: main
   :platform: Windows, Unix, others
   :synopsis: The main executable file to be run by user to run the application.

.. moduleauthor:: František Brožka

The main executable file to be run by user to run the application.

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

import sys

import record_dir_info

def main():
	"""Main function of the script. Parse command line arguments, check them, read input csv file correct it and write the corrected csv rows into output csv file."""
	print "initializing application RecordDirInfo"
	recordfs = record_dir_info.RecordDirInfo()
	print "recording is in progress ... this may take a long time, hours or even days, you can terminate the process e.g. by closing the terminal window"
	recordfs.run()
	print "success, recording finished succesfully"
	sys.exit(0)


if __name__ == "__main__":
	main()

