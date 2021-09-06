# Hourly Electric Load Forecast for PJMI - Pittsburgh, USA - For 7 Days

Datasets used - 
- [Hourly Electric Load Data](https://www.kaggle.com/robikscube/hourly-energy-consumption)
- [Hourly Temperature Data](https://www.kaggle.com/selfishgene/historical-hourly-weather-data)

## Hourly Electric Load Data
PJM Interconnection LLC (PJM) is a regional transmission organization (RTO) in the United States. It is part of the Eastern Interconnection grid operating an electric transmission system serving all or parts of Delaware, Illinois, Indiana, Kentucky, Maryland, Michigan, New Jersey, North Carolina, Ohio, Pennsylvania, Tennessee, Virginia, West Virginia, and the District of Columbia.

The hourly power consumption data comes from PJM's website and are in megawatts (MW).

The regions have changed over the years so data may only appear for certain dates per region.
## Hourly Temperature Data
The dataset contains ~5 years of high temporal resolution (hourly measurements) data of various weather attributes, such as temperature, humidity, air pressure, etc.

This data is available for 30 US and Canadian Cities, as well as 6 Israeli cities.
I've organized the data according to a common time axis for easy use.
Each attribute has it's own file and is organized such that the rows are the time axis (it's the same time axis for all files), and the columns are the different cities (it's the same city ordering for all files as well).
Additionally, for each city we also have the country, latitude and longitude information in a separate file.






For detailed explanation on how things work, check out [Nuxt.js docs](https://nuxtjs.org).
