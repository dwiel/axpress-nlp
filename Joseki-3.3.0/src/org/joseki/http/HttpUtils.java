/*
 * (c) Copyright 2004, 2005, 2006, 2007, 2008, 2009 Hewlett-Packard Development Company, LP
 * All rights reserved.
 * [See end of file]
 */

package org.joseki.http;

import javax.servlet.http.HttpServletRequest ;
import javax.servlet.http.HttpServletResponse ;

import org.apache.commons.logging.*;
import org.joseki.util.Convert;

/** org.joseki.server.http.HttpUtils
 * 
 * @author Andy Seaborne
 * @version $Id: HttpUtils.java,v 1.7 2008/12/28 19:51:04 andy_seaborne Exp $
 */

public class HttpUtils
{
    private static Log log = LogFactory.getLog(HttpUtils.class) ;

    /// Relevant headers:
    //  "Accept", "Accept-Encoding", "Accept-Charset"
    // Setting: Content-type, Content-Encoding
    
    // More complex preferences matching would be to weight the prefs and maximze
    // accept q * pref q.  No need to be that complicated at the moment.
    
    public static AcceptItem chooseCharset(HttpServletRequest httpRequest,
                                           AcceptList myPrefs,
                                           AcceptItem defaultAcceptItem)
    {
        String a = httpRequest.getHeader("Accept-Charset") ;
        if ( log.isDebugEnabled() )
            log.debug("Accept-Charset request: "+a) ;
        
        AcceptItem item = choose(a, myPrefs, defaultAcceptItem) ;
        
        if ( log.isDebugEnabled() )
            log.debug("Charset chosen: "+item) ;

        return item ;
    }
    
    public static AcceptItem chooseContentType(HttpServletRequest httpRequest,
                                               AcceptList myPrefs,
                                               AcceptItem defaultAcceptItem)
    {
        String a = httpRequest.getHeader("Accept") ;
        if ( log.isDebugEnabled() )
            log.debug("Accept request: "+a) ;
        
        AcceptItem item = choose(a, myPrefs, defaultAcceptItem) ;

        if ( log.isDebugEnabled() )
            log.debug("Content type chosen: "+item) ;

        return item ;
    }
        
    public static AcceptItem choose(String headerString, AcceptList myPrefs,
                                    AcceptItem defaultAcceptItem)
    {
        if ( headerString == null )
            return defaultAcceptItem ;
        
        AcceptList headerList = new AcceptList(headerString) ;
        
        if ( myPrefs == null )
            return headerList.first() ;

        AcceptItem i = AcceptList.match(headerList, myPrefs) ;
        if ( i == null )
            return defaultAcceptItem ;
        return i ;
    }
    
    
    public static String match(String headerString, String str)
    {
        AcceptList l = new AcceptList(headerString) ;
        AcceptItem aItem = new AcceptItem(str) ;
        AcceptItem m = l.match(aItem) ;
        if ( m == null )
            return null ;
        return m.toHeaderString() ;
    }
    
    public static boolean accept(String headerString, String str)
    {
        AcceptList l = new AcceptList(headerString) ;
        AcceptItem aItem = new AcceptItem(str) ;
        return l.accepts(aItem) ;
    }
    
    static String fmtRequest(HttpServletRequest request)
    {
        StringBuffer sbuff = new StringBuffer() ;
        sbuff.append(request.getMethod()) ;
        sbuff.append(" ") ;
        sbuff.append(Convert.decWWWForm(request.getRequestURL()));
        
        String qs = request.getQueryString();
        if (qs != null)
        {
            String tmp = request.getQueryString() ;
            tmp = Convert.decWWWForm(tmp) ;
            tmp = tmp.replace('\n', ' ') ;
            tmp = tmp.replace('\r', ' ') ;
            // You may need to split this - Eclipse bug means it wants the AbstractStringBuffer class 
            sbuff.append("?").append(tmp);
        }
        return sbuff.toString() ;
    }

    public static String httpResponseCode(int responseCode)
    {
        switch (responseCode)
        {
        case HttpServletResponse.SC_CONTINUE: return "SC_CONTINUE" ;
        case HttpServletResponse.SC_SWITCHING_PROTOCOLS: return "SC_SWITCHING_PROTOCOLS" ;
        case HttpServletResponse.SC_OK: return "SC_OK" ;
        case HttpServletResponse.SC_CREATED: return "SC_CREATED" ;
        case HttpServletResponse.SC_ACCEPTED: return "SC_ACCEPTED" ;
        case HttpServletResponse.SC_NON_AUTHORITATIVE_INFORMATION: return "SC_NON_AUTHORITATIVE_INFORMATION" ;
        case HttpServletResponse.SC_NO_CONTENT: return "SC_NO_CONTENT" ;
        case HttpServletResponse.SC_RESET_CONTENT: return "SC_RESET_CONTENT" ;
        case HttpServletResponse.SC_PARTIAL_CONTENT: return "SC_PARTIAL_CONTENT" ;
        case HttpServletResponse.SC_MULTIPLE_CHOICES: return "SC_MULTIPLE_CHOICES" ;
        case HttpServletResponse.SC_MOVED_PERMANENTLY: return "SC_MOVED_PERMANENTLY" ;
        case HttpServletResponse.SC_MOVED_TEMPORARILY: return "SC_MOVED_TEMPORARILY" ;
        case HttpServletResponse.SC_SEE_OTHER: return "SC_SEE_OTHER" ;
        case HttpServletResponse.SC_NOT_MODIFIED: return "SC_NOT_MODIFIED" ;
        case HttpServletResponse.SC_USE_PROXY: return "SC_USE_PROXY" ;
        case HttpServletResponse.SC_TEMPORARY_REDIRECT: return "SC_TEMPORARY_REDIRECT" ;
        case HttpServletResponse.SC_BAD_REQUEST: return "SC_BAD_REQUEST" ;
        case HttpServletResponse.SC_UNAUTHORIZED: return "SC_UNAUTHORIZED" ;
        case HttpServletResponse.SC_PAYMENT_REQUIRED: return "SC_PAYMENT_REQUIRED" ;
        case HttpServletResponse.SC_FORBIDDEN: return "SC_FORBIDDEN" ;
        case HttpServletResponse.SC_NOT_FOUND: return "SC_NOT_FOUND" ;
        case HttpServletResponse.SC_METHOD_NOT_ALLOWED: return "SC_METHOD_NOT_ALLOWED" ;
        case HttpServletResponse.SC_NOT_ACCEPTABLE: return "SC_NOT_ACCEPTABLE" ;
        case HttpServletResponse.SC_PROXY_AUTHENTICATION_REQUIRED: return "SC_PROXY_AUTHENTICATION_REQUIRED" ;
        case HttpServletResponse.SC_REQUEST_TIMEOUT: return "SC_REQUEST_TIMEOUT" ;
        case HttpServletResponse.SC_CONFLICT: return "SC_CONFLICT" ;
        case HttpServletResponse.SC_GONE: return "SC_GONE" ;
        case HttpServletResponse.SC_LENGTH_REQUIRED: return "SC_LENGTH_REQUIRED" ;
        case HttpServletResponse.SC_PRECONDITION_FAILED: return "SC_PRECONDITION_FAILED" ;
        case HttpServletResponse.SC_REQUEST_ENTITY_TOO_LARGE: return "SC_REQUEST_ENTITY_TOO_LARGE" ;
        case HttpServletResponse.SC_REQUEST_URI_TOO_LONG: return "SC_REQUEST_URI_TOO_LONG" ;
        case HttpServletResponse.SC_UNSUPPORTED_MEDIA_TYPE: return "SC_UNSUPPORTED_MEDIA_TYPE" ;
        case HttpServletResponse.SC_REQUESTED_RANGE_NOT_SATISFIABLE: return "SC_REQUESTED_RANGE_NOT_SATISFIABLE" ;
        case HttpServletResponse.SC_EXPECTATION_FAILED: return "SC_EXPECTATION_FAILED" ;
        case HttpServletResponse.SC_INTERNAL_SERVER_ERROR: return "SC_INTERNAL_SERVER_ERROR" ;
        case HttpServletResponse.SC_NOT_IMPLEMENTED: return "SC_NOT_IMPLEMENTED" ;
        case HttpServletResponse.SC_BAD_GATEWAY: return "SC_BAD_GATEWAY" ;
        case HttpServletResponse.SC_SERVICE_UNAVAILABLE: return "SC_SERVICE_UNAVAILABLE" ;
        case HttpServletResponse.SC_GATEWAY_TIMEOUT: return "SC_GATEWAY_TIMEOUT" ;
        case HttpServletResponse.SC_HTTP_VERSION_NOT_SUPPORTED: return "SC_HTTP_VERSION_NOT_SUPPORTED" ;
        default: return "Unknown HTTP response code: "+responseCode ;
        }        
    }
}

/*
 * (c) Copyright 2004, 2005, 2006, 2007, 2008, 2009 Hewlett-Packard Development Company, LP
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