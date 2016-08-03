#!/usr/bin/python
# -*- coding: utf-8 -*-

"""\
runinfls.py
  version 1.10 (created on 2011-09-13)
  Developed by Adam Twardoch. Opensource under the MIT License.
USAGE
  python runinfls.py fontlabscripttorun
DESCRIPTION
  This script and Python module allows to execute FontLab scripts
  (written in Python) in FontLab Studio from the commandline 
  or from within other Python scripts. 
  Please look into the docstrings of the functions for more info.
""" 

import sys, os, os.path, tempfile, subprocess, warnings, shutil

def _warn(message, exit = False):
	sys.stderr.write(message + "\n")
	sys.stderr.flush()
	if exit: 
		sys.exit(2)

def _getTempFilename(fileext = ""):
  tmpf = tempfile.NamedTemporaryFile(suffix=fileext)
  tmpfn = tmpf.name
  tmpf.close()
  return tmpfn

def findFontLabStudio():
	"""
	Tries to locate FontLab Studio on the user's hard drive and returns 
	a dictionary with keys: 
	  "found" : True if FontLab Studio has been found, False if not found 
	    (then other keys will not exist)
	  "os" : "Windows" if on Windows, "Mac OS X" if on Mac OS X
	  "version" : guessed version of FLS
	  "path" : path to FontLab Studio
	  "subprocesscall" : first part of the args list to be used 
	    with subprocess.Popen
	Currently, following versions of FontLab Studio are supported: 
	  FontLab Studio 5.0.x on Windows
	  FontLab Studio 5.0.x on Mac OS X
	  FontLab Studio 5.1 on Mac OS X
	If none of the applications can be found, the function attempts to 
	launch the .flw file through the system shell. 
	"""
	fontlabapp = {"found" : False, "os" : "Unknown"}
	# Check for Microsoft Windows
	if sys.platform == "win32": 
		fontlabapp["os"] = "Windows"
		if "PROGRAMFILES" in os.environ: 
			appfolder = os.environ["PROGRAMFILES"]
		else: 
			appfolder = os.path.join("C:", "Program Files")
		if os.path.exists(os.path.join(appfolder, "FontLab", "Studio5", "Studio5.exe")): 
			fontlabapp["found"] = True
			fontlabapp["version"] = "5.0"
			fontlabapp["path"] = os.path.join(appfolder, "FontLab", "Studio5", "Studio5.exe")
			fontlabapp["subprocesscall"] = [fontlabapp["path"]]
		else: 
			fontlabapp["found"] = True
			fontlabapp["version"] = "?.?"
			fontlabapp["path"] = ""
			fontlabapp["subprocesscall"] = ["explorer"]
	# Check for Mac OS X
	elif sys.platform == "darwin":
		fontlabapp["os"] = "Mac OS X" 
		appfolder = os.path.join("/", "Applications")
		if os.path.exists(os.path.join(appfolder, "FontLab Studio 5.app")): 
			fontlabapp["found"] = True
			fontlabapp["version"] = "5.1"
			fontlabapp["path"] = os.path.join(appfolder, "FontLab Studio 5.app")
			fontlabapp["subprocesscall"] = ["open", "-a", "FontLab Studio 5.app"] # "-n" parameter indicates new instance
		elif os.path.exists(os.path.join(appfolder, "FontLab Studio", "FontLab Studio.app")): 
			fontlabapp["found"] = True
			fontlabapp["version"] = "5.0"
			fontlabapp["path"] = os.path.join(appfolder, "FontLab Studio", "FontLab Studio.app")
			fontlabapp["subprocesscall"] = ["open", "-a", "FontLab Studio.app"] # "-n" parameter indicates new instance
		else: 
			fontlabapp["found"] = True
			fontlabapp["version"] = "?.?"
			fontlabapp["path"] = ""
			fontlabapp["subprocesscall"] = ["open"] 
	else: 
		_warn("FontLab Studio can only be located on Mac OS X or Microsoft Windows.")
	return fontlabapp

def prepTempFLW(flwref, flwreftype = "path", quitFontLabWhenFinished = False):
	"""
	ARGUMENTS
	  flwref : a the input script to be executed in FLS
	  flwreftype : if "path", flwref is treated as a path to a Python file, 
	    if "file", flwref is treated as a pointer to a Python file, 
	    if "str", flwref is treated as a string containing the script.
	  quitFontLabWhenFinished : True if FLS should quit after execution
	DESCRIPTION
	The input script file (which must be written in Python) will be executed 
	in FontLab Studio. This function creates a temporary .flw file. 
	If flwreftype was "path", the function inserts the __file__ variable 
	with the path to the input script file (so the script can refer to it), 
	then inserts a command to remove itself once it has been run in FLS. 
	Then, it inserts the original contents of the input script file. 
	If the quitFontLabWhenFinished argument is True, it also inserts 
	a final command for FLS to quit after it has finished executing. 
	"""
	tmpflwpath = _getTempFilename(".flw")
	tmpflwfile = file(tmpflwpath, "w")
	flwpath = None
	flw = ""
	if flwreftype == "path": 
		if os.path.exists(flwref): 
			flwpath = flwref
			flwfile = file(flwpath, "r")
			flw = flwfile.read()
			flwfile.close()
	elif flwreftype == "file": 
		flwfile = flwref
		flw = flwfile.read()
		flwfile.close()
	elif flwreftype == "str": 
		flw = flwref
	tmpflw = "\n__tmpfile__ = %r\n" % (tmpflwpath)
	tmpflw += """
import os, os.path
if os.path.exists(__tmpfile__): 
	os.remove(__tmpfile__)
"""
	if flwpath: 
		tmpflw += "__file__ = %r\n" % (os.path.abspath(flwpath))
	tmpflw += "\n%s\n" % (flw)
	if quitFontLabWhenFinished: 
		tmpflw += "\nsys.exit(0)\n"
	tmpflwfile.write(tmpflw)
	tmpflwfile.close()
	return tmpflwpath

def runFontLabStudioWithFLW(flwpath, createFallback = True, quitFontLabWhenFinished = False):
	"""
	ARGUMENTS
	  flwpath : a path to the input .flw file to be executed in FLS
	  createFallback : if True, a fallback execution solution will 
	    be offered
	  quitFontLabWhenFinished : if True, FLS should quit after execution
	DESCRIPTION
	The input .flw file (which must be written in Python) will be executed 
	in FontLab Studio. This function tries to locate the most recent 
	FontLab Studio version installed on the user's system. Then, it creates
	a temporary .flw file (containing the __file__ variable pointing to 
	flwpath, then the contents of the input .flw file and, 
	if quitFontLabWhenFinished is True, a command for FLS to quit after 
	the execution). Then, it launches FLS with it. 
	If createFallback is True and FLS cannot be located automatically, 
	a simple manual execution solution will be offered.
	"""
	success = False
	fallbacktext = ""
	if not os.path.exists(flwpath): 
		_warn("Input .flw file does not exist at:\n%s" % (flwpath))
		return success
	fontlabapp = findFontLabStudio()
	tmpflwpath = prepTempFLW(flwpath)
	if fontlabapp["found"]: 
		(procout, procerr) = subprocess.Popen(fontlabapp["subprocesscall"] + [tmpflwpath], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
		success = True
	elif createFallback: 
		fallbackpath = os.path.join(os.path.expanduser("~"), "RunThisInFLS.flw")
		shutil.copy(tmpflwpath, fallbackpath)
		os.remove(tmpflwpath)
		fallbacktext = "FontLab Studio could not be located automatically in any of the standard locations. However, if you have FontLab Studio installed, you can execute this package manually. We have created a special file:\n%s\n" % (fallbackpath)
		if fontlabapp["os"] == "Windows": 
			fallbacktext += "Open FontLab Studio and drag that file from Windows explorer onto the FontLab Studio application window.\n"
		elif fontlabapp["os"] == "Mac OS X": 
			fallbacktext += "Open FontLab Studio and drag that file from Finder onto the FontLab Studio dock icon.\n"
			success = True
		else: 
			fallbacktext += "Drag that file onto the FontLab Studio window or icon.\n"
		success = True
	else: 
		fallbacktext = "FontLab Studio could not be located automatically in any of the standard locations. The execution was not successful."
		success = False
	print fallbacktext
	return success

def usage():
	print __doc__
	sys.exit(2)
def main(flwpath):
	if flwpath: 
		if len(flwpath) == 1: 
			runFontLabStudioWithFLW(flwpath[0], createFallback = True, quitFontLabWhenFinished = False)
	else: 
		usage()
if __name__ == "__main__":
  main(sys.argv[1:])
