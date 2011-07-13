/*
 * (c) Copyright 2008, 2009 Hewlett-Packard Development Company, LP
 * All rights reserved.
 * [See end of file]
 */

package org.joseki.http;

import java.io.IOException;
import java.io.Reader;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.hp.hpl.jena.util.FileUtils;

import org.joseki.Joseki;
import org.joseki.Request;

public class ServletUpdate extends Servlet
{
    public ServletUpdate() { super("Joseki/Update") ; }
    
    @Override
    public void doGet(HttpServletRequest httpRequest, HttpServletResponse httpResponse)
    {
        log.info("Update received by HTTP Get - rejected") ;
        try
        {
            httpResponse.sendError(HttpServletResponse.SC_BAD_REQUEST,
                                   "SPARQL:/Update request received via GET - must use POST") ;
        } catch (IOException ex)
        {}
    }
    
    @Override
    public void doPost(HttpServletRequest httpRequest, HttpServletResponse httpResponse)
    {
        doCommon(httpRequest, httpResponse) ;
    }
    
    @Override
    protected Request setupRequest(String serviceURI, HttpServletRequest httpRequest) throws IOException
    {
        if ( isHTMLForm(httpRequest) )
        {
            // It's an HTTP FORM
            Request r =  super.setupRequest(serviceURI, httpRequest, Joseki.OP_UPDATE) ;
            return r ;
        }

        // ------------------- 
        // Not a form.
        // Verify charset here.
        String charEnc = httpRequest.getCharacterEncoding() ;
        Reader reader = null ;
        if ( charEnc == null )
            reader = FileUtils.asBufferedUTF8(httpRequest.getInputStream()) ;
        else
        {
            if ( ! charEnc.equalsIgnoreCase("UTF-8") )
                log.warn(serviceURI+": request not UTF-8: "+charEnc) ;
            reader = httpRequest.getReader() ;
        }
        Request r = new Request(serviceURI, reader) ;
        r.setParam(Joseki.OPERATION, Joseki.OP_UPDATE) ;
        return r ;
    }
}

/*
 * (c) Copyright 2008, 2009 Hewlett-Packard Development Company, LP
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