/*
 * (c) Copyright 2005, 2006, 2007, 2008, 2009 Hewlett-Packard Development Company, LP
 * All rights reserved.
 * [See end of file]
 */

package org.joseki;

import static org.joseki.vocabulary.JosekiSchemaBase.poolSize;

import java.util.concurrent.BlockingDeque;
import java.util.concurrent.LinkedBlockingDeque;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import com.hp.hpl.jena.rdf.model.Resource;

import com.hp.hpl.jena.assembler.Assembler;

import com.hp.hpl.jena.sparql.util.graph.GraphUtils;

import com.hp.hpl.jena.query.Dataset;

public class DatasetDesc
{
    static Log log = LogFactory.getLog(DatasetDesc.class) ;
    Resource datasetRoot ; 
    Dataset dataset = null ;    // Unpooled slot.
    int sizeOfPool = -1 ;       // No pool.
    BlockingDeque<Dataset> pool = null ;
    
    public DatasetDesc(Resource datasetRoot)
    { 
        this.datasetRoot = datasetRoot ;
    }

    /** Called to create early (e.g. for checking) */
    public void initialize()
    {
        if ( datasetRoot.hasProperty(poolSize) )
        {
            if ( ! GraphUtils.exactlyOneProperty(datasetRoot, poolSize) )
                log.fatal("Multiple pool size property ("+Utils.nodeLabel(datasetRoot)+")") ;
            
            String x = GraphUtils.getStringValue(datasetRoot, poolSize) ;
            try {
                sizeOfPool = Integer.parseInt(x) ;
            } catch (NumberFormatException ex)
            {
                log.fatal("Not a number: "+x) ;
                throw ex ; 
            }
            pool = new LinkedBlockingDeque<Dataset>(sizeOfPool) ;
            for ( int i = 0 ; i < sizeOfPool ; i++ )
                pool.addLast(newDataset()) ;
            log.info(String.format("Pool size %d for dataset %s", sizeOfPool, Utils.nodeLabel(datasetRoot))) ;
        }
        else
            dataset = newDataset() ;
    }
    
    private Dataset newDataset()
    {
        return (Dataset)Assembler.general.open(getResource())  ;
    }

    public Resource getResource() { return datasetRoot ; }
    
    public Dataset acquireDataset(Request request, Response response)
    {
        if ( dataset != null )
            return dataset ;
        // From pool.
        try
        { 
            log.debug("Take from pool") ; 
            return pool.takeFirst() ;
        } catch (InterruptedException ex)
        {
            throw new JosekiServerException("Failed to get a dataset from the pool (InterruptedException): "+ex.getMessage()) ;
        }
    }
    
    public void returnDataset(Dataset ds)
    {
        
        if ( pool != null )
        {
            log.debug("Return to pool") ;
            pool.addLast(ds) ;
        }
    }
    
    @Override
    public String toString()
    {
        if ( dataset != null )
            return dataset.toString() ;
        
        return "Dataset not set : "+Utils.nodeLabel(datasetRoot) ;
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
