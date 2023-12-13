# Project Name

## Map Services

**Author: Antonios Koutroumpas**
**Contact: antonkout@gmail.com**

### Overview
This module contains two repositories which construct a webmap framework.

### Modules
**excavations_webmap:** 
Contains the creation of an interactive webmap to visualize the excavation results at the Amfissa region.
- Features:
    - Search Excavations: Allows users to search for specific excavations based on criteria such as location, time period, or excavation type
    - Retrieve Artifacts: Provides an endpoint to retrieve artifacts discovered during excavations along with detailed information.
    - Filter Data: Users can apply filters to narrow down the search results and obtain more specific information.

**rs_download_API:** 
Contains a dash API module facilitates tools to download Sentinel 1/2/3 and Landsat products.
- Features:
    - Satellite Selection: Users can choose from a variety of satellites, including Sentinel-1, Sentinel-2, Sentinel-3, and Landsat-8.
    - Time Range Selection: Specify a time range to narrow down the search for satellite products.
    - Cloudiness Control: Set the maximum acceptable cloudiness level to filter search results.
    - Product Download: Download satellite products by providing the desired product ID and output folder.

### License
This project is licensed under the [MIT License](LICENSE).