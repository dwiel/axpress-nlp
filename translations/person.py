import re

def loadTranslations(axpress) :
  axpress.n.bind('person', '<http://dwiel.net/axpress/person/0.1/>')
  rule = axpress.rule

  def match_email(vars) :
    # http://code.activestate.com/recipes/65215/ (r5)
    email = vars['email']
    if len(email) > 7:
      if ' ' in email :
        return False
      if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
        return True
    return False    
  #rule("parse email", """
  #  person[axpress.is] = _email
  #""", """
  #  person[person.email_address] = _email
  #""", input_function = match_email)

