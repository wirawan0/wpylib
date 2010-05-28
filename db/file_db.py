# $Id: file_db.py,v 1.4 2010-05-28 18:46:16 wirawan Exp $
#
# wpylib.db.file_db module
# Created: 20100205
# Wirawan Purwanto
#

"""File fingerprint database."""

import md5
import numpy
import os.path
import time

try:
  import sqlite3
except:
  import pysqlite2.dbapi2 as sqlite3

default_debug_level = 0

class file_rec(tuple):
  pass

class file_table(object):
  # dtype for numpy (if wanted)
  dtype = numpy.dtype([
                       ('filename', 'S256'),
                       ('md5', 'S32'),
                       ('date', 'i4'),
                       ('time', 'i4'),
                       ('size', 'i8'),
                      ])
  # dtype map from python types to sqlite3 types:
  sqlite_dtype_map = {
    str: 'TEXT',
    int: 'INTEGER',
    float: 'REAL',
  }

  indexable_row_type = sqlite3.Row

  def __init__(self, src_name, table_name='filedb', extra_fields=[]):
    self.src_name = src_name
    self.table_name = table_name
    if isinstance(src_name, str): # os.path.isfile(src_name):
      self.db = sqlite3.connect(src_name)
      self.dbc = self.db.cursor()
    elif isinstance(src_name, sqlite3.Connection):
      self.db = src_name
      self.dbc = self.db.cursor()
    else:
      raise ValueError, "Invalid src_name data type"
    self.db.text_factory = str
    self.sql_params = {
        'table_name': table_name,
    }
    self.debug = default_debug_level

    create_sql = """\
      CREATE TABLE IF NOT EXISTS '%(table_name)s' (
        filename TEXT,
        md5sum TEXT,
        date INTEGER,
        time INTEGER,
        size INTEGER""" \
        + "".join([", '%s' %s" % (dname, self.sqlite_dtype_map[dtyp])
                     for (dname,dtyp) in extra_fields
                  ]) \
        + """
      );
      """
    self.exec_sql(create_sql)
    self.db.commit()

  def exec_sql(self, stmt, params=None):
    sql_stmt = stmt % self.sql_params
    if params:
      if self.debug:
        print "--SQL::", sql_stmt.rstrip()
        print "--val::", params
      return self.dbc.execute(sql_stmt, params)
    else:
      if self.debug:
        print "--SQL::", sql_stmt.rstrip()
      return self.dbc.execute(sql_stmt)

  def add_fields(self, dtypes):
    """Adds columns to the table."""
    for (dname, dtyp) in dtypes:
      self.exec_sql("ALTER TABLE '%(table_name)s' ADD COLUMN" \
                    + " '%s' %s;" % (dname, self.sqlite_dtype_map[dtyp])
                   )
    self.db.commit()

  def register_file(self, filename, replace=False, extra_values=None):
    """Register a file, note its mtime, and size, and digests its content."""
    filestats = get_file_stats(filename)
    fields = [
      ('md5sum', filestats['md5sum']),
      ('date', filestats['mdate']),
      ('time', filestats['mtime']),
      ('size', filestats['size']),
    ] + [
      kwpair for kwpair in extra_values
    ]
    dnames = [ dname for (dname,dval) in fields ]
    dvals = [ dval for (dname,dval) in fields ]

    if replace:
      # Test if we want to replace or to add.
      count = [
        x for x in self.exec_sql(
          "SELECT count(*) from '%(table_name)s' where filename = ?;",
          (filename,)
        )
      ][0][0]
      if count == 0: replace = False

    if replace:
      # WARNING: This will replace all the occurences of the entry with
      # the same filename.
      # Replaceable insert is not intended for tables with duplicate entries
      # of the same filename.
      insert_sql = "UPDATE '%(table_name)s' SET " \
        + ', '.join(["'%s' = ?" % d for d in dnames]) \
        + " WHERE filename = ?;"
      vals = tuple(dvals + [filename])
    else:
      insert_sql = "INSERT INTO '%(table_name)s' (filename, " \
        + ", ".join(["'%s'" % d for d in dnames]) \
        + ") VALUES (?" + ',?'*(len(fields)) + ");"
      vals = tuple([filename] + dvals)
    self.exec_sql(insert_sql, vals)

  def flush(self):
    self.db.commit()

  def get_filenames(self):
    """Reads all the file names in the table to memory."""
    return [
      rslt[0] for rslt in
        self.exec_sql("SELECT filename FROM '%(table_name)s' ORDER BY filename;")
    ]

  def __getitem__(self, filename):
    """Reads all the entries matching in the `filename' field."""
    if filename.find("%") >= 0:
      sql_stmt = "SELECT * FROM '%(table_name)s' WHERE filename LIKE ?;"
    else:
      sql_stmt = "SELECT * FROM '%(table_name)s' WHERE filename = ?;"
    return [ rslt for rslt in self.exec_sql(sql_stmt, (filename,)) ]

  def __setitem__(self, filename, newdata):
    """Updates the metadata on the filename. Any other field than the filename
    can be updated. The filename serves as a unique key here.
    The newdata can be a hash, like this:

       A_file_table[filename] = {'date': 20041201, 'time': 122144}

    or a list of tuples:

       A_file_table[filename] = [('date': 20041201), ('time': 122144)]
    """
    if isinstance(newdata, dict) or "keys" in dir(newdata):
      dnames = newdata.keys()
      dvals = [ newdata[k] for k in dnames ]
    else:
      # Assuming an iterable with ('field', 'value') tuples.
      dnames = [ dname for (dname,dval) in newdata ]
      dvals = [ dval for (dname,dval) in newdata ]
    update_sql = "UPDATE '%(table_name)s' SET " \
      + ', '.join(["'%s' = ?" % d for d in dnames]) \
      + " WHERE filename = ?;"
    vals = tuple(dvals + [filename])
    self.exec_sql(update_sql, vals)

  def __contains__(self, filename):
    """Counts the number of record entries matching in the `filename' field."""
    if filename.find("%") >= 0:
      sql_stmt = "SELECT count(*) FROM '%(table_name)s' WHERE filename LIKE ?;"
    else:
      sql_stmt = "SELECT count(*) FROM '%(table_name)s' WHERE filename = ?;"
    return [ rslt for rslt in self.exec_sql(sql_stmt, (filename,)) ][0][0]

  count = __contains__

  def fields(self):
    """Returns the field names of the table of the latest query."""
    return [ z[0] for z in self.dbc.description ]

  def row_kind(self, kind=None):
    if kind:
      self.db.row_factory = kind
      # We will reload the cursor to account for the new factory
      self.dbc = self.db.cursor()
    return self.db.row_factory


def md5_digest_file(filename):
  """Digests the content of a file."""
  ff = open(filename, "rb")
  bufsize = 32768
  stuff = ff.read(bufsize)
  digest = md5.new()
  while len(stuff) > 0:
    digest.update(stuff)
    stuff = ff.read(bufsize)
  ff.close()
  return digest.digest()


def str2hexstr(md5sum):
  """Return the hex representation of a string."""
  return "".join([ "%02x" % ord(c) for c in md5sum ])


def get_file_stats(filename, get_md5sum=True):
  stats = os.stat(filename)
  mtime = time.localtime(stats.st_mtime)
  Mdate = mtime.tm_year * 10000 + mtime.tm_mon * 100 + mtime.tm_mday
  Mtime = mtime.tm_hour * 10000 + mtime.tm_min * 100 + mtime.tm_sec
  size = stats.st_size
  if get_md5sum:
    md5sum = str2hexstr(md5_digest_file(filename))  # this step is EXPEN$IVE
  else:
    md5sum = None
  return {
    'filename': filename,
    'mdate': Mdate,
    'mtime': Mtime,
    'size': size,
    'md5sum': md5sum,
  }

