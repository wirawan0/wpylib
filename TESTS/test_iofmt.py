

def test_with_text_output1():
  """[20140804]
  Test text_output with() facility."""
  from wpylib.iofmt.text_output import text_output
  from wpylib.shell_tools import run
  from os import getpid, system
  mypid = getpid()
  print "pid = %d" % mypid
  print "Open files:"
  system("lsof -p %d" % mypid)
  print "### entering the 'with' block"
  with text_output("/tmp/babiku") as O:
    O("this is a test from pid %d\n" % mypid)
    system("lsof -p %d | tail" % mypid)
    print "### closing now"
  system("lsof -p %d | tail" % mypid)

