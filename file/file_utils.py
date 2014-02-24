#!/usr/bin/python
# $Id: file_utils.py,v 1.2 2010-09-27 19:54:29 wirawan Exp $
#
# pyqmc.utils.file_utils module
# File-manipulation utilities
#
# Wirawan Purwanto
# Created: 20090601
#
# Routines put here are commonly used in my own scripts.
# They are not necessarily suitable for general-purpose uses; evaluate
# your needs and see if they can them as well.
#
# 20090601: Created as pyqmc.utils.file_utils .
# 20100927: Moved to wpylib.file.file_utils .
#
"""
Common file-manipulation utilities.

This module is part of wpylib project.
"""

import bz2
import glob
import gzip
import os
import os.path
try:
  import subprocess
  has_subprocess = True
except:
  has_subprocess = False

try:
  import lzma
  has_lzma = True
except:
  try:
    from backports import lzma
    has_lzma = True
  except:
    has_lzma = False


from wpylib.sugar import is_iterable


class super_file(object):
  '''"Super-file" hack wrapper for a file-like object.
  Intended to allow extra capabilities to file-like iterators such as:
  * ability to push back text lines for the subsequent next() calls.
    This is to provide some level of rewinding in parsing text files.
  * what else?
  '''
  def __init__(self, obj):
    '''Creates a super_file wrapper around the "obj" object.'''
    self.obj = obj
    self.pushback = []
  def __iter__(self):
    return self
  def close(self):
    return self.obj.close()
  def flush(self):
    return self.obj.flush()
  def next(self):
    if len(self.pushback) > 0:
      return self.pushback.pop()
    else:
      return self.obj.next()
  def push(self, s):
    self.pushback.append(s)


def open_input_file(fname, superize=0):
  if fname.endswith(".bz2"):
    fobj = bz2.BZ2File(fname, "r")
  elif fname.endswith(".gz") or fname.endswith(".Z"):
    fobj = gzip.GzipFile(fname, "r")
  elif fname.endswith(".lzma"):
    # until lzma has a "standard" python module, we use "lzma" executable:
    if has_lzma:
      fobj = lzma.LZMAFile(fname, "r")
    else:
      lzma_exe = path_search(os.environ["PATH"].split(os.pathsep),
                             ("lzma", "xz"),
                             filetest=is_executable_file)
      if lzma_exe == None:
        raise IOError, "Cannot find lzma or xz executable file."
      if has_subprocess:
        px = subprocess.Popen((lzma_exe, "-dc", fname), stdout=subprocess.PIPE)
        fobj = px.stdout
      else:
        fobj = os.popen('" -dc "' + fname + '"', "r")
  elif fname.endswith(".xz"):
    # until lzma has a "standard" python module, we use "lzma" executable:
    if has_lzma:
      fobj = lzma.LZMAFile(fname, "r")
    elif has_subprocess:
      px = subprocess.Popen(("xz", "-dc", fname), stdout=subprocess.PIPE)
      fobj = px.stdout
    else:
      fobj = os.popen('xz -dc "' + fname + '"', "r")
  else:
    fobj = open(fname, "r")

  if superize:
    return super_file(fobj)
  else:
    return fobj


# Miscellaneous functions:
# - extended path manipulation/file inquiries (os.path-like functionalities)

def file_exists_nonempty(path):
  """Determines whether a given path is a regular file of
  nonzero size."""
  return os.path.isfile(path) and os.stat(path).st_size > 0

def is_executable_file(path):
  """Determines whether a regular file exists and is executable.
  This implements the "-x" action of the shell's test command.
  """
  # Ref: http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
  return os.path.isfile(path) and os.access(path, os.X_OK)

def dirname2(path):
  """Returns the directory part of a path.
  The difference from os.path.dirname is that if the directory
  part is empty, it is converted to '.' (the current directory)."""
  d = os.path.dirname(path)
  if d == '': d = '.'
  return d


# The following 3 routines are from
# http://code.activestate.com/recipes/208993-compute-relative-path-from-one-directory-to-anothe/
# by Cimarron Taylor
# (PSF license)
#
# (WP note: not sure if relpath below adds functionality or has different effects
# compared to os.path.relpath available in Python 2.6+).

def _pathsplit(p, rest=[]):
  (h,t) = os.path.split(p)
  if len(h) < 1: return [t]+rest
  if len(t) < 1: return [h]+rest
  return _pathsplit(h,[t]+rest)

def _commonpath(l1, l2, common=[]):
  if len(l1) < 1: return (common, l1, l2)
  if len(l2) < 1: return (common, l1, l2)
  if l1[0] != l2[0]: return (common, l1, l2)
  return _commonpath(l1[1:], l2[1:], common+[l1[0]])

def relpath(p1, p2):
  """Computes the relative path of p2 with respect to p1."""
  (common,l1,l2) = _commonpath(_pathsplit(p1), _pathsplit(p2))
  p = []
  if len(l1) > 0:
    p = [ '../' * len(l1) ]
  p = p + l2
  return os.path.join( *p )

# /// end code snippet

def path_split_all(p):
  """Completely decompose a filename path into individual components
  that can be rejoined later.
  """
  return _pathsplit(p)


def path_prep(*paths):
  """Like os.path.join, except that the directory part is created \
  on-the-fly as needed."""
  from os.path import dirname, isdir, join
  path = join(*paths)
  d = dirname(path)
  mkdir_p(d)
  return path

def mkdir_p(name):
  """A pure python implementation of my shell favorite `mkdir -p' command.
  To conform to that command's behavior, we will not issue an error
  if the file name exists and is a directory.
  Returns 1 if new directories are made, returns -1 if nothing is done."""
  from os.path import isdir
  if isdir(name):
    return -1
  else:
    os.makedirs(name)
    return 1


# - globbing

def glob_files(filespec):
  '''Processes a glob string, or does nothing (pass-on only) if an iterable object
  (e.g. list or tuple) is already given.
  When globbing is done, the result is sorted for predictability.'''
  if getattr(filespec, "__iter__", False):
    return filespec # no re-sorting
  elif isinstance(filespec, basestring):
    return sorted(glob.glob(filespec))
  else:
    raise ValueError, "Don't know how to glob for an object of " + type(filespec)


# - file searches and filesystem scans

def list_dir_entries(D, symlinks=False, sort=False):
  """Returns a list of files (actually, non-dirs) and dirs in a given directory.
  If symlinks == True, the symbolic links will be separated from the rest.
  This routine builds upon os.listdir() routine.

  Will return a 4-tuple, containing:

    - dir entries
    - regular file and other non-dir entries
    - symlink dir entries
    - symlink regular file and other non-dir entries

  The latter two would be empty if symlinks == False.
  """
  from os.path import isdir, islink, join
  entries = os.listdir(D)
  dirs, nondirs = [], []
  if symlinks:
    s_dirs, s_nondirs = [], []
  else:
    s_dirs, s_nondirs = dirs, nondirs

  rslt = {
    # +-- symlink?
    # v     v--- dir or not
    False: { True: dirs, False: nondirs },
    True: { True: s_dirs, False: s_nondirs },
  }
  for E in entries:
    full_E = join(D,E)
    rslt[bool(islink(full_E))][bool(isdir(full_E))].append(E)

  if sort:
    if not isinstance(sort, dict):
      sort = {}

    dirs.sort(**sort)
    nondirs.sort(**sort)
    if symlinks:
      s_dirs.sort(**sort)
      s_nondirs.sort(**sort)

  if symlinks:
    return (dirs, nondirs, s_dirs, s_nondirs)
  else:
    return (dirs, nondirs, [], [])


def path_search(*specs, **opts):
  '''Generalized path search.
  Multiple paths can be specified for different parts of the sought filename,
  and the first file found is returned.

  Additional options:
  * pathsep="/"  -- path separator
  * filetest=os.path.isfile  -- filetest operator to be used
  * raise_error=False  -- do we want to raise an exception if the file
    is not found after all possible searches?
  '''
  path_join = os.path.join
  # FIXME: this can be extremely expensive!
  xspecs = []
  xlen = []
  xstride = []
  xtot = 1
  pathsep = opts.get("pathsep", "/")
  filetest = opts.get("filetest", os.path.isfile)

  for spec in specs:
    if not is_iterable(spec): # maybe a string?
      xspecs.append((spec,))
      xlen.append(1)
    else:
      xspecs.append(tuple([ x for x in spec ]))
      xlen.append(len(xspecs[-1]))
    xstride.append(xtot)
    xtot *= xlen[-1]

  for idx in xrange(xtot):
    idx0 = idx
    # Construct the filename based on the index: we reconstruct
    # the indices for all the parts given in the argument, then
    # concatenate them to get the full pathname
    s = ""
    for d in xrange(len(xspecs)-1,-1,-1):
      a = idx0 / xstride[d]
      if s == "":
        s = xspecs[d][a]
      else:
        s = xspecs[d][a] + pathsep + s
      idx0 = idx0 % xstride[d]
      #print a,
    #print s
    if filetest(s):
      return s

  if opts.get("raise_error", False):
    raise ValueError, "Cannot find file with specified combination"
  else:
    return None


def scan_directories(D, testdir):
  """Recursively scans a directory tree for candidate of
  relevant directories, where testdir(D,dirs,files)
  return a True boolean value.

  We will *not* follow symlinks.

  The testdir function must have this kind of prototype:

     testdir(D, dirs, files)

  where:

  - D (first positional argument) is the directory under consideration
  - dirs (named argument) is a list containing all subdirectory entries
    contained in D (symlinks or not).
  - files (named argument) is a list containing all non-subdirectory
    entries contained in D (other symlinks, files, pipes, sockets, etc).
  """
  rslt = []
  for (d, dirs, files) in os.walk(D, topdown=True):
    if testdir(d, dirs=dirs, files=files):
      rslt.append(d)
  return rslt


def untar(archive, subdir=None, verbose=None, files=[]):
  '''Extracts a TAR archive. The destination directory can be given; otherwise
  the files are extracted to the current directory.
  Assuming GNU tar which accepts -z and -j switches.
  LZMA compression is supported via lzma program.
  '''
  opts = [ 'tar' ]
  # Python doc says: "the arguments to the child process must start with the
  # name of the command being run"

  if subdir:
    opts += [ "-C", subdir ]

  if archive.endswith(".tar.bz2") or archive.endswith(".tbz2") or archive.endswith(".tbz") or archive.endswith(".tb2"):
    opts.append("-j")
  elif archive.endswith(".tar.Z") or archive.endswith(".tar.gz") or archive.endswith(".tgz"):
    opts.append("-z")
  elif archive.endswith(".tar.lzma") or archive.endswith(".tza") or archive.endswith(".tlz"):
    opts.append("--use-compress-program=lzma")
  elif archive.endswith(".tar.xz") or archive.endswith(".txz"):
    opts.append("--use-compress-program=xz")

  if verbose:
    for i in xrange(verbose): opts.append("-v")

  opts += [ "-xf", archive ]
  opts += files

  return os.spawnvp(os.P_WAIT, "tar", opts)


