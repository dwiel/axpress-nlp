/*
 * (c) Copyright 2005, 2006, 2007, 2008, 2009 Hewlett-Packard Development Company, LP
 * All rights reserved.
 * [See end of file]
 */

package org.joseki;

import com.hp.hpl.jena.rdf.model.Literal;
import com.hp.hpl.jena.rdf.model.RDFNode;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.shared.PrefixMapping;
import com.hp.hpl.jena.vocabulary.RDFS;


public class Utils
{
    
    public static String stringFromNode(RDFNode n)
    {
        if ( n instanceof Resource )
        {
            Resource r = (Resource)n ;
            if ( r.isAnon() )
                return null ;
            return r.getURI() ;
        }        
        Literal lit = (Literal)n ;
        return lit.getLexicalForm() ;
    }        
    
    // Node presentation
    public static String nodeLabel(RDFNode n)
    {
        if ( n == null )
            return "<null>" ;
        if ( n instanceof Resource )
            return strForResource((Resource)n) ;
        
        Literal lit = (Literal)n ;
        return lit.getLexicalForm() ;
    }

    public static String strForResource(Resource r) { return strForResource(r, r.getModel()) ; }
    
    private static String strForResource(Resource r, PrefixMapping pm)
    {
        if ( r == null )
            return "NULL ";
        if ( r.hasProperty(RDFS.label))
        {
            RDFNode n = r.getProperty(RDFS.label).getObject() ;
            if ( n instanceof Literal )
                return ((Literal)n).getString() ;
        }
        
        if ( r.isAnon() )
            return "<<blank node>>" ;

        if ( pm == null )
            pm = r.getModel() ;

        return strForURI(r.getURI(), pm ) ;
    }
    
    public static String strForURI(String uri, PrefixMapping pm)
    {
        if ( pm != null )
        {
            String x = pm.shortForm(uri) ;
            
            if ( ! x.equals(uri) )
                return x ;
        }
        return "<"+uri+">" ;
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