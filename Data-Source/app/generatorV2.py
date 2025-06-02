import pandas as pd
import numpy  as np

# for the time stamps
from datetime import datetime

# --------------------------------------------------------------
# ToDos: add 3rd Sensor Dataset from a third partner (optional)

# --- define constants ---
fs   = 8000     # 8kHz
T_ab = 1/fs


recording_time = 10                     # in seconds [s], given
len_signal = int(recording_time * fs)   # signal length
time_ticks = np.arange(len_signal)*T_ab # normal recording

# for the DQ-Signals    (also "Sensors")
rot_amp = 1000
s1 = 0.37   # in seconds [s]: accel starts
s2 = 6.7    # in seconds [s]: decel starts
s3 = 7.7    # in seconds [s]: second decel starts

switch_duration = 0.15   # in seconds [s]
n_switch_samples = int(switch_duration/T_ab)

# general:
error_signal_probability = 1/3
peA  = 1/3  # probability that component A is broken, Partner A
peB  = 1/3  # probability that component B is broken, Partner B
peCB = 1/3  # probability that something is broken with the integration

# - helper functions -
# create ramp:
def sigmoid(n_points):
    return 1/(1 + np.exp(-np.linspace(-10, 10, n_points)))
# NOTE: other "ramp"-ups possible 

# create "step":
def add_step(signal_, t_step, fs, amp, n_switch_samples=n_switch_samples):
    signal_[int(t_step*fs):int(t_step*fs)+n_switch_samples] += amp * sigmoid(n_switch_samples)  # just add the ramp
    signal_[int(t_step*fs)+n_switch_samples:]               += amp                              # continue with reached value till end

# add some local variance
def add_var(signal_, t_start, fs, amp, n_switch_samples=n_switch_samples):
    signal_[int(t_start*fs):int(t_start*fs)+n_switch_samples] *= amp    # simple variance increase

# add a "jump?" in Sensor B instead
def add_jump(signal_, t_start, fs, amp, n_switch_samples=n_switch_samples):
    signal_[int(t_start*fs):int(t_start*fs)+n_switch_samples] += amp*np.sin(np.linspace(0, np.pi, n_switch_samples))


# --- Signal Generators ---

# generate DQ Signal:
def generate_DQ(s2_overwrite=None):
    # create placeholder for the ramps:
    motion_c_signal = np.zeros(len_signal)

    # add all "steps" 
    add_step(motion_c_signal, s1, fs,  rot_amp)
    if s2_overwrite is not None:
        add_step(motion_c_signal, s2_overwrite,   fs, -rot_amp)
        add_step(motion_c_signal, s2_overwrite+1, fs, -rot_amp)
    else:
        add_step(motion_c_signal, s2, fs, -rot_amp)
        add_step(motion_c_signal, s3, fs, -rot_amp)

    return motion_c_signal



# generate Sensor Signal A:
def generate_Sensor_A(ac=None, f_idx=None, s2_overwrite=None):
    # sensor specific parameters  
    freqs      = np.array([500, 700, 1000])    
    amp_means  = np.array([0.008, 0.006, 0.0045])
    amp_var_percent = 0.14   # how much % around the mean the amplitude is allowed to vary
                             # could be a parameter

    # generate the harmonic components:
    signal_gen = np.zeros(len_signal)       # generated signal, placeholder
    for idx_f, f_a in enumerate(zip(freqs, amp_means)):
        f = f_a[0]
        a_mean = f_a[1]

        # sample amplitude
        amp_variation = a_mean * amp_var_percent
        a = a_mean + np.random.uniform(low=-amp_variation, high=amp_variation)

        # overwrite this amplitude?
        if ac is not None and f_idx is not None:
            if f_idx == idx_f:
                a = ac
        # NOTE: extend this to raise an ERROR if only one is given

        signal_gen = signal_gen + a*np.sin(2*np.pi*f*time_ticks)
        # break

    # add some gaussian noise:
    noise_parameter = 0.3   # percentage of the half signal difference 
    noise_amp = (np.max(signal_gen) - np.min(signal_gen))/2*noise_parameter
    signal_gen = signal_gen + np.random.randn(len_signal)*noise_amp


    add_var(signal_gen, s1, fs,  8)

    if s2_overwrite is not None:
        add_var(signal_gen, s2_overwrite,   fs,  np.random.choice([6, 7, 8]))
        add_var(signal_gen, s2_overwrite+1, fs,  8)
    else:
        add_var(signal_gen, s2, fs,  np.random.choice([6, 7, 8]))
        add_var(signal_gen, s3, fs,  8)

    return signal_gen



def generate_Sensor_B(ac=None, f_idx=None, s2_overwrite=None):
    # note: since the s2 overwrite isn't implemented here it results in a break deliberate break of the causal chain
    #       it's not clear if we want this here or not

    # sensor specific parameters
    freqs      = np.array([500, 700, 1000, 2500])    
    amp_means  = np.array([0.004, 0.008, 0.006, 0.0045])
    amp_var_percent = 0.14   # how much % around the mean the amplitude is allowed to vary
                             # could be a parameter

    # generate the harmonic components:
    signal_gen = np.zeros(len_signal)       # generated signal, placeholder
    for idx_f, f_a in enumerate(zip(freqs, amp_means)):
        f = f_a[0]
        a_mean = f_a[1]

        # sample amplitude
        amp_variation = a_mean * amp_var_percent
        a = a_mean + np.random.uniform(low=-amp_variation, high=amp_variation)

        # overwrite this amplitude?
        if ac is not None and f_idx is not None:
            if f_idx == idx_f:
                a = ac
        # NOTE: extend this to raise an ERROR if only one is given

        signal_gen = signal_gen + a*np.sin(2*np.pi*f*time_ticks)
        # break

    # add some gaussian noise:
    noise_parameter = 0.3   # percentage of the half signal difference 
    noise_amp = (np.max(signal_gen) - np.min(signal_gen))/2*noise_parameter
    signal_gen = signal_gen + np.random.randn(len_signal)*noise_amp



    add_jump(signal_gen, s1, fs,  -1.3, n_switch_samples=n_switch_samples//2) 
    
    if s2_overwrite is not None:
        add_jump(signal_gen, s2_overwrite,   fs,  1.3, n_switch_samples=n_switch_samples//2)
        add_jump(signal_gen, s2_overwrite+1, fs,  1.3, n_switch_samples=n_switch_samples//2)
    else:
        add_jump(signal_gen, s2, fs,  1.3, n_switch_samples=n_switch_samples//2)
        add_jump(signal_gen, s3, fs,  1.3, n_switch_samples=n_switch_samples//2)
    
    return signal_gen



# --- create dataframe ---
def create_df(signal_sensor1, signal_sensor2, motion_c_signal):
    # create new file:
    df_gen = pd.DataFrame() # columns=['Time', 'Sensor1', 'Sensor2', 'DQ1', 'DQ2'] 
    # note: DQ are also "sensors"


    # meta-data:
    units = ['s'] + ['g']*2 + ['rpm']*2
    conv_factors = [1] + [0.00390625]*2 + [0.001]*2


    # add the individual data:
    df_gen['Time']    = datetime.now().timestamp() + time_ticks     # time starts 'now' and lasts 10s
    df_gen['Sensor1'] = signal_sensor1 #* (1/conv_factors[0])
    df_gen['Sensor2'] = signal_sensor2 #* (1/conv_factors[1])
    df_gen['DQ1']     = motion_c_signal #* (1/conv_factors[2])
    df_gen['DQ2']     = -motion_c_signal #* (1/conv_factors[3])

    # add meta-data:
    df_gen_meta = pd.DataFrame(columns=df_gen.columns)
    df_gen_meta.loc[df_gen_meta.shape[0], :] = units
    # df_gen_meta.loc[df_gen_meta.shape[0], :] = conv_factors

    # merge:
    df_gen = pd.concat([df_gen_meta, df_gen], ignore_index=True)


    ds_name = "FullDS_" + str(datetime.fromtimestamp(df_gen['Time'].values[2])).replace(':', '-').replace(' ', '-').replace('.', '-')
    return ds_name, df_gen



def generate_error_type(error_type=None):
    # create normal signal
    motion_c_signal = generate_DQ()
    signal_sensor1  = generate_Sensor_A()
    signal_sensor2  = generate_Sensor_B()

    if error_type == 0: # Component A
        signal_sensor1  = generate_Sensor_A(ac=0.013, f_idx=0, s2_overwrite=None)
        signal_sensor2  = generate_Sensor_B(ac=0.008, f_idx=0, s2_overwrite=None)
    if error_type == 1: # Component B
        signal_sensor1  = generate_Sensor_A(ac=0.001, f_idx=1, s2_overwrite=None)
        signal_sensor2  = generate_Sensor_B(ac=0.001, f_idx=1, s2_overwrite=None)
    if error_type == 2: # Integration
        # overwrite motion signal
        motion_c_signal = generate_DQ(s2_overwrite=4.2)
    # else: # return normal signal:

    return signal_sensor1, signal_sensor2, motion_c_signal

    


def generate_df(ac=None, f_idx=None, s2_overwrite=None, c_break=None, error_type=None, store_file=False):
    # check if a specific dataset is to be generated:
    if ac is not None or f_idx is not None or s2_overwrite is not None or c_break is not None:
        motion_c_signal = generate_DQ(s2_overwrite=s2_overwrite)
        if c_break:
            signal_sensor1  = generate_Sensor_A(ac=ac, f_idx=f_idx, s2_overwrite=None)
            signal_sensor2  = generate_Sensor_B(ac=ac, f_idx=f_idx, s2_overwrite=None)
        else:
            signal_sensor1  = generate_Sensor_A(ac=ac, f_idx=f_idx, s2_overwrite=s2_overwrite)
            signal_sensor2  = generate_Sensor_B(ac=ac, f_idx=f_idx, s2_overwrite=s2_overwrite)
    else:   
        # decide if a normal or anomalous dataset is to be generated
        if error_type is not None:
            signal_sensor1, signal_sensor2, motion_c_signal = generate_error_type(error_type)
        else:
            if np.random.uniform() < error_signal_probability:
                # choose type of error:
                error_type = int(np.random.choice([0,1,2], p=[peA, peB, peCB]))
            signal_sensor1, signal_sensor2, motion_c_signal = generate_error_type(error_type)
            
        

    # combine signals to dataframe:
    ds_name, df_gen = create_df(signal_sensor1, signal_sensor2, motion_c_signal)
    
    if store_file:
        df_gen.to_csv(ds_name + ".csv")

    return ds_name, df_gen, error_type
