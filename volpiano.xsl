<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xs="http://www.w3.org/2001/XMLSchema"
                xmlns:map="http://www.w3.org/2005/xpath-functions/map"
                version="3.0"
                exclude-result-prefixes="#all">
  <xsl:output method="html" version="5" encoding="UTF-8" indent="yes"/>
  <xsl:strip-space elements="*"/>

  <xsl:template match=".[. instance of map(*)]">
    <html>
      <head>
        <meta charset="utf-8"/>
        <title>VOLPIANO</title>
        <style>
.volpiano {
  font-family: Volpiano;
  font-size: 4rem;
}
    </style>
      </head>
      <body>
        <h1>Volpiano Test</h1>
        <div>
          <xsl:variable name="map" select="."/>
          <xsl:for-each select="map:keys(.)">
            <div>
              <h2>
                <xsl:value-of select="."/>
              </h2>
              <div class="volpiano">
                <xsl:value-of select="$map(.)"/>
              </div>
            </div>
          </xsl:for-each>
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
