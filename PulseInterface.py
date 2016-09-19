import PulseGeneration
import numpy as np


def make_pulse(sampling_rate, global_onset, global_offset, params_list):
    longest_t = []
    pulses = list()

    for params in params_list:
        if params['type'] == 'Simple':
            this_pulse, t = PulseGeneration.simple_pulse(sampling_rate, params)
        elif params['type'] == 'Noise':
            this_pulse, t = PulseGeneration.noise_pulse(sampling_rate, params)
        else:
            raise ValueError

        pulses.append(this_pulse)
        if len(t) > len(longest_t):
            longest_t = t

    pulse_matrix = np.zeros((len(pulses), len(longest_t) + (global_onset + global_offset) * sampling_rate))

    for p, pulse in enumerate(pulses):
        pulse_matrix[p][(global_onset * sampling_rate):(global_onset * sampling_rate)+len(pulse)] = pulse

    t = np.linspace(0, pulse_matrix.shape[1] / sampling_rate, pulse_matrix.shape[1])

    return pulse_matrix, t