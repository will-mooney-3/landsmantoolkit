Landsman's Toolkit
===============

Simple script to extract text from TIF files and perform basic searches on
that text. Named as it was written to help a landsman do their work with
a bunch of scanned documents.

Requirements
===============

The following must be installed to use the toolkit:

-- Python
-- OpenCV
-- NumPy
-- Tesseract (https://code.google.com/p/tesseract-ocr)
-- Python-Tesseract (https://code.google.com/p/python-tesseract/)

I *strongly* recommend that Windows users install the SimpleCV superpack for
the first three requirements. It can be found at http://www.simplecv.org/download.

Usage
=====

After installing the requirements, plop the script in the parent directory of
the files you would like to extract text from. Open up a command prompt,
change to that directory, and run the script with "python main.py". Everything
else should be self explanitory.

Mini Disclaimer
===============

This software was written as a very quick script to help with a very specific
task. It is by no means optimized and does not have tests. The furthest I am
planning on making changes is possibly making a GUI interface in the future so
people will not have to use the command line and maybe allowing the user to
specify which directory to look in rather than assuming the current working
directory. Use at your own risk.
