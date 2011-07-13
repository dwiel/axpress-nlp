/*
 * (c) Copyright 2004, 2005, 2006, 2007, 2008, 2009 Hewlett-Packard Development Company, LP
 * All rights reserved.
 * [See end of file]
 */

package org.joseki.http;

import java.io.InputStream;
import javax.servlet.ServletContext;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import com.hp.hpl.jena.util.Locator;
import com.hp.hpl.jena.util.FileUtils;
import com.hp.hpl.jena.util.TypedStream;

/** org.joseki.server.LocatorServletContext
 * 
 * @author Andy Seaborne
 * @version $Id: LocatorServletContext.java,v 1.6 2008/12/28 19:51:04 andy_seaborne Exp $
 */

public class LocatorServletContext implements Locator
{
    static Log logger = LogFactory.getLog(LocatorServletContext.class) ;
    ServletContext servletContext = null ;
    
    public LocatorServletContext(ServletContext context)
    {
        servletContext = context ;
    }
    
    public TypedStream open(String resourceName)
    {
        if ( servletContext == null)
            return null ;

        String fn = FileUtils.toFilename(resourceName) ;
        if ( fn == null )
        {
            logger.trace("LocatorServletContext: failed to open: "+resourceName) ; 
            return null ;
        }

        InputStream in = servletContext.getResourceAsStream(fn);
        if (in != null)
            logger.debug("Reading as servlet resource: " + resourceName);
        return new TypedStream(in) ;

    }

    public String getName() { return "LocatorServletContext" ; }
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