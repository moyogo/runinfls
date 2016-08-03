See
http://forum.fontlab.com/python-scripting/new-script-runinfls-py-to-execute-fontlab-python-scripts-from-outside-of-fls/

Attached is a Python script "runinfls.py" which can be used to execute another FontLab Python script from outside of FontLab Studio.
This runinfls.py script can be used from the commandline, where the script to be executed is given as argument (the filename or extension of the script does not matter). It can also be used as a module within other scripts. In such case, the Python code to be executed within FLS can be given as a file path, Python file object, or string.
The main advantage of the runinfls.py script is that:
1. It automatically locates the most recent version of FontLab Studio and executes the script within it.
2. It adds the missing \__file__ functionality, i.e. when the script is running from a file, FontLab Studio "knows" its original location.
The latter functionality can potentially be useful when writing installation routines that should put some files inside of the FontLab data folders.
The script comes with a small example file. Unpack the attached runinfls-1.10.zip archive, and then:
To run it on Mac OS X, open Terminal, navigate to the unpacked contents (using "cd") and type:
```bash
python runinfls.py test.flpy
```
To run it on Windows, click on the Start button, type in "cmd" (or choose Run and type in "cmd"), navigate to the unpacked contents (using "cd") and type:
```
c:\python24\python runinfls.py test.flpy
```

The runinfls.py script is opensource under the MIT License.

Regards,<br/>
Adam Twardoch<br/>
Fontlab Ltd.
