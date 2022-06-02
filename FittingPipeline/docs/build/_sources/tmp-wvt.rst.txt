.. _tmp-wvt:

WVT Algorithm
=============
This section will contain the pseudo-algorithm of my python code.

Before we are able to begin our algorithm (WVT) in earnest, we must have a decent initial guess! 

Enter Bin Accretion

Bin accretion algorithm
^^^^^^^^^^^^^^^^^^^^^^^
*Pseudocode*
.. code-block::

    While Pixels left to be assigned
	While Criteria not all met
	    Calculate pixel closest to bin centroid;
	    Calculate Adjacency;
	    Calculate Roundness;
	    Calculate Potential Signal-to-Noise;
	    if Criteria all met
		Add pixel to Bin;
		Start new bin;
		elif Signal-to-Noise too low
		    Mark pixels unassigned;
    Reassign all unassigned pixels to nearest bin;
    
Main algorithm
^^^^^^^^^^^^^^

With that out of the way we can discuss how I actually calculated the three different criteria: Adjacency, Roundness, Potential Signal-to-Noise.

1. Adjaceny: This one is simple: just check if the pixels are neighbors!
2. Roundness: Ok so now we finally need to calculate some stuff... More explicity R_{equiv} and R_{max}. R_{max} is the maximum distance from the centroid for ALL pixels in bin. R_{equiv} is a wonderfully horrendous quantity which is "the radius of a disk around the bin". Lets do a quick little derivation...

	Area_{circle} = \pi r_{circle}^2 == n\pi\frac{d_{pix}}{2}^^2 = Area_{bin}
	
Solving for $r_{circle}$ we get,
	r_{circle} = \sqrt{\frac{n}{\pi}} \ d
	
And now we can calculate the roundness parameter which describes the compactness of the bin:
	
	Roundness = \frac{R_{max}}{R_{equiv}} - 1

We generally shoot for a value of $Roundness = 0.3$.

3. Potential Signal-to-Noise: We add the pixel to the bin and then recompute the Signal-to-Noise. This needs to be less than the target Signal-to-Noise.


And now to the main event (which is not very much coding wise compared to bin accretion).

*Pseudocode*
.. code-block::
	initialization --> read in Bin Accretion Data;
	While Bins not converged
	    For bin in Bins
		Recalculate Signal-to-Noise;
		Calculate Area;
		Calculate Centroid;
		Calculate Scale Length;
	    Reassign Pixel to Closest Bin;

And again we need to define two properties: Area and Scale Length.

1. Area: Area of bin. This is basically just the area of the pixels in the bin...

	A_{bin} = (Pixel\_Length)^2*N_{pixels} 

2. Scale Length: This scale length is the KEY to the WEIGHTED part of WVT.

	\sqrt{\frac{A_{bin}}{\pi}\frac{S/N}{(S/N)_{target}}}





WVT routines
==================

.. automodule:: TemperatureMapPipeline.WVT
    :members:

