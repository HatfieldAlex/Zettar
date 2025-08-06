# ⚡ Zettar

**Turning messy grid data into actionable insights**  
Zettar is a platform that helps developers identify feasible Points of Connection (POCs) for new site projects — such as factories, renewable energy installations, or EV charging hubs — to the electricity grid. It focuses specifically on analysing other applications at each connection point, cleaning and structuring raw, inconsistent DNO data into a standardised, easy‑to‑interpret format, making it instantly valuable for site selection.


## 🌍 Why Zettar Exists
DNO application datasets are often released in messy, inconsistent formats, making it hard to understand current capacity or demand, or gauge how many projects are already in the queue. Zettar transforms this data into a clean, searchable, map‑based tool - giving developers a clear view of grid availability and enabling faster, smarter siting decisions.

## 🚀 Features
- **Location & Connection Search:** Drop a pin and choose a connection type (Primary, BSP, or GSP) to find the nearest relevant substation.  
- **Interactive Mapping:** Powered by the Google Maps API, the map-based UI makes it easy to explore potential sites visually.  
- **Up-to-date DNO Data:** Displays generation and demand application data for substations including capacity, number of applicants, and application status.


## 🛠 Data Wrangling & Processing
Zettar’s Django backend provides a set of custom management commands that can be run to:
1. Ingest raw, messy DNO datasets.  
2. Standardise naming conventions, formats, and units.  
3. Transform inconsistent source data into a clean, structured, user‑friendly format, and return to the user where required.  

Currently, only National Grid data has been processed and integrated, with support for additional DNO datasets planned.

## 📍 Geospatial Capabilities
- **PostGIS-powered spatial queries** for identifying the nearest substations to any user-selected location.  
- Geographic filtering and proximity calculations for capacity mapping.  
- Integration with Google Maps for accurate, interactive visualisation.

## 💻 Tech Stack
- **Backend:** Python, Django  
- **Frontend:** Alpine.js, Tailwind CSS  
- **Database:** PostgreSQL with PostGIS extension  
- **Data Sources:** National Grid DNO dataset (additional DNOs planned)  
- **APIs:** Google Maps  
- **Deployment:** Dockerised environment hosted on Render.com


