#ifndef __FFT_H__
#define __FFT_H__

typedef unsigned int size_t;

void compute_vibration(double *vReal, double *vImag, unsigned short sample_size);
bool find_peak(double *vReal, size_t length, double sample_freq, double &frequency, double &magnitude);
short g_to_mercalli(float g);

#endif