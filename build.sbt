name := "GeoTrie"

version := "0.1"

scalaVersion := "2.12.10"


resolvers += "Osgeo Repo" at "http://download.osgeo.org/webdav/geotools/"
resolvers += "Boundless" at "http://repo.boundlessgeo.com/main"
resolvers += "imageio" at "http://maven.geo-solutions.it"

// https://mvnrepository.com/artifact/org.elasticsearch/elasticsearch-geo
libraryDependencies += "org.elasticsearch" % "elasticsearch-geo" % "7.2.0"

// https://mvnrepository.com/artifact/com.vividsolutions/jts
libraryDependencies += "com.vividsolutions" % "jts" % "1.13"

// https://mvnrepository.com/artifact/org.geotools/geotools
libraryDependencies += "org.geotools" % "geotools" % "22.0"

// https://mvnrepository.com/artifact/org.geotools/gt-main
libraryDependencies += "org.geotools" % "gt-main" % "22.0"

// https://mvnrepository.com/artifact/org.geotools/gt-swing
libraryDependencies += "org.geotools" % "gt-swing" % "22.0"

assemblyMergeStrategy in assembly := {
  case PathList("META-INF", "eclipse.inf") => MergeStrategy.last
  case x =>
    val oldStrategy = (assemblyMergeStrategy in assembly).value
    oldStrategy(x)
}