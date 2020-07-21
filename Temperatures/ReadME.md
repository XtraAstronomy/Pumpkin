This directory contains the code necessary to create a thermal map of a cluster given a
bin map in which each bin has the number of components necessary. This was used
to create the multi-component thermal maps of the Perseus cluster for the paper
entitled "A Novel Machine Learning Approach to Disentangle Multi-Temperature Regions in Galaxy Clusters".

This assumes that we have a few things:
1 - A bin map of the cluster labelled by number of underlying thermal components
2 - Extracted spectra for each bin region

Both of those items will have already been created if you have been following
each step as laid out in the primary README.md of the parent repository.

In order to create the temperature maps, simply run:
`python Temperature_Maps.py Perseus.i`
