<div align="center">
  <table style="margin: 0 auto; border: 1px solid #ccc;">
    <tr>
      <td align=center>
        <img src="../pages/static/pages/images/zettar_logo.svg" style="width:100%; height:auto;">
      </td>
    </tr>
  </table>
</div>

<p style="text-align: center;">
  Zettar helps developers find viable grid connection points by turning messy DNO data into clean insights using geospatial technology and up-to-date application data. Available at <a href="https://www.zettar.tech" target="_blank">www.zettar.tech</a>.
</p>

## 📷 Interface Preview  
<div align="center">
  <img src="images/zettar_full_page_screenshot.png" style="width:100%; height:auto;">
</div>


## 📘 Product Overview
Zettar is a platform that helps developers identify feasible Points of Connection (POCs) for new site projects - such as factories, renewable energy installations, or EV charging hubs - to the National Grid of Great Britain. It focuses specifically on analysing other applications at each connection point, cleaning and structuring raw, inconsistent DNO data into a standardised, easy‑to‑interpret format, making it instantly valuable for site selection.

DNO application datasets are often released in messy, inconsistent formats, making it hard to understand current capacity or demand, or gauge how many projects are already in the queue. Zettar transforms this data into a clean, searchable, map‑based tool - giving developers a clear view of grid availability and enabling faster, smarter siting decisions.

### Features

- **Location & Connection Search:** Drop a pin and choose a connection type (Primary, BSP, or GSP) to find the nearest relevant substation.  
- **Interactive Mapping:** Powered by the Google Maps API, the map-based UI makes it easy to explore potential sites visually.  
- **Up-to-date DNO Data:** Displays generation and demand application data for substations including capacity, number of applicants, and application status.



## 💻 Technology

###  Tech Stack
- **Backend:** Python, Django  
- **Frontend:** Alpine.js, Tailwind CSS  
- **Database:** PostgreSQL with PostGIS extension  
- **Data Sources:** National Grid DNO dataset (additional DNOs planned)  
- **APIs:** Google Maps  
- **Deployment:** Dockerised environment hosted on Render.com

### Geospatial Intelligence

- **PostGIS (PostgreSQL extension)**: powers spatial queries to determine proximity - e.g., locating the nearest substations to any given point - and supports spatial joins, geometry operations, and more
- **GeoDjango**: Django's geographic framework extends the ORM with support for spatial data type to enable direct storage and manipulation of geospatial data in Django models. GeoDjango integrates with libraries such as GEOS and GDAL, as well as the PostGIS Postgres extension, to enable geospatial data handling
- **Google Maps API Integration**: Delivers an intuitive, interactive visualisation layer for all spatial data, allowing users to explore infrastructure and network elements in real-world context

## 📊 Data 

### Wrangling & Processing

Zettar’s Django backend provides a set of custom management commands that can be run to:
1. Ingest raw, messy DNO datasets.  
2. Standardise naming conventions, formats, and units.  
3. Transform inconsistent source data into a clean, structured, user‑friendly format, and return to the user where required. 

###  Sources

There are 14 electricity distribution licence areas across Great Britain, operated by six groups: UK Power Networks, National Grid Electricity Distribution, SP Energy Networks, Northern Powergrid, Electricity North West, and Scottish and Southern Electricity Networks.

<div align="center" style="margin-bottom: 10px;">
  <img src="images/gb_electricity_distribution_map.jpg" style="width:100%; height:auto;">
</div>

<p>
  Each group publishes substation geolocation and application data independently. The links below reference the datasets currently used in this project. So far only National Grid data has been processed and integrated, with support for additional DNOs planned.
</p>

| Name | Description | Link |
| :---: | :---: | :---: |
| Primary Substation Locations (NGED) | Geographic locations of primary substations managed by National Grid DNOs | [View](https://connecteddata.nationalgrid.co.uk/dataset/primary-substation-location-easting-northings) |
| New Connections (NGED) | Dataset of new connection applications to National Grid DNOs | [View](https://connecteddata.nationalgrid.co.uk/dataset/new-connections)  |

###  Dataset Quality Commentary

The data is inconsistently provided in various formats, requiring separate cleaning for each dataset. While some datasets were more accessible than others, none could be integrated without significant preprocessing. Below is a summary of my thoughts on the accessibility of each dataset.

| DNO | Substation Geolocation Data Quality | Substation Application Data Quality |
| :---: | :---: | :---: |
| UK Power Networks |  Medium | Medium |
| National Grid Electricity Distribution | Medium | Medium |
| SP Energy Networks | Low | Low |
| Northern Powergrid | High | High |
| Electricity North West | High | Medium |
| Scottish and Southern Electricity Networks | Low | Low |

An illustrative case study with NGED revealed the inconsistent ways substations were labeled in the dataset. Rather than using a dedicated column for substation type, the type was often embedded within the name itself with inconsistent formatting - examples include "Primary Substation", "S/S", "S/Stn", "Power Station", "Primary", and "S Stn.". Similarly, voltage values were inconsistently presented as "kv", "kV", "Kv", or "KV". While many of these variations didn’t directly affect data accuracy, some entries were so unstructured that informed assumptions had to be made during cleaning and processing.

### Schema Diagram

<div align="center" style="margin-bottom: 10px;">
  <img src="images/db_schema_drawSQL.png" style="width:100%; height:auto;">
</div>

## 🔍 Retrospective

### Data Cleaning and Processing 

Although the dataset was relatively small, it required extensive wrangling due to inconsistent formats and numerous quirks in the source data. I initially tackled the problem using a purely functional approach, with dispatch functions directing the processing flow. This allowed me to move quickly, uncover the underlying patterns, and implement the core logic.

The method worked well for the first datasets (NGED) but proved difficult to extend when I moved on to the UKPN datasets. Even so, starting functionally was the right call - it allowed Zettar to process at least one dataset within the time available fully. Had I started with creating a sophisticated data-wrangling pipeline, perhaps based on object-oriented design, I may not have been able to complete even a single DNO, and therefore would have no prototype to demonstrate. 

In retrospect, the optimal approach would have been to begin functionally, then refactor into a unified data-wrangling system once the core logic was in place. Designing the system after gaining familiarity with the data’s quirks would have ensured it reflected its true complexity, rather than assumptions made too early. Perhaps the key lesson is to fully understand the complete family of datasets before committing to the computational processing.


### Code Style, Conventions, and Structure

While I applied coding conventions and maintained a readable structure within the Django setup, these were introduced on a case-by-case basis rather than through a unified process. This approach worked well for a medium-sized personal project and supported rapid delivery, but it also meant conventions were not entirely consistent across the repository, and some areas could benefit from restructuring.

A lightweight, repeatable process for integrating style and quality checks, such as automated linting from the outset, could have preserved the project’s pace while ensuring a coherent feel throughout. For instance, I could have made greater use of Django’s app functionality to separate concerns more cleanly.

### Testing

Testing was applied to key functions and proved valuable in catching issues early. However, broader coverage - particularly for the supporting data-processing functions - would have strengthened the project. As with code styling, a regular, built-in testing rhythm could have ensured consistency without slowing development.

## 🧭 Product Roadmap

- **Full DNO Coverage**: Currently, Zettar only integrates data from the National Grid DNO. The goal is to expand coverage across all six DNO groups in Great Britain. Each dataset is published in a different format, so this expansion will require tailored data cleaning for each group
- **Demand Side Integration**: At present, Zettar focuses on formal generation and demand applications at substations. However, incorporating informal demand indicators - such as developer interest tracked within Zettar - could enhance site selection insights. This would need to be implemented carefully to avoid creating a self-fulfilling feedback loop.
- **Get more informative description of DNO data**: Beyond inconsistent formatting, raw DNO datasets often lack clear or useful descriptions. Key information is missing or ambiguous, leading to assumptions during processing. Incorporating clarification requests directly into Zettar could make the tool more self-sufficient - helping users understand the data without needing to contact DNOs themselves, which can be time-consuming.