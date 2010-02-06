# $Id: file_db.py,v 1.1 2010-02-06 23:21:09 wirawan Exp $
#
# wpylib.db.filedb module
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
  import pysqlite2 as sqlite3

class file_rec(tuple):
  pass

class file_db(object):
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

  def __init__(self, src_name, table_name='filedb', extra_fields=[]):
    self.src_name = src_name
    self.table_name = table_name
    if os.path.isfile(src_name):
      self.db = sqlite3.connect(src_name)
      self.dbc = self.db.cursor()
    else:
      self.db = sqlite3.connect(src_name)
      self.dbc = self.db.cursor()
    self.db.text_factory = str
    self.sql_params = {
        'table_name': table_name,
    }
    self.debug = 1

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
        + ', '.join(["'%s' = ?" % dname for dname in dnames]) \
        + " WHERE filename = ?;"
      vals = tuple(dvals + [filename])
    else:
      insert_sql = "INSERT INTO '%(table_name)s' (filename, " \
        + ", ".join(["'%s'" % dname for dname in dnames]) \
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

  def __contains__(self, filename):
    """Counts the number of record entries matching in the `filename' field."""
    if filename.find("%") >= 0:
      sql_stmt = "SELECT count(*) FROM '%(table_name)s' WHERE filename LIKE ?;"
    else:
      sql_stmt = "SELECT count(*) FROM '%(table_name)s' WHERE filename = ?;"
    return [ rslt for rslt in self.exec_sql(sql_stmt, (filename,)) ][0][0]

  count = __contains__


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


def get_file_stats(filename):
  stats = os.stat(filename)
  mtime = time.localtime(stats.st_mtime)
  Mdate = mtime.tm_year * 10000 + mtime.tm_mon * 100 + mtime.tm_mday
  Mtime = mtime.tm_hour * 10000 + mtime.tm_min * 100 + mtime.tm_sec
  size = stats.st_size
  md5sum = str2hexstr(md5_digest_file(filename))  # this step is EXPEN$IVE
  return {
    'filename': filename,
    'mdate': Mdate,
    'mtime': Mtime,
    'size': size,
    'md5sum': md5sum,
  }

