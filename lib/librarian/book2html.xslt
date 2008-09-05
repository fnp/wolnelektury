<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:wl="http://wolnelektury.pl/functions" >

<xsl:output method="xml" encoding="utf-8" doctype-public="-//W3C//DTD XHTML 1.1//EN" doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd" indent="yes" />


<xsl:template match="utwor">
    <html>
        <head>
            <title>book2html output</title>
            <meta http-equiv="content-type" content="text/html;charset=utf-8"/>
            <link rel="stylesheet" href="master.css" type="text/css" media="all" charset="utf-8" />
        </head>
        <body>
            <xsl:apply-templates select="powiesc|opowiadanie|liryka_l|liryka_lp|dramat_wierszowany_l|dramat_wierszowany_lp|dramat_wspolczesny" />
            <xsl:if test="count(descendant::*[self::pe or self::pa or self::pr or self::pt][not(parent::extra)])">
                <div id="footnotes">
                    <h3>Przypisy</h3>
                    <xsl:for-each select="descendant::*[self::pe or self::pa or self::pr or self::pt][not(parent::extra)]">
                        <div>
                            <a name="{concat('footnote-', generate-id(.))}" />
                            <a href="{concat('#anchor-', generate-id(.))}" class="annotation">[<xsl:number value="count(preceding::*[self::pa or self::pe or self::pr or self::pt]) + 1" />]</a>
                            <xsl:choose>
                                <xsl:when test="count(akap|akap_cd|strofa) = 0">
                                    <p><xsl:apply-templates select="text()|*" mode="inline" /></p>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:apply-templates select="text()|*" mode="inline" />
                                </xsl:otherwise>
                            </xsl:choose>
                        </div>
                    </xsl:for-each>
                </div>
            </xsl:if>
        </body>
    </html>
</xsl:template>


<!-- ============================================================================== -->
<!-- = MASTER TAG                                                                 = -->
<!-- = (can contain block tags, paragraph tags, standalone tags and special tags) = -->
<!-- ============================================================================== -->
<xsl:template match="powiesc|opowiadanie|liryka_l|liryka_lp|dramat_wierszowany_l|dramat_wierszowany_lp|dramat_wspolczesny">
    <xsl:if test="nazwa_utworu">
        <h1>
            <xsl:apply-templates select="autor_utworu|dzielo_nadrzedne|nazwa_utworu|podtytul" mode="header" />
        </h1>
    </xsl:if>
    <xsl:apply-templates />
</xsl:template>


<!-- ==================================================================================== -->
<!-- = BLOCK TAGS                                                                       = -->
<!-- = (can contain other block tags, paragraph tags, standalone tags and special tags) = -->
<!-- ==================================================================================== -->
<xsl:template match="nota">
    <div class="note"><xsl:apply-templates /></div>
</xsl:template>

<xsl:template match="lista_osob">
    <div class="person-list">
        <h3><xsl:value-of select="naglowek_listy" /></h3>
        <ol>
            <xsl:apply-templates select="lista_osoba" />
        </ol>
    </div>
</xsl:template>

<xsl:template match="dedykacja">
    <div class="dedication"><xsl:apply-templates /></div>
</xsl:template>

<xsl:template match="kwestia">
    <div class="kwestia">
        <xsl:apply-templates select="strofa|akap" />
    </div>
</xsl:template>

<xsl:template match="dlugi_cytat|poezja_cyt">
    <blockquote><xsl:apply-templates /></blockquote>
</xsl:template>

<xsl:template match="motto">
    <div class="motto"><xsl:apply-templates mode="inline" /></div>
</xsl:template>


<!-- ========================================== -->
<!-- = PARAGRAPH TAGS                         = -->
<!-- = (can contain inline and special tags)  = -->
<!-- ========================================== -->
<!-- Title page -->
<xsl:template match="autor_utworu" mode="header">
    <span class="author"><xsl:apply-templates mode="inline" /></span>
</xsl:template>

<xsl:template match="nazwa_utworu" mode="header">
    <span class="title"><xsl:apply-templates mode="inline" /></span>
</xsl:template>

<xsl:template match="dzielo_nadrzedne" mode="header">
    <span class="collection"><xsl:apply-templates mode="inline" /></span>
</xsl:template>

<xsl:template match="podtytul" mode="header">
    <span class="subtitle"><xsl:apply-templates mode="inline" /></span>
</xsl:template>

<!-- Section headers (included in index)-->
<xsl:template match="naglowek_akt|naglowek_czesc|srodtytul">
    <h2><xsl:apply-templates mode="inline" /></h2>
</xsl:template>

<xsl:template match="naglowek_scena|naglowek_rozdzial">
    <h3><xsl:apply-templates mode="inline" /></h3>
</xsl:template>

<xsl:template match="naglowek_osoba|naglowek_podrozdzial">
    <h4><xsl:apply-templates mode="inline" /></h4>
</xsl:template>

<!-- Other paragraph tags -->
<xsl:template match="miejsce_czas">
    <p class="place-and-time"><xsl:apply-templates mode="inline" /></p>
</xsl:template>

<xsl:template match="didaskalia">
    <div class="didaskalia"><xsl:apply-templates mode="inline" /></div>
</xsl:template>

<xsl:template match="lista_osoba">
    <li><xsl:apply-templates mode="inline" /></li>
</xsl:template>

<xsl:template match="akap|akap_dialog|akap_cd">
    <p class="paragraph"><xsl:apply-templates mode="inline" /></p>
</xsl:template>

<xsl:template match="strofa">
    <div class="stanza">
        <xsl:choose>
            <xsl:when test="count(br) > 0">     
                <xsl:call-template name="verse">
                    <xsl:with-param name="line-content" select="br[1]/preceding-sibling::text() | br[1]/preceding-sibling::node()" />
                    <xsl:with-param name="line-number" select="1" />
                </xsl:call-template>    
                <xsl:for-each select="br">		
        			<!-- Each BR tag "consumes" text after it -->
                    <xsl:variable name="lnum" select="count(preceding-sibling::br)" />
                    <xsl:call-template name="verse">
                        <xsl:with-param name="line-number" select="$lnum+2" />
                        <xsl:with-param name="line-content" 
                            select="following-sibling::text()[count(preceding-sibling::br) = $lnum+1] | following-sibling::node()[count(preceding-sibling::br) = $lnum+1]" />
                    </xsl:call-template>
                </xsl:for-each>
            </xsl:when>
            <xsl:otherwise>
                <xsl:call-template name="verse">
                    <xsl:with-param name="line-content" select="text() | node()" />
                    <xsl:with-param name="line-number" select="1" />
                 </xsl:call-template>           
            </xsl:otherwise>
        </xsl:choose>
    </div>
</xsl:template>

<xsl:template name="verse">
    <xsl:param name="line-content" />
    <xsl:param name="line-number" />
    <p>
        <xsl:choose>
            <xsl:when test="name($line-content) = 'wers_akap'">
                <xsl:attribute name="style">padding-left: 1em</xsl:attribute>
            </xsl:when>
            <xsl:when test="name($line-content) = 'wers_wciety'">
                <xsl:attribute name="style">padding-left: <xsl:value-of select="$line-content/@typ" />em</xsl:attribute>
            </xsl:when>
        </xsl:choose>
        <xsl:apply-templates select="$line-content" mode="inline" />
    </p>
</xsl:template>

<xsl:template match="motto_podpis">
    <p class="motto_podpis"><xsl:apply-templates mode="inline" /></p>
</xsl:template>


<!-- ================================================ -->
<!-- = INLINE TAGS                                  = -->
<!-- = (contain other inline tags and special tags) = -->
<!-- ================================================ -->
<!-- Annotations -->
<xsl:template match="pa|pe|pr|pt" mode="inline">
    <a name="{concat('anchor-', generate-id(.))}" />
    <a href="{concat('#footnote-', generate-id(.))}" class="annotation">[<xsl:number value="count(preceding::*[self::pa or self::pe or self::pr or self::pt]) + 1" />]</a>
</xsl:template>

<!-- Other inline tags -->
<xsl:template match="mat" mode="inline">
    <em class="math"><xsl:apply-templates mode="inline" /></em>
</xsl:template>

<xsl:template match="didask_tekst" mode="inline">
    <em class="didaskalia"><xsl:apply-templates mode="inline" /></em>
</xsl:template>

<xsl:template match="slowo_obce" mode="inline">
    <em class="foreign-word"><xsl:apply-templates mode="inline" /></em>
</xsl:template>

<xsl:template match="tytul_dziela" mode="inline">
    <em class="book-title">
        <xsl:if test="@typ = '1'">„</xsl:if><xsl:apply-templates mode="inline" /><xsl:if test="@typ = '1'">”</xsl:if>
    </em>
</xsl:template>

<xsl:template match="wyroznienie" mode="inline">
    <em class="author-emphasis"><xsl:apply-templates mode="inline" /></em>
</xsl:template>

<xsl:template match="osoba" mode="inline">
    <em class="person"><xsl:apply-templates mode="inline" /></em>
</xsl:template>


<!-- ============================================== -->
<!-- = STANDALONE TAGS                            = -->
<!-- = (cannot contain any other tags)            = -->
<!-- ============================================== -->
<xsl:template match="sekcja_swiatlo">
    <hr class="spacer" />
</xsl:template>


<!-- ================ -->
<!-- = SPECIAL TAGS = -->
<!-- ================ -->
<!-- Themes -->
<xsl:template match="begin" mode="inline">
    <xsl:variable name="mnum" select="concat('m', substring(@id, 2))" />
    <span class="theme-begin" fid="{substring(@id, 2)}">
        <xsl:value-of select="string(following::motyw[@id=$mnum]/text())" />
    </span>
</xsl:template>

<xsl:template match="end" mode="inline">
    <span class="theme-end" fid="{substring(@id, 2)}"> </span>
</xsl:template>

<xsl:template match="begin|end">
    <xsl:apply-templates select='.' mode="inline" />
</xsl:template>

<xsl:template match="motyw" mode="inline" />


<!-- ================ -->
<!-- = IGNORED TAGS = -->
<!-- ================ -->
<xsl:template match="extra|uwaga" />
<xsl:template match="extra|uwaga" mode="inline" />


<!-- ======== -->
<!-- = TEXT = -->
<!-- ======== -->
<xsl:template match="text()" />
<xsl:template match="text()" mode="inline">
    <xsl:value-of select="wl:substitute_entities(.)" />
</xsl:template>


</xsl:stylesheet>

