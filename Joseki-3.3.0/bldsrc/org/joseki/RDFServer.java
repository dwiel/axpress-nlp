/*
 * (c) Copyright 2003, 2004, 2005, 2006, 2007, 2008, 2009 Hewlett-Packard Development Company, LP
 * [See end of file]
 */

package org.joseki;

import java.util.List;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.mortbay.jetty.Connector;
import org.mortbay.jetty.Server;
import org.mortbay.jetty.nio.SelectChannelConnector;
import org.mortbay.jetty.webapp.WebAppContext;
import org.mortbay.util.MultiException;

/** Standalone server.
 * 
 * @version $Id: RDFServer.java,v 1.21 2009/01/18 19:02:19 andy_seaborne Exp $
 * @author  Andy Seaborne
 */


public class RDFServer
{
    static final Log log = LogFactory.getLog(RDFServer.class.getName()) ;

    public static final String ServiceRegistryName = "Service Registry" ;
    static int count = 0 ;

    Server server = null ;
    WebAppContext webAppContextJoseki = null ;
    boolean earlyInitialize = true ;
    
    int port = -1 ;

    /** System property for the port number. */    
    public static final String propertyPort       = "org.joseki.rdfserver.port" ;

    /** Default location for the Joseki server */
    public static final String defaultServerBaseURI = "/" ;
    
    /** Default configuration file */
    public static final String defaultConfigFile = "joseki-config.ttl" ;

    /** Create a new RDFServer on the default port or as specifed by the system property jena.rdfserver.port */
    public RDFServer() { this(defaultConfigFile) ; }

    /** Create a new RDFServer using the named configuration file
     * @param configFile
     */
    public RDFServer(String configFile)
    {
        String tmp = System.getProperty(propertyPort, Joseki.defaultPort+"") ;
        int p = Integer.parseInt(tmp) ;
        init(configFile, p, defaultServerBaseURI) ;
    }

    /** Create a new RDFServer
     * @param configFile
     * @param port
     */
    public RDFServer(String configFile, int port) { init(configFile, port, defaultServerBaseURI) ; }

    /** Creates new RDFServer using the named configuration file
     * @param configFile
     * @param port
     * @param serverBaseURI
     */
    public RDFServer(String configFile, int port, String serverBaseURI) 
    {
        init(configFile, port, serverBaseURI) ;
    }

    private void init(String configFile, int port, String serverBaseURI) 
    {
        if (earlyInitialize)
            Dispatcher.initServiceRegistry(configFile) ;
        else
            // Set system property so the dispatcher finds it later,
            // probably during servlet creation on first request,
            // or SOAP service initialization 
            System.setProperty(Joseki.configurationFileProperty, configFile) ;

        // Build the web application and server
        try {
            // And the Jetty server uses SLF4J

            // Server, with one NIO-based connector, large input buffer size (for long URLs).
            server = new Server() ;
            Connector connector = new SelectChannelConnector() ;
            connector.setPort(port);
            connector.setHeaderBufferSize(16*1024) ;
            server.addConnector(connector) ;

            // Add the webapp.
            webAppContextJoseki = new WebAppContext(server, "webapps/joseki", "/") ;
            server.addHandler(webAppContextJoseki) ;

            // Or configure from an external file.
//            if ( false )
//            {
//                // This will mount Joseki at /joseki.
//                // java.io.FileNotFoundException
//                XmlConfiguration configuration = new XmlConfiguration(new URL("file:etc/jetty.xml")) ; 
//                //or use new XmlConfiguration(new FileInputStream("myJetty.xml"));
//                configuration.configure(server);
//            }
//            else
//            {
//                webAppContextJoseki = new WebAppContext(server, "webapps/joseki", "/") ;
//                server.addHandler(webAppContextJoseki) ;
//            }
            
            // Start server.
            server.start();
        } catch (Exception ex)
        {
            log.warn("RDFServer: Failed to create web application server: "+ex) ;
        }
    }

    
    // This code builds the configuration very early,
    // before the web application exists and before the servlet exists
    // let alone intitialised.
    // This means that files read now must be found without the servlet context
    // (just the current directory and the classpath).
    // However, it does mean that it happens now and not during the first request
    // received, which greatly helps simple use (and Joseki development).
    
    private Configuration createConfiguration(String configFile)
    {
//        if (System.getProperty(configurationFile) == null)
//            // This tells the servlet to load nothing later - not even from the
//            // default location
//            // Rather than know the servlet class, we set a system property.
//            System.setProperty(configurationFile, noConfValue);
//        
        try
        {
            // The servlet finds it from the registry.
            ServiceRegistry services = new ServiceRegistry();
            Registry.add(ServiceRegistryName, services);

            if (configFile == null)
            {
                log.info("No initial configuration");
                return null ;
            }
            Configuration conf = new Configuration(configFile, services) ;
            return conf ;
        }
        catch (Exception ex)
        {
            if (ex instanceof ConfigurationErrorException)
                throw (ConfigurationErrorException)ex;
            throw new ConfigurationErrorException(ex);
        }
    }
    
    /** Start the server */
    public void start()
    {
        try {
            if ( ! server.isStarted() )
                server.start() ;
            //org.mortbay.util.Log.instance().disableLog();
            
        } catch (MultiException ex)
        {
            @SuppressWarnings("unchecked")
            List<Throwable> exs = ex.getThrowables() ;
            java.net.BindException bindException = null ;
            for ( Throwable ex2 : exs )
            {
                if ( ex2 instanceof java.net.BindException )
                {
                    bindException = (java.net.BindException)ex2 ;
                    continue ;
                }
                log.warn("MultiException: "+ex2) ;
            }
            
            if ( bindException != null )
            {
                log.error("Bind exception: "+bindException.getMessage()) ;
                //System.err.println("Bind exception: "+bindException.getMessage()) ;
                System.exit(99) ;
            }
            throw new JosekiServerException("Failed to start web application server") ;
        }
        catch (Exception exMisc)
        {
            log.warn("Exception (server startup): "+exMisc) ;
            exMisc.printStackTrace(System.err) ;
            System.exit(98) ;
        }
        
        if ( ! earlyInitialize )
            return ; 

        
//        // Check that the service registry seen by the webapp is the
//        // same as the one created during initialization.  That is, the
//        // webapp does not have its own class for this.
//        
//        try {
//            ClassLoader cl = webAppContextJoseki.getClassLoader() ;
//            
//            if ( cl == null )
//            {    
//                log.warn("No classloader for webapp!") ;
//                return ;
//            }
//
//            Class cls = cl.loadClass(ServiceRegistry.class.getName());
//
//            if ( ! cls.isAssignableFrom(ServiceRegistry.class))
//            {    
//                log.warn("Found another service configuration subsystem in the web apllication");
//                log.warn("Suspect a second copy of joseki.jar in WEB-INF/lib") ;
//                throw new ConfigurationErrorException("ServiceRegistry clash") ;
//            }
//        } catch (ClassNotFoundException ex)
//        {
//            log.info("Class not found");
//        }
    }

    public void waitUntilStarted()
    {
        server.isStarted() ;
        //try { Thread.sleep(1000) ; } catch (Exception ex) {} 
    }
    
    /** Stop the server.  On exit from this method, it is <strong>not</strong>
     *  guaranteed that all server threads have ended. 
     */
    
    public void stop()
    {
        try
        {
            server.stop() ;
        } catch (Exception e)
        {
            log.warn("Problems stopping server: ",e) ;
        }
        
    }

    public int getPort() { return port ; }
   
    public Server getServer() { return server ; }
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
