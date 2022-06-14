#include "fft.h"
#include "arduinoFFT.h"
arduinoFFT FFT = arduinoFFT(); /* Create FFT object */

#define SISM_FREQ_LOW_BOUND_Hz 2
#define SISM_FREQ_HIGH_BOUND_Hz 20
#define SISM_MAG_LOW_BOUND_G 0.0276

void compute_vibration(double *vReal, double *vImag, unsigned short sample_size)
{
    FFT.Windowing(vReal, sample_size, FFT_WIN_TYP_HANN, FFT_FORWARD); /* Weigh data */
    FFT.Compute(vReal, vImag, sample_size, FFT_FORWARD);                 /* Compute FFT */
    FFT.ComplexToMagnitude(vReal, vImag, sample_size);
}

bool find_peak(double *vReal, size_t length, double sample_freq, double &frequency, double &magnitude)
{
    bool result = false;
    double highest_mag = 0;
    double highest_freq = 0;
    for (size_t i = 0; i < length; i++)
    {
        double current_freq = (i * 1.0 * sample_freq) / length;
        if (current_freq < SISM_FREQ_LOW_BOUND_Hz || current_freq > SISM_FREQ_HIGH_BOUND_Hz)
        {
            continue;
        }
        if (vReal[i] > highest_mag && vReal[i] > SISM_MAG_LOW_BOUND_G)
        {
            highest_mag = vReal[i];
            highest_freq = current_freq;
            result = true;
        }
    }
    if (result)
    {
        frequency = highest_freq;
        magnitude = highest_mag;
    }

    return result;
}

short g_to_mercalli(float g)
{
    if (g >= SISM_MAG_LOW_BOUND_G && g < 0.0276)
    { // IV
        return 4;
    }
    else if (g >= 0.0276 && g < 0.115)
    {
        return 5;
    }
    else if (g >= 0.115 && g < 0.215)
    {
        return 6;
    }
    else if (g >= 0.215 && g < 0.401)
    {
        return 7;
    }
    else if (g >= 0.401 && g < 0.747)
    {
        return 8;
    }
    else if (g >= 0.747 && g < 1.39)
    {
        return 9;
    }
    else if (g >= 1.39)
    { // X+
        return 10;
    }
}