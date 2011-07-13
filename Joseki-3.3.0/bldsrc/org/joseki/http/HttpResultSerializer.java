/*
 * (c) Copyright 2003, 2004, 2005, 2006, 2007, 2008, 2009 Hewlett-Packard Development Company, LP
 * [See end of file]
 */

package org.joseki.http;

import java.io.*;

import org.apache.commons.logging.* ;

import javax.servlet.http.* ; 
import org.joseki.Joseki ;

import org.joseki.* ;
import org.joseki.util.NullOutputStream ; 

import com.hp.hpl.jena.rdf.model.*;
import com.hp.hpl.jena.shared.JenaException;

/** Extracting operation data from HTTP servlet requests and formatting results for sending back.
 * 
 * @author      Andy Seaborne
 * @version     $Id: HttpResultSerializer.java,v 1.10 2008/12/28 19:51:04 andy_seaborne Exp $
 */
public class HttpResultSerializer
{
    static Log log = LogFactory.getLog(HttpResultSerializer.class) ;
    
    public HttpResultSerializer() {}

    
    public boolean writeModel(Model resultModel, Request request,
                             HttpServletRequest httpRequest,
                             HttpServletResponse httpResponse, String mimeType)
    {
        String writerType = Joseki.getWriterType(mimeType) ;
        if ( writerType == null )
        {
            // No writer found.  Default it ...
            writerType = Joseki.getWriterType(Joseki.serverContentType) ;
            //logger.warn("MIME type for response if null: force use of "+writerType) ;
        }   
             
        if (false)
            try {
                FileOutputStream out = new FileOutputStream("response.n3");
                resultModel.write(out, "N3");
                out.close() ;
            } catch (IOException ex) { log.fatal("Failed to write 'response.n3'", ex) ; }
        
        if ( false )
        {
            log.info("Result model ("+writerType+")") ;
            StringWriter sw = new StringWriter() ;
            //resultModel.write(sw, writerType);
            resultModel.write(sw, "N3");
            log.info("\n"+sw.toString()) ;
            
        }

        // Write result model.
        // Need to do this robustly.  The model may contain bad URIs
        // which may cause the writer to crash part way though.
        // To check this, we write to a null output sink first.  If this
        // works, we can create a HTTP response.
        
        RDFWriter rdfw = resultModel.getWriter(writerType) ;
        
        if ( writerType.equals("RDF/XML-ABBREV") || writerType.equals("RDF/XML") )
        {
            rdfw.setProperty("showXmlDeclaration", "true") ;

            if ( writerType.equals("RDF/XML-ABBREV") )
                // Workaround for the j.cook.up bug.
                rdfw.setProperty("blockRules", "propertyAttr") ;
        }
        
        // TODO Allow a mode of write to buffer (memory, disk), write buffer later.
        // Time/space tradeoff.
        try {
            OutputStream out = new NullOutputStream() ;
            rdfw.write(resultModel, out, null) ;
            try { out.flush() ; } catch (IOException ioEx) {}
        } catch (JenaException ex)
        {
            // Failed to write the model :-(
            log.warn("Exception test writing model: "+ex.getMessage(), ex) ;
            sendPanic(request, httpRequest, httpResponse, ex,
                    "Server internal error: can't write the model.") ;
            throw ex ;
        }
        
        // Managed to write it.
        
        log.trace("HTTP response 200") ;
        try {
            rdfw.write(resultModel, httpResponse.getOutputStream(), null) ;
            httpResponse.getOutputStream().flush() ;
        }
        catch (IOException ex) { log.warn("Failed to write response", ex) ; }
        return true ;
    }

    
    /** Set HTTP header */
    
    public void setHttpResponse(HttpServletRequest httpRequest,
                                 HttpServletResponse httpResponse,
                                 String mimeType, String charset) 
    {
        // ---- Set up HTTP Response
        // Stop caching (not that ?queryString URLs are cached anyway)
        if ( Joseki.serverHttpExplicitNoCache )
        {
            httpResponse.setHeader("Cache-Control", "no-cache") ;
            httpResponse.setHeader("Pragma", "no-cache") ;
        }

        httpResponse.setHeader(Joseki.httpHeaderField, Joseki.httpHeaderValue) ;

        //HttpUtils.setContentHeaders(httpRequest, httpResponse) ;
        
        // See: http://www.w3.org/International/O-HTTP-charset.html
        if ( mimeType != null )
        {
            String contentType = mimeType ;
            if ( charset != null )
                contentType = contentType+"; charset="+charset ;
            log.trace("Content-Type for response: "+contentType) ;
            httpResponse.setContentType(contentType) ;
        }
    }
    
    // 400 is SPARQL malformed query
    // 500 is SPARQL query request refused
    
    // SPARQL/Update errors result in "Bad request"
    static int SPARQL_MalformedQuery        = HttpServletResponse.SC_BAD_REQUEST ;
    static int SPARQL_QueryRequestRefused   = HttpServletResponse.SC_INTERNAL_SERVER_ERROR ;
    static int SPARQL_UpdateFailed          = HttpServletResponse.SC_BAD_REQUEST ;
    
    public void sendError(ExecutionException execEx, HttpServletResponse response)
    {
        try {
            int httpRC = -1;
            String httpMsg = execEx.shortMessage ;
            if (execEx.shortMessage == null)
                httpMsg = ReturnCodes.errorString(execEx.returnCode);
    
            switch (execEx.returnCode)
            {
                case ReturnCodes.rcOK :
                    httpRC = 200;
                    break;
                case ReturnCodes.rcQueryParseFailure :
                    httpRC = SPARQL_MalformedQuery;
                    break;
                case ReturnCodes.rcQueryExecutionFailure :
                    httpRC = SPARQL_QueryRequestRefused;
                    break;
                case ReturnCodes.rcNoSuchQueryLanguage :
                    httpRC = HttpServletResponse.SC_NOT_IMPLEMENTED ;
                    break;
                case ReturnCodes.rcInternalError :
                    httpRC = HttpServletResponse.SC_INTERNAL_SERVER_ERROR;
                    break;
                case ReturnCodes.rcJenaException :
                    httpRC = SPARQL_QueryRequestRefused ;
                    break ;
                case ReturnCodes.rcNoSuchURI:
                    httpRC = HttpServletResponse.SC_NOT_FOUND ;
                    break ;
                case ReturnCodes.rcSecurityError:
                    httpRC = HttpServletResponse.SC_FORBIDDEN ;
                    break ;
                case ReturnCodes.rcOperationNotSupported:
                    httpRC = HttpServletResponse.SC_NOT_IMPLEMENTED ;
                    break ;
                case ReturnCodes.rcArgumentUnreadable:
                    httpRC = HttpServletResponse.SC_INTERNAL_SERVER_ERROR ;
                    break ;
                case ReturnCodes.rcImmutableModel:
                    httpRC = HttpServletResponse.SC_METHOD_NOT_ALLOWED ;
                    break ;
                case ReturnCodes.rcConfigurationError:
                    httpRC = SPARQL_QueryRequestRefused ;
                    break ;
                case ReturnCodes.rcArgumentError:
                    httpRC = SPARQL_MalformedQuery ;
                    break ;
                case ReturnCodes.rcNotImplemented:
                    httpRC = HttpServletResponse.SC_NOT_IMPLEMENTED ;
                    break ;
                case ReturnCodes.rcServiceUnavailable:
                    httpRC = HttpServletResponse.SC_SERVICE_UNAVAILABLE ;
                    break ;
                case ReturnCodes.rcResourceNotFound:
                    httpRC = HttpServletResponse.SC_INTERNAL_SERVER_ERROR ;
                    break ;
                case ReturnCodes.rcBadRequest:
                    httpRC = SPARQL_MalformedQuery ;
                    break ;
                case ReturnCodes.rcUpdateExecutionFailure:
                    httpRC = SPARQL_UpdateFailed ;
                    break ;
                default :
                    httpRC = HttpServletResponse.SC_INTERNAL_SERVER_ERROR;
                    break;
            }
            response.setHeader(Joseki.httpHeaderField, Joseki.httpHeaderValue) ;
            response.sendError(httpRC, httpMsg) ;
        } catch (Exception ex2) { log.warn("Problems sending error", ex2) ; } 
    }
    
    
    // Things are going very badly 
    public void sendPanic( Request request,
                           HttpServletRequest httpRequest,
                           HttpServletResponse httpResponse,
                           Exception ex,
                           String msg)
    {
        try {
            httpResponse.setContentType("text/plain");
            httpResponse.setHeader(Joseki.httpHeaderField, Joseki.httpHeaderValue);
            httpResponse.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
    
            PrintWriter pw = httpResponse.getWriter();
            pw.println(msg);
            pw.println();
            pw.println("URI = " + request.getServiceURI());
//            if ( request != null )
//            {
//                for (Iterator iter = request.getParamPairs().listIterator(); iter.hasNext();)
//                {
//                    Params.Pair  p = (Params.Pair)iter.next();
//                    pw.println("    "+p.getName() + " = " + p.getValue()) ;
//                }
//                pw.println() ;
//            }
            if ( ex != null )
                ex.printStackTrace(pw) ;
            pw.flush();
            return;
        } catch (Exception ex2) { log.warn("Problems sending panic", ex2) ; }
    }
    
//  /** Send a response.  
//  * @param resultModel
//  * @param request
//  * @param httpRequest
//  * @param httpResponse
//  * @return true for a successful send, false for any problem (ie.e HTTP repsonse if not 200)
//  */
// 
// public boolean sendResponse(Model resultModel, Request request,
//                          HttpServletRequest httpRequest,
//                          HttpServletResponse httpResponse)
// {
//     // Shouldn't be null - should be empty model
//     if (resultModel == null)
//     {
//         log.warn("Result is null pointer for result model") ;
//         sendPanic(request, httpRequest, httpResponse, null,
//                   "Server internal error: processor returned a null pointer, not a model") ;
//         return false;                 
//     }
//
//     String mimeType = HttpUtils.chooseMimeType(httpRequest);
//
//     setHttpResponse(httpRequest, httpResponse, mimeType);        
//     return writeModel(resultModel, request, httpRequest, httpResponse, mimeType) ;
// }

}


/*
 *  (c) Copyright 2003, 2004, 2005, 2006, 2007, 2008, 2009 Hewlett-Packard Development Company, LP
 *  All rights reserved.
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
