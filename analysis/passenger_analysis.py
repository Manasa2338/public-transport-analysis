import pandas as pd

df = pd.read_csv("data/transport_data.csv")

print("===== PASSENGER ANALYSIS =====")

# Basic statistics
print("\nTotal passengers:", df["passengers"].sum())
print("Average passengers:", round(df["passengers"].mean(), 2))
print("Maximum passengers:", df["passengers"].max())
print("Minimum passengers:", df["passengers"].min())

# Passengers by route
print("\n===== PASSENGERS BY ROUTE =====")
route_passengers = df.groupby("route_id")["passengers"].sum()
print(route_passengers)

# Passengers by source station
print("\n===== PASSENGERS BY SOURCE =====")
source_passengers = df.groupby("source")["passengers"].sum()
print(source_passengers)

# Passengers by destination station
print("\n===== PASSENGERS BY DESTINATION =====")
destination_passengers = df.groupby("destination")["passengers"].sum()
print(destination_passengers)

# Peak hour
df["hour"] = df["time"].str[:2].astype(int)

hourly_passengers = df.groupby("hour")["passengers"].sum()

print("\n===== HOURLY PASSENGERS =====")
print(hourly_passengers)

peak_hour = hourly_passengers.idxmax()

print("\nPeak hour:", peak_hour, ":00")
print("Peak passengers:", hourly_passengers.max())