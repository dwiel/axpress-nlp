/*
 * (c) Copyright 2003, 2004, 2005, 2006, 2007, 2008, 2009 Hewlett-Packard Development Company, LP
 * [See end of file]
 */

package joseki;

import jena.cmdline.* ;

import org.joseki.* ;

/** Command line application to run an RDF Server
 *
 * @author  Andy Seaborne
 * @version $Id: rdfserver.java,v 1.10 2008/12/28 19:51:05 andy_seaborne Exp $
 */


public class rdfserver
{
    public static String defaultConfigFile = RDFServer.defaultConfigFile ;
    
    public static boolean VERBOSE = false ;
    public static boolean DEBUG = false ;

    public static final int defaultPort = Joseki.defaultPort ;
    public static int port = defaultPort ;
    
    public static final String PortArg = "port" ;

    public static void main (String args[])
    {
        port = Integer.parseInt(System.getProperty("jena.rdfserver.port", defaultPort+"")) ;
        
        String usageMessage = rdfserver.class.getName()+
                                " [--verbose] [--port N] "+
                                "dataSourceConfigFile" ;
                                
        
        CommandLine cmd = new CommandLine() ;
        cmd.setUsage(usageMessage) ;
        
        ArgDecl verboseDecl = new ArgDecl(false, "-v", "--verbose") ;
        cmd.add(verboseDecl) ;
        cmd.add("--debug", false) ;
        cmd.add("--help", false) ;
        cmd.add(PortArg, true) ;

        // Addition argument, after the flags, is a query
        cmd.process(args) ;
        
        if ( cmd.contains("help") )
        {
            System.out.println(usageMessage) ;
            System.exit(0) ;
        }

        if ( cmd.contains(PortArg) )
            port = Integer.parseInt(cmd.getArg(PortArg).getValue()) ;

        if ( cmd.contains("--debug") )
        {    
            DEBUG = true ;
            Joseki.serverContentType = "application/n3" ;
        }
        
        if ( cmd.contains(verboseDecl) )
            VERBOSE = true ;
        
        if ( cmd.numItems() > 1 )
        {
            System.err.println("Must specify exactly one configuration file (or use default : "+defaultConfigFile+")") ;
            System.err.println(usageMessage) ;
            System.exit(1) ;
        }
        
        String configFile = null ;

        if ( cmd.numItems() > 0 )
            configFile = cmd.getItem(0) ;
        else
            configFile = defaultConfigFile ;

        try {
            RDFServer server = new RDFServer(configFile, port) ;
            server.start() ;
        } catch (ConfigurationErrorException confEx)
        {
            // Flush console logging
            System.out.flush() ;
            System.err.println();
            System.err.println("Failed to load the configuration file - see log") ;
            // Errors have already come out on the logging
            System.err.println(confEx.getMessage()) ;
            confEx.printStackTrace(System.err) ;
            System.err.println();
            System.exit(99) ;
        }
        // Server threads running elsewhere.
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
