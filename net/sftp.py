# $Id: sftp.py,v 1.1 2010-05-28 18:42:29 wirawan Exp $
#
# wpylib.net.sftp_robot module
# Created: 20100226
# Wirawan Purwanto
#
"""
SFTP-related module.

A better implementation is based on paramiko secure shell library
(http://www.lag.net/paramiko/).
A clunky implementation is based on `sftp' program. But the status inquiry
only works for Linux OS since it uses /proc/$PID approach.
"""

import getpass
import os
import stat
import sys
import time

try:
  import paramiko
  has_paramiko = True
except:
  has_paramiko = False

if has_paramiko:
  class sftp_client(object):
    """Python-controllable SFTP client.
    It's better to have no password (i.e. using private/public key authentication)
    to avoid additional security issues with python, password being passed around
    in clear text."""
    def __init__(self, hostname, username=None, port=22, password=None):
      conn = paramiko.SSHClient()
      if username == None:
        username = getpass.getuser()
  
      self.conn = conn
      self.username = username
      self.hostname = hostname
      self.port = hostname
  
      # Default init stage:
      conn.load_system_host_keys()
      #print "here1"
      conn.load_host_keys(os.path.expanduser("~/.ssh/known_hosts"))
      #print "here1"
      conn.set_missing_host_key_policy(paramiko.RejectPolicy()) # default=paranoid
      #print "here1"
      conn.connect(hostname=hostname, username=username, password=password,
                   port=port,
                  )
      sftp = conn.open_sftp()
      self.sftp = sftp
  
    def cd(self, path):
      self.sftp.chdir(path)
  
    def getcwd(self):
      self.sftp.getcwd()
  
    def get(self, remotepath, localpath, callback=None):
      # TODO: progress bar
      self.sftp.get(remotepath, localpath, callback)
      # Preserve the attributes as much as I can do it
      stats = self.sftp.stat(remotepath)
      os.utime(localpath, (stats.st_atime, stats.st_mtime))
      os.chmod(localpath, stats.st_mode)

    def put(self, localpath, remotepath, callback=None):
      # TODO: progress bar
      self.sftp.put(localpath, remotepath, callback)
      # Preserve the attributes as much as I can do it
      stats = os.stat(localpath)
      self.sftp.utime(remotepath, (stats.st_atime, stats.st_mtime))
      self.sftp.chmod(remotepath, stats.st_mode)

    def close(self):
      self.sftp.close()


# TODO: recode the sftp driver from

class sftp_driver(object):
  """Python controllable SFTP client built upon OpenSSH's sftp program."""
  def __init__(self, hostname, username=None, port=22, password=None):
    raise NotImplementedError
  # TODO


class sftp_status_callback(object):
  """SFTP progress bar for sftp_client object above.

  Example usage:

      statproc = sftp_status_callback(fname=remote_root + "/myfile.txt")
      sftp.get(remote_root + "/myfile.txt", "mylocalfile.txt", statproc)
      statproc.done()

  """
  def __init__(self, fname, out=sys.stderr):
    self.first = True
    self.fname = fname
    self.out = out
    self.marks = [ 0, 10, 20, 30, 40, 50, 60, 70, 80, 90 ]
    self.nbars = 25
    self.lastbar = 0
    self.begin_time = time.time()
  def printbar(self, bar):
    if bar > self.lastbar:
      dbar = bar - self.lastbar
      self.out.write("*" * dbar)
      self.out.flush()
      self.lastbar = bar
  def __call__(self, nbytes, filesize):
    if self.first:
      self.first = False
      self.filesize = filesize
      self.last = 0
      self.out.write("%-40s : %12d " % (self.fname[-40:], self.filesize))
      self.out.flush()
    self.cursize = nbytes
    curbar = int(float(nbytes) / self.filesize * self.nbars)
    self.printbar(curbar)
  def done(self):
    self.end_time = time.time()
    dtime = self.end_time - self.begin_time
    self.out.write("  %.2f kibps\n" % (self.filesize / 1024.0 / dtime))
    self.out.flush()

