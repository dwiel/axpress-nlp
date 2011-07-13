/*
 * (c) Copyright 2005, 2006, 2007, 2008, 2009 Hewlett-Packard Development Company, LP
 * All rights reserved.
 * [See end of file]
 */

package org.joseki.junit;


import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.joseki.vocabulary.TestProtocolVocab;

import com.hp.hpl.jena.n3.IRIResolver;
import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.rdf.model.Statement;
import com.hp.hpl.jena.rdf.model.StmtIterator;
import com.hp.hpl.jena.util.FileManager;
import com.hp.hpl.jena.vocabulary.RDF;
import com.hp.hpl.jena.vocabulary.RDFS;

public class Manifest
{   
    // DELETE when protocol tests use same vocabulary
    private static Log log = LogFactory.getLog(Manifest.class) ;
    String filename ;
    Model manifest ;
    String manifestName ;
    //List includedFiles = new ArrayList() ;
    Resource manifestRes = null ;
    
    public Manifest(String fn)
    {
        filename = IRIResolver.resolveGlobal(fn) ;
        manifest = FileManager.get().loadModel(filename) ;
        parseManifest() ;
    }

    public String getName() { return manifestName ; } 
    
//    public Iterator includedManifests() { return includedFiles.iterator() ; }


    
    private void parseManifest()
    {
        StmtIterator manifestStmts =
            manifest.listStatements(null, RDF.type, TestProtocolVocab.Manifest) ;
        
        if ( !manifestStmts.hasNext() )
        {
            log.warn("No manifest in manifest file: "+filename) ;
            return ; 
        }

        Statement manifestItemStmt = manifestStmts.nextStatement();
        if ( manifestStmts.hasNext() )
        {
            log.warn("Multiple manifests in manifest file: "+filename) ;
            return ; 
        }
        
        manifestRes = manifestItemStmt.getSubject();
        manifestName = TestUtils.getLiteral(manifestRes, RDFS.label) ;
        if ( manifestName == null )
            manifestName = TestUtils.getLiteral(manifestRes, RDFS.comment) ;
        manifestStmts.close();
    }
    
    // For every test item.
    public void apply(ManifestItemHandler gen)
    {
        
        StmtIterator manifestStmts =
            manifest.listStatements(null, RDF.type, TestProtocolVocab.Manifest);
        
        for (; manifestStmts.hasNext();)
        {
            Statement manifestItemStmt = manifestStmts.nextStatement();
            Resource manifestRes = manifestItemStmt.getSubject();
            
            // For each item in this manifest
            StmtIterator listIter = manifestRes.listProperties(TestProtocolVocab.entries);
            for (; listIter.hasNext();)
            {
                //List head
                Resource listItem = listIter.nextStatement().getResource();
                for (; !listItem.equals(RDF.nil);)
                {
                    Resource entry = listItem.getRequiredProperty(RDF.first).getResource();
                    String testName = TestUtils.getLiteral(entry, TestProtocolVocab.name) ;
//                    Resource action = TestUtils.getResource(entry, TestManifest.action) ;
//                    Resource result = TestUtils.getResource(entry, TestManifest.result) ;
                    gen.processManifestItem(manifestRes, entry, testName) ;//, action, result) ;
                    // Move to next list item
                    listItem = listItem.getRequiredProperty(RDF.rest).getResource();
                }
            }
            listIter.close();
        }
        manifestStmts.close();
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