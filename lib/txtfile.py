#!/usr/bin/python2.7
import os, codecs

class TxtFile(object):
    
    PM        = unichr(0x00B1)
    CHI       = unichr(0x1D712)
    SQUARE    = unichr(0x00B2)
    CHISQUARE = unichr(0x1D712) + unichr(0x00B2)
    
    def __init__(self, path, mode, enc='utf-8'):
        # if file/directory does not exist create dirs and file
        if not os.path.exists(path):
            os.mkdir(os.path.dirname(path))
            codecs.open(path, 'a', enc).close()
        # open file with actual mode
        self._file = codecs.open(path, mode, enc)
        
    @classmethod
    def fromRelPath(cls, path, mode, enc='utf-8'):
        d = os.getcwd()
        p = os.path.abspath(os.path.join(d, path))
        return cls(p, mode, enc)
    
    def getFile(self):
        return self._file
    
    def write(self, text):
        self._file.write(text)
           
    def writeline(self, text='', *args):
        if not args:
            self._file.write(text + '\n')
        else:
            self._file.write(text.join(args) + '\n')
    
    def writelines(self, lines):
        self._file.writelines(lines)
    
    def close(self):
        self._file.close()
        
    def __enter__(self):
        return self
        
    def __exit__(self, type, value, traceback):
        self.close()