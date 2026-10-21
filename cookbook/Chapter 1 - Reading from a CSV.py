# %%
import pandas as pd
import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns


# %%
# Reading data from a csv file
# You can read data from a CSV file using the `read_csv` function. By default, it assumes that the fields are comma-separated.

# We're going to be looking at some cyclist data from Montréal. Here's the [original page](http://donnees.ville.montreal.qc.ca/dataset/velos-comptage) (in French), but it's already included in this repository. We're using the data from 2012.

# This dataset is a list of how many people were on 7 different bike paths in Montreal, each day.

broken_df = pd.read_csv("../data/bikes.csv", encoding="ISO-8859-1")

# TODO: please load the data with the Polars library (do not forget to import Polars at the top of the script) and call it pl_broken_df
pl_broken_df = pl.read_csv("../data/bikes.csv", encoding="ISO-8859-1")

# %%
# Look at the first 3 rows
broken_df[:3]

# TODO: do the same with your polars data frame, pl_broken_df
pl_broken_df.head(3)

# %%
# You'll notice that this is totally broken! `read_csv` has a bunch of options that will let us fix that, though. Here we'll

# * change the column separator to a `;`
# * Set the encoding to `'latin1'` (the default is `'utf8'`)
# * Parse the dates in the 'Date' column
# * Tell it that our dates have the day first instead of the month first
# * Set the index to be the 'Date' column

fixed_df = pd.read_csv(
    "../data/bikes.csv",
    sep=";",
    encoding="latin1",
    parse_dates=["Date"],
    dayfirst=True,
    index_col="Date",
)
fixed_df[:3]

# TODO: do the same (or similar) with polars
# Polars has no index, so "Date" stays a normal column
pl_fixed_df = pl.read_csv(
    "../data/bikes.csv",
    separator=";",
    encoding="latin1",
).with_columns(pl.col("Date").str.to_date("%d/%m/%Y"))
pl_fixed_df.head(3)


# %%
# Selecting a column
# When you read a CSV, you get a kind of object called a `DataFrame`, which is made up of rows and columns. You get columns out of a DataFrame the same way you get elements out of a dictionary.

# Here's an example:
fixed_df["Berri 1"]

# TODO: how would you do this with a Polars data frame?
# Idiomatic Polars: select() returns a DataFrame
pl_fixed_df.select(pl.col("Berri 1"))
# Square brackets return a Series, closest to the pandas output above
pl_fixed_df["Berri 1"]


# %%
# Plotting is quite easy in Pandas
fixed_df["Berri 1"].plot()

# TODO: how would you do this with a Polars data frame?
# seaborn can't read a Polars DataFrame here (pandas 1.4.2 is too old),
# and .to_pandas() needs pyarrow, which is not in environment.yml.
# A dict of lists (a "Mapping") works, so we pass that instead.
plt.figure()
sns.lineplot(data=pl_fixed_df.to_dict(as_series=False), x="Date", y="Berri 1")

# %%
# We can also plot all the columns just as easily. We'll make it a little bigger, too.
# You can see that it's more squished together, but all the bike paths behave basically the same -- if it's a bad day for cyclists, it's a bad day everywhere.

fixed_df.plot(figsize=(15, 10))

# TODO: how would you do this with a Polars data frame? With Polars data frames you might have to use the Seaborn library and it mmight not work out of the box as with pandas.
# seaborn draws one line per group, so we reshape the table from wide to long:
# one row per (Date, bike path) instead of one column per bike path.
# The two "données non disponibles" columns are empty, so Polars read them as
# strings; after unpivot, "cyclists" becomes a string column, so we cast it back.
pl_long_df = pl_fixed_df.unpivot(
    index="Date", variable_name="bike_path", value_name="cyclists"
).with_columns(pl.col("cyclists").cast(pl.Int64))
plt.figure(figsize=(15, 10))
sns.lineplot(
    data=pl_long_df.to_dict(as_series=False), x="Date", y="cyclists", hue="bike_path"
)
