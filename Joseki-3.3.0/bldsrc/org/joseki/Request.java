
/*
 * (c) Copyright 2003, 2004, 2005, 2006, 2007, 2008, 2009 Hewlett-Packard Development Company, LP
 * [See end of file]
 */


package org.joseki;

import java.io.Reader;
import java.util.*;

/** General Request 
 * @author      Andy Seaborne
 * @version     $Id: Request.java,v 1.11 2009/01/18 19:02:19 andy_seaborne Exp $
 */
public class Request
{
    // How the operation was described.
    String serviceURI = null ;
    Reader input = null ;

    final static Object noValue = new Object() ; 
    // Parameters :: key => List of values pairs
    
    Map<String, List<String>> params = new HashMap<String, List<String>>();

    public Request(String uri, Reader input)
    {
        serviceURI = uri ;
        this.input = input ;
    }
    
    // ---- Parameters
    
    public String getParam(String param)
    { 
        List<String> x = getParamsOrNull(param) ;
        if ( x == null )
            return null ;
        return x.get(0);
    }
    
    public List<String> getParams(String param)
    {
            if ( ! params.containsKey(param) ) 
                return new ArrayList<String>() ;
            List<String> x = params.get(param) ;
            return x ;
    }
    
    private List<String> getParamsOrNull(String param)
    {
            if ( ! params.containsKey(param) ) 
                return null ;
            List<String> x = params.get(param) ;
            if ( x.size() == 0 )
                return null ;
            return x ;
    }
    
    // NB This will be empty for a x-www-form-urlencoded request
    public Reader getStream() { return input ; }
    
    
    public void setParam(String name, String value)
    {
        if ( ! params.containsKey(name) )
            params.put(name, new ArrayList<String>()) ;
        List<String> x = params.get(name) ;
        x.add(value) ;
    }

    public boolean containsParam(String param)
    {
        return getParamsOrNull(param) != null ;
    }
    
    public Iterator<String> parameterNames()
    {
        List<String> x = new ArrayList<String>() ;
        for ( Iterator<String> iter = params.keySet().iterator() ; iter.hasNext() ; )
        {
            String k = iter.next() ;
            List<String> z = params.get(k) ;
            if ( z.size() != 0 )
                x.add(k) ;
        }
        return x.iterator() ;
    }
    
    /** @return Returns the serviceURI. */
    public String getServiceURI()
    {
        return serviceURI ;
    }
    
    public String paramsAsString()
    {
        StringBuffer sBuff = new StringBuffer() ;
        boolean first = true ;
        for ( Iterator<String> iter = parameterNames() ; iter.hasNext(); )
        {
            String k = iter.next() ;
            List<String> x = getParamsOrNull(k) ;
            if ( x != null )
                for ( String v : x )
                {
                    if ( ! first )
                        sBuff.append(" ") ;
                    first = false ;
                    sBuff.append(k) ;
                    sBuff.append("=") ;
                    sBuff.append(v) ;
                }
        }
        return sBuff.toString() ; 
    }
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
