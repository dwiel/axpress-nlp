/*
 * (c) Copyright 2005, 2006, 2007, 2008, 2009 Hewlett-Packard Development Company, LP
 * All rights reserved.
 * [See end of file]
 */

package org.joseki;

import com.hp.hpl.jena.shared.JenaException;
import com.hp.hpl.jena.shared.NotFoundException;
import com.hp.hpl.jena.util.FileManager;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;


public class Dispatcher
{
    private static Log log = LogFactory.getLog(Dispatcher.class) ;
    
    static Configuration   configuration = null ;
    static ServiceRegistry serviceRegistry = null ;
    public static Configuration   getConfiguration()      { return configuration ; }
    public static ServiceRegistry getServiceRegistry()    { return serviceRegistry ; }
    
    //Dispatcher dispatcher = new Dispatcher() ;
    
    public static void dispatch(String serviceURI, Request request, Response response) throws ExecutionException
    {
        if ( serviceRegistry == null )
        {
            log.fatal("Service registry not initialized") ;
            throw new ExecutionException(ReturnCodes.rcInternalError, "Service registry not initialized") ;
        }
        
        try {
            Service service = serviceRegistry.find(serviceURI) ;
            if ( service == null )
            {
                log.info("404 - Service <"+serviceURI+"> not found") ;
                throw new ExecutionException(ReturnCodes.rcNoSuchURI, "Service <"+serviceURI+"> not found") ;
            }
            
            if ( !service.isAvailable() )
            {
                log.info("Service is not available") ;
                throw new ExecutionException(ReturnCodes.rcServiceUnavailable, "Service <"+serviceURI+"> unavailable") ;
            }
    
            final ServiceRequest serviceRequest = service.instance(request, response) ;
            serviceRequest.start() ;
            ResponseCallback cb = new ResponseCallback(){
                public void callback()
                {
                    log.debug("ResponseCallback: service request finish") ;
                    serviceRequest.finish() ;
                }} ;
            response.addCallback(cb) ;
            serviceRequest.exec(request, response) ;
            response.sendResponse() ;
        }
        catch (ExecutionException ex)
        {
            response.sendException(ex) ;
            return ;
        }
    }

    //  This method contains the pragmatic algorithm to determine the configuration URI.
    //  
    //  In this order (i.e. specific to general) to find the filename:
    //  System property org.joseki.rdfserver.config => a URI.
    
    //  Resource:                
    //  System property:         jena.rdfserver.modelmap => file name
    //  Webapp init parameter:   jena.rdfserver.modelmap
    //  Servlet init parameter:  jena.rdfserver.modelmap
    //  and then the file is loaded.

    public static void initServiceRegistry()
    {
        initServiceRegistry(FileManager.get()) ;
    }

    
    public static void initServiceRegistry(FileManager fileManager)
    {
        initServiceRegistry(fileManager, null) ;
    }
    
    public static void initServiceRegistry(String configURI)
    {
        initServiceRegistry(FileManager.get(), configURI) ;
    }
    
    public static void initServiceRegistry(FileManager fileManager, String configURI)
    {    
        if ( configURI == null )
            configURI = System.getProperty(Joseki.configurationFileProperty, RDFServer.defaultConfigFile) ;
        setConfiguration(fileManager, configURI) ;
    }
    
    public static synchronized void setConfiguration(FileManager fileManager, String configURI)
    {
        if ( serviceRegistry != null )
        {
            //log.debug("Service registry already initialized") ;
            return ;
        }
        
        if ( configURI == null )
        {
            log.fatal("Null for configuration URI") ;
            return ;
        }
        
        // Already squirreled away somewhere?
        serviceRegistry = (ServiceRegistry)Registry.find(RDFServer.ServiceRegistryName) ;
        
        if ( serviceRegistry != null )
        {
            log.debug("Using globally registered service registry") ;
            return ;
        }

        // Better find one.

        ServiceRegistry tmp = new ServiceRegistry() ;
        try {
            configuration = new Configuration(fileManager, configURI, tmp) ;
            log.info("Loaded data source configuration: " + configURI);
        } catch (NotFoundException ex)
        {
            throw new ConfigurationErrorException("Not found: "+ex.getMessage(), ex) ;
            //return false;
        } catch (JenaException rdfEx)
        {
            // Trouble processing a configuration 
            throw new ConfigurationErrorException("RDF Exception: "+rdfEx.getMessage(), rdfEx) ;
            //return false ;
        }
            
        Registry.add(RDFServer.ServiceRegistryName, tmp) ;
        serviceRegistry = (ServiceRegistry)Registry.find(RDFServer.ServiceRegistryName) ;
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