/*
 * (c) Copyright 2005, 2006, 2007, 2008, 2009 Hewlett-Packard Development Company, LP
 * All rights reserved.
 * [See end of file]
 */

package org.joseki.junit;

/* Many thanks to Elias Torres [elias@torrez.us] for 
 * making this work with the Data Access Working Group protocol
 * tests.
 */

import junit.framework.TestSuite;
import org.joseki.vocabulary.TestProtocolVocab;

import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.rdf.model.Statement;
import com.hp.hpl.jena.rdf.model.StmtIterator;
import com.hp.hpl.jena.shared.NotFoundException;
import com.hp.hpl.jena.sparql.engine.http.HttpParams;
import com.hp.hpl.jena.util.FileManager;


public class ProtocolTestGenerator implements ManifestItemHandler
{
    //String target ;
    TestSuite testSuite ;
    
    public ProtocolTestGenerator(TestSuite ts)
    {
        this.testSuite = ts ;
    }
    
    /*
     *         [
            ptest:name "select-svcsupplied" ;
            ptest:comment "SELECT with service-supplied RDF dataset" ;
            ptest:serviceDataSet [
                ptest:defaultGraph [
                    ptest:graphName example:books;
                    ptest:graphData <http://www.w3.org/2001/sw/DataAccess/proto-tests/data/select/svcsupplied-data.ttl>
                ]
            ] ;
            ptest:query <svcsupplied-query.rq> ;
            ptest:acceptType "application/sparql-results+xml" ;
            ptest:preferredResult [
                ptest:result <svcsupplied-results.xml> ;
                ptest:resultCode "200" ;
                ptest:resultContentType "application/sparql-results+xml"
            ]
        ]

     */

    public boolean processManifestItem(Resource manifest,
                                       Resource entry, 
                                       String testName) 
//                                       Resource action,
//                                       Resource result)
    {
        String name = TestUtils.getLiteral(entry, TestProtocolVocab.name) ;
        String comment = TestUtils.getLiteral(entry, TestProtocolVocab.comment) ;
        
        Resource dataset = TestUtils.getResource(entry, TestProtocolVocab.dataSet) ;
        Resource svcDataset = TestUtils.getResource(entry, TestProtocolVocab.serviceDataSet) ;
        
        Resource queryDataset = TestUtils.getResource(entry, TestProtocolVocab.queryDataSet) ;
        
        Resource target = TestUtils.getResource(entry, TestProtocolVocab.service) ;
        
        // In fact, this is a file 
        String queryLoc = TestUtils.getLiteralOrURI(entry, TestProtocolVocab.query) ;
        
        String acceptType = TestUtils.getLiteral(entry, TestProtocolVocab.acceptType) ;
        Resource result = TestUtils.getResource(entry, TestProtocolVocab.preferredResult) ;
        if ( result == null )
        {
            System.err.println("Warning: no results to test : "+name) ;
            return false ;
        }
        
        int rc = Integer.parseInt(TestUtils.getLiteral(result, TestProtocolVocab.resultCode)) ;
        String resultContentType = TestUtils.getLiteral(result, TestProtocolVocab.resultContentType) ;
        
        
        //System.out.println("Test: "+name) ;
        if ( target == null )
        {
            System.err.println(name+" : No service - skipped") ;
            return false;
        }
        
        // In fact, this is also a file         
        String responseLoc = TestUtils.getLiteralOrURI(result, TestProtocolVocab.result) ;
        
        
        String responseStr = null;
        
        if( responseLoc != null )
        {        
	        try {
	        	responseStr = FileManager.get().readWholeFileAsUTF8(responseLoc) ;
	        } catch(NotFoundException nfe) {
	        	System.err.println(name+" : Response file does not exist - skipped");
	        	return false;        	
	        }
        }

        ProtocolTest test = new ProtocolTest(name, target.getURI(), acceptType, rc, resultContentType, responseStr) ;
        // ---- query
        String qStr = FileManager.get().readWholeFileAsUTF8(queryLoc) ;
        
        // ---- graph URI substitution
        parseQueryDataset(test, queryDataset, qStr);
        
        // ---- default graph / protocol
        if ( dataset == null && svcDataset == null )
            System.err.println(test.getName()+": No dataset and no service dataset") ;

        parseDataset(test, dataset) ;
        testSuite.addTest(test) ;
        
        // Other args.
        
        return true; 
    }

    public void parseDataset(ProtocolTest test, Resource ds)
    {
        if ( ds == null )
            return ;
        
        Resource g = TestUtils.getResource(ds, TestProtocolVocab.defaultGraph) ; 
        parseGraph(test, g, true) ;
        
        StmtIterator sIter = ds.listProperties(TestProtocolVocab.namedGraph) ;
        while(sIter.hasNext())
        {
            Statement stmt = sIter.nextStatement() ;
            Resource gn = stmt.getResource() ;
            parseGraph(test, gn, false) ;
        }
        sIter.close() ;
    }
    
    public void parseGraph(ProtocolTest test, Resource g, boolean isDefault)
    {
        Resource gn = TestUtils.getResource(g, TestProtocolVocab.graphName) ;
        Resource gd = TestUtils.getResource(g, TestProtocolVocab.graphData) ;
        if ( gd == null )
            return ;
        
        if ( isDefault )
            test.getParams().addParam(HttpParams.pDefaultGraph, gd.getURI()) ;
        else
            test.getParams().addParam(HttpParams.pNamedGraph, gd.getURI()) ;
    }
    
    /**
     * This method substitutes any graph URIs in the query string with those
     * found in the ptest:queryDataset of the manifest item. 
     * 
     * @param test
     * @param ds
     * @param qStr
     */
    public void parseQueryDataset(ProtocolTest test, Resource ds, String qStr)
    {
    	if ( ds != null ) {
     	
	        Resource g = TestUtils.getResource(ds, TestProtocolVocab.defaultGraph) ; 
	        if(g != null) {
	            String gn = TestUtils.getLiteralOrURI(g, TestProtocolVocab.graphName) ;
	            String gd = TestUtils.getLiteralOrURI(g, TestProtocolVocab.graphData) ;
	            // if(qStr.contains(gn))
                if ( qStr.indexOf(gn) >= 0 )
	            	qStr = qStr.replaceFirst(gn, gd);
	        }
	        
	        StmtIterator sIter = ds.listProperties(TestProtocolVocab.namedGraph) ;
	        while(sIter.hasNext())
	        {
	            Statement stmt = sIter.nextStatement() ;
	            Resource ng = stmt.getResource() ;
	            String gn = TestUtils.getLiteralOrURI(ng, TestProtocolVocab.graphName) ;
	            String gd = TestUtils.getLiteralOrURI(ng, TestProtocolVocab.graphData) ;
	            //if(qStr.contains(gn))
                if ( qStr.indexOf(gn) >= 0 )
	            	qStr = qStr.replaceFirst(gn, gd);
	        }
	        sIter.close() ;
	        
        }
        
        test.getParams().addParam("query", qStr) ;
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