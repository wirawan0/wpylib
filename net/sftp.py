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
      conn.set_missing_host_key_policy(paramiko.RejectPolicy) # default=paranoid
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
      # Save the attributes as much as I can do it
      stats = self.sftp.stat(remotepath)
      os.utime(localpath, (stats.st_atime, stats.st_mtime))
      os.chmod(localpath, stats.st_mode)



# TODO: recode the sftp driver from

class sftp_driver(object):
  """Python controllable SFTP client built upon OpenSSH's sftp program."""
  def __init__(self, hostname, username=None, port=22, password=None):
    raise NotImplementedError
  # TODO
