/*
 * (c) Copyright 2003, 2004, 2005, 2006, 2007, 2008, 2009 Hewlett-Packard Development Company, LP
 * [See end of file]
 */

package org.joseki.module;

import org.apache.commons.logging.* ;

import org.joseki.vocabulary.JosekiModule ;
import org.joseki.util.PrintUtils ;

import com.hp.hpl.jena.rdf.model.* ;
import com.hp.hpl.jena.shared.* ;

/**
 * Load classes and instantiate new objects based on loadable classes.
 * Understands the RDF properties for naming and initializing a new instance. 
 * 
 * @author  Andy Seaborne
 * @version $Id: Loader.java,v 1.8 2008/12/28 19:51:05 andy_seaborne Exp $
 */

public class Loader
{
    private static Log log = LogFactory.getLog(Loader.class.getName());

    protected static ClassLoader classLoader = chooseClassLoader() ;

    public Loader()
    {
    }
 
    public Loadable loadAndInstantiateImplementation(Resource bindingResource, Class<?> expectedType)  
    {
        log.debug("Attempt to load: "+PrintUtils.fmt(bindingResource)) ;
        
        Resource implementation = null ;
        try
        {
            // Alternative: pass in a top level resource and do ...
            // There can be many bindings
            //bindingResource = thing.getProperty(JosekiModule.binding).getResource() ;
            
            // Should be only one. 
            implementation = bindingResource
                                .getProperty(JosekiModule.implementation)
                                .getResource() ;
            log.trace("Implementation: "+PrintUtils.fmt(implementation)) ;

        } catch (JenaException ex)
        {
            throw new LoaderException("Binding/Implementation structure incorrect") ;
        }
        catch (NullPointerException nullEx)
        {
            throw new LoaderException("No definition for "+PrintUtils.fmt(bindingResource)) ;
        }

        return loadAndInstantiateClass(implementation, bindingResource, expectedType) ;
    }
        
    public Loadable loadAndInstantiateClass(Resource implementation, Resource initResource, Class<?> expectedType)
    {
        String className = "<<unset>>" ;
        try {
            RDFNode n = implementation.getRequiredProperty(JosekiModule.className).getObject() ;
            className = classNameFromNode(n);
            if ( className == null )
            {
                // This should not happen as we used "getRequiredProperty"
                throw new LoaderException("Class name not found") ;
            }
            log.trace("Class name: "+className) ;
        } catch (PropertyNotFoundException noPropEx)
        {
            throw new LoaderException("No property 'className'") ;
        }

        try {            
            log.trace("Load module: " + className);
            Class<?> classObj = null ;
            try {
                classObj = classLoader.loadClass(className);
            } catch (ClassNotFoundException ex)
            {
                throw new LoaderException("Class not found: "+className);
            }
            
            if ( classObj == null )
                throw new LoaderException("Null return from classloader");
            
            log.debug("Loaded: "+className) ;
            
            if ( ! Loadable.class.isAssignableFrom(classObj) )
                throw new LoaderException(className + " does not support interface Loadable" ) ;

            Loadable module = (Loadable)classObj.newInstance();
            log.trace("New Instance created") ;
            
            if ( expectedType != null && ! expectedType.isInstance(module) )
                throw new LoaderException("  " + className + " is not of class "+expectedType.getName()) ;

            // Looks good - now initialize it.
            if ( initResource != null )
                module.init(initResource, implementation) ;

            //logger.debug("  Class: " + className);
            //log.debug("Module: " + uriInterface) ; 
            log.debug("Implementation: "+className);
            return module;
        }
        catch (LoaderException ex ) { throw ex; }
        catch (Exception ex)
        {
            throw new LoaderException("Unexpected exception loading class " + className, ex);
        }
    }
    
    static private ClassLoader chooseClassLoader()
    {
        ClassLoader classLoader = Thread.currentThread().getContextClassLoader(); ;
    
        if ( classLoader != null )
        	log.trace("Using thread classloader") ;
        
//        if (classLoader == null)
//        {
//            classLoader = this.getClass().getClassLoader();
//            if ( classLoader != null )
//                logger.trace("Using 'this' classloader") ;
//        }
        
        if ( classLoader == null )
        {
            classLoader = ClassLoader.getSystemClassLoader() ;
            if ( classLoader != null )
                log.trace("Using system classloader") ;
        }
        
        if ( classLoader == null )
            throw new LoaderException("Failed to find a classloader") ;
        return classLoader ;
    }
    
    public static String classNameFromNode(RDFNode n)
    {
        String className = null ;
        
        if ( n instanceof Literal )
        {
            Literal lit = (Literal)n ;
            className = lit.getLexicalForm() ;
            if ( className.startsWith("java:") ) 
                className.substring("java:".length()) ; 
            return className ;
        }

        Resource r = (Resource)n ;
        if ( r.isAnon() )
            return null ;
        
        if ( ! r.getURI().startsWith("java:") )
            throw new LoaderException("Class name is a URI but not from the java: scheme") ;
        className = r.getURI().substring("java:".length()) ;
        return className ; 
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
