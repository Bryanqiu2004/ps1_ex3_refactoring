# %%
import pandas as pd
import polars as pl
import matplotlib.pyplot as plt


# Make the graphs a bit prettier, and bigger
plt.style.use("ggplot")
plt.rcParams["figure.figsize"] = (15, 5)

# This is necessary to show lots of columns in pandas 0.12.
# Not necessary in pandas 0.13.
pd.set_option("display.width", 5000)
pd.set_option("display.max_columns", 60)

# %%
# Let's continue with our NYC 311 service requests example.
# because of mixed types we specify dtype to prevent any errors
complaints = pd.read_csv("../data/311-service-requests.csv", dtype="unicode")

# %%
# TODO: rewrite the above using the polars library (you might have to import it above) and call the data frame pl_complaints
# Same approach as Chapter 2: only "Incident Zip" has mixed values
# (e.g. "N/A" and "77092-2016"), so we read just that column as a string
# instead of reading every column as text like dtype="unicode" does.
pl_complaints = pl.read_csv(
    "../data/311-service-requests.csv",
    schema_overrides={"Incident Zip": pl.String},
)

# %%
# 3.1 Selecting only noise complaints
# I'd like to know which borough has the most noise complaints. First, we'll take a look at the data to see what it looks like:
complaints[:5]

# %%
# TODO: rewrite the above in polars
pl_complaints.head(5)

# %%
# To get the noise complaints, we need to find the rows where the "Complaint Type" column is "Noise - Street/Sidewalk".
noise_complaints = complaints[complaints["Complaint Type"] == "Noise - Street/Sidewalk"]
noise_complaints[:3]

# %%
# TODO: rewrite the above in polars
# filter() keeps only the rows where the condition is True
pl_noise_complaints = pl_complaints.filter(
    pl.col("Complaint Type") == "Noise - Street/Sidewalk"
)
pl_noise_complaints.head(3)


# %%
# Combining more than one condition
is_noise = complaints["Complaint Type"] == "Noise - Street/Sidewalk"
in_brooklyn = complaints["Borough"] == "BROOKLYN"
complaints[is_noise & in_brooklyn][:5]

# %%
# TODO: rewrite the above using the Polars library. In polars these conditions are called Expressions.
# Check out the Polars documentation for more info.
# Expressions are only evaluated inside filter(), so they can be defined once
# and reused on any data frame with these columns. The pl_ prefix avoids
# overwriting the pandas is_noise / in_brooklyn variables above.
pl_is_noise = pl.col("Complaint Type") == "Noise - Street/Sidewalk"
pl_in_brooklyn = pl.col("Borough") == "BROOKLYN"
pl_complaints.filter(pl_is_noise & pl_in_brooklyn).head(5)


# %%
# If we just wanted a few columns:
complaints[is_noise & in_brooklyn][
    ["Complaint Type", "Borough", "Created Date", "Descriptor"]
][:10]

# %%
# TODO: rewrite the above using the polars library
(
    pl_complaints.filter(pl_is_noise & pl_in_brooklyn)
    .select(["Complaint Type", "Borough", "Created Date", "Descriptor"])
    .head(10)
)


# %%
# 3.3 So, which borough has the most noise complaints?
is_noise = complaints["Complaint Type"] == "Noise - Street/Sidewalk"
noise_complaints = complaints[is_noise]
noise_complaints["Borough"].value_counts()

# %%
# TODO: rewrite the above using the polars library
# Reuse the pl_is_noise expression defined above.
# sort=True because Polars' value_counts() is not sorted by default.
pl_noise_complaints = pl_complaints.filter(pl_is_noise)
pl_noise_complaints["Borough"].value_counts(sort=True)


# %%
# What if we wanted to divide by the total number of complaints?
noise_complaint_counts = noise_complaints["Borough"].value_counts()
complaint_counts = complaints["Borough"].value_counts()

noise_complaint_counts / complaint_counts.astype(float)

# %%
# TODO: rewrite the above using the polars library
# Polars has no index, so the two count tables cannot be divided directly
# like in pandas. Instead we join them on "Borough" and divide the columns.
# how="left" keeps every borough (like pandas, which would give NaN for a
# borough without noise complaints), and sort() matches the pandas order.
# Division in Polars always returns floats, so no astype(float) is needed.
pl_noise_complaint_counts = (
    pl_noise_complaints["Borough"].value_counts().rename({"count": "noise_count"})
)
pl_complaint_counts = (
    pl_complaints["Borough"].value_counts().rename({"count": "total_count"})
)
pl_noise_ratio = (
    pl_complaint_counts.join(pl_noise_complaint_counts, on="Borough", how="left")
    .with_columns((pl.col("noise_count") / pl.col("total_count")).alias("noise_ratio"))
    .sort("Borough")
)
pl_noise_ratio


# %%
# Plot the results
(noise_complaint_counts / complaint_counts.astype(float)).plot(kind="bar")
plt.title("Noise Complaints by Borough (Normalized)")
plt.xlabel("Borough")
plt.ylabel("Ratio of Noise Complaints to Total Complaints")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# %%
# TODO: rewrite the above using the polars library. NB: polars' plotting method is sometimes unstable. You might need to use seaborn or matplotlib for plotting.
# matplotlib accepts Polars Series directly, so no conversion is needed here.
plt.figure()
plt.bar(pl_noise_ratio["Borough"], pl_noise_ratio["noise_ratio"])
plt.title("Noise Complaints by Borough (Normalized)")
plt.xlabel("Borough")
plt.ylabel("Ratio of Noise Complaints to Total Complaints")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
