/*
 * (c) Copyright 2005, 2006, 2007, 2008, 2009 Hewlett-Packard Development Company, LP
 * All rights reserved.
 * [See end of file]
 */

package org.joseki;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.joseki.module.Loadable;
import org.joseki.module.Loader;
import org.joseki.module.LoaderException;

import com.hp.hpl.jena.query.*;
import com.hp.hpl.jena.rdf.model.Literal;
import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.RDFNode;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.rdf.model.Statement;
import com.hp.hpl.jena.rdf.model.StmtIterator;
import com.hp.hpl.jena.shared.JenaException;
import com.hp.hpl.jena.shared.NotFoundException;
import com.hp.hpl.jena.sparql.core.assembler.AssemblerUtils;
import com.hp.hpl.jena.sparql.core.assembler.DatasetAssemblerVocab;
import com.hp.hpl.jena.sparql.resultset.ResultSetRewindable;
import com.hp.hpl.jena.sparql.util.StringUtils;
import com.hp.hpl.jena.util.FileManager;
import com.hp.hpl.jena.vocabulary.RDF;
import com.hp.hpl.jena.vocabulary.RDFS;

public class Configuration
{
    private static Log log = LogFactory.getLog(Configuration.class) ;
    
    Loader loader = new Loader() ;
    Model confModel ;
    Resource server ;
    // --------
    
    ServiceRegistry registry = null ;
    Map<String, Service> services = new HashMap<String, Service>() ;
    Set<String> badServiceRefs = new HashSet<String>() ;    // Service references that failed initially checking. 
    Map<Resource, DatasetDesc> datasets = new HashMap<Resource, DatasetDesc>() ;          // Dataset resource to description
    
    // Stats
    int numServices = 0 ;
    int numServiceTriples = 0 ;
    
    int numDatasets = 0 ;
    int numNamedGraphs = 0 ;
    int numDefaultGraphs = 0 ;
    
    int warnings = 0 ;
    
    // Ensure that the DataSource assembler from ARQ is loaded (processes Datasets)
    static {  AssemblerUtils.init() ; }
    
    public Configuration(String filename, ServiceRegistry registry)
    {
        this(FileManager.get(), filename, registry) ;
    }
    
    public Configuration(FileManager fileManager, String filename, ServiceRegistry registry)
    {
        this.registry = registry ;
        confModel = ModelFactory.createDefaultModel() ;

        Set<String> filesDone = new HashSet<String>() ;
        
        try {
            log.info("==== Configuration ====") ;
            readConfFile(fileManager, confModel, filename, filesDone) ;
            processModel() ;
        } catch (RuntimeException ex)
        {
            log.fatal("Failed to parse configuration file", ex) ;
            // Clear an structures we may have partialy built.
            confModel = null ;
            services = null ;
            datasets = null ;
            throw ex ;
        }
    }

    private void processModel()
    {
        checkServiceReferences() ;
        server = findServer() ;
        initServer(server) ;
        log.info("==== Datasets ====") ;
        findDatasets() ;
        log.info("==== Services ====") ;
        findServices() ;
        log.info("==== Bind services to the server ====") ;
        bindServices(registry) ;
        log.info("==== Initialize datasets ====") ;
        for ( String name : registry.names() )
        {
            Service s = registry.find(name) ;
            try {
                if ( s.getDatasetDesc() != null )
                    s.getDatasetDesc().initialize() ;
            } catch(Exception ex)
            { 
                log.warn("Failed to build dataset from description (service name: "+name+"): "+ex.getMessage(), ex) ;
                continue ;
            }
        }
        
        log.info("==== End Configuration ====") ;
    }
    
    public int getWarnings() { return warnings ; }

    /** @return Returns the numDatasets. */
    public int getNumDatasets()
    {
        return numDatasets ;
    }

    /** @return Returns the numDefaultGraphs. */
    public int getNumDefaultGraphs()
    {
        return numDefaultGraphs ;
    }

    /** @return Returns the numNamedGraphs. */
    public int getNumNamedGraphs()
    {
        return numNamedGraphs ;
    }

    /** @return Returns the numServices. */
    public int getNumServices()
    {
        return numServices ;
    }
    // ----------------------------------------------------------
    // Configuration model

    /** @param numServiceTriples The numServiceTriples to set. */
    public void setNumServiceTriples(int numServiceTriples)
    {
        this.numServiceTriples = numServiceTriples ;
    }

    private void readConfFile(FileManager fileManager, Model confModel2, String filename, Set<String> filesDone)
    {
        if ( filesDone.contains(filename) )
            return ;
        
        log.info("Loading : "+Utils.strForURI(filename, null) ) ;
        // Load into a separate model in case of errors
        Model conf = null ; 
            
        try {
            conf = fileManager.loadModel(filename) ;
            filesDone.add(filename) ;
        } catch (NotFoundException ex)
        {
            warn("Failed to load: "+ex.getMessage()) ;
            return ;
        }
        
        String s[] = new String[]{ "SELECT ?i { ?x joseki:include ?i }" } ;
        Query query = makeQuery(s) ; 
        QueryExecution qexec = QueryExecutionFactory.create(query, conf);

        List<String> includes = new ArrayList<String>() ;

        try {
            for ( ResultSet rs = qexec.execSelect() ; rs.hasNext() ; )
            {
                QuerySolution qs = rs.nextSolution() ;
                RDFNode rn = qs.get("i") ;
                if ( rn instanceof Literal )
                {
                    warn("Skipped: include should be a URI, not a literal: "+Utils.nodeLabel(rn) ) ;
                    continue ;
                }
                Resource r  = (Resource)rn ;
                if ( r.isAnon() )
                {
                    warn("Skipped: include should be a URI, not a blank node") ;
                    continue ;
                }
                    
                log.info("Include : "+Utils.nodeLabel(r)) ;
                includes.add(r.getURI()) ;
            }
        } finally { qexec.close() ; } 
        
        confModel.add(conf) ;
        for ( Iterator<String> iter = includes.iterator() ; iter.hasNext() ; )
        {
            String fn = iter.next() ; 
            readConfFile(fileManager, confModel, fn, filesDone) ; 
        }
    }
    
    // ----------------------------------------------------------
    // The server

    private Resource findServer()
    {
        List<RDFNode> x = findByType(JosekiVocab.Server) ;
        if ( x.size() == 0 )
        {
            warn("No server description found") ;
            throw new ConfigurationErrorException("No server description") ;
        }
        
        if ( x.size() > 1 )
        {
            warn("Multiple server descriptions found") ;
            throw new ConfigurationErrorException("Too many server descriptions ("+x.size()+")") ;
        }
        
        return (Resource)x.get(0) ; 
    }

    private void initServer(Resource server)
    {
        if ( server.hasProperty(JosekiVocab.initialization) )
        {
            StmtIterator sIter = server.listProperties(JosekiVocab.initialization) ;
            for( ; sIter.hasNext(); )
            {
                Statement s = sIter.nextStatement() ;
                Resource initResource = s.getResource() ;
                Loadable obj = loader.loadAndInstantiateImplementation(initResource, ServerInitialization.class) ;
                // The object will have been called during loading.
                //ServerInitialization initObj = (ServerInitialization)obj ;
            }
            
            
        }
    }
    
    // ----------------------------------------------------------
    // Services
    
    private void checkServiceReferences()
    {
        // Check for services with two or more references
        // and services with the same reference
        String s[] = new String[]{
            "SELECT *",
            "{",
            "  ?service  joseki:serviceRef  ?serviceRef ;",
            "    }",
            "ORDER BY ?serviceRef" } ;

        Query query = makeQuery(s) ;
        Map<String, RDFNode> refs = new HashMap<String, RDFNode>() ;      // Reference -> service      
        Map<RDFNode, String> services = new HashMap<RDFNode, String>() ;  // Service -> reference
        
        QueryExecution qexec = QueryExecutionFactory.create(query, confModel) ;
        try {
            
            ResultSetRewindable rs = ResultSetFactory.makeRewindable(qexec.execSelect()) ;
            if ( log.isDebugEnabled() )
            {
                String x = ResultSetFormatter.asText(rs) ;
                if ( x.endsWith("\n") )
                    x = x.substring(0, x.length()-2) ;
                x = "Services References: \n"+x ; 
                log.info(x) ;
                rs.reset() ;
            }
            
            for ( ; rs.hasNext() ; )
            {
                this.numServiceTriples ++;
                QuerySolution qs = rs.nextSolution() ;
                RDFNode service = qs.getResource("service") ;
                String ref = serviceRef(qs.get("serviceRef")) ;
                if ( ref == null ) 
                {
                    warn("Service references are literals (a URI ref which will be relative to the server)") ;
                    continue ;
                }
                
                boolean good = true ;
                if ( refs.containsKey(ref) )  
                {
                    if ( ! badServiceRefs.contains(ref) )
                        warn("Duplicate service reference: "+ref) ;
                    good = false ;
                }
                
                if ( services.containsKey(service) ) 
                {
                    String r = services.get(service) ; 
                    warn("Services has same references: \""+ref+"\" and \""+r+"\"") ;
                    badServiceRefs.add(r) ;
                    good = false ;
                }
                
                if ( good )
                {
                    refs.put(ref, service) ;
                    services.put(service, ref) ;
                }
                else
                    badServiceRefs.add(ref) ;
            }
        } finally { qexec.close() ; }
    }
    
    private Set<RDFNode> findServices()
    {
        String s[] = new String[]{
            "SELECT *",
            "{",
            "  ?service  joseki:serviceRef  ?serviceRef ;",
            "            joseki:processor   ?proc ." ,
            "  ?proc     module:implementation",
            "                [ module:className ?className ]" ,
            "    }",
            "ORDER BY ?serviceRef ?className" } ;

        Query query = makeQuery(s) ;
        QueryExecution qexec = QueryExecutionFactory.create(query, confModel) ;
            
        ResultSetRewindable rs = ResultSetFactory.makeRewindable(qexec.execSelect()) ;
        if ( log.isDebugEnabled() )
        {
            String x = ResultSetFormatter.asText(rs) ;
            if ( x.endsWith("\n") )
                x = x.substring(0, x.length()-2) ;
            x = "Services: \n"+x ; 
            log.info(x) ;
            rs.reset() ;
        }
        
        // Does not mean the services are asscoiated with the server. 
        Set<RDFNode> serviceResources = new HashSet<RDFNode>() ; 
        
        try {
            for ( ; rs.hasNext() ; )
            {
                QuerySolution qs = rs.nextSolution() ;
                RDFNode serviceNode = qs.getResource("service") ;
                Resource procRes = qs.getResource("proc") ;
                RDFNode className = qs.get("className") ;
                
                // ---- Check reference
                String ref = serviceRef(qs.get("serviceRef")) ;
                if ( ref == null )
                    continue ;
                
                if ( badServiceRefs.contains(ref) )
                {
                    log.info("Skipping: "+ref) ;
                    // Warning already done
                    continue ;
                }
                

                // ---- Check duplicates
                if ( services.containsKey(ref) ) 
                {
                    Service srv = services.get(ref) ;
                    srv.setAvailability(false) ;
                    warn("Duplicate service reference: "+ref) ;
                    continue ;
                }
                
                log.info("Service reference: \""+ref+"\"") ;
                
                // ---- Implementing class name
                // This done in the loader as well but a check here is more informative 
                String javaClass = null ;
                javaClass = classNameFromNode(className) ;
                if ( javaClass == null )
                    continue ;
                log.info("  Class name: "+javaClass) ;
                
                // ----
                Processor proc = null ;
                try {
                    proc =(Processor)loader.loadAndInstantiateImplementation(procRes, Processor.class) ;
                } catch (LoaderException ex)
                {
                    warn(""+ex.getMessage()) ;
                    continue ;
                }
                
                if ( proc == null )
                {
                    warn("Failed to load "+javaClass) ;
                    continue ;
                }
                
                // Now get the dataset 
                DatasetDesc dataset = null ;
                
                try {
                    dataset = getDatasetForService(ref) ;
                } catch(Exception ex)
                { 
                    log.warn("Problems with dataset: "+ex.getMessage(), ex) ;
                    continue ;
                 }
                
                Service service = new Service(proc, ref, dataset) ;
                services.put(ref, service) ;
                numServices ++ ;
                
                // Record all well-formed services found.
                serviceResources.add(serviceNode) ;
            }
        } catch (JenaException ex)
        {
            log.fatal("Problems finding services") ;
            throw ex ;
        }
        finally { qexec.close() ; }
        
//        // Check that we don't find more part forms services 
//        // than well formed service descriptions
//        checkServicesImpls(serviceResources) ;
//
//        // Check that we don't find more part formed service impls
//        // than well formed service descriptions
        
        return serviceResources ;
    }

    private DatasetDesc getDatasetForService(String ref)
    {
        String s[] = new String[]{
            "SELECT *",
            "{",
            "  ?service  joseki:serviceRef  '"+ref+"' ;",
            "            joseki:dataset     ?dataset ." ,
            "    }",
            "ORDER BY ?serviceRef ?className" } ;
        
        Query query = makeQuery(s) ;
        QueryExecution qexec = QueryExecutionFactory.create(query, confModel) ;

        ResultSet rs = qexec.execSelect() ;
//        ResultSetRewindable rs = ResultSetFactory.makeRewindable(qexec.execSelect()) ;
//        if ( log.isDebugEnabled() )
//        {
//            String x = ResultSetFormatter.asText(rs) ;
//            if ( x.endsWith("\n") )
//                x = x.substring(0, x.length()-2) ;
//            x = "Datasets for service: \n"+x ; 
//            log.info(x) ;
//            rs.reset() ;
//        }
        
        
        List<RDFNode> x = new ArrayList<RDFNode>() ;
        try {
            for ( ; rs.hasNext() ; )
            {
                QuerySolution qs = rs.nextSolution() ;
                x.add(qs.get("dataset")) ;
            }
        } finally { qexec.close() ; }
        
        if ( x.size() == 0 )
            return null ;

        if ( x.size() > 1 )
        {
            warn(""+x.size()+" dataset descriptions for service <"+ref+">") ;
            throw new RuntimeException("Too many dataset descriptions") ;
        }

        RDFNode n = x.get(0) ;
        log.info("Dataset: "+Utils.nodeLabel(n)) ;
        DatasetDesc desc = datasets.get(n) ;
        return desc ;
    }

//    private void checkServicesImpls(Set definedServices)
//    {
//        // ---- Check : class names for implementations
//        List x = findByType(JosekiVocab. .ServicePoint) ;
//        for ( Iterator iter = x.iterator() ; iter.hasNext() ; )
//        {
//            Resource r = (Resource)iter.next() ;
//            if ( !definedServices.contains(r) )
//                 warn("No implementation for service: "+Utils.nodeLabel(r) ) ;
//        }
//    }

    // ----------------------------------------------------------
    // Server set up
    
    private void bindServices(ServiceRegistry registry)
    {
        for ( Iterator<String> iter = services.keySet().iterator() ; iter.hasNext() ; )
        {
            String ref = iter.next() ;
            Service srv = services.get(ref) ;
            if ( ! srv.isAvailable() )
            {
                log.info("Service skipped: "+srv.getRef()) ;
                continue ;
            }
            ref = Service.canonical(ref) ;
            registry.add(ref, srv) ;
            log.info("Service: "+srv.getRef()) ;
        }
    }

    // ----------------------------------------------------------
    // Datasets

    private void findDatasets()
    {
        if ( false )
        {
            // Debug
            List<RDFNode> x = findByType(DatasetAssemblerVocab.tDataset) ;

            for ( Iterator<RDFNode> iter = x.iterator()  ; iter.hasNext() ; )
            {
                Resource r = (Resource)iter.next() ;
                log.info("Dataset: "+Utils.nodeLabel(r)) ;
            }
        }

        // Warn about old stuff.
        checkForJMS() ;
        checkForJosekiDatasetDesc() ;

        // Need to do validity checking on the configuration model.
        // Can also do like services - once with a fixed query then reduce elements
        // to see if we find the same things
        
        // The config file does not have RDFS applied (when used with assemblers it does)
        // Look for immediate subclasses of ja:RDFDataset as well.
        
        String[] s = new String[] {
            "SELECT ?x ?dft ?graphName ?graphData",
            "{ { ?x a ja:RDFDataset } UNION { ?x a [ rdfs:subClassOf ja:RDFDataset ] }",  
            "  OPTIONAL { ?x ja:defaultGraph ?dft }",
            "  OPTIONAL { ?x ja:namedGraph  [ ja:graphName ?graphName ; ja:graph ?graphData ] }",  
            "}", 
            "ORDER BY ?x ?dft ?graphName"
        } ;


        Query query = makeQuery(s) ;
        QueryExecution qexec = QueryExecutionFactory.create(query, confModel) ;
        try {
            
            ResultSetRewindable rs = ResultSetFactory.makeRewindable(qexec.execSelect()) ;
            // Lots of bnodes - no help.
            if ( false && log.isDebugEnabled() )
            {
                String x = ResultSetFormatter.asText(rs) ;
                if ( x.endsWith("\n") )
                    x = x.substring(0, x.length()-2) ;
                x = "Datasets: \n"+x ; 
                log.info(x) ;
                rs.reset() ;
            }
            
            if ( false )
            {
                ResultSetRewindable rs2 = ResultSetFactory.makeRewindable(rs) ;
                ResultSetFormatter.out(System.out, rs2, query) ;
                rs2.reset() ;
                rs = rs2 ;
            }

            DatasetDesc src = null ;
            Resource ds = null ;
            Resource dft = null ;
            for ( ; rs.hasNext() ; )
            {
                QuerySolution qs = rs.nextSolution() ;
                Resource x = qs.getResource("x") ;

                // No - SDB datsets do not do any of this.
                // Cope with no datset description, but print useful stuff
                // if there is a broken one.
                
//                if ( dftGraph == null && graphName == null )
//                    // Note the named graph match assumed a well-formed name/data pair
//                    warn("Dataset with no default graph and no named graphs: "+ Utils.nodeLabel(x)) ;

                Resource dftGraph = qs.getResource("dft") ; 
                Resource graphName = qs.getResource("graphName") ;
                Resource graphData = qs.getResource("graphData") ;

                // New dataset
                if ( ! x.equals(ds) )
                {
                    log.info("New dataset: "+Utils.nodeLabel(x)) ;

                    src = new DatasetDesc(x) ;
                    datasets.put(x, src) ;
                    
                    // The rest is just checking structures ...
                    numDatasets ++ ;

                    // -- Checking
                    if ( dftGraph != null )
                    {
                        log.info("  Default graph : "+Utils.nodeLabel(dftGraph)) ;
                        //src.setDefaultGraphDesc(dftGraph) ;
                        numDefaultGraphs++ ;
                    }
                    dft = dftGraph ;
                }
                else
                {
                    // -- Checking
                    // Check one default model.
                    if ( dftGraph != null && !dftGraph.equals(dft) )
                        warn("  Two default graphs") ;
                }

                if ( graphName != null )
                {
                    log.info("  Graph / named : <"+graphName+">") ;

                    if ( graphName.isAnon() )
                        throw new ConfigurationErrorException("Graph name can't be a blank node") ; 

                    if ( graphData == null )
                    {
                        warn("  Graph name but no graph data: <"+graphName.getURI()+">") ;
                        throw new ConfigurationErrorException("No data for graph <"+graphName.getURI()+">") ;
                    }

                    numNamedGraphs++ ; 
                }

                ds = x ;
            }
        } finally { qexec.close() ; }
    }
    
    private void checkForJMS()
    {
        String[] s = new String[] {
            "SELECT ?modelDesc",
            "{ ?modelDesc ?p ?o .",
            "  FILTER regex(str(?p), '^http://jena.hpl.hp.com/2003/08/jms#')",
            "}",  
        } ;
        Query query = makeQuery(s) ;
        QueryExecution qexec = QueryExecutionFactory.create(query, confModel) ;
        try {
            ResultSet rs = qexec.execSelect() ;
            for ( ; rs.hasNext() ; )
            {
                QuerySolution qs = rs.nextSolution() ;
                Resource m = qs.getResource("modelDesc") ;
                log.warn("**** Use of Jena Model Spec vocabulary is deprecated: "+Utils.nodeLabel(m)+" [use Assembler vocabulary instead]") ;
            }
        } finally { qexec.close() ; }
        
    }

    private void checkForJosekiDatasetDesc()
    {
        /* Check for: old stuff.
            Class:     joseki:RDFDataSet
            Property:  joseki:defaultGraph
            Property:  joseki:namedGraph
            Property:  joseki:graphName (very old - would need one of the above)
            Property:  joseki:graphData (very old - would need one of the above)
         */

        {
            String[] s = new String[]{
                stdHeaders(),
                "ASK",
                "{ ?x rdf:type joseki:RDFDataSet }"
            } ;
            Query query = makeQuery(s) ;
            QueryExecution qexec = QueryExecutionFactory.create(query, confModel) ;
            if ( qexec.execAsk() )
            {
                log.warn("Use of old style joseki:RDFDataSet is not supported") ;
                log.warn("Use Jena assembler ja:RDFDataset") ;
            }
            qexec.close() ;
        }
        
        {
            String[] s = new String[] {
                stdHeaders(),
                "ASK",
                "{ { ?s joseki:defaultGraph ?p }",
                "  UNION",
                "  { ?s joseki:namedGraph ?p }  ",
                "}",  
            } ;
            Query query = makeQuery(s) ;
            QueryExecution qexec = QueryExecutionFactory.create(query, confModel) ;
            if ( qexec.execAsk()  )
            {
                log.warn("Use of old style joseki:defaultGraph/joseki:namedGraph is not supported") ;
                log.warn("Use Jena assembler ja:defaultGraph/ja:namedGraph") ;
            }
            qexec.close() ;
        }
    }
    
//    private void checkNamedGraphDescriptions()
//    {
//        // Check with reduced queries
//        
//        String[] s = new String[] {
//           "SELECT ?x ?ng ?graphName ?graphData",
//           "{ ?x joseki:namedGraph  ?ng ." +
//           "  OPTIONAL { ?ng joseki:graphName ?graphName }",  
//           "  OPTIONAL { ?ng joseki:graphData ?graphData }",  
//           "}", 
//           "ORDER BY ?ng ?graphName ?graphData"
//           } ;
//        Query query = makeQuery(s) ;
//        QueryExecution qexec = QueryExecutionFactory.create(query, confModel) ;
//        try {
//            ResultSet rs = qexec.execSelect() ;
//            for ( ; rs.hasNext() ; )
//            {
//                QuerySolution qs = rs.nextSolution() ;
//                Resource x         = qs.getResource("x") ;
//                //Resource ng        = qs.getResource("ng") ;
//                Resource graphName = qs.getResource("graphName") ;
//                Resource graphData = qs.getResource("graphData") ;
//                
//                if ( graphName == null && graphData == null )
//                    warn("Named graph description with no name and no data. Part of "+Utils.nodeLabel(x)) ;
//                
//                if ( graphName != null && graphData == null )
//                    warn("Named graph description a name but no data: Name = "+Utils.nodeLabel(graphName)) ;
//                
//                if ( graphName == null && graphData != null )
//                    warn("Named graph description with data but no name: "+Utils.nodeLabel(graphData)) ;
//            }
//        } finally { qexec.close() ; }
//    }

    private void checkBoundServices(Set<Resource> definedServices, Set<Resource> boundServices)
    {
        Set<Resource> x = new HashSet<Resource>(definedServices) ;
        x.removeAll(boundServices) ;
        for ( Resource srv : x  )
            warn("Service not attached to a server: "+Utils.nodeLabel(srv)) ;
    }
    
    // ----------------------------------------------------------
    // Utilities
    
    private String serviceRef(RDFNode node)
    {
        if ( ! ( node instanceof Literal ) ) 
            return null ;
        Literal lit = ((Literal)node) ;
        if ( ! lit.getLanguage().equals("") )
            log.warn("Service reference has a language tag") ;
        String ref = lit.getLexicalForm() ;
        return ref ;
    }
    
    private List<RDFNode> findByType(Resource r)
    {
        if ( r.isAnon() )
        {
            warn("BNode for type - not supported (yet)") ;
            return null ;
        }
        
        return findByType(r.getURI()) ;
    }
    
    private List<RDFNode> findByType(String classURI)
    {
        // Keep in same order that the query finds them.
        List<RDFNode> things = new ArrayList<RDFNode>() ; 
        
        String s = "PREFIX rdf: <"+RDF.getURI()+">\nSELECT ?x { ?x rdf:type <"+classURI+"> }" ;
        Query q = makeQuery(s) ;
        QueryExecution qexec = QueryExecutionFactory.create(q, confModel) ;
        try {
            for ( ResultSet rs = qexec.execSelect() ; rs.hasNext() ; )
            {
                QuerySolution qs = rs.nextSolution() ;
                RDFNode n = qs.get("x") ;
                things.add(n) ;
            }
        } finally { qexec.close() ; }
        return things ;
    }
    
    
    // ------------------------------------------------------
        
    private Query makeQuery(String[] a) 
    {
//        StringBuffer sBuff = new StringBuffer() ;
//        stdHeaders(sBuff) ;
//        sBuff.append("\n") ;
//        
//        for ( int i = 0 ; i < a.length ; i++ )
//        {
//            if ( i != 0 )
//                sBuff.append("\n") ;
//            sBuff.append(a[i]) ;
//        }
//        
//        String qs = sBuff.toString() ;
        String qs = stdHeaders()+StringUtils.join("\n", a) ;
        return makeQuery(qs) ;
    }

    private Query makeQuery(String qs) 
    {
        try {
            Query query = QueryFactory.create(qs, Syntax.syntaxARQ) ;
            return query ;
        } catch (QueryParseException ex)
        {
            System.out.println(qs) ;
            log.fatal("Query failed: "+ex.getMessage()) ;
            throw new ConfigurationErrorException("Internal error") ;
        }
    }

    
    private String stdHeaders()
    {
        StringBuffer sBuff = new StringBuffer() ;
        stdNS(sBuff, "rdf",  RDF.getURI()) ;
        stdNS(sBuff, "rdfs", RDFS.getURI()) ;
        stdNS(sBuff, "module" , "http://joseki.org/2003/06/module#") ;
        stdNS(sBuff, "joseki" ,  JosekiVocab.getURI()) ;
        stdNS(sBuff, "ja" ,  DatasetAssemblerVocab.getURI()) ;
        return sBuff.toString() ;
    }
    
    private static void stdNS(StringBuffer sBuff, String prefix, String namespace)
    {
        sBuff.append("PREFIX ") ;
        sBuff.append(prefix) ;
        sBuff.append(":") ;
        sBuff.append("  ") ;
        sBuff.append("<") ;
        sBuff.append(namespace) ;
        sBuff.append(">") ;
        sBuff.append("\n") ;
    }
    
    private String classNameFromNode(RDFNode n)
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
        {
            warn("Class name is a blank node") ;
            return null ;
        }
        
        if ( ! r.getURI().startsWith("java:") )
        {
            warn("Class name is a URI but not from the java: scheme: "+r) ;
            return null ;
        }
        className = r.getURI().substring("java:".length()) ;
        return className ; 
    }
    
    private void warn(String msg)
    {
        log.warn("** "+msg) ;
        warnings++ ;
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