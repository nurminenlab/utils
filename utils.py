def getFilePath(windowTitle="Select binary file",filetypes=None):
    from pathlib import Path
    from tkinter import Tk
    from tkinter import filedialog

    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    binFullPath = Path(filedialog.askopenfilename(title=windowTitle,filetypes=filetypes))
    root.destroy()
    return binFullPath

def open_mat_file(filename):
    import scipy.io
    try:
        mat = scipy.io.loadmat(filename)
        return mat
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None

def get_spike_times(clusters, spike_times):
    # returns a dictionary of spike times for each cluster
    import numpy as np
    
    unique_clusters = np.unique(clusters)
    result = {}
    for cluster in unique_clusters:
        result[cluster] = spike_times[np.where(clusters==cluster)]

    return result

def extract_stimulus_times(trialsDF, stimulusDF):
    # Initialize an empty list to store the stimulus times for each trial
    stimulus_times_per_trial = []

    # Iterate over each row (trial) in the trials DataFrame
    for index, row in trialsDF.iterrows():
        # Get the start and stop times for the current trial
        start_time = row['trialstart']
        stop_time = row['trialstop']

        # Extract the stimulus times that are between the start and stop times
        stimulus_times = stimulusDF[(stimulusDF['stimstart'] >= start_time) & (stimulusDF['stimstart'] <= stop_time)]

        # Append the stimulus times for the current trial to the list
        stimulus_times_per_trial.append(stimulus_times)

    return stimulus_times_per_trial

def return_good_cluster_indices(clusters,KSlabels):
    import numpy as np
    KSlabels = KSlabels[KSlabels['KSLabel\r'] == 'good\r']
    good_clusters = KSlabels['cluster_id'].values
    good_clusters_inds = np.array([],dtype=int)
    for c in good_clusters:
        inds = np.where(clusters == c)[0]
        good_clusters_inds = np.append(good_clusters_inds,inds)

    return good_clusters_inds

def find_good_trials(vals):
    import numpy as np
    good_trials = []
    for trial in range(vals.shape[1]):
        if vals[0,trial]['trial_error'][0] == 'no_error':
            good_trials.append(trial)
    return np.array(good_trials)