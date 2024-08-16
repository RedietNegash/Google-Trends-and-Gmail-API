from pytrends.request import TrendReq
import seaborn
import pandas as pd

# Set the option to prepare for future changes
pd.set_option('future.no_silent_downcasting', True)

# for styling
seaborn.set_style("darkgrid")

# initialize a new Google Trends Request Object
pt = TrendReq(hl="en-US", tz=360)

# set the keyword & timeframe
pt.build_payload(["Python", "Java"], timeframe="all")

# get the interest over time
iot = pt.interest_over_time()
print(iot)

# plot it
print(iot.plot(figsize=(10, 6)))



# get hourly historical interest
# data = pt.get_historical_interest(
#     ["data science"], 
#     year_start=2022, month_start=1, day_start=1, hour_start=0,
#     year_end=2022, month_end=2, day_end=10, hour_end=23,
# )
# data

# ""

# inc_low_vol=True: Includes regions with lower search volumes. This ensures that you get data from places with fewer searches as well.
# inc_geo_code=True: Includes geographic codes, which provide additional location data for the regions
# """"

# Set the keyword to extract data
kw = "python"
pt.build_payload([kw], timeframe="all")

# Get the interest by country
ibr = pt.interest_by_region("COUNTRY", inc_low_vol=True, inc_geo_code=True)

# Sort the countries by interest in descending order
sorted_ibr = ibr[kw].sort_values(ascending=False)

# Print the sorted interest by country
print(sorted_ibr)




# get related topics of the keyword
rt = pt.related_topics()
related_rt=rt[kw]["top"]
print(related_rt)

# get related queries to previous keyword
rq = pt.related_queries()
related_rq=rq[kw]["top"]
print(related_rq)

# get suggested searches
print(pt.suggestions("python"))


# trending searches per region
ts = pt.trending_searches(pn="united_kingdom")
print(ts[:5])


# real-time trending searches
pt.realtime_trending_searches()