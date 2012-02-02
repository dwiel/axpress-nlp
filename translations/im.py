import sys, xmpp

# Google Talk constants
FROM_GMAIL_ID = "zdwiel@gmail.com"
GMAIL_PASS = open('/home/dwiel/.gmpw').read().strip()
GTALK_SERVER = "talk.google.com"
TO_GMAIL_ID = "zdwiel@gmail.com"

def send_im(vars) :
  message = vars['message']
  addr = vars['addr']
  
  jid=xmpp.protocol.JID(FROM_GMAIL_ID)
  cl=xmpp.Client(jid.getDomain(),debug=[])
  if not cl.connect((GTALK_SERVER,5222)):
    vars['response'] = 'Can not connect to server.'
    return
  if not cl.auth(jid.getNode(),GMAIL_PASS):
    vars['response'] = 'Can not auth with server.'
    return

  cl.send(xmpp.Message(addr, message))
  cl.disconnect()
  
  vars['response'] = "said %s to %s" % (message, addr)

def loadTranslations(axpress, n) :
  n.bind('im', '<http://dwiel.net/axpress/im/0.1/>')
  n.bind('person', '<http://dwiel.net/axpress/person/0.1/>')

  def rule(name, input, output, fn=None, input_function=None, **kwargs) :
    options = {
      n.meta.name   : name,
      n.meta.input  : input,
      n.meta.output : output,
      n.meta.function : fn,
      n.meta.input_function : input_function
    }
    options.update(kwargs)
    axpress.register_translation(options)
  
  # this seems to be something different ... or maybe not :)
  # TODO: allow optionally accepting a person's name here for the response
  rule("send im", """
    person[person.email_address] = _addr
    message[string.text] = _message
    response = im.send(person, message)
  """, """
    response[string.text] = _response
  """, send_im)
  
  rule("say hi", """
    foo[axpress.is] = "say hi to %person_str%"
    person[axpress.is] = person_str
  """, """
    foo = im.send(person, 'hi')
  """)