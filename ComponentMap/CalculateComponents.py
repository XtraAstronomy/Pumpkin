"""
Python subroutine to apply PCA and RFC to extracted data
"""
import os
import tqdm
import numpy as np
from astropy.io import fits

def calc_comps(base_dir, ObsIDs, source_file, output_dir, classifier, pca, num_bins):
    """
    Calculate the number of components in each bin
    Args:
        base_dir - Ful path to cluster data
        ObsIDs - list of ObsIDs
        source_file - inputs['source_file']
        output_dir - inputs['output_dir']
        classifier - Pretrained RFC operator
        pca - Pretrained PCA operator
        num_bins - Number of regions
    """
    # For each observation ID , read in the data, apply PCA, and apply the RFC.
    Probabilities = {}
    Spectra = {}
    for obsid in ObsIDs:
        print('We are on ObsID: '+obsid)
        os.chdir(base_dir+'/'+obsid+'/repro/'+output_dir)
        # Read in Spectral Data using astropy
        chan_min = 0  # Minimum value for channel
        chan_max = 600  # Maximum value for channel
        Counts = []
        spectra_taken = []  # Keep track of all the spectra used
        # Some will be skipped because they were not created
        for spec_ct in range(num_bins):
            try:
                spec = fits.open(source_file+'_'+str(spec_ct)+'.pi')
                spec = spec[1].data
                vals = list(spec[chan_min:chan_max][:])
                channel = list(list(zip(*vals))[0])
                counts = list(list(zip(*vals))[3])
                counts_max = np.max(counts)
                counts_norm = [count/counts_max for count in counts]
                Counts.append(counts_norm)
                spectra_taken.append(spec_ct)
            except:
                pass
        # Apply PCA and Machine Learning Algo
        Perseus_Proj = pca.transform(Counts)
        Perseus_Pred = classifier.predict(Perseus_Proj)
        with open(base_dir+'/'+obsid+'/repro/'+output_dir+obsid+'_RFC.txt', 'w+') as f:
            f.write('bin components\n')
            ct = 0
            for val in Perseus_Pred:
                f.write('%i %s\n'%(spectra_taken[ct], val))
                ct += 1
        # Calculate probability for each bin (in matrix form where row == bin)
        probs = classifier.predict_proba(Perseus_Proj)
        Probabilities[obsid] = probs
        Spectra[obsid] = spectra_taken


    # We now aggregate the probabilities and select the maximum value for each
    spec_list_final = list(set(Spectra['3209']) & set(Spectra['4289']))  # Get list of spectra
    Probabilities_final = {}  # spec_num: aggregate_probabilities
    Classification_final = {}  # spec_num: class
    for ct, spec in enumerate(spec_list_final):
        prob1 = np.array(Probabilities['3209'][ct])
        prob2 = np.array(Probabilities['4289'][ct])
        agg = prob1 + prob2
        Probabilities_final[spec] = agg
        Classification_final[spec] = [np.argmax(agg), np.max(agg)]
    with open(base_dir+'/final_classification.txt', 'w+') as f1:
        f1.write('bin components percentage\n')
        ct = 0
        for key,item in Classification_final.items():
            f1.write('%i %s %s\n'%(key, item[0], item[1]))
            ct += 1
