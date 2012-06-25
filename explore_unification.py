facts  = query       = new_query   = query             = """
  x[foo.a] = s
  x[foo.b] = 1
"""

output = out_triples = var_triples = transition[input] = """
  y[foo.a] = t
  y[foo.b] = 2
"""

"""
this shouldn't match.  If we want to add 2 to y, we should match y in the
input.  variables bound by the input will remain bound through the output
even if the unification with the new triples doesn't work.
"""

'input' : """
  x[axpress.is] = "remove %item% (from |)(my |)todo( list|)"
""",
'output' : """
  x[axpress.is] = "show todo list"
"""

""" in this case above, we want to allow x to unify even though its axpress.is
property is different """

in : """
  foo.x[y] = " hello "
""",
out : """
  foo.x[y] = "hello"
"""

# A) this one makes you think ...
in  : [x foo.y 1]
out : [x foo.y 2]

# B) this one seems perfectly ok - these two triples can co-exist with x being ==
in  : [x 1 foo.y]
out : [x 2 foo.y]

# which makes it pretty clear that we are dealing in dictionaries or objects, 
# not sets of triples.  If these were plain sets of tripples then there 
# would be no difference between A and B

# ok, one way to get around this is to say that new_triples must 'connectedly'
# unify to existing triples.  By this I mean that for a new_triple to unify to 
# an existing triple, there must be a known link between them ...
# NO that isn't good enough either.  Imagine a case:

existing : [[x .name "Earth"],
            [x .near l1],
            [l1 .type .planet],
            [l1 .population 1],
            [l1 .alias "Red Planet"],
            [l1 .name "Mars"]]
            
in       : [[x .name _n]]
out      : [[x .near l2],
            [l2 .type .star],
            [l2 .brightness 1],
            [l2 .alias "Sol"],
            [l2 .size _s]]
fn : ...

"""
In this case above, we wouldn't want to unify l1 and l2.  This is because 
l1.type == .planet and l2.type == .star.  It is not because 
l1.pop == 1 and l2.brightness == 1.  Similary, l1.alias == "Red Planet" and 
l2.alias == "Sol" shouldn't stop l1 and l2 from unifying.

Solutions :

create a dict type which matches in the specific ways described ...
  some properties shouldn't have two values, some are OK to have
  multiple values (see freebase)
can we avoid the problem in any reasonable way?

input binding this shouldn't match
output binding ... this probably shouldn't match
  however, if foo.b is axpress.is, we may want to be able to
  unify this partially ...
On the other hand it doesn't make sense to paritally match a bnode

y != x
"""

"""
holy katz!  now it looks like there is a problem with the way the dependencies 
are being created!
"""

"""
The general rule is this:

when binding new_triples with existing facts, there is a set of input bindings
that were used in the input matching.  Those triples can have new properties
added to them.  

--- not quite right ...

If a variable is bound to a literal or lit_var in the input, then it can be 
bound to something new in the output

If new_triples are being unified with existing triples, then literals must 
match.  If there are two new triples with x in them, then both triples must be 
able to simultaneously unifiy into existing triples in order for a unification on
x to be made.
"""




"""
'facts' [
  [ n.var.image, n.glob.glob, 'pictures/*.jpg', ],
  [ n.var.image, n.file.filename, n.out_lit_var.filename, ],
  [ n.var.bnode1, n.call.arg1, n.var.image, ],
  [ n.var.bnode1, n.call.arg2, 4, ],
  [ n.var.bnode1, n.call.arg3, 4, ],
  [ n.var.bnode1, n.call.arg4, n.image.antialias, ],
  [ n.var.bnode1, n.image.thumbnail, n.var.thumb, ],
  [ n.var.bnode2, n.call.arg1, n.var.thumb, ],
  [ n.var.bnode2, n.call.arg2, 0, ],
  [ n.var.bnode2, n.call.arg3, 0, ],
  [ n.var.bnode2, n.image.pixel, n.var.pixel, ],
  [ n.var.dist, n.type.number, n.var.bnode4, ],
  [ n.var.bnode3, n.call.arg1, n.color.red, ],
  [ n.var.bnode3, n.call.arg2, n.var.pixel, ],
  [ n.var.bnode3, n.color.distance, n.var.bnode4, ],
  [ n.var.dist, n.type.number, n.out_lit_var.distance, ],
  [ n.var.image, n.file.filename, n.lit_var.out_filename_out_1, ],
  [ n.var.image, n.pil.image, n.lit_var.pil_image_out_4, ],
  [ n.var.image, n.display.html, n.lit_var.html_out_21, ],
  [ n.var.thumb, n.pil.image, n.lit_var.thumb_image_out_28, ],
]
'pattern' [
  [ n.var.image, n.image.average_color, n.var.color, ],
  [ n.var.bnode6, n.call.arg1, n.var.image, ],
  [ n.var.bnode6, n.call.arg2, 1, ],
  [ n.var.bnode6, n.call.arg3, 1, ],
  [ n.var.bnode6, n.image.thumbnail, n.var.thumb, ],
  [ n.var.bnode7, n.call.arg1, n.var.thumb, ],
  [ n.var.bnode7, n.call.arg2, 0, ],
  [ n.var.bnode7, n.call.arg3, 0, ],
  [ n.var.bnode7, n.image.pixel, n.var.pixel, ],
  [ n.var.pixel, n.pil.color, n.var.color, ],
]
"""