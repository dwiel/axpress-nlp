/*
 * (c) Copyright 2005, 2006, 2007, 2008, 2009 Hewlett-Packard Development Company, LP
 * All rights reserved.
 * [See end of file]
 */

package org.joseki.graph;

import java.util.Iterator;
import java.util.List;

import com.hp.hpl.jena.graph.BulkUpdateHandler;
import com.hp.hpl.jena.graph.Graph;
import com.hp.hpl.jena.graph.Triple;
import com.hp.hpl.jena.graph.impl.WrappedBulkUpdateHandler;

public class LimitingBulkUpdateHandler extends WrappedBulkUpdateHandler
{
    LimitingGraph lGraph ;
    
    public LimitingBulkUpdateHandler(LimitingGraph graph, BulkUpdateHandler bulk)
    {
        super(graph, bulk) ;
        this.lGraph = graph ;
    }
    
    @Override
    public void add( Triple [] triples )
    {
        lGraph.count = lGraph.count+triples.length ;
        lGraph.checkSize() ;
        super.add(triples) ;
    }
    
    @SuppressWarnings("unchecked")
    @Override
    public void add( List triples )
    {
        lGraph.count = lGraph.count+triples.size() ;
        lGraph.checkSize() ;
        super.add(triples);
    }
    
    @SuppressWarnings("unchecked")
    @Override
    public void add( Iterator it )
    {
        for ( ; it.hasNext() ; )
        {
            Triple t = (Triple)it.next() ;
            lGraph.count++ ;
            lGraph.checkSize() ;
            graph.add(t) ;
        }
    }
    
    @Override
    public void add( Graph g, boolean withReifications )
    {
        // Not perfect
        lGraph.count = lGraph.count+g.size() ;
        lGraph.checkSize() ;
        super.add(g, withReifications) ;
    }
    
    @Override
    public void add( Graph g )
    {
        lGraph.count = lGraph.count+g.size() ;
        lGraph.checkSize() ;
        super.add( g );
    }
}

/*
 * (c) Copyright 2005, 2006, 2007, 2008, 2009 Hewlett-Packard Development Company, LP
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. The name of the author may not be used to endorse or promote products
 *    derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
 * IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 * IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
 * NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
 * THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */