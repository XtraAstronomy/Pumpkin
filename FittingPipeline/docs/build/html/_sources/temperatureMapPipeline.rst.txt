.. _temperature-map-pipeline:

Temperature Map
===============

This program will results in:

- A Weighted Voronoi Tessellation Map
- Spectra for each bin
- Temperature and Abundance Maps
- Hardness Maps


In order to run this program you need the following:

	1. Reprocessed Chandra ObsIDs --> you also need to merge them (merge\_obs)
	Fits image of region of interest created from merged Observations
	
	2. To run the program please supply those items (and other relevant info) in an input file (see Inputs folder for examples) and execute the following command:

	`python Temperature_Maps.py Inputs/example.i`





.. toctree::
   :maxdepth: 2

   tmp-fits
   tmp-plots
   tmp-bins
   tmp-wvt






