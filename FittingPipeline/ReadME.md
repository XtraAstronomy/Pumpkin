Create profile for galaxy cluster by fitting spectra

This program will results in:
- Spectra for each region
- Temperature, Abundance, Cooling Time, Pressure, and Density Plots


In order to run this program you need the following:
1. Reprocessed Chandra ObsIDs
  example: 4636/repro/

To run the program please supply those items (and other relevant info) in an input file (see Inputs folder for examples)
and execute the following command:

`python Temperature_Profiles.py Inputs/example.i`

Region files should be in the regions sub-directory. They should be labeled by name_count
where count corresponds to their annulus number. For example, if we have two regions, ann_1 and ann_2,
then ann_2 would be the outer annulus and ann_1 would be the inner annulus.

What does the program do?

- Create extracted region pi files for each ObsID in their reprocessed (repro) folders.
- Fit normal and deprojected spectra in each annulus
- Create text files and plots of thermodynamic variables (temperature, abundance, normalization, density, pressure, cooling time)
