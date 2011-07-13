/*
 * (c) Copyright 2004, 2005, 2006, 2007, 2008, 2009 Hewlett-Packard Development Company, LP
 * All rights reserved.
 * [See end of file]
 */

package org.joseki.http;

/** org.joseki.server.http.MainAccept
 * 
 * @author Andy Seaborne
 * @version $Id: MainAccept.java,v 1.7 2008/12/28 19:51:04 andy_seaborne Exp $
 */

public class MainAccept
{
    // Bug:
    //  Accept: application/n3,application/rdf+xml;q=0.5 ==> application/rdf+xml
    // 
    
    public static void main(String[] argv)
    {
        String acceptFirefox = "text/xml,  application/xml,  application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5" ;
        String acceptIE = "image/gif, image/x-xbitmap, image/jpeg, image/pjpeg, application/x-shockwave-flash, application/vnd.ms-excel, application/vnd.ms-powerpoint, application/msword, */*" ;
        String xAccept =  "image/gif,image/jpeg" ;
        String qAccept =  "application/n3,application/rdf+xml;q=0.5" ;
        
//        testOne("ISO-8859-1,utf-8;q=0.7,*;q=0.7") ;
//        testOne(ffAccept) ;
//        testOne("text/xml;charset=utf-8") ;
//        testOne("text/*,text/plain;x=*,*/*,*/plain,text/*") ;
//        testOne(ieAccept) ;
//        testOne(" , a,,  ") ;
        
        AcceptItem dft = new AcceptItem("default") ;
//        AcceptItem aText = new AcceptItem("text/*") ;
//        
        //AcceptList myPrefs1 = new AcceptList(new String[]{"application/xml","text/*"}) ;
        //AcceptList myPrefs2 = new AcceptList(new String[]{"application/rdf+xml"}) ;
        AcceptList myPrefs3 = new AcceptList(new String[]{"application/rdf+xml", "application/n3"}) ;
//        
//        AcceptList alIE = new AcceptList(acceptIE) ;
//        AcceptList alFF = new AcceptList(acceptFirefox) ;
//        AcceptList alX = new AcceptList(xAccept) ;
//        
//        chooseTest(acceptIE, myPrefs1, dft) ;
//        chooseTest(acceptFirefox, myPrefs1, dft) ;
//        chooseTest(acceptIE, myPrefs2, dft) ;
//        chooseTest(acceptFirefox, myPrefs2, dft) ;
//
//        acceptTest(alFF, aText) ;
//        acceptTest(alIE, aText) ;
//        acceptTest(alX, aText) ;

        chooseTest(qAccept, myPrefs3, dft) ;
        
    }

    public static void chooseTest(String header, AcceptList myPrefs, AcceptItem dft)
    {
        System.out.println("Choose Test") ;
        System.out.println("Header: "+header) ;
        myPrefs.toString() ;
        System.out.println("List:   "+myPrefs) ;
        
        AcceptItem a = HttpUtils.choose(header, myPrefs, dft) ;
      
        if ( a == null )
            System.out.println("no match") ;
        else
            System.out.println("Match: "+a) ; 
        System.out.println() ;
    }
    
    public static void acceptTest(AcceptList aList, AcceptItem aItem)
    {
        System.out.println("Accept Test") ;
        System.out.println("List: "+aList) ;
        System.out.println("Item: "+aItem) ;
        System.out.println(aList.accepts(aItem)?"yes":"no") ;
        System.out.println() ;
        
    }
    
    public static void parseTest(String s)
    {
        System.out.println("Parse Test") ;
        AcceptList al = new AcceptList(s) ;
        System.out.println(al.toString()) ;
        System.out.println(al.toHeaderString()) ;
        System.out.println() ;
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