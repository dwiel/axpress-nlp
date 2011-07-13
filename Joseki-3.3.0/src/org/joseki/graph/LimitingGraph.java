/*
 * (c) Copyright 2005, 2006, 2007, 2008, 2009 Hewlett-Packard Development Company, LP
 * All rights reserved.
 * [See end of file]
 */

package org.joseki.graph;

import com.hp.hpl.jena.graph.BulkUpdateHandler;
import com.hp.hpl.jena.graph.Graph;
import com.hp.hpl.jena.graph.Triple;
import com.hp.hpl.jena.graph.impl.GraphWithPerform;

import com.hp.hpl.jena.graph.impl.WrappedGraph;
import com.hp.hpl.jena.shared.AddDeniedException;

public class LimitingGraph extends WrappedGraph implements GraphWithPerform
{
    int limit = 10000 ;
    int count = 0 ;
    
    LimitingBulkUpdateHandler bulk ;
    
    public LimitingGraph(Graph graph, int triplesLimit)
    {
        super(graph) ;
        this.limit = triplesLimit ;
        bulk = new LimitingBulkUpdateHandler(this, graph.getBulkUpdateHandler()) ;
    }

    @Override
    public void add( Triple t ) throws AddDeniedException
    {
        count++ ;
        checkSize() ;
        super.add(t) ;
    }

    /** returns this Graph's bulk-update handler */
    @Override
    public BulkUpdateHandler getBulkUpdateHandler()
    {
        return bulk ;
    }
    
    void checkSize()
    {
        if ( count > limit )
            throw new AddDeniedException("Attempt to exceed graph limit ("+limit+")") ;
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