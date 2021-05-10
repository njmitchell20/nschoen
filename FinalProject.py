#Natalie Schoen and Nathan Mitchell
#GEOG:3050
#Final Project
#May 9th, 2021

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

#function takes a polygon feature class, CSV, damage metric field from CSV, a SV score Field, a field to normalize the damage(pop/sqmi), and an empty gdb as inputs.
#function ouputs reclass_damageField_Class field on the input feature class which denotes the risk rank of flooding
#fcPolygon = "SVI2018_FLORIDA_county"
#inputCSV = "Florida.csv"
#damageField = PropertyDam
#normField = E_TOTPOP/AREA_SQMI
#SVField = RPL_THEMES
#polyjField = "COUNTY"
#csvjField = "County Name"
#geodatabase = any gdb, empty is nice

def floodVulnerability(fcPolygon, inputCSV, polyjField, csvjField, damageField, normField, SVField,  geodatabase):
    import arcpy
    arcpy.env.overwriteOutput = True
    #exception handling
    if arcpy.Exists(geodatabase):
        #set workspace to user input geodatabase
        arcpy.env.workspace = geodatabase
        print("Environment workspace is set to: ", geodatabase)
    else:
        print("Workspace", geodatabase, "does not exist!")
        sys.exit(1)
    spatial_ref = arcpy.Describe(fcPolygon).spatialReference
    if spatial_ref.name != "GCS_North_American_1983":
        print("Coordinate system error: Spatial reference of ", fcPolygon, " should be projected as 'GCS_North_American_1983' to match the projection of the basemap.")
        arcpy.management.DefineProjection(fcPolygon, "GCS_North_American_1983")
    desc_shapefile = arcpy.Describe(fcPolygon)
    if desc_shapefile.shapeType != "Polygon":
        print("Error shapeType: ", fcPolygon, "needs to be a polygon type!")
        sys.exit(1)
    #add inputCSV to workspace
    arcpy.TableToTable_conversion(inputCSV, arcpy.env.workspace, "FloodCSV")
    #add shapefile to workspace
    arcpy.conversion.FeatureClassToGeodatabase(fcPolygon, geodatabase)  
    #join CSV to shapefile
    arcpy.management.AddJoin(fcpolygon, polyjField, flCSV, csvjField)
    #ReclassifyField() does not take inputs from a joined field, a new field must be added
    arcpy.management.AddField(fcPolygon, "n_"+damageField, "LONG")
    #new field is equal to old field divided by the normalizing field
    arcpy.management.CalculateField(fcPolygon, "n_"+damageField, !damageField!/!normField!,"PYTHON_9.3")
    #remove the join before executing ReclassifyField()
    arcpy.management.RemoveJoin(fcPolygon)
    #breaking the damage into 5 quantiles to rank the risk for each polygon
    #functions creates 2 new fields on fcPolygon: reclass_damageField_Class & reclass_damageField_Range, Class is the flod risk ranked 1-5 by damage
    arcpy.management.ReclassifyField(fcPolygon, "n_"+damageField, "QUANTILE", 5, "", "", "", "ACS", "rc_"+damageField)
    #OLS regression which yields: Adjusted R-Squared, Jarque-Bera p-value, Koenker (BP) Statistic p-value, Max Variance Inflation Factor, and Global Moran's I p-value
    #pdf report generated at geodatabase/OutRep.pdf
    arcpy.stats.ExploratoryRegression(fcPolygon, "n_"+damageField, [SVField],"","OutRep")
        
