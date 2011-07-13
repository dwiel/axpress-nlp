/*
 * (c) Copyright 2005, 2006, 2007, 2008, 2009 Hewlett-Packard Development Company, LP
 * All rights reserved.
 * [See end of file]
 */

package org.joseki.http;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import javax.servlet.ServletOutputStream;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.joseki.*;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.shared.JenaException;

import com.hp.hpl.jena.query.QueryException;
import com.hp.hpl.jena.query.ResultSet;
import com.hp.hpl.jena.query.ResultSetFormatter;


public class ResponseHttp extends Response
{
    private static Log log = LogFactory.getLog(ResponseHttp.class) ;
    HttpResultSerializer ser = new HttpResultSerializer() ;
    
    static AcceptItem defaultCharset      = new AcceptItem(Joseki.charsetUTF8) ;
    static AcceptList prefCharset         = new AcceptList("utf-8") ;
    
    interface OutputContent { void output(ServletOutputStream out) ; }

    // These EXCLUDE application/xml
    static AcceptItem defaultContentType  = new AcceptItem(Joseki.contentTypeRDFXML) ;
    
    static String[] x = { //Joseki.contentTypeXML ,
                          Joseki.contentTypeRDFXML ,
                          Joseki.contentTypeTurtle ,
                          Joseki.contentTypeTurtleAlt ,
                          Joseki.contentTypeN3 ,
                          Joseki.contentTypeN3Alt ,
                          Joseki.contentTypeNTriples,
                          Joseki.contentTypeNTriplesAlt
                          } ;

    // MIME types we offer 
    static AcceptList prefContentType     = new AcceptList(x) ;

    // The correct names for the above.
    static Map<String, String> correctedTypes = new HashMap<String, String>() ;
    static {
        correctedTypes.put(Joseki.contentTypeXML, Joseki.contentTypeRDFXML) ;
        correctedTypes.put(Joseki.contentTypeN3Alt, Joseki.contentTypeN3) ;
        correctedTypes.put(Joseki.contentTypeTurtleAlt, Joseki.contentTypeTurtle) ;
        correctedTypes.put(Joseki.contentTypeNTriplesAlt, Joseki.contentTypeNTriples) ;
    }
    
    
    private HttpServletResponse httpResponse ;
    private HttpServletRequest httpRequest ; 
    
    
    static final String paramStyleSheet = "stylesheet" ;
    static final String paramAccept     = "accept" ;
    static final String paramOutput     = "output" ;        // See Yahoo! developer: http://developer.yahoo.net/common/json.html 
    static final String paramCallback   = "callback" ;
    static final String headerAccept    = "Accept" ;
    
    ResponseHttp(Request request, HttpServletRequest httpRequest, HttpServletResponse httpResponse) 
    { 
        // TODO Move content negotiation to constructor so early failures.
        super(request) ;
        this.httpResponse = httpResponse ;
        this.httpRequest = httpRequest ; 
    }
    
    @Override
    protected void doResponseModel(Model model) throws QueryExecutionException
    {
        String mimeType = null ;        // Header request type 
        String charset = null ;
        
        // Return text/plain if it looks like a browser.
        String acceptHeader = paramAcceptField() ;
        if ( acceptHeader == null )
            acceptHeader = Joseki.contentTypeRDFXML ;
        
//        String textContentType =  HttpUtils.match(acceptHeader, "text/*") ; 
//
//        if ( textContentType != null )
//        {
//            // Send to a browser.  Send as whatever the default type is for the 
//            writerMimeType = Joseki.contentTypeForText ;
//            mimeType = Joseki.contentTypeForText ;
//            log.debug("MIME type (text-like): "+writerMimeType) ;
//        }
        
//     // ---- Choose the content type and serialization.
//        if ( HttpUtils.accept(acceptField, Joseki.contentTypeXML) ||  
//             HttpUtils.accept(acceptField, Joseki.contentTypeResultsXML) )
//            contentType = Joseki.contentTypeResultsXML ;
//        
//        if ( acceptField.equalsIgnoreCase(Joseki.contentTypeResultsJSON) )
//            contentType = Joseki.contentTypeResultsJSON ;
        
        
        AcceptItem i = HttpUtils.choose(acceptHeader, prefContentType, defaultContentType) ;
        if ( i != null )
        	mimeType = i.getAcceptType() ;
        
        // Ignore charset unless RDF/XML
        if (  mimeType != null && mimeType.equals(Joseki.contentTypeRDFXML) )
        {
            AcceptItem i2 = HttpUtils.chooseCharset(httpRequest,  prefCharset, defaultCharset) ;
            if ( i2 != null )
            	charset = i.getAcceptType() ;
        }
        String writerMimeType = mimeType ;
        
        // If the requets is for test/plain, send N3 (sanity - avoid N-triples) 
        if ( mimeType != null && mimeType.equals(Joseki.contentTypeTextPlain) )
            // text/plain => text/rdf+n3
            writerMimeType = Joseki.contentTypeN3 ;
        
        if ( mimeType == null )
        {
            try
            {
                httpResponse.sendError(HttpServletResponse.SC_NOT_ACCEPTABLE) ;
            } catch (IOException ex)
            {
                log.warn("Internal server error") ;
                try { httpResponse.sendError(HttpServletResponse.SC_INTERNAL_SERVER_ERROR) ; }
                catch (Exception e) {}
            }
        }
        
        if ( correctedTypes.containsKey(mimeType) )
            mimeType = correctedTypes.get(mimeType) ;
        
        if ( mimeType.equals(Joseki.contentTypeN3) )
            // Force to UTF-8 for N3 always
            charset = Joseki.charsetUTF8 ;
        
        ser.setHttpResponse(httpRequest, httpResponse, mimeType, charset);   
        
        try {
            try {
                ser.writeModel(model, request, httpRequest, httpResponse, writerMimeType) ;
            }
//            catch (RDFException rEx)
//            {
//                log.warn("JenaException", jEx);
//            }
            catch (JenaException jEx)
            {
                //msg(Level.WARNING, "RDFException", rdfEx);
                log.warn("JenaException: "+jEx.getMessage(), jEx);
                //printStackTrace(printName + "(execute)", rdfEx);
                httpResponse.sendError(
                        HttpServletResponse.SC_INTERNAL_SERVER_ERROR,
                        "JenaException: " + jEx.getMessage());
                return;
            } catch (Exception ex)
            {
                try {
                    log.warn("Internal server error", ex) ;
                    httpResponse.sendError(HttpServletResponse.SC_INTERNAL_SERVER_ERROR) ;
                } catch (Exception e) {}
            }
        } catch (IOException ioEx)
        {
            //msg(Level.WARNING,"IOException in normal response") ;
            log.warn("IOException in normal response") ;
            try {
                httpResponse.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
                httpResponse.flushBuffer();
                httpResponse.getWriter().close();
            } catch (Exception e) { }
        }
    }
    
    @Override
    protected void doResponseResultSet(ResultSet resultSet) throws QueryExecutionException
    {
        doResponseResult(resultSet, null) ;
    }
    
    @Override
    protected void doResponseBoolean(final Boolean result) throws QueryExecutionException
    {
        doResponseResult(null, result) ;
    }

    
    // One of the other argument must be null
    private void doResponseResult(final ResultSet resultSet, final Boolean booleanResult) throws QueryExecutionException
    {
        if ( resultSet == null && booleanResult == null )
        {
            log.warn("doResponseResult: Both result set and boolean result are null") ; 
            throw new QueryExecutionException(ReturnCodes.rcInternalError, "Both result set and boolean result are null") ;
        }
        
        if ( resultSet != null && booleanResult != null )
        {
            log.warn("doResponseResult: Both result set and boolean result are set") ; 
            throw new QueryExecutionException(ReturnCodes.rcInternalError, "Both result set and boolean result are set") ;
        }
        
        boolean wantsStyle = request.containsParam(paramStyleSheet) ;
        String acceptField = paramAcceptField() ;
        if ( acceptField == null )
            acceptField = Joseki.contentTypeResultsXML ;
        
        String outputField = paramOutput() ;
        String contentType = Joseki.contentTypeResultsXML ;
        
        // ---- Choose the content type and serialization.
        if ( HttpUtils.accept(acceptField, Joseki.contentTypeXML) ||  
             HttpUtils.accept(acceptField, Joseki.contentTypeResultsXML) )
            contentType = Joseki.contentTypeResultsXML ;
        
        if ( acceptField.equalsIgnoreCase(Joseki.contentTypeResultsJSON) )
            contentType = Joseki.contentTypeResultsJSON ;
        
        // Serialialization is the content type unless overridden. 
        String serializationType = contentType ;

        // output field causes the serialization to be set
        if ( outputField != null )
        {
            serializationType = outputField ;
            contentType = Joseki.contentTypeResultsJSON ;
        }

        // ---- Form: XML
        if ( serializationType.equals(Joseki.contentTypeResultsXML) )
        {
            final String stylesheetURL = paramStylesheet() ;
            if ( stylesheetURL != null )
                contentType = Joseki.contentTypeXML ; 

            try {
                output(contentType, null, new OutputContent()
                {
                    public void output(ServletOutputStream out)
                    {
                        if ( resultSet != null )
                            ResultSetFormatter.outputAsXML(out, resultSet, stylesheetURL) ;
                        if ( booleanResult != null )
                            ResultSetFormatter.outputAsXML(out, booleanResult.booleanValue(), stylesheetURL) ;
                    }
                }) ;
            }
            catch (QueryException qEx)
            {
                log.info("Query execution error (SELECT/XML): "+qEx) ;
                throw new QueryExecutionException(ReturnCodes.rcQueryExecutionFailure, qEx.getMessage()) ;
            }
            catch (org.mortbay.jetty.EofException eofEx) { }
            catch (IOException ioEx)
            {
                if ( ! ( ioEx instanceof java.io.EOFException ) )
                    log.warn("IOException[(SELECT/XML)] (ignored) "+ioEx, ioEx) ;
                else
                    log.debug("IOException[(SELECT/XML)] (ignored) "+ioEx, ioEx) ;
            }
            // This catches things like NIO exceptions.
            catch (Exception ex) { log.debug("Exception [SELECT/XML]"+ex, ex) ; } 
            return ;
        }

        // ---- Form: JSON
        if ( serializationType.equals(Joseki.contentTypeResultsJSON) )
        {
            try {
                if ( outputField != null && outputField.equals(Joseki.contentOutputJSON) )
                    contentType = Joseki.contentTypeTextPlain ;

                jsonOutput(contentType, new OutputContent(){
                    public void output(ServletOutputStream out)
                    {
                        if ( resultSet != null )
                            ResultSetFormatter.outputAsJSON(out, resultSet) ;
                        if (  booleanResult != null )
                            ResultSetFormatter.outputAsJSON(out, booleanResult.booleanValue()) ;
                    }
                }) ;
            }
            catch (QueryException qEx)
            {
                log.info("Query execution error (SELECT/JSON): "+qEx) ;
                throw new QueryExecutionException(ReturnCodes.rcQueryExecutionFailure, qEx.getMessage()) ;
            }
            catch (org.mortbay.jetty.EofException eofEx) { }
            catch (IOException ioEx)
            {
                if ( ! ( ioEx instanceof java.io.EOFException ) )
                    log.warn("IOException[SELECT/JSON] (ignored) "+ioEx, ioEx) ;
                else
                    log.debug("IOException [SELECT/JSON] (ignored) "+ioEx, ioEx) ;
            }
            // This catches things like NIO exceptions.
            catch (Exception ex) { log.debug("Exception [SELECT/JSON] "+ex, ex) ; } 
            return ;
        }

        // Not JSON.  Not XML.  Send as a model.
        Model m = null ;
        if ( resultSet != null )
            m = ResultSetFormatter.toModel(resultSet) ;
        if ( booleanResult != null )
            m = ResultSetFormatter.toModel(booleanResult.booleanValue()) ;
        doResponseModel(m) ;
    }
    
    
    @Override
    protected void doResponseNothing() throws QueryExecutionException
    {
    }

    @Override
    protected void doException(ExecutionException execEx)
    {
        HttpResultSerializer httpSerializer = new HttpResultSerializer() ;
        httpSerializer.setHttpResponse(httpRequest, httpResponse, null, null) ;
        
        String httpMsg = execEx.shortMessage ;
        if (execEx.shortMessage == null)
            httpMsg = ReturnCodes.errorString(execEx.returnCode);

            //msg("Error in operation: URI = " + uri + " : " + httpMsg);
            
        ExecutionException ex = execEx ;
        if ( execEx instanceof QueryExecutionException )
            // Don't detail queryex ecution problems (e.g. parse errors).
            ex = null ;
        
        log.info("Error: URI = " + request.getServiceURI() + " : " + httpMsg) ;
        httpSerializer.sendError(execEx, httpResponse) ;
    }
    
    private void output(String contentType, String charset, OutputContent proc)  throws IOException
    {
        ser.setHttpResponse(httpRequest, httpResponse, contentType, charset);  
        httpResponse.setStatus(HttpServletResponse.SC_OK) ;
        httpResponse.setHeader(Joseki.httpHeaderField, Joseki.httpHeaderValue);
        ServletOutputStream out = httpResponse.getOutputStream() ;
        proc.output(out) ;
        out.flush() ;
        httpResponse.flushBuffer();
    }

    private void jsonOutput(String contentType, OutputContent proc) throws IOException
    {
        String callback = paramCallback() ;
        String outputField = paramOutput() ;
        ServletOutputStream out = httpResponse.getOutputStream() ;
        
        if ( callback != null )
        {
            out.print(callback) ;
            out.println("(") ;
        }
        
        output(contentType, Joseki.charsetUTF8, proc) ;
        
        if ( callback != null )
        {
            out.print(")") ;
            out.println() ;
        }
        out.flush() ;
        httpResponse.flushBuffer();
    }

    private String paramStylesheet() { return fetchParam(paramStyleSheet) ; }
    
    private String paramOutput()     { return expandShortName(fetchParam(paramOutput)) ; }
    
    private String paramAcceptField()
    {
        String acceptField = httpRequest.getHeader(headerAccept) ;
        String acceptParam = fetchParam(paramAccept) ;
        
        if ( acceptParam != null )
            acceptField = acceptParam ;
        if ( acceptField == null )
            return null ;
        
//        // Catch an easy mistake to make.  Unfortunately, can't get the message to the caller very easily. 
//        if ( acceptField.indexOf(" ") >= 0 ) // acceptField.contains() in Java 1.5
//        {
//            log.warn("The accept parameter value has a space in it - did you mean '+'?");
//            log.warn("You need to use %2B - '+' is the encoding of a space") ;  
//        }
        
        return expandShortName(acceptField) ; 
    }

    private String expandShortName(String str)
    {
        if ( str == null )
            return null ;
        // Some short names.
        if ( str.equalsIgnoreCase(Joseki.contentOutputJSON) ) 
            return Joseki.contentTypeResultsJSON ;
        if ( str.equalsIgnoreCase(Joseki.contentOutputSPARQL) )
            return Joseki.contentTypeResultsXML ;
        if ( str.equalsIgnoreCase(Joseki.contentOutputXML) )
            return Joseki.contentTypeResultsXML ;
        return str ;
    }
    
    private String paramCallback() { return fetchParam(paramCallback) ; }
    
    private String fetchParam(String parameterName)
    {
        String value = null ;
        if ( request.containsParam(parameterName) )
        {
            value = request.getParam(parameterName) ;
            if ( value != null )
            {
                value = value.trim() ;
                if ( value.length() == 0 )
                    value = null ;
            }
        }
        return value ;
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