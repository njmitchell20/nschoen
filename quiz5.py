def calculateRoadSegmentsInPolygon(input_geodatabase, fcA, fcB, fcB_id_field):
   #OBJECTIVE: calculate the total length of road segments in meters from fcB (polyline) in fcA (polygon)
   #import packages
   import arcpy
   import sys
   #create output file with the same name as existing file by overwriting it
   arcpy.env.overwriteOutput = True
   #test for existence of data types
   if arcpy.Exists(input_geodatabase):
      #set workspace to user input geodatabase
      arcpy.env.workspace = input_geodatabase
      print("Environment workspace is set to: ", input_geodatabase)
   else:
      print("Workspace", input_geodatabase, "does not exist!")
      sys.exit(1)
   #use try to identify errors in the types of data  
   try:
      #use the describe function to determine the element data type
      desc_fcA = arcpy.Describe(fcA)
      desc_fcB = arcpy.Describe(fcB)
      #ensure that feature class A is a polyon data type
      if desc_fcA.shapeType != "Polygon":
         print("Error shapeType: ", fcA, "need to be a polygon type!")
         sys.exit(1)
      #ensure that feature class B is a polyline data type
      if desc_fcB.shapeType != "Polyline":
         print("Error shapeType: ", fcB, "need to be a polyline type!")
         sys.exit(1)
      #ensure that the two feature classes are in the same coordinate system
      if desc_fcA.spatialReference.name != desc_fcB.spatialReference.name:
         print("Coordinate system error: Spatial reference of", fcA, "and", fcB, "should be the same.")
         sys.exit(1)
      #check to see if the input feature class field exists
      fields = [f.name for f in arcpy.ListFields(fcB)]
      if fcB_id_field in fields:
         print(fcB_id_field, "exists in", fcB)
      else:
         print(fcB_id_field, "does NOT exist in", fcB)
         sys.exit(1)
      #add a new field to feature class B to keep track of how many line segments are in each polygon
      arcpy.AddField_management(fcB, "total_length", "DOUBLE")
      print("Total length field is added to", fcB)
      # calculate total length in meters
      arcpy.CalculateGeometryAttributes_management(fcB, [["total_length", "LENGTH_GEODESIC"]], "METERS")
      print("Total length in meters are calculated for", fcB)
      #calculate geometric intersection between class features
      fcB_inters_fcA = "fcB_intersects_fcA"
      arcpy.Intersect_analysis([fcB, fcA], fcB_inters_fcA)
      print(fcB, "is intersected with", fcA)
      #create output field to calculate area for feature class A
      areaA_field = "areaA_sqmi"
      arcpy.AddField_management(fcB_inters_fcA, areaA_field, "DOUBLE")
      print("Area in sq miles field is added to the intersected feature class: ", fcB_inters_fcA)
      #calculate length of fcB in fcA
      arcpy.CalculateGeometryAttributes_management(fcB_inters_fcA, [[areaA_field, "LENGTH_GEODESIC"]], "METERS")
      print("Total length in meters are calculated for the intersected feature class: ", fcB_inters_fcA)
      #create a dictonary to store values
      fcB_dict = dict()
      #use search cursor to iterate through rows and get the field values from the ID field
      with arcpy.da.SearchCursor(fcB_inters_fcA, [fcB_id_field, areaA_field]) as cursor:
          for row in cursor:
              id_ = row[0]
              if id_ in fcB_dict.keys():
                  fcB_dict[id_] += row[1]
              else:
                  fcB_dict[id_] = row[1]
      #delete data from the intersected feature class
      arcpy.Delete_management(fcB_inters_fcA)
      print("Temporary intersection feature class", fcB_inters_fcA, "is deleted")
      print("Area of multiple polylines in", fcA, "is summed in a dictionary of", fcB, "with", fcB_id_field)
      arcpy.AddField_management(fcB, areaA_field, "DOUBLE")
      #use update cursor to update data in the field by looking through other fields
      with arcpy.da.UpdateCursor(fcB, [fcB_id_field, areaA_field]) as cursor:
          for row in cursor:
             if row[0] in fcB_dict.keys():
                row[1] = fcB_dict[row[0]]
             else:
                row[1] = 0
             cursor.updateRow(row)
       print("Total length of polylines in", fcB, "is updated for each polygon in", fcA)
   #add an exception to finish the try code earlier mentioned
   except Exception:
      e = sys.exc_info()[1]
      print(e.args[0])       