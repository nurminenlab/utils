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

def save_KS_probe_info():
    from lib import readSGLX
    import numpy as np

    try:
        # it extract the channel map and geometry from the probe file and saves at save_path
        binFullPath = getFilePath(windowTitle="Select binary ap file",
                                  filetypes=[("sGLX binary","*.bin")])    

        meta = readSGLX.readMeta(binFullPath)
        probe_info = readSGLX.KS_probe_info(meta)
        save_path = binFullPath.parent.parent.parent        
        for key in probe_info.keys():
            np.save(f"{save_path}/{key}.npy", probe_info[key])
    except:
        print('Error: could not save probe info.')
    
    return None


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

def return_good_cluster_indices(clusters,KSlabels,unit_type = 'all'):
    import numpy as np
    if unit_type == 'all':
        inds_good = np.where(KSlabels['KSLabel\r'] == 'good\r')[0]
        inds_mua = np.where(KSlabels['KSLabel\r'] == 'mua\r')[0]
        inds = np.append(inds_good,inds_mua)
        KSlabels = KSlabels.loc[inds]
    elif unit_type == 'good':
        KSlabels = KSlabels[KSlabels['KSLabel\r'] == 'good\r']
    elif unit_type == 'mua':
        KSlabels = KSlabels[KSlabels['KSLabel\r'] == 'mua\r']
    else:
        print('unit_type must be either "all", "good" or "mua"')
        return None        
        
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

def detect_blinks(pupil_diameters, threshold_factor=5):
    import numpy as np
    # Calculate the derivative of the pupil diameters    
    derivative = np.diff(pupil_diameters)

    # Calculate the standard deviation of the derivative
    std_dev = np.std(derivative)

    # Identify the indices where the absolute value of the derivative exceeds the threshold
    blink_indices = np.where(np.abs(derivative) > threshold_factor * std_dev)[0]

    return blink_indices

def replace_blinks_with_nan(pupil_diameters, blink_indices,sample_rate,mask_length=0.1):
    # Define the range around each blink to replace with NaNs
    range_around_blink = int(mask_length*sample_rate)

    # For each blink index, replace the range around it with NaNs
    for blink_index in blink_indices:
        start = max(0, blink_index - range_around_blink)
        end = min(len(pupil_diameters), blink_index + range_around_blink)
        pupil_diameters[start:end] = np.nan

    return pupil_diameters

def interpolate_nans(pupil_diameters):
    # Identify the indices of the NaN values
    nan_indices = np.where(np.isnan(pupil_diameters))[0]

    # Identify the indices of the non-NaN values
    non_nan_indices = np.where(~np.isnan(pupil_diameters))[0]

    # Interpolate the NaN values
    pupil_diameters[nan_indices] = np.interp(nan_indices, non_nan_indices, pupil_diameters[non_nan_indices])

    return pupil_diameters

def interactive_plot(pupil_diameters):
    from matplotlib.widgets import SpanSelector, Button
    
    # Function to be called when an interval is selected
    def onselect(xmin, xmax):
        # Convert the x-values to indices
        imin, imax = int(xmin), int(xmax)
        # Replace the selected interval with NaNs
        pupil_diameters[imin:imax] = np.nan

    # Function to be called when the button is pressed
    def on_button_press(event):
        plt.close(fig)
    
    fig, ax = plt.subplots()

    # Plot the pupil diameters
    ax.plot(pupil_diameters)

    # Create a SpanSelector
    span = SpanSelector(ax, onselect, 'horizontal', useblit=True,
                        props=dict(alpha=0.5, facecolor='red'))

    # Create a Button
    button_ax = plt.axes([0.8, 0.025, 0.1, 0.04])
    button = Button(button_ax, 'Done', color='lightgoldenrodyellow', hovercolor='0.975')
    button.on_clicked(on_button_press)

    plt.show()

    return pupil_diameters