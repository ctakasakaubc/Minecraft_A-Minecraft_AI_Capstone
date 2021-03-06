# Determine Optimal Mining Location Per Ore

## What You'll Need:

- A mine (World is Provided!)
- A pick
- 15 minutes

## 1. Load into the "Peer Testing 2" Minecraft World

## 2. Open the CodeBuilder by pressing 'c' and choose "Localhost:3000"

## 3. Copy the connect command and run it in the Minecraft chat (you must close the CodeBuilder)

## 4. Subscribe to the "Block Broken" event

## 5. Talk to "Tutorial Tom" for further instructions!

## 6. Are you done the job that "Coal Smith" gave you? If so, it's time to open the CodeBuilder by pressing 'c' in Minecraft!

## 7. Now open the CodeBuilder again and run the Python code below. You can copy and paste each chunk into a new cell

```python
# read in your updated Minecraft event data
df = update_event_data()


# let's check what kinds of blocks you broke!
print(pd.unique(df["block"]))
# remove any extra blocks you may have mined (make sure there are only 6!)
df = df[df["block"] != "stone"]
# check that it's been updated! There should only be 6
print(pd.unique(df["block"]))
print(len(pd.unique(df["block"])))


# now you can start setting up our model!
# you now need to find all 6 clusters of ore and make a simple map
k_means = KMeans(n_clusters = 6)
# only fit the data to the location data of each block broken
k_means.fit(df[["posX","posZ"]])
# only using location data ensures our model doesn't cheat
# and use block labels to sort the data!
prediction = k_means.predict(df[["posX","posZ"]])


# your model is now complete, but we want to visualize it!
x_arr = df["posX"].values
z_arr = df["posZ"].values


# finally, we can see the clusters!
plt.scatter(x_arr, z_arr, c=k_means.labels_, cmap='rainbow')
plt.show()
```

## This printed out a map of sorts that tries to tell us where each ore is located in the mine. Try to figure out which ore is marked in blue!