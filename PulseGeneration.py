import scipy.signal as signal
import numpy as np
import matplotlib.pyplot as plt


def square_pulse(sampling_rate, duration, frequency, duty):
    t = np.linspace(0, duration, sampling_rate * duration, endpoint=False)
    return (np.array(signal.square(2 * np.pi * frequency * t, duty=duty)) / 2) + 0.5, t


def shatter_pulse(sampling_rate, duration, frequency, duty, shatter_frequency, shatter_duty):

    if shatter_frequency < frequency:
        raise ValueError('Shatter frequency must not be lower than major frequency.')

    t = np.linspace(0, duration, sampling_rate * duration, endpoint=False)

    guide_pulse, _ = square_pulse(sampling_rate, duration, frequency, duty)
    shattered_pulse = (np.array(signal.square(2 * np.pi * shatter_frequency * t, duty=shatter_duty)) / 2) + 0.5

    return guide_pulse * shattered_pulse, t


def simple_pulse(sampling_rate, params):
    # Build main portion of pulse
    if params['fromDuty']:
        frequency = params['frequency']
        duty = params['duty']
    else:
        assert params['fromValues']
        frequency = 1.0 / (params['pulse_width'] + params['pulse_delay'])
        duty = params['pulse_width'] / (params['pulse_width'] + params['pulse_delay'])

    if params['fromLength']:
        duration = params['length']
    else:
        assert params['fromRepeats']
        if params['fromValues']:
            duration = (params['pulse_width'] + params['pulse_delay']) * params['repeats']
        else:
            assert params['fromDuty']
            duration = (1.0 / frequency) * params['repeats']

    if params['isClean']:
        pulse, t = square_pulse(sampling_rate, duration, frequency, duty)
    else:
        assert params['isShatter']
        pulse, t = shatter_pulse(sampling_rate, duration, frequency, duty, params['shatter_frequency'],
                                 params['shatter_duty'])

    # Attach onset and offset
    onset = np.zeros(sampling_rate * params['onset'])
    offset = np.zeros(sampling_rate * params['offset'])

    total_length = round(duration + params['onset'] + params['offset'], 10) # N.B. Have to round here due to floating point representation problem

    return np.hstack((onset, pulse, offset)), np.linspace(0, total_length, total_length*sampling_rate)


def multi_simple_pulse(sampling_rate, global_onset, global_offset, params_list):
    longest_t = []
    pulses = list()

    for params in params_list:
        this_pulse, t = simple_pulse(sampling_rate, params)
        pulses.append(this_pulse)
        if len(t) > len(longest_t):
            longest_t = t

    pulse_matrix = np.zeros((len(pulses), len(longest_t) + (global_onset + global_offset) * sampling_rate))

    for p, pulse in enumerate(pulses):
        pulse_matrix[p][(global_onset * sampling_rate):(global_onset * sampling_rate)+len(pulse)] = pulse

    t = np.linspace(0, pulse_matrix.shape[1] / sampling_rate, pulse_matrix.shape[1])

    return pulse_matrix, t


def noise_pulse(sampling_rate, params):
    # Build main portion of pulse
    pulse_length = int(sampling_rate / params['frequency'])
    if params['fromLength']:
        duration = params['length']
    else:
        assert params['fromRepeats']
        duration = (params['repeats'] * pulse_length) / sampling_rate

    guide_pulse = []

    seed = params['seed']
    amp_min = params['amp_min']
    amp_max = params['amp_max']

    t = np.linspace(0, duration, sampling_rate * duration)
    np.random.seed(int(params['seed']))
    while len(guide_pulse) < len(t):
        rand_param = np.random.uniform(amp_min, amp_max)
        guide_pulse = np.hstack((guide_pulse, np.ones(pulse_length) * rand_param))

    guide_pulse = guide_pulse[0:sampling_rate*duration]

    pulse = (np.array(signal.square(2 * np.pi * params['shatter_frequency'] * t, duty=guide_pulse)) / 2) + 0.5

    # Attach onset and offset
    onset = np.zeros(sampling_rate * params['onset'])
    offset = np.zeros(sampling_rate * params['offset'])

    total_length = round(duration + params['onset'] + params['offset'], 10)
    return np.hstack((onset, pulse, offset)), np.linspace(0, total_length, total_length * sampling_rate)


def multi_noise_pulse(sampling_rate, global_onset, global_offset, params_list):
    longest_t = []
    pulses = list()

    for params in params_list:
        this_pulse, t = noise_pulse(sampling_rate, params)
        pulses.append(this_pulse)
        if len(t) > len(longest_t):
            longest_t = t

    pulse_matrix = np.zeros((len(pulses), len(longest_t) + (global_onset + global_offset) * sampling_rate))

    for p, pulse in enumerate(pulses):
        pulse_matrix[p][(global_onset * sampling_rate):(global_onset * sampling_rate) + len(pulse)] = pulse

    t = np.linspace(0, pulse_matrix.shape[1] / sampling_rate, pulse_matrix.shape[1])

    return pulse_matrix, t


# params = {'fromLength': True, 'fromRepeats': False, 'frequency': 20, 'repeats': 5, 'seed': 1, 'amp_min': 0.1,
#           'amp_max': 0.9, 'shatter_frequency': 500, 'length': 1, 'onset': 0.1, 'offset': 0.1}
#
# pulse, t = noise_pulse(10000, params)
#
# plt.plot(t, pulse)
# plt.show()



