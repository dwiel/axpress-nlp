<html>
  <head>
    <title>Force-Directed Layout</title>
    <script type="text/javascript" src="../protovis.min.js"></script>
    
    <style type="text/css">

body {
  margin: 0;
}

    </style>
  </head>
  <body>
    <script type="text/javascript">
    // This file contains the weighted network of coappearances of characters in
// Victor Hugo's novel "Les Miserables". Nodes represent characters as indicated
// by the labels, and edges connect any pair of characters that appear in the
// same chapter of the book. The values on the edges are the number of such
// coappearances. The data on coappearances were taken from D. E. Knuth, The
// Stanford GraphBase: A Platform for Combinatorial Computing, Addison-Wesley,
// Reading, MA (1993).
//
// The group labels were transcribed from "Finding and evaluating community
// structure in networks" by M. E. J. Newman and M. Girvan.

var miserables = {
  nodes:[
    % for t in c.axpress.compiler.translations :
      {nodeName:"${t[c.n.meta.name]}", group:${c.lookup_filename_id(t[c.n.meta.filename])} },
    % endfor
  ],
  links:[
    % for id, ts in c.axpress.compiler.translation_matrix.iteritems() :
      % for t in ts :
        {source:${id-1}, target:${t[c.n.meta.id]-1}, value:0.32},
      % endfor
    %endfor
  ]
};
    </script>
    <script type="text/javascript+protovis">

var w = document.body.clientWidth,
    h = document.body.clientHeight,
    colors = pv.Colors.category19();

var vis = new pv.Panel()
    .width(w)
    .height(h)
    .fillStyle("white")
    .event("mousedown", pv.Behavior.pan())
    .event("mousewheel", pv.Behavior.zoom());

var force = vis.add(pv.Layout.Force)
    .nodes(miserables.nodes)
    .links(miserables.links);

force.link.add(pv.Line).size(function(d) 1000);

force.node.add(pv.Dot)
    .size(function(d) (d.linkDegree + 4) * Math.pow(this.scale, -1.5))
    .fillStyle(function(d) d.fix ? "brown" : colors(d.group))
    .strokeStyle(function() this.fillStyle().darker())
    .lineWidth(1000)
    .title(function(d) d.nodeName)
    .event("mousedown", pv.Behavior.drag())
    .event("drag", force)
  .anchor("center").add(pv.Label)
    .text(function(d) d.nodeName);

vis.render();

    </script>
  </body>
</html>