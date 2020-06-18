# grabazure-eta-prediction
Microsoft Azure Hackathon 2020 - Grab Data Science Chal

## Steps
When importing the dataset UNSELECT:
1.	trj_id
2.	avg_speed
3.	osname
4.	day
5.	month

When creating Automated ML:
1.	Select Regression 
2.	For featurization settings specify the column dtypes:
a.	Avg_bearing: numeric
b.	Day of week: categorical
c.	Is_weekday: categorical
d.	Hour: categorical
e.	Time_group: categorical
f.	Origin_avg_daily_rainfall: numeric
g.	Dest_avg_daily_rainfall: numeric
h.	Origin_lat: numeric
i.	Origin_lng: numeric
j.	Dest_lat: numeric
k.	Dest_lng: numeric
l.	Origin_region: categorical
m.	Origin_subregion: categorical
n.	Dest_region: categorical
o.	Dest_subregion: categorical
p.	Euclid_dist: numeric
3.	Select the primary metrics to be ‘normalsed root mean squared error’
4.	Validation: k-fold cross validation = 5

After it has completed, this should be the feature importance ranking, we might exclude the origin and dest region and subregions 

