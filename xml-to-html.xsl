<?xml version="1.0"?>

<!--

XSLT script to format SPARQL Query Results XML Format into xhtml

Copyright © 2004, 2005 World Wide Web Consortium, (Massachusetts
Institute of Technology, European Research Consortium for
Informatics and Mathematics, Keio University). All Rights
Reserved. This work is distributed under the W3C® Software
License [1] in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.

[1] http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231

Version 1 : Dave Beckett (DAWG)
Version 2 : Jeen Broekstra (DAWG)
Customization for SPARQler: Andy Seaborne

-->

<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns="http://www.w3.org/1999/xhtml"
		xmlns:res="http://www.w3.org/2005/sparql-results#"
		exclude-result-prefixes="res xsl">

  <!--
	<xsl:output
	method="html"
	media-type="text/html"
	doctype-public="-//W3C//DTD HTML 4.01 Transitional//EN"
	indent="yes"
	encoding="UTF-8"/>
  -->

  <!-- or this? -->

  <xsl:output
  method="xml" 
  indent="yes"
  encoding="UTF-8" 
  doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
  doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"
  omit-xml-declaration="no" />


  <xsl:template name="header">
	<div>
	  <h2>Header</h2>
	  <xsl:for-each select="res:head/res:link"> 
	<p>Link to <xsl:value-of select="@href"/></p>
	  </xsl:for-each>
	</div>
  </xsl:template>

  <xsl:template name="boolean-result">
	<div>
	  <!--      
	<h2>Boolean Result</h2>
	  -->      
	  <p>ASK => <xsl:value-of select="res:boolean"/></p>
	</div>
  </xsl:template>


  <xsl:template name="vb-result">
	<div>
	  <!--
	<h2>Variable Bindings Result</h2>
	<p>Ordered: <xsl:value-of select="res:results/@ordered"/></p>
	<p>Distinct: <xsl:value-of select="res:results/@distinct"/></p>
	  -->

	  <table>
	<xsl:text>
	</xsl:text>
	<tr>
	  <xsl:for-each select="res:head/res:variable">
<!--	  	<xsl:choose>
		<xsl:when name="title"> -->
			<th><xsl:value-of select="@name"/></th>
<!--	    </xsl:when>
		</xsl:choose> -->
	  </xsl:for-each>
	</tr>
	<xsl:text>
	</xsl:text>
	<xsl:for-each select="res:results/res:result">
	  <tr>
		<xsl:apply-templates select="."/>
	  </tr>
	</xsl:for-each>
	  </table>
	</div>
  </xsl:template>
  
  <xsl:template name="pastqueries">
	<xsl:for-each select="res:pastqueries/res:query">
	  <xsl:value-of select="text()"/><br />
	</xsl:for-each>
  </xsl:template>
  
  <xsl:template name="sparqlquery">
	<xsl:for-each select="res:sparqlquery">
      <center>
        <a href="javascript:;" onmousedown="toggleDiv('mydiv');">SPARQL query</a>
      </center>
      <div id="mydiv" style="display:none">
        <xmp>
          <xsl:value-of select="text()"/>
        </xmp>
      </div>
	</xsl:for-each>
  </xsl:template>

  <xsl:template match="res:result">
	<xsl:variable name="current" select="."/>
	<xsl:for-each select="//res:head/res:variable">
	  <xsl:variable name="name" select="@name"/>
	  <td>
	<xsl:choose>
	  <xsl:when test="$current/res:binding[$name='from']">
		<!-- apply template for the correct value type (bnode, uri, literal) -->
		XXX <xsl:apply-templates select="$current/res:binding[@name=$name]"/>
	  </xsl:when>
	  <xsl:when test="$current/res:binding[@name=$name]">
		<!-- apply template for the correct value type (bnode, uri, literal) -->
		<xsl:apply-templates select="$current/res:binding[@name=$name]"/>
	  </xsl:when>
	  <xsl:otherwise>
		<!-- no binding available for this variable in this solution -->
	  </xsl:otherwise>
	</xsl:choose>
	  </td>
	</xsl:for-each>
  </xsl:template>

  <xsl:template match="res:bnode">
	<xsl:text>_:</xsl:text>
	<xsl:value-of select="text()"/>
  </xsl:template>

  <xsl:template match="res:uri">
	<xsl:variable name="uri" select="text()"/>
	<xsl:text>&lt;</xsl:text>
	<xsl:value-of select="$uri"/>
	<xsl:text>&gt;</xsl:text>
  </xsl:template>

  <xsl:template match="res:literal">
	<xsl:text></xsl:text>
	<xsl:value-of select="text()"/>
	<xsl:text></xsl:text>

	<xsl:choose>
	  <xsl:when test="@datatype">
	<!-- datatyped literal value -->
	^^&lt;<xsl:value-of select="@datatype"/>&gt;
	  </xsl:when>
	  <xsl:when test="@xml:lang">
	<!-- lang-string -->
	@<xsl:value-of select="@xml:lang"/>
	  </xsl:when>
	</xsl:choose>
  </xsl:template>

<xsl:template match="res:sparql">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
	<head>
		<title><xsl:value-of select="//res:pastqueries/res:fullquery" /></title>
		<style><![CDATA[
			h1 { font-size: 150% ; }
			h2 { font-size: 125% ; }
			table { border-collapse: collapse ; border: 1px solid black ; }
			td, th
			{ border: 1px solid black ;
				padding-left:0.5em; padding-right: 0.5em; 
				padding-top:0.2ex ; padding-bottom:0.2ex 
			}
			body {
				background-color: #eee;
				margin: 0;
			}
			]]>
		</style>
		<script language="javascript"><![CDATA[
			function toggleDiv(divid){
			  if(document.getElementById(divid).style.display == 'none'){
				document.getElementById(divid).style.display = 'block';
			  }else{
				document.getElementById(divid).style.display = 'none';
			  }
			}
			]]>
        </script>
		<link rel="stylesheet" href="index.css" />
	</head>
	<body>
		<a href="show-rules.php">rules</a>
		<form action="exec.php" method="post">
			<input id="main-form-query" type="text" name="query" size="60" />
			<input id="lastquery" type="hidden" name="lastquery">
			  <xsl:attribute name="value"><xsl:value-of select="//res:pastqueries/res:fullquery" /></xsl:attribute>
			</input>
			<input id="main-form-sid" type="hidden" name="sid" value="100" />
		</form>
	
		<center><h3><xsl:value-of select="//res:pastqueries/res:fullquery" /></h3></center>
		
		<xsl:if test="res:head/res:link">
		<xsl:call-template name="header"/>
		</xsl:if>
	
		<xsl:choose>
		<xsl:when test="res:boolean">
			<xsl:call-template name="boolean-result" />
		</xsl:when>
	
		<xsl:when test="res:results">
			<xsl:call-template name="vb-result" />
		</xsl:when>
	
		</xsl:choose>
		
<!--		<xsl:if test="res:pastqueries">
			<xsl:call-template name="pastqueries" />
		</xsl:if>
	-->	
		<xsl:if test="res:sparqlquery">
			<xsl:call-template name="sparqlquery" />
		</xsl:if>
	</body>
</html>
</xsl:template>
</xsl:stylesheet>
