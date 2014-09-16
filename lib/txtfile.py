#!/usr/bin/python2.7
"""Basic writing to encoded text files"""

__author__ = "Benjamin Rottler (benjamin@dierottlers.de)"

import os, codecs  # paths, encoded text files

class TxtFile(object):
    """Basic writing to encoded text files"""
    
    PM        = unichr(0x00B1)                      # plus/minus
    CHI       = unichr(0x1D712)
    SQUARE    = unichr(0x00B2)
    CHISQUARE = unichr(0x1D712) + unichr(0x00B2)
    
    def __init__(self, path, mode, enc='utf-8'):
        """Constructor, opens file
        
        Arguments:
        path -- absolute path to file
        mode -- write mode (usually 'w' for overwriting or 'a' for appending)
        enc  -- encoding (default = 'utf-8')
        """
        # if file/directory does not exist create dirs and file
        if not os.path.exists(path):
            if not os.path.exists(os.path.dirname(path)):
                os.mkdir(os.path.dirname(path))
            codecs.open(path, 'a', enc).close()
        # open file with actual mode
        self._file = codecs.open(path, mode, enc)
        
    @classmethod
    def fromRelPath(cls, path, mode, enc='utf-8'):
        """Creates a new instance of TxtFile from a relative path
        
        Arguments:
        path -- relative path to file
        mode -- write mode (usually 'w' for overwriting or 'a' for appending)
        enc  -- encoding (default = 'utf-8')
        """
        d = os.getcwd()
        p = os.path.abspath(os.path.join(d, path))
        return cls(p, mode, enc)
    
    def getFile(self):
        """returns handle to file"""
        return self._file
    
    def write(self, text):
        """writes text to file
        
        Arguments:
        text -- text to write
        """
        self._file.write(text)
           
    def writeline(self, text='', *args):
        """writes text and finishes line with a linebreak. 
        If more than one argument is given, joins 2nd to last argument with first one and finishes line with a linebreak
        
        Arguments:
        text  -- text to write or text, which is used to join other arguments
        *args -- additional arguments, which are joined by first one
        """
        if not args:
            self._file.write(text + '\n')
        else:
            self._file.write(text.join(args) + '\n')
    
    def writelines(self, lines):
        """writes multiple lines
        
        Arguments:
        lines -- a list of lines to write
        """
        self._file.writelines(lines)
    
    def close(self):
        """closes file"""
        self._file.close()
        
    def __enter__(self):
        """if entering with-statement, returns instance"""
        return self
        
    def __exit__(self, type, value, traceback):
        """if exiting with-statement, close file"""
        self.close()