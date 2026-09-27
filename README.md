🚇 Web-Based Public Transport Passenger Flow and Mobility Network Analytics

A web-based analytics dashboard for exploring Chennai Metro passenger flow, station-level ridership, mobility network structure, peak-hour patterns, ticket usage, and ridership predictions.

The project uses Python, Streamlit, Pandas, NetworkX, and Scikit-learn to provide an interactive platform for analyzing Chennai Metro transportation data.

📌 Project Overview

Public transportation systems generate large amounts of passenger and operational data. Analyzing this data can help understand passenger demand, station activity, peak periods, and the structure of the transportation network.

This project develops a Web-Based Public Transport Passenger Flow and Mobility Network Analytics system using Chennai Metro data.

The application provides interactive dashboards for:

Passenger flow analysis
Station-level analysis
Metro network analysis
Peak-hour analysis
Ticket and payment-media analysis
Ridership predictions
Web usage analytics
Automated reports
Dataset exploration
🎯 Objectives

The main objectives of this project are:

Analyze passenger boarding patterns across Chennai Metro stations.
Identify stations with higher passenger activity.
Analyze passenger flow over time.
Identify peak passenger hours.
Represent metro stations as nodes in a transportation network.
Analyze network properties using graph algorithms.
Examine station characteristics and catchment-area features.
Visualize available ridership predictions.
Analyze different ticketing and payment methods.
Provide an interactive web-based dashboard for transportation analytics.
🖥️ Application Features
📊 Dashboard

The dashboard provides an overall view of the metro system, including:

Total passenger boardings
Number of stations
Number of metro lines
Number of observation days
Daily passenger flow
Hourly passenger flow
Top stations by passenger activity
Peak-hour information
🕸️ Network Analysis

Metro stations are represented as nodes in a graph.

The application calculates:

Degree Centrality
Betweenness Centrality
Closeness Centrality
Number of nodes
Number of edges
Network density
Average degree

The network visualization helps explore the structural characteristics of the metro system.

Note: The available station-flow dataset contains station-level boardings rather than individual origin-destination passenger journeys. Therefore, passenger OD routes are not directly inferred from the data.

🚉 Station Analysis

Users can select individual stations and examine:

Station passenger boardings
Daily station flow
Metro line
Phase
Station layout
Geographic coordinates
Population characteristics
Population density
Nearby POIs
Bus stops
Metro network features
Interchange information
📈 Passenger Flow Analysis

Users can filter passenger data by:

Date
Metro line
Station

The application displays:

Passenger-flow trends
Station-level passenger activity
Filtered datasets
Downloadable CSV reports
⏰ Peak Hour Analysis

The application analyzes hourly passenger boardings to identify:

Peak passenger hour
Peak passenger volume
Average hourly passenger flow
Top passenger-flow hours
Daily peak-hour patterns
🎫 Ticket Analytics

The dashboard provides analysis of different ticket and payment media, including available categories such as:

NCMC
Mobile QR
Static QR
Paper QR
Paytm QR
WhatsApp QR
PhonePe QR
Trip Cards
Tourist Cards
Tokens
Other available ticket/payment categories
🔮 Ridership Predictions

The project includes a supplied Chennai Metro ridership prediction dataset.

The dashboard displays:

Station
Line
Phase
Predicted ridership
Lower confidence bound
Upper confidence bound

The predictions are presented for analytical and visualization purposes.

🌐 Web Analytics

The application records dashboard usage information such as:

Page visits
Route-search activity when applicable

This demonstrates the use of web analytics alongside transportation analytics.

📑 Reports

The application provides downloadable reports for:

Station-level analysis
Line-level analysis
Hourly passenger flow
Network analysis
Dataset summaries

Reports can be downloaded as CSV files.

🗂️ Dataset

The project uses a supplied Chennai Metro dataset containing multiple data sources.

Main datasets
Dataset	Description
cmrl_stationflow_daily.csv	Daily passenger boardings by station
cmrl_hourly_ridership.csv	System-wide hourly passenger boardings
cmrl_ticket_mix.csv	Daily ticket/payment-media information
cmrl_system_monthly.csv	Monthly system-level passenger ridership
cmrl_station_summary.csv	Station-level benchmark statistics
chennai_metro_stations.csv	Metro station master directory
chennai_station_catchment_features.csv	Station catchment and built-environment features
chennai_metro_ridership_predictions.csv	Supplied station-level ridership predictions

Additional dataset resources may include GeoJSON files, an Excel workbook, and a starter notebook.

🧠 Graph Analytics

The project applies graph-based methods to the metro station network.

Degree Centrality

Measures the relative number of connections associated with a station.

Betweenness Centrality

Measures how frequently a station lies along shortest paths between other stations in the constructed network.

Closeness Centrality

Measures how close a station is to other stations based on shortest-path distances.

These measures help explore the structural role of stations within the constructed metro network.

🛠️ Technologies Used
Python
Streamlit
Pandas
NumPy
NetworkX
Matplotlib
Scikit-learn
SQLite
GitHub
Streamlit Community Cloud
📁 Project Structure
public_transport_analysis/
│
├── data/
│   ├── cmrl/
│   │   ├── cmrl_stationflow_daily.csv
│   │   ├── cmrl_hourly_ridership.csv
│   │   ├── cmrl_ticket_mix.csv
│   │   ├── cmrl_system_monthly.csv
│   │   ├── cmrl_station_summary.csv
│   │   ├── chennai_metro_stations.csv
│   │   ├── chennai_station_catchment_features.csv
│   │   └── chennai_metro_ridership_predictions.csv
│   │
│   └── web_analytics.db
│
├── streamlit_app.py
├── requirements.txt
└── README.md

☁️ Deployment

The application can be deployed using Streamlit Community Cloud.

Deployment process
Upload the project to GitHub.
Open Streamlit Community Cloud.
Connect the GitHub repository.
Select the main branch.
Select:
streamlit_app.py

as the main application file.

Deploy the application.
🔄 Application Workflow
Chennai Metro Dataset
        ↓
Data Loading
        ↓
Data Cleaning & Processing
        ↓
Passenger Flow Analysis
        ↓
Station & Network Analysis
        ↓
Graph Analytics
        ↓
Peak Hour Analysis
        ↓
Ticket Analytics
        ↓
Prediction Analysis
        ↓
Interactive Streamlit Dashboard
        ↓
Reports & Visualizations
