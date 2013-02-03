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
# not sets of triples.  If these were plain sets of triples then there 
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
===> can we avoid the problem in any reasonable way? <===

I wonder if we can assume that nothing should have two values, and find some
  other way to express the multivaluebility of a property.
  axpress.is is a good case where we may want multiple values
What if we allow multiple values if one is already set, but do a merge if
  they are just two vars ... I feel like you're closing off possibilities that
  way ...  Do we need to be able to allow both possibilities to be searched (
  that they should be merged and that they should not)  The issue is if this
  ever causes problems where both paths needs to be taken and then merged at
  some point in the future.
  That still runs into the above problem of knowing if one planet could be 
  unified with another, which feels like it simply needs context.  You need to
  know what a planet is to know how they can merge.  This feels like a whole
  can of worms though ...
  - how complex can the rules about what is mergable get?

y != x
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
