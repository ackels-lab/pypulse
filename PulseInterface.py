from PyPulse import PulseGeneration
import numpy as np


def make_pulse(sampling_rate, global_onset, global_offset, params_list, *,invert_chan_list=[]):
    longest_t = []
    pulses = list()

    for params in params_list:
        if params['type'] == 'Simple':
            this_pulse, t = PulseGeneration.simple_pulse(sampling_rate, params)
        elif params['type'] == 'Noise':
            this_pulse, t = PulseGeneration.noise_pulse(sampling_rate, params)
        elif params['type'] == 'DummyNoise':
            this_pulse, t = PulseGeneration.dummy_noise_pulse(sampling_rate, params)
        elif params['type'] == 'RandomNoise':
            this_pulse, t = PulseGeneration.random_simple_pulse(sampling_rate, params)
        elif params['type'] == 'Plume':
            this_pulse, t = PulseGeneration.plume_pulse(sampling_rate, params)
        elif params['type'] == 'ContCorr':
            this_pulse, t = PulseGeneration.spec_time_pulse(sampling_rate, params)
        elif params['type'] == 'Anti Plume':
            this_pulse, t = PulseGeneration.anti_plume_pulse(sampling_rate, params)
        elif params['type'] == 'Binary':
            this_pulse, t = PulseGeneration.binary_pulse(sampling_rate, params)
        else:
            raise ValueError

        pulses.append(this_pulse)
        if len(t) > len(longest_t):
            longest_t = t
    
    pulse_matrix = []
    print(invert_chan_list)
    for pulse_index, this_pulse in enumerate(pulses):
        if pulse_index in invert_chan_list:
            full_pulse = np.ones(len(longest_t)+ int((global_onset + global_offset) * sampling_rate))
        else:
            full_pulse = np.zeros(len(longest_t)+ int((global_onset + global_offset) * sampling_rate))
        pulse_matrix.append(full_pulse)
    pulse_matrix = np.array(pulse_matrix)

#    pulse_matrix = np.zeros((len(pulses), len(longest_t) + int((global_onset + global_offset) * sampling_rate)))

    for p, pulse in enumerate(pulses):
        pulse_matrix[p][int(global_onset * sampling_rate):int(global_onset * sampling_rate)+len(pulse)] = pulse

    t = np.linspace(0, pulse_matrix.shape[1] / sampling_rate, pulse_matrix.shape[1])

    return pulse_matrix, t