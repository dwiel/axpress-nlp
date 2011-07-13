/*
 * (c) Copyright 2005, 2006, 2007, 2008, 2009 Hewlett-Packard Development Company, LP
 * All rights reserved.
 * [See end of file]
 */

package org.joseki.junit;

import java.io.ByteArrayInputStream;
import java.io.InputStream;

import junit.framework.TestCase;
import org.joseki.Joseki;

import com.hp.hpl.jena.query.*;
import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.sparql.engine.http.HttpContentType;
import com.hp.hpl.jena.sparql.engine.http.HttpQuery;
import com.hp.hpl.jena.sparql.engine.http.Params;
import com.hp.hpl.jena.sparql.engine.http.QueryExceptionHTTP;
import com.hp.hpl.jena.sparql.resultset.ResultSetRewindable;
import com.hp.hpl.jena.sparql.resultset.XMLInput;

public class ProtocolTest extends TestCase
{
    HttpQuery httpQuery = null ;
    int responseCode = -1 ;
    String acceptType ;
    String responseType ;
    String response ;
    
    public ProtocolTest(String name, String target, String acceptType, int responseCode,  String responseType, String response)
    { 
        super(name) ;
        httpQuery = new HttpQuery(target) ;
        this.responseCode = responseCode ;
        this.acceptType = acceptType ;
        this.responseType = responseType ;
        this.response = response;
    }
        
    public Params getParams() { return httpQuery ; }
    public HttpQuery getHttpQuery() { return httpQuery ; }
    
    @Override
    protected void runTest() throws Exception
    {
        if ( acceptType != null )
            httpQuery.setAccept(acceptType) ;
        try {
            InputStream in = httpQuery.exec() ;
            assertEquals("Different response codes", responseCode, httpQuery.getConnection().getResponseCode() ) ;
            String cType = httpQuery.getConnection().getContentType() ;
            cType = new HttpContentType(cType).getMediaType() ;
            assertEquals("Different content types", responseType, cType) ;

            Query query = QueryFactory.create(this.httpQuery.getValue("query"));

            if(this.responseType.equals(Joseki.contentTypeResultsXML)) {
            	
            	if(query.getQueryType() == Query.QueryTypeAsk) {

            		// Convert the query response to boolean
            		boolean qresult = XMLInput.booleanFromXML(in) ;
                	
                	// Convert the expected to ResultSet and then to Model
                	ByteArrayInputStream exin = new ByteArrayInputStream(this.response.getBytes());
                	boolean exresult = XMLInput.booleanFromXML(exin) ;
                	
                	assertEquals("ASK result did not match", exresult, qresult);

            		
            	} else if(query.getQueryType() == Query.QueryTypeSelect) {

                	// Convert the query response to ResultSet and then to Model
                	ResultSetRewindable qrs = ResultSetFactory.makeRewindable(ResultSetFactory.fromXML(in));
                	Model qmodel = ResultSetFormatter.toModel(qrs);

                	/*
                	  
                	//Debugging only
                	 
                	qrs.reset();
                	ResultSetFormatter.out(System.err, qrs);
                	
                	qrs.reset();
                	System.err.println(ResultSetFormatter.asXMLString(qrs));
                	
                	*/
                	
                	// Convert the expected to ResultSet and then to Model
                	ByteArrayInputStream exin = new ByteArrayInputStream(this.response.getBytes());
                	ResultSet rs = ResultSetFactory.fromXML(exin);
                	Model model = ResultSetFormatter.toModel(rs);
                	
                	assertTrue("ResultSet are not isomorphic", model.isIsomorphicWith(qmodel));
            		
            	}
            }
            
        } catch (QueryExceptionHTTP ex)
        {
            int rc = ex.getResponseCode() ;
            if ( responseCode == 200 )
                fail("Got an error response ("+rc+") when expecting OK") ;
            assertEquals(responseCode, rc) ;
        }
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