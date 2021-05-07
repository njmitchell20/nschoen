#Natalie Schoen and Nathan Mitchell
#GEOG:3050
#Final Project
#May 5th, 2021

#Data sources:
#SVI shapefile: https://www.atsdr.cdc.gov/placeandhealth/svi/data_documentation_download.html
#flood hazard areas map: https://www.arcgis.com/home/item.html?id=11955f1b47ec41a3af86650824e0c634
#Instructions for flood hazard area map: In ArcGIS Pro, open a map and select Add Data from the Map Tab. Select Data at the top of the drop down menu. The Add Data dialog box will open on the left side of the box, expand Portal if necessary, then select Living Atlas. Type "flood hazard areas" in the search box, browse to the layer then click OK.
#flood hazard areas map: specifically the feature class "1% Annual Chance Flood Hazard"

#1. Create a file geodatabase and import the SVI shapefile and flood hazard areas data into the geodatabase
#2. Check that the projections of the datafiles are the same (basemap uses USA Contiguous Albers Equal Area Conic USGS version)
#3. Check that the input SVI shapefile is a polygon type file
#4. Calculate % area of each census tract in Florida that has a 1% Annual Chance Flood Hazard
#https://support.esri.com/en/technical-article/000010997
#   a) Create a new field in the SVI shapefile to find total area of flood land in census tracts
#   b) Use intersect analysis to calculate geometric intersection of input features
#   c) Clip the total area by census tract boundaries
#   d) Calculate geometry for the new field using AREA_GEODESIC to determine total area of flood land within each census tract
#   e) Create another new field in the SVI shapefile to find percentage area of total land 
#   f) Calculate geometry for the field using flood land area / total area of census tracts * 100
# Preform a spatial autocorrelation test: https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-statistics/incremental-spatial-autocorrelation.htm
# Preform an explanatory regression model: https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-statistics/exploratory-regression.htm

#Caglar suggestions:
#spatial autocorrelation and hot spots to analyze each variable and the geographic clustering and variation
#You can then run spatial regression models to evaluate the hypotheses on the effect of various factors on vulnerability from floods

def floodVulnerability(fcPolygon, geodatabase):
    import arcpy
    arcpy.env.overwriteOutput = True
    folder = "C:\Users\nschoen\OneDrive - University of Iowa\Documents\ArcGIS\Projects\finalProject"
    arcpy.env.workspace = folder
    arcpy.CreateFileGDB_management(folder, geodatabase)
    #add SVI shapefile to the geodatabase 
    shapefile = geodatabase + fcPolygon
    #not sure to use fcPolygon or actual name
    #shapefile = geodatabase + "/SVI2018_FLORIDA_tract.shp" 
    if arcpy.Exists(geodatabase):
        #set workspace to user input geodatabase
        arcpy.env.workspace = geodatabase
        print("Environment workspace is set to: ", geodatabase)
    else:
        print("Workspace", geodatabase, "does not exist!")
        sys.exit(1)
    spatial_ref = arcpy.Describe(shapefile).spatialReference
    if spatial_ref.name != "Albers equal area conic":
        print("Coordinate system error: Spatial reference of ", shapefile, " should be projected as 'Albers equal area conic' to match the projection of the flood hazard area basemap.")
        #arcpy.management.Project(in_dataset, out_dataset, out_coor_system, {transform_method}, {in_coor_system}, {preserve_shape}, {max_deviation}, {vertical})
        #https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/project.htm
    desc_shapefile = arcpy.Describe(shapefile)
    if desc_shapefile.shapeType != "Polygon":
        print("Error shapeType: ", shapefile, "needs to be a polygon type!")
        sys.exit(1)
    
    