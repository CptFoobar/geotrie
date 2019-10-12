package io.sidhant.geospatial

import java.io.File
import org.geotools.swing.data.JFileDataStoreChooser

class Driver {
  val file: File = JFileDataStoreChooser.showOpenFile("shp", null)
  println(file.getAbsoluteFile)
}
