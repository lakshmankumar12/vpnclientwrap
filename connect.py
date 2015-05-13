#!/usr/bin/python

import sys
import pexpect

try:
  import credentials_vpn
except ImportError:
  print "Please have a creditials_vpn.py as in Readme"
  sys.exit(1)

def general_expect(child, expect_list, intent_desc, eof_ok=0, print_output=0, timeout=0, timeout_ok=0):
  ''' Wrapper on top of pexpect's child.expect([expect-list])

      intent_desc  is a string, that will printed if expect throws a exception.
      eof_ok       if non-0, returns len(expect_list)+1 when eof is hit. Otherwise eof is bad
      print_output is whether to emit child's stdout in the good-case condition
                   O/p is always stored into general_expect_failure on error
      timeout_ok   if non-0, then timeout doesn't raise Exception. You will get len(expect_list)+2 as result.
      timeout      if non-0, is passed to expect, otherwise Not. You can wait infinitely with this wrapper. Sorry.

      Note that child.before and child.after are still available to caller to consume
  '''
  after = 1
  try:
    error = ""
    if timeout:
      result = child.expect(expect_list, timeout)
    else:
      result = child.expect(expect_list)
      if result >= len(expect_list):
        #huh!
        error = "Got none of the expected result!"
  except pexpect.EOF:
    after = 0
    if eof_ok:
      result = len(expect_list)+1
    else:
      error="Eof hit:\n"
  except pexpect.TIMEOUT:
    after = 0
    if timeout_ok:
      result = len(expect_list)+2
    else:
      error="Timeout out without matches:\n"
  if print_output:
    output = child.before
    if after:
      output += child.after
    print child.before
  if error:
    err_str = "Error while doing:" + intent_desc + "\n" + "Error:" + error + "\n"
    open("general_expect_failure","w").write(err_str+child.before)
    raise Exception(err_str);
  return result

sudo_pass_expect=r'\[sudo\] password for '+credentials_vpn.username
vpn_pass_expect=r'Password for VPN:'
serv_sig_accept=r'Would you like to connect to this server\? \(Y\/N\)'
tunnel_done=r'STATUS::Tunnel running'

userarg=credentials_vpn.domainname+'\\'+credentials_vpn.username
while True:
  child=pexpect.spawn("sudo",[credentials_vpn.program,"--server",credentials_vpn.servername,"--vpnuser",userarg])
  vpn_pass_sent = 0
  print "waiting for passwords"
  while not vpn_pass_sent:
    res=general_expect(child,[sudo_pass_expect, vpn_pass_expect], "finish vpn password")
    if res == 0:
      print "sending su pass"
      child.sendline(credentials_vpn.supass)
    else:
      print "sending vpn pass"
      child.sendline(credentials_vpn.vpnpass)
      vpn_pass_sent = 1

  print "awaiting signature"
  general_expect(child,serv_sig_accept,"Signature from machine",print_output=1,timeout=20)
  child.sendline("yes")

  general_expect(child,tunnel_done,"Tunnelling started")

  print "tunnel done"
  tunnel_time = 0
  while True:
    result = general_expect(child,"Tunnel closed","Waiting for tunnel-closing",timeout=60,timeout_ok=1,eof_ok=1)
    if result == 2:
      tunnel_time += 60
      if tunnel_time > 3600:
        print "Great going .. On for an hour.. "
        tunnel_time = 0
      continue
    if result == 1:
      print "oops: vpn-client closed"
      break
    print "oops: tunnel seems closed"
    child.sendcontrol("c")
    child.sendcontrol("c")
    child.terminate()
    break
  del child

