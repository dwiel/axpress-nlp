/*
 * (c) Copyright 2003, 2004, 2005, 2006, 2007, 2008, 2009 Hewlett-Packard Development Company, LP
 * [See end of file]
 */

package org.joseki;

import java.util.* ;

/** Constants and other definitions.
 * @author      Andy Seaborne
 * @version     $Id: Joseki.java,v 1.34 2008/12/28 19:51:04 andy_seaborne Exp $
 */
public class Joseki
{
    /** The root package name for ARQ */   
    public static final String PATH = "org.joseki";
   
    /** The product name */   
    public static final String NAME = "Joseki";
   
    /** The Joseki website */   
    public static final String WEBSITE = "http://www.joseki.org/";
   
    /** The full name of the current Joseki version */   
    public static final String VERSION = "3.3.0";
   
    /** The major version number for this release of Joseki */
    public static final String MAJOR_VERSION = "3";
   
    /** The minor version number for this release of Joseki */
    public static final String MINOR_VERSION = "3";
   
    /** The version status for this release of Joseki */
    public static final String VERSION_STATUS = "";
   
    /** The date and time at which this release was built */   
    public static final String BUILD_DATE = "2009-02-17 17:35 +0000";

    /** The Java system property name of the default configuration file */
    public static final String configurationFileProperty  = "org.joseki.rdfserver.config" ;
    
    public static final int defaultPort = 2020 ; 
    // TODO automate version number (read from file?) 
    public static String version = "3.2" ;
    public static String httpHeaderField = "X-Joseki-Server" ;
    public static String httpHeaderValue = "Joseki-"+version ;
    
    // TODO Split constants into client-side and server-side constants.
    
    //public static final String baseURI = "http://joseki.org/" ;

    public static final String contentTypeN3              = "text/rdf+n3" ;
    public static final String contentTypeN3Alt           = "application/n3" ;

    // Correct (at the moment)
    public static final String contentTypeTurtle          = "application/x-turtle" ;
    // Ideal
    public static final String contentTypeTurtleAlt       = "application/turtle" ;
    
    public static final String contentTypeRDFXML          = "application/rdf+xml" ;
    
    // MIME type for N-triple is text/plain (!!!)
    public static final String contentTypeNTriples        = "text/plain" ;
    public static final String contentTypeNTriplesAlt     = "application/n-triples" ;
    
    public static final String contentTypeXML             = "application/xml" ;
    public static final String contentTypeResultsXML      = "application/sparql-results+xml" ;
    public static final String contentTypeResultsJSON     = "application/sparql-results+json" ;
    
    // There is no MIME for a SPARQL query.
    // Either it is a GET or it is a "x-www-form-urlencoded"
    
    //public static final String contentSPARQL_X            = "application/x-sparql-query" ;
    public static final String contentSPARQLUpdate_X      = "application/x-sparql-update" ;

    //public static final String contentSPARQL              = "application/sparql-query" ;
    public static final String contentSPARQLUpdate        = "application/sparql-update" ;

    
    // Short names for "output="
    public static final String contentOutputJSON          = "json" ;
    public static final String contentOutputXML           = "xml" ;
    public static final String contentOutputSPARQL        = "sparql" ;

    public static final String contentTypeTextPlain       = "text/plain" ;
    //public static final String contentTypeTextJavascript  = "text/javascript" ;
    //public static final String contentTypeForText         = contentTypeTextPlain ;
    
    public static final String charsetUTF8                = "utf-8" ;
    
    public static String serverContentType                = contentTypeRDFXML ;
    public static String clientContentType                = contentTypeRDFXML ;
    
    // Hidden paramters  - illegal HTTP names
    public static final String VERB          = "%verb" ;
    public static final String OPERATION     = "%operation" ;
    
    // Names.
    public static final String OP_QUERY      = "query" ;
    public static final String OP_UPDATE     = "update" ;
    
    // Various control falgs and settings.

    public static boolean serverHttpExplicitNoCache = true ;
    //public static boolean serverDebug = false ;
    //public static boolean clientDebug = false ;
    
    public static String getReaderType(String contentType)
    {
        return jenaReaders.get(contentType) ;
    }

    public static String getWriterType(String contentType)
    {
        return jenaWriters.get(contentType) ;
    }

    public static String setReaderType(String contentType, String writerName)
    {
        return jenaReaders.put(contentType, writerName) ;
    }

    public static String setWriterType(String contentType, String writerName)
    {
        return jenaWriters.put(contentType, writerName) ;
    }
    
    static Map<String, String> jenaReaders = new HashMap<String, String>() ;
    static {
        setReaderType(contentTypeN3, "N3") ;
        setReaderType(contentTypeN3Alt, "N3") ;
        setReaderType(contentTypeRDFXML, "RDF/XML") ;
        setReaderType(contentTypeNTriples, "N-TRIPLE") ;
        setReaderType(contentTypeXML, "RDF/XML") ;
        setReaderType(contentTypeTurtle, "TURTLE") ;
        setReaderType(contentTypeTurtleAlt, "TURTLE") ;
    }
    
    static Map<String, String> jenaWriters = new HashMap<String, String>() ;
    static {
        setWriterType(contentTypeXML, "RDF/XML-ABBREV") ;
        setWriterType(contentTypeN3, "N3") ;
        setWriterType(contentTypeN3Alt, "N3") ;
        setWriterType(contentTypeRDFXML, "RDF/XML-ABBREV") ;
        setWriterType(contentTypeNTriples, "N-TRIPLE") ;
        setWriterType(contentTypeTurtle, "TURTLE") ;
        setWriterType(contentTypeTurtleAlt, "TURTLE") ;
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
 
