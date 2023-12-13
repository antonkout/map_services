# Searching & Downloading Satellite Products API
Web Api to Search and Download satellite products.

### Required Python Libraries
------------------------------------------------

```
dash == 2.0.0
google-cloud-bigquery == 2.20.0
google-auth == 1.31.0
sentinelsat == 1.0.1
folium == 0.12.1
geopandas == 0.9.0
shapely == 1.7.1
landsatxplore == 0.12.1
pyproj == 2.6.1
```

### Description
------------------------------------------------
A Wep Map API  for Searching and Downloading <b>Sentinel-1</b>, <b>Sentinel-2</b>, <b>Sentinel-3</b> and <b>Landsat-8</b> products created in Dash. This script combines four different APIS in one user-friendly interface providing needed information of the searched products. 

<b>The utilized APIs are:</b>
  <li>The <b>Sentinelsat</b> that searchs and retrieves metadata of Sentinel satellite images from the Copernicus Open Access Hub. (https://sentinelsat.readthedocs.io/en/stable/)</li>
  <li>The <b>Google Cloud Storage</b> for downloading Sentinel-2 orthorectified, map-projected Level-1C images containing top-of-atmosphere reflectance data. (https://cloud.google.com/storage/docs/public-datasets/sentinel-2)</li>
  <li>The <b>Landsatxplore</b> which provides an interface to the EarthExplorer portal to search and download Landsat Collections scenes. (https://github.com/yannforget/landsatxplore)</li>
<br>
In order to download Sentinel-2 imagery from google cloud storage a key_json file is needed to be created. Detailed instructions are provided here: https://www.stitchdata.com/docs/destinations/google-bigquery/v2/connecting-google-bigquery-to-stitch. 
</br>
<br>
<p align="center">
  <img src="https://user-images.githubusercontent.com/39597223/144752813-2b9fe956-b8b7-4c58-b249-92e51f79eca9.png" width="700" height="400" >
</p>

 <br>
 This Webmap API combines in one script the <b>folium</b> utilities of creating a map enviroment drawing a user defined polygon of area of interest to search satellite products, together
 with <b>dash</b> module in order to create this API and publish it localy. 
 <br/>
 <br>
 
 ### Webmap for searching and downloading satellite imagery
------------------------------------------------
 <br>
<p align="center">
  <img src="https://user-images.githubusercontent.com/39597223/144754131-e6479ebb-7b14-4211-8453-aed331367848.gif" width="500" height="400" >
  </p>
