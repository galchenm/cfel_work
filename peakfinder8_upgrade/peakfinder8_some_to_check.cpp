//   This file is part of OnDA.
//
//   OnDA is free software: you can redistribute it and/or modify
//   it under the terms of the GNU General Public License as published by
//   the Free Software Foundation, either version 3 of the License, or
//   (at your option) any later version.
//
//   OnDA is distributed in the hope that it will be useful,
//   but WITHOUT ANY WARRANTY; without even the implied warranty of
//   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//   GNU General Public License for more details.
//
//   You should have received a copy of the GNU General Public License
//   along with OnDA.  If not, see <http://www.gnu.org/licenses/>.

#include <cstdlib>
#include <cmath>
#include <cstring>
#include <stdio.h>

#include <math.h>
#include <ctype.h>
#include <stdarg.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <fstream>
#include <time.h>
#include <bits/stdc++.h>
#include <algorithm>
#include <vector>

//#include "peakfinder8.hh"

#ifndef linux

int rint(float x)
{
  double xd = x;
  double t = ((xd) + 6755399441055744.0);
  return *((int *)(&t));
}
#endif
extern "C" {
#ifndef PEAKFINDER8_H
#define PEAKFINDER8_H

typedef struct {
public:
    long        nPeaks;
    long        nHot;
    float       peakResolution;         // Radius of 80% of peaks
    float       peakResolutionA;        // Radius of 80% of peaks
    float       peakDensity;            // Density of peaks within this 80% figure
    float       peakNpix;               // Number of pixels in peaks
    float       peakTotal;              // Total integrated intensity in peaks
    int     memoryAllocated;
    long        nPeaks_max;

    float       *peak_maxintensity;     // Maximum intensity in peak
    float       *peak_totalintensity;   // Integrated intensity in peak
    float       *peak_sigma;            // Signal-to-noise ratio of peak
    float       *peak_snr;              // Signal-to-noise ratio of peak
    float       *peak_npix;             // Number of pixels in peak
    float       *peak_com_x;            // peak center of mass x (in raw layout)
    float       *peak_com_y;            // peak center of mass y (in raw layout)
    long        *peak_com_index;        // closest pixel corresponding to peak
    float       *peak_com_x_assembled;  // peak center of mass x (in assembled layout)
    float       *peak_com_y_assembled;  // peak center of mass y (in assembled layout)
    float       *peak_com_r_assembled;  // peak center of mass r (in assembled layout)
    float       *peak_com_q;            // Scattering vector of this peak
    float       *peak_com_res;          // REsolution of this peak
} tPeakList;

void allocatePeakList(tPeakList *peak, long NpeaksMax);
void freePeakList(tPeakList peak);
#endif // PEAKFINDER8_H
void allocatePeakList(tPeakList *peak, long NpeaksMax)
{
    peak->nPeaks = 0;
    peak->nPeaks_max = NpeaksMax;
    peak->nHot = 0;
    peak->peakResolution = 0;
    peak->peakResolutionA = 0;
    peak->peakDensity = 0;
    peak->peakNpix = 0;
    peak->peakTotal = 0;

    peak->peak_maxintensity = (float *) calloc(NpeaksMax, sizeof(float));
    peak->peak_totalintensity = (float *) calloc(NpeaksMax, sizeof(float));
    peak->peak_sigma = (float *) calloc(NpeaksMax, sizeof(float));
    peak->peak_snr = (float *) calloc(NpeaksMax, sizeof(float));
    peak->peak_npix = (float *) calloc(NpeaksMax, sizeof(float));
    peak->peak_com_x = (float *) calloc(NpeaksMax, sizeof(float));
    peak->peak_com_y = (float *) calloc(NpeaksMax, sizeof(float));
    peak->peak_com_index = (long *) calloc(NpeaksMax, sizeof(long));
    peak->peak_com_x_assembled = (float *) calloc(NpeaksMax, sizeof(float));
    peak->peak_com_y_assembled = (float *) calloc(NpeaksMax, sizeof(float));
    peak->peak_com_r_assembled = (float *) calloc(NpeaksMax, sizeof(float));
    peak->peak_com_q = (float *) calloc(NpeaksMax, sizeof(float));
    peak->peak_com_res = (float *) calloc(NpeaksMax, sizeof(float));
    peak->memoryAllocated = 1;
}


void freePeakList(tPeakList peak)
{
    free(peak.peak_maxintensity);
    free(peak.peak_totalintensity);
    free(peak.peak_sigma);
    free(peak.peak_snr);
    free(peak.peak_npix);
    free(peak.peak_com_x);
    free(peak.peak_com_y);
    free(peak.peak_com_index);
    free(peak.peak_com_x_assembled);
    free(peak.peak_com_y_assembled);
    free(peak.peak_com_r_assembled);
    free(peak.peak_com_q);
    free(peak.peak_com_res);
    peak.memoryAllocated = 0;
}


struct radial_stats
{
    float *roffset;
    float *rthreshold;
    float *lthreshold;
    float *rsigma;
    int *rcount;
    int n_rad_bins;
};


struct peakfinder_intern_data
{
    char *pix_in_peak_map;
    int *infs;
    int *inss;
    int *peak_pixels;
};


struct peakfinder_peak_data
{
    int num_found_peaks;
    int *npix;
    float *com_fs;
    float *com_ss;
    int *com_index;
    float *tot_i;
    float *max_i;
    float *sigma;
    float *snr;
};


static void compute_num_radial_bins(int w, int h, float *r_map, float *max_r)
{
    int ifs, iss;
    int pidx;
    //clock_t tStart = clock();
    for ( iss=0 ; iss<h ; iss++ ) {
        for ( ifs=0 ; ifs<w ; ifs++ ) {
            pidx = iss * w + ifs;
            if ( r_map[pidx] > *max_r ) {
                *max_r = r_map[pidx];
            }
        }
    }
    //printf("Time of compute_num_radial_bins taken: %.2fs\n", (double)(clock() - tStart)/CLOCKS_PER_SEC);
}


static struct radial_stats* allocate_radial_stats(int num_rad_bins)
{
    struct radial_stats* rstats;

    rstats = (struct radial_stats *)malloc(sizeof(struct radial_stats));
    if ( rstats == NULL ) {
        return NULL;
    }

    rstats->roffset = (float *)malloc(num_rad_bins*sizeof(float));
    if ( rstats->roffset == NULL ) {
        free(rstats);
        return NULL;
    }

    rstats->rthreshold = (float *)malloc(num_rad_bins*sizeof(float));
    if ( rstats->rthreshold == NULL ) {
        free(rstats);
        free(rstats->roffset);
        return NULL;
    }

    rstats->lthreshold = (float *)malloc(num_rad_bins*sizeof(float));
    if ( rstats->lthreshold == NULL ) {
        free(rstats);
        free(rstats->rthreshold);
        free(rstats->roffset);
        return NULL;
    }

    rstats->rsigma = (float *)malloc(num_rad_bins*sizeof(float));
    if ( rstats->rsigma == NULL ) {
        free(rstats);
        free(rstats->roffset);
        free(rstats->rthreshold);
        free(rstats->lthreshold);
        return NULL;
    }

    rstats->rcount = (int *)malloc(num_rad_bins*sizeof(int));
    if ( rstats->rcount == NULL ) {
        free(rstats);
        free(rstats->roffset);
        free(rstats->rthreshold);
        free(rstats->lthreshold);
        free(rstats->rsigma);
        return NULL;
    }

    rstats->n_rad_bins = num_rad_bins;

    return rstats;
}


static void free_radial_stats(struct radial_stats *rstats)
{
    free(rstats->roffset);
    free(rstats->rthreshold);
    free(rstats->lthreshold);
    free(rstats->rsigma);
    free(rstats->rcount);
    free(rstats);
}


static void fill_radial_bins(float *data,
                             int w,
                             int h,
                             float *r_map,
                             char *mask,
                             float *rthreshold,
                             float *lthreshold,
                             float *roffset,
                             float *rsigma,
                             int *rcount)
{
    int iss, ifs;
    int pidx;

    int curr_r;
    float value;
    //clock_t tStart = clock();
    int max_num_pix = -1;

    for ( iss = 0; iss<h ; iss++ ) {
        for ( ifs = 0; ifs<w ; ifs++ ) {
            pidx = iss * w + ifs;

            if(r_map[pidx] < 0)
                continue;

            curr_r = (int)rint(r_map[pidx]);
            
            
            if ( mask[pidx] != 0 ) {
                value = data[pidx];
                if ( value < rthreshold[curr_r] && value>lthreshold[curr_r]) {
                    roffset[curr_r] += value;
                    rsigma[curr_r] += (value * value);
                    rcount[curr_r] += 1;
                }
            }
        }
    }

    //for ( iss = 0; iss<h ; iss++ ) {
    //    for ( ifs = 0; ifs<w ; ifs++ ) {
    //        pidx = iss * w + ifs;
    //
    //
    //        curr_r = (int)rint(r_map[pidx]);
    //        
    //        
    //        if ( mask[pidx] != 0 ) {
    //
    //            if ( rcount[curr_r] > max_num_pix) {
    //                max_num_pix = rcount[curr_r];
    //            }
    //        }
    //    }
    //}

    //printf("MAX NUM PIX IN BIN is %i\n", max_num_pix);


    //printf("Time fill_radial_bins taken: %.2fs\n", (double)(clock() - tStart)/CLOCKS_PER_SEC);
}

//UPT
static void fill_radial_bins_offset(float *data,
                             int maxRad,
                             int lenLinearArrayRandomInd,
                             int* LinearArrayRandomInd,
                             int* Offset1DArray,
                             int *r_map,
                             char *mask,
                             float *rthreshold,
                             float *lthreshold,
                             float *roffset,
                             float *rsigma,
                             int *rcount)
{
    int pidx;
    int curr_r;
    float value;
    for(int r=0; r<maxRad-1; r++)
    {
        for(int  j=Offset1DArray[r]; j<Offset1DArray[r+1]; j++)
        {
            pidx = LinearArrayRandomInd[j];
            if ( mask[pidx] != 0 ) 
            {
                value = data[pidx];
                if ( value < rthreshold[r] && value>lthreshold[r]) {
                    roffset[r] += value;
                    rsigma[r] += (value * value);
                    rcount[r] += 1;
                }
            }  
        }
    }
}


static void compute_radial_stats(float *rthreshold,
                                 float *lthreshold,
                                 float *roffset,
                                 float *rsigma,
                                 int *rcount,
                                 int num_rad_bins,
                                 float min_snr,
                                 float acd_threshold)
{
    int ri;
    float this_offset, this_sigma;
    //std::ofstream myfile;
    //myfile.open ("example.txt");

    //clock_t tStart = clock();
    for ( ri=0 ; ri<num_rad_bins ; ri++ ) {

        if ( rcount[ri] == 0 ) {
            roffset[ri] = 0;
            rsigma[ri] = 0;
            rthreshold[ri] = 1e9;
            lthreshold[ri] = -1e9;
        } else {
            this_offset = roffset[ri] / rcount[ri];
            this_sigma = rsigma[ri] / rcount[ri] - (this_offset * this_offset);
            if ( this_sigma >= 0 ) {
                this_sigma = sqrt(this_sigma);
            }

            //myfile << this_offset <<"\n";

            roffset[ri] = this_offset;
            rsigma[ri] = this_sigma;
            rthreshold[ri] = roffset[ri] + min_snr*rsigma[ri];
            lthreshold[ri] = roffset[ri] - min_snr*rsigma[ri];

            if ( rthreshold[ri] < acd_threshold ) {
                rthreshold[ri] = acd_threshold;
            }
        }
    }
    //myfile.close();
    //printf("Time compute_radial_stats taken: %.2fs\n", (double)(clock() - tStart)/CLOCKS_PER_SEC);

}


static struct radial_stats *compute_radial_bins(float *data,
                                                char *mask,
                                                int num_pix,
                                                float *r_map,
                                                int iterations,
                                                float min_snr,
                                                float acd_threshold,
                                                int num_pix_fs,
                                                int num_pix_ss)
{
    float max_r;
    int it_counter;
    int i;
    int num_rad_bins;
    struct radial_stats *rstats;

    max_r = -1e9;
    //clock_t tStart = clock();

    compute_num_radial_bins(num_pix_fs, num_pix_ss, r_map, &max_r);

    num_rad_bins = (int)ceil(max_r) + 1;

    // Allocate and zero arrays
    rstats = allocate_radial_stats(num_rad_bins);
    if ( rstats == NULL ) {
        return NULL;
    }

    for ( i=0; i<num_rad_bins; i++ ) {
        rstats->rthreshold[i] = 1e9;
        rstats->lthreshold[i] = -1e9;
      }

    // Compute sigma and average of data values at each radius
    // From this, compute the ADC threshold to be applied at each radius
    // Iterate a few times to reduce the effect of positive outliers (ie: peaks)
    for ( it_counter=0 ; it_counter<iterations ; it_counter++ ) {

        for ( i=0; i<num_rad_bins; i++ ) {
            rstats->roffset[i] = 0;
            rstats->rsigma[i] = 0;
            rstats->rcount[i] = 0;
        }

        fill_radial_bins(data,
                         num_pix_fs,
                         num_pix_ss,
                         r_map,
                         mask,
                         rstats->rthreshold,
                         rstats->lthreshold,
                         rstats->roffset,
                         rstats->rsigma,
                         rstats->rcount);



        compute_radial_stats(rstats->rthreshold,
                             rstats->lthreshold,
                             rstats->roffset,
                             rstats->rsigma,
                             rstats->rcount,
                             num_rad_bins,
                             min_snr,
                             acd_threshold);

    }
    //printf("Time compute_radial_bins taken: %.2fs\n", (double)(clock() - tStart)/CLOCKS_PER_SEC);
    
    return rstats;
}


//UPT
static struct radial_stats *compute_radial_bins_offset(float *data,
                                                char *mask,
                                                int num_pix,
                                                int *r_map,
                                                int iterations,
                                                float min_snr,
                                                float acd_threshold,
                                                int num_pix_fs,
                                                int num_pix_ss,
                                                int maxRad,
                                                int lenLinearArrayRandomInd,
                                                int* LinearArrayRandomInd,
                                                int* Offset1DArray)
{
    
    int it_counter;
    int i;
    int num_rad_bins;
    struct radial_stats *rstats;

    //clock_t tStart = clock();


    num_rad_bins = maxRad +1;
    


    // Allocate and zero arrays
    rstats = allocate_radial_stats(num_rad_bins);
    if ( rstats == NULL ) {
        return NULL;
    }

    for ( i=0; i<num_rad_bins; i++ ) {
        rstats->rthreshold[i] = 1e9;
        rstats->lthreshold[i] = -1e9;
      }

    // Compute sigma and average of data values at each radius
    // From this, compute the ADC threshold to be applied at each radius
    // Iterate a few times to reduce the effect of positive outliers (ie: peaks)
    for ( it_counter=0 ; it_counter<iterations ; it_counter++ ) {

        for ( i=0; i<num_rad_bins; i++ ) {
            rstats->roffset[i] = 0;
            rstats->rsigma[i] = 0;
            rstats->rcount[i] = 0;
        }

        fill_radial_bins_offset(data,
                                maxRad,
                                lenLinearArrayRandomInd,
                                LinearArrayRandomInd,
                                Offset1DArray,
                                r_map,
                                mask,
                                rstats->rthreshold,
                                rstats->lthreshold,
                                rstats->roffset,
                                rstats->rsigma,
                                rstats->rcount);

        

        compute_radial_stats(rstats->rthreshold,
                             rstats->lthreshold,
                             rstats->roffset,
                             rstats->rsigma,
                             rstats->rcount,
                             num_rad_bins,
                             min_snr,
                             acd_threshold);

    }
    //printf("Time compute_radial_bins_offset taken: %.2fs\n", (double)(clock() - tStart)/CLOCKS_PER_SEC);
    
    return rstats;
}


//UPT2 MEDIAN

// Function for calculating mean 
float findMean(float *a, int n) 
{ 
    int sum = 0; 
    for (int i = 0; i < n; i++) 
        sum += a[i]; 
    if(n!=0)
      {
        return (float)sum / (float)n;
      }
      else
      {
        return 0;
      }
} 

// Function for calculating median 
float findMedian(float *a, int n) 
{ 
    // First we sort the array 
    std::sort(a, a + n);
    // check for even case 
    if (n % 2 != 0) 
        return (float)a[n / 2]; 
  
    return (float)(a[(n - 1) / 2] + a[n / 2]) / 2.0; 
} 

// Function for calculating variance 
float variance(float *a, int n) 
{ 
    // Compute mean (average of elements)
    float mean =  findMean(a, n);
  
    // Compute sum squared  
    // differences with mean. 
    float sqDiff = 0; 
    for (int i = 0; i < n; i++)  
        sqDiff += (a[i] - mean) *  
                  (a[i] - mean); 
    return sqDiff / n; 
} 
  
float standardDeviation(float *arr, int n) 
{ 
    
    return sqrt(variance(arr, n)); 
}

float sigmaMAD(const std::vector<float>& arr, std::vector<float>& tmpDefect, float medianValue) 
{   
    float k = 1.48;
    //float lenDataArrRb = n * sizeof(float);
    //float* DataArrR = (float*) malloc(lenDataArrRb);
    //memset(DataArrR, 0, lenDataArrRb);

    //std::vector<float> DataArrR(n);
    tmpDefect.resize(arr.size());


    for(int i=0;i<arr.size();i++)
    {
        tmpDefect[i] = abs(arr[i] - medianValue);

    }
    std::nth_element(tmpDefect.begin(), tmpDefect.begin() + tmpDefect.size()/2, tmpDefect.end());
    float mad = tmpDefect[tmpDefect.size()/2];
    
    //free (DataArrR);
    return k*mad;
}

static struct radial_stats *compute_radial_bins_offset_median(float *data,
                                                char *mask,
                                                int *r_map,
                                                float min_snr,
                                                float acd_threshold,
                                                int maxRad,
                                                int lenLinearArrayRandomInd,
                                                int* LinearArrayRandomInd,
                                                int* Offset1DArray)
{
    
    int it_counter;
    int i;
    int num_rad_bins;
    struct radial_stats *rstats;

    num_rad_bins = maxRad +1;
    
    // Allocate and zero arrays
    rstats = allocate_radial_stats(num_rad_bins);
    if ( rstats == NULL ) {
        return NULL;
    }



    // Compute sigma and medain of data values at each radius
    // From this, compute the ADC threshold to be applied at each radius
    // Iterate a few times to reduce the effect of positive outliers (ie: peaks)
    int pidx;

    for ( i=0; i<num_rad_bins; i++ ) {
        rstats->rthreshold[i] = 1e9;
        rstats->lthreshold[i] = -1e9;
        rstats->roffset[i] = 0;
        rstats->rsigma[i] = 0;
        rstats->rcount[i] = 0;
      }

    std::vector<float> tmpDefect;
    std::vector<float> shellData;

    for(int r=0; r<maxRad-1; r++)
    {

      int lenShellData = Offset1DArray[r+1] - Offset1DArray[r];
      shellData.resize(lenShellData);
      
      if(lenShellData == 0){
        continue;
      }

      int validDataCount = 0;


      for(int  j=Offset1DArray[r]; j<Offset1DArray[r+1]; j++)
      {
          pidx = LinearArrayRandomInd[j];
          if ( mask[pidx] != 0 ) 
          {
            shellData[validDataCount] = data[pidx];
            validDataCount++;
          }  
      }

      shellData.resize(validDataCount);

      std::nth_element(shellData.begin(), shellData.begin() + validDataCount/2, shellData.end());
      float shellMedian  = shellData[validDataCount/2];
      rstats->roffset[r] = shellMedian;
      rstats->rsigma[r] = sigmaMAD(shellData, tmpDefect, shellMedian);

      rstats->rcount[r] = validDataCount;
      rstats->rthreshold[r] = rstats->roffset[r] + min_snr*rstats->rsigma[r];
      rstats->lthreshold[r] = rstats->roffset[r] - min_snr*rstats->rsigma[r];

      if ( rstats->rthreshold[r] < acd_threshold ) {
          rstats->rthreshold[r] = acd_threshold;
      }
    }

    return rstats;
}

////////////


struct peakfinder_peak_data *allocate_peak_data(int max_num_peaks)
{
    struct peakfinder_peak_data *pkdata;

    pkdata = (struct peakfinder_peak_data*)malloc(sizeof(struct peakfinder_peak_data));
    if ( pkdata == NULL ) {
        return NULL;
    }

    pkdata->npix = (int *)malloc(max_num_peaks*sizeof(int));
    if ( pkdata->npix == NULL ) {
        free(pkdata);
        free(pkdata->npix);
        return NULL;
    }

    pkdata->com_fs = (float *)malloc(max_num_peaks*sizeof(float));
    if ( pkdata->com_fs == NULL ) {
        free(pkdata->npix);
        free(pkdata);
        return NULL;
    }

    pkdata->com_ss = (float *)malloc(max_num_peaks*sizeof(float));
    if ( pkdata->com_ss == NULL ) {
        free(pkdata->npix);
        free(pkdata->com_fs);
        free(pkdata);
        return NULL;
    }

    pkdata->com_index = (int *)malloc(max_num_peaks*sizeof(int));
    if ( pkdata->com_ss == NULL ) {
        free(pkdata->npix);
        free(pkdata->com_fs);
        free(pkdata->com_ss);
        free(pkdata);
        return NULL;
    }

    pkdata->tot_i = (float *)malloc(max_num_peaks*sizeof(float));
    if ( pkdata->tot_i == NULL ) {
        free(pkdata->npix);
        free(pkdata->com_fs);
        free(pkdata->com_ss);
        free(pkdata->com_index);
        free(pkdata);
        return NULL;
    }

    pkdata->max_i = (float *)malloc(max_num_peaks*sizeof(float));
    if ( pkdata->max_i == NULL ) {
        free(pkdata->npix);
        free(pkdata->com_fs);
        free(pkdata->com_ss);
        free(pkdata->com_index);
        free(pkdata->tot_i);
        free(pkdata);
        return NULL;
    }

    pkdata->sigma = (float *)malloc(max_num_peaks*sizeof(float));
    if ( pkdata->sigma == NULL ) {
        free(pkdata->npix);
        free(pkdata->com_fs);
        free(pkdata->com_ss);
        free(pkdata->com_index);
        free(pkdata->tot_i);
        free(pkdata->max_i);
        free(pkdata);
        return NULL;
    }

    pkdata->snr = (float *)malloc(max_num_peaks*sizeof(float));
    if ( pkdata->snr == NULL ) {
        free(pkdata->npix);
        free(pkdata->com_fs);
        free(pkdata->com_ss);
        free(pkdata->com_index);
        free(pkdata->tot_i);
        free(pkdata->max_i);
        free(pkdata->sigma);
        free(pkdata);
        return NULL;
    }

    return pkdata;
}


static void free_peak_data(struct peakfinder_peak_data *pkdata) {
    free(pkdata->npix);
    free(pkdata->com_fs);
    free(pkdata->com_ss);
    free(pkdata->com_index);
    free(pkdata->tot_i);
    free(pkdata->max_i);
    free(pkdata->sigma);
    free(pkdata->snr);
    free(pkdata);
}


static struct peakfinder_intern_data *allocate_peakfinder_intern_data(int data_size,
                                                                      int max_pix_count)
{

    struct peakfinder_intern_data *intern_data;

    intern_data = (struct peakfinder_intern_data *)malloc(sizeof(struct peakfinder_intern_data));
    if ( intern_data == NULL ) {
        return NULL;
    }

    intern_data->pix_in_peak_map =(char *)calloc(data_size, sizeof(char));
    if ( intern_data->pix_in_peak_map == NULL ) {
        free(intern_data);
        return NULL;
    }

    intern_data->infs =(int *)calloc(data_size, sizeof(int));
    if ( intern_data->infs == NULL ) {
        free(intern_data->pix_in_peak_map);
        free(intern_data);
        return NULL;
    }

    intern_data->inss =(int *)calloc(data_size, sizeof(int));
    if ( intern_data->inss == NULL ) {
        free(intern_data->pix_in_peak_map);
        free(intern_data->infs);
        free(intern_data);
        return NULL;
    }

    intern_data->peak_pixels =(int *)calloc(max_pix_count, sizeof(int));
    if ( intern_data->peak_pixels == NULL ) {
        free(intern_data->pix_in_peak_map);
        free(intern_data->infs);
        free(intern_data->inss);
        free(intern_data);
        return NULL;
    }

    return intern_data;
}


static void free_peakfinder_intern_data(struct peakfinder_intern_data *pfid)
{
    free(pfid->peak_pixels);
    free(pfid->pix_in_peak_map);
    free(pfid->infs);
    free(pfid->inss);
    free(pfid);
}



static void peak_search(int p,
                        struct peakfinder_intern_data *pfinter,
                        float *copy, char *mask, float *r_map,
                        float *rthreshold, float *roffset,
                        int *num_pix_in_peak, int asic_size_fs,
                        int asic_size_ss, int aifs, int aiss,
                        int num_pix_fs, float *sum_com_fs,
                        float *sum_com_ss, float *sum_i, int max_pix_count)
{

    int k, pi;
    int curr_radius;
    float curr_threshold;
    int curr_fs;
    int curr_ss;
    float curr_i;

    int search_fs[9] = { 0, -1, 0, 1, -1, 1, -1, 0, 1 };
    int search_ss[9] = { 0, -1, -1, -1, 0, 0, 1, 1, 1 };
    int search_n = 9;
    //clock_t tStart = clock();
    // Loop through search pattern
    for ( k=0; k<search_n; k++ ) {

        if ( (pfinter->infs[p] + search_fs[k]) < 0 ) continue;
        if ( (pfinter->infs[p] + search_fs[k]) >= asic_size_fs ) continue;
        if ( (pfinter->inss[p] + search_ss[k]) < 0 ) continue;
        if ( (pfinter->inss[p] + search_ss[k]) >= asic_size_ss ) continue;

        // Neighbour point in big array
        curr_fs = pfinter->infs[p] + search_fs[k] + aifs * asic_size_fs;
        curr_ss = pfinter->inss[p] + search_ss[k] + aiss * asic_size_ss;
        pi = curr_fs + curr_ss * num_pix_fs;

        curr_radius = (int)rint(r_map[pi]);
        curr_threshold = rthreshold[curr_radius];

        // Above threshold?
        if ( copy[pi] > curr_threshold
          && pfinter->pix_in_peak_map[pi] == 0
          && mask[pi] != 0 ) {

            curr_i = copy[pi] - roffset[curr_radius];
            *sum_i += curr_i;
            *sum_com_fs += curr_i * ((float)curr_fs);  // for center of mass x
            *sum_com_ss += curr_i * ((float)curr_ss);  // for center of mass y

            pfinter->inss[*num_pix_in_peak] = pfinter->inss[p] + search_ss[k];
            pfinter->infs[*num_pix_in_peak] = pfinter->infs[p] + search_fs[k];
            pfinter->pix_in_peak_map[pi] = 1;
            if ( *num_pix_in_peak < max_pix_count ) {
                  pfinter->peak_pixels[*num_pix_in_peak] = pi;
            }
            *num_pix_in_peak = *num_pix_in_peak + 1;
        }
    }
    //printf("Time peak_search taken: %.2fs\n", (double)(clock() - tStart)/CLOCKS_PER_SEC);
    
}

//UPT
static void peak_search_offset(int p,
                        struct peakfinder_intern_data *pfinter,
                        float *copy, char *mask, int *r_map,
                        float *rthreshold, float *roffset,
                        int *num_pix_in_peak, int asic_size_fs,
                        int asic_size_ss, int aifs, int aiss,
                        int num_pix_fs, float *sum_com_fs,
                        float *sum_com_ss, float *sum_i, int max_pix_count)
{

    int k, pi;
    int curr_radius;
    float curr_threshold;
    int curr_fs;
    int curr_ss;
    float curr_i;

    int search_fs[9] = { 0, -1, 0, 1, -1, 1, -1, 0, 1 };
    int search_ss[9] = { 0, -1, -1, -1, 0, 0, 1, 1, 1 };
    int search_n = 9;
    //clock_t tStart = clock();
    // Loop through search pattern
    for ( k=0; k<search_n; k++ ) {

        if ( (pfinter->infs[p] + search_fs[k]) < 0 ) continue;
        if ( (pfinter->infs[p] + search_fs[k]) >= asic_size_fs ) continue;
        if ( (pfinter->inss[p] + search_ss[k]) < 0 ) continue;
        if ( (pfinter->inss[p] + search_ss[k]) >= asic_size_ss ) continue;

        // Neighbour point in big array
        curr_fs = pfinter->infs[p] + search_fs[k] + aifs * asic_size_fs;
        curr_ss = pfinter->inss[p] + search_ss[k] + aiss * asic_size_ss;
        pi = curr_fs + curr_ss * num_pix_fs;

        curr_radius = r_map[pi];
        curr_threshold = rthreshold[curr_radius];

        // Above threshold?
        if ( copy[pi] > curr_threshold
          && pfinter->pix_in_peak_map[pi] == 0
          && mask[pi] != 0 ) {

            curr_i = copy[pi] - roffset[curr_radius];
            *sum_i += curr_i;
            *sum_com_fs += curr_i * ((float)curr_fs);  // for center of mass x
            *sum_com_ss += curr_i * ((float)curr_ss);  // for center of mass y

            pfinter->inss[*num_pix_in_peak] = pfinter->inss[p] + search_ss[k];
            pfinter->infs[*num_pix_in_peak] = pfinter->infs[p] + search_fs[k];
            pfinter->pix_in_peak_map[pi] = 1;
            if ( *num_pix_in_peak < max_pix_count ) {
                  pfinter->peak_pixels[*num_pix_in_peak] = pi;
            }
            *num_pix_in_peak = *num_pix_in_peak + 1;
        }
    }
    //printf("Time peak_search taken: %.2fs\n", (double)(clock() - tStart)/CLOCKS_PER_SEC);
    
}


static void search_in_ring(int ring_width, int com_fs_int, int com_ss_int,
                           float *copy, float *r_map,
                           float *rthreshold, float *roffset,
                           char *pix_in_peak_map, char *mask, int asic_size_fs,
                           int asic_size_ss, int aifs, int aiss,
                           int num_pix_fs,float *local_sigma, float *local_offset,
                           float *background_max_i, int com_idx,
                           int local_bg_radius)
{
    int ssj, fsi;
    float pix_radius;
    int curr_fs, curr_ss;
    int pi;
    int curr_radius;
    float curr_threshold;
    float curr_i;

    int np_sigma;
    int np_counted;
    int local_radius;

    float sum_i;
    float sum_i_squared;

    //ring_width = 2 * local_bg_radius; //what's the reason to reset at the beginning input parameter???

    sum_i = 0;
    sum_i_squared = 0;
    np_sigma = 0;
    np_counted = 0;
    local_radius = 0;
    
    //clock_t tStart = clock();
    for ( ssj = -ring_width ; ssj<ring_width ; ssj++ ) {
        for ( fsi = -ring_width ; fsi<ring_width ; fsi++ ) {

            // Within-ASIC check
            if ( (com_fs_int + fsi) < 0 ) continue;
            if ( (com_fs_int + fsi) >= asic_size_fs ) continue;
            if ( (com_ss_int + ssj) < 0 ) continue;
            if ( (com_ss_int + ssj) >= asic_size_ss )
            continue;

            // Within outer ring check
            pix_radius = sqrt(fsi * fsi + ssj * ssj);
            if ( pix_radius>ring_width ) continue;

            // Position of this point in data stream
            curr_fs = com_fs_int + fsi + aifs * asic_size_fs;
            curr_ss = com_ss_int + ssj + aiss * asic_size_ss;
            pi = curr_fs + curr_ss * num_pix_fs;

            curr_radius = (int)rint(r_map[pi]);
            curr_threshold = rthreshold[curr_radius];

            // Intensity above background ??? just intensity?
            curr_i = copy[pi];

            // Keep track of value and value-squared for offset and sigma calculation
            if ( curr_i < curr_threshold && pix_in_peak_map[pi] == 0 && mask[pi] != 0 ) {

                np_sigma++;
                sum_i += curr_i;
                sum_i_squared += (curr_i * curr_i);

                if ( curr_i > *background_max_i ) {
                    *background_max_i = curr_i;
                }
            }
            np_counted += 1;
        }
    }

    // Calculate local background and standard deviation
     if ( np_sigma != 0 ) {
        *local_offset = sum_i / np_sigma;
        *local_sigma = sum_i_squared / np_sigma - (*local_offset * *local_offset);
        if (*local_sigma >= 0) {
            *local_sigma = sqrt(*local_sigma);
        } else {
            *local_sigma = 0.01;
        }
     } else {
        local_radius = (int)rint(r_map[(int)rint(com_idx)]);
        *local_offset = roffset[local_radius];
        *local_sigma = 0.01;
    }
    //printf("Time search_in_ring taken: %.2fs\n", (double)(clock() - tStart)/CLOCKS_PER_SEC);
}

//UPT
static void search_in_ring_offset(int ring_width, int com_fs_int, int com_ss_int,
                           float *copy, int *r_map,
                           float *rthreshold, float *roffset,
                           char *pix_in_peak_map, char *mask, int asic_size_fs,
                           int asic_size_ss, int aifs, int aiss,
                           int num_pix_fs,float *local_sigma, float *local_offset,
                           float *background_max_i, int com_idx,
                           int local_bg_radius)
{
    int ssj, fsi;
    float pix_radius;
    int curr_fs, curr_ss;
    int pi;
    int curr_radius;
    float curr_threshold;
    float curr_i;

    int np_sigma;
    int np_counted;
    int local_radius;

    float sum_i;
    float sum_i_squared;

    ring_width = 2 * local_bg_radius;

    sum_i = 0;
    sum_i_squared = 0;
    np_sigma = 0;
    np_counted = 0;
    local_radius = 0;
    
    //clock_t tStart = clock();
    for ( ssj = -ring_width ; ssj<ring_width ; ssj++ ) {
        for ( fsi = -ring_width ; fsi<ring_width ; fsi++ ) {

            // Within-ASIC check
            if ( (com_fs_int + fsi) < 0 ) continue;
            if ( (com_fs_int + fsi) >= asic_size_fs ) continue;
            if ( (com_ss_int + ssj) < 0 ) continue;
            if ( (com_ss_int + ssj) >= asic_size_ss )
            continue;

            // Within outer ring check
            pix_radius = sqrt(fsi * fsi + ssj * ssj);
            if ( pix_radius>ring_width ) continue;

            // Position of this point in data stream
            curr_fs = com_fs_int + fsi + aifs * asic_size_fs;
            curr_ss = com_ss_int + ssj + aiss * asic_size_ss;
            pi = curr_fs + curr_ss * num_pix_fs;

            curr_radius = r_map[pi];
            curr_threshold = rthreshold[curr_radius];

            // Intensity above background ??? just intensity?
            curr_i = copy[pi];

            // Keep track of value and value-squared for offset and sigma calculation
            if ( curr_i < curr_threshold && pix_in_peak_map[pi] == 0 && mask[pi] != 0 ) {

                np_sigma++;
                sum_i += curr_i;
                sum_i_squared += (curr_i * curr_i);

                if ( curr_i > *background_max_i ) {
                    *background_max_i = curr_i;
                }
            }
            np_counted += 1;
        }
    }

    // Calculate local background and standard deviation
     if ( np_sigma != 0 ) {
        *local_offset = sum_i / np_sigma;
        *local_sigma = sum_i_squared / np_sigma - (*local_offset * *local_offset);
        if (*local_sigma >= 0) {
            *local_sigma = sqrt(*local_sigma);
        } else {
            *local_sigma = 0.01;
        }
     } else {
        local_radius = r_map[(int)rint(com_idx)];
        *local_offset = roffset[local_radius];
        *local_sigma = 0.01;
    }
    //printf("Time search_in_ring taken: %.2fs\n", (double)(clock() - tStart)/CLOCKS_PER_SEC);
}


static void process_panel(int asic_size_fs, int asic_size_ss, int num_pix_fs,
                          int aiss, int aifs, float *rthreshold,
                          float *lthreshold, float *roffset, int *peak_count,
                          float *copy, struct peakfinder_intern_data *pfinter,
                          float *r_map, char *mask, int *npix, float *com_fs,
                          float *com_ss, int *com_index, float *tot_i,
                          float *max_i, float *sigma, float *snr,
                          int min_pix_count, int max_pix_count,
                          int local_bg_radius, float min_snr, int max_n_peaks)
{
    int pxss, pxfs;
    int num_pix_in_peak;
    //clock_t tStart = clock();

    // Loop over pixels within a module
    for ( pxss=1 ; pxss<asic_size_ss-1 ; pxss++ ) {
        for ( pxfs=1 ; pxfs<asic_size_fs-1 ; pxfs++ ) {

            float curr_thresh;
            int pxidx;
            int curr_rad;

            pxidx = (pxss + aiss * asic_size_ss) * num_pix_fs +
            pxfs + aifs * asic_size_fs;

            curr_rad = (int)rint(r_map[pxidx]);
            curr_thresh = rthreshold[curr_rad];

            if ( copy[pxidx] > curr_thresh
              && pfinter->pix_in_peak_map[pxidx] == 0
              && mask[pxidx] != 0 ) {   //??? not sure if needed

                // This might be the start of a new peak - start searching
                float sum_com_fs, sum_com_ss;
                float sum_i;
                float peak_com_fs, peak_com_ss;
                float peak_com_fs_int, peak_com_ss_int;
                float peak_tot_i, pk_tot_i_raw;
                float peak_max_i, pk_max_i_raw;
                float peak_snr;
                float local_sigma, local_offset;
                float background_max_i;
                int lt_num_pix_in_pk;
                int ring_width;
                int peak_idx;
                int com_idx;
                int p;

                pfinter->infs[0] = pxfs;
                pfinter->inss[0] = pxss;
                pfinter->peak_pixels[0] = pxidx;
                num_pix_in_peak = 0; //y 1;

                sum_i = 0;
                sum_com_fs = 0;
                sum_com_ss = 0;

                // Keep looping until the pixel count within this peak does not change
                do {
                    lt_num_pix_in_pk = num_pix_in_peak;

                    // Loop through points known to be within this peak
                    for ( p=0; p<=num_pix_in_peak; p++ ) { //changed from 1 to 0 by O.Y.
                        peak_search(p,
                                    pfinter, copy, mask,
                                    r_map,
                                    rthreshold,
                                    roffset,
                                    &num_pix_in_peak,
                                    asic_size_fs,
                                    asic_size_ss,
                                    aifs, aiss,
                                    num_pix_fs,
                                    &sum_com_fs,
                                    &sum_com_ss,
                                    &sum_i,
                                    max_pix_count);
                    }

                } while ( lt_num_pix_in_pk != num_pix_in_peak );

                // Too many or too few pixels means ignore this 'peak'; move on now
                if ( num_pix_in_peak < min_pix_count || num_pix_in_peak > max_pix_count ) continue;

                // If for some reason sum_i is 0 - it's better to skip
                if ( fabs(sum_i) < 1e-10 ) continue;

                // Calculate center of mass for this peak from initial peak search
                peak_com_fs = sum_com_fs / fabs(sum_i);
                peak_com_ss = sum_com_ss / fabs(sum_i);

                com_idx = (int)rint(peak_com_fs) + (int)rint(peak_com_ss) * num_pix_fs;

                peak_com_fs_int = (int)rint(peak_com_fs) - aifs * asic_size_fs;
                peak_com_ss_int = (int)rint(peak_com_ss) - aiss * asic_size_ss;

                // Calculate the local signal-to-noise ratio and local background in an annulus around
                // this peak (excluding pixels which look like they might be part of another peak)
                local_sigma = 0.0;
                local_offset = 0.0;
                background_max_i = 0.0;

                ring_width = 2 * local_bg_radius;

                search_in_ring(ring_width, peak_com_fs_int,
                               peak_com_ss_int,
                               copy, r_map, rthreshold,
                               roffset,
                               pfinter->pix_in_peak_map,
                               mask, asic_size_fs,
                               asic_size_ss,
                               aifs, aiss,
                               num_pix_fs,
                               &local_sigma,
                               &local_offset,
                               &background_max_i,
                               com_idx, local_bg_radius);

                // Re-integrate (and re-centroid) peak using local background estimates
                peak_tot_i = 0;
                pk_tot_i_raw = 0;
                peak_max_i = 0;
                pk_max_i_raw = 0;
                sum_com_fs = 0;
                sum_com_ss = 0;

                for ( peak_idx = 0 ;
                    peak_idx < num_pix_in_peak && peak_idx < max_pix_count ;
                    peak_idx++ ) {

                    int curr_idx;
                    float curr_i;
                    float curr_i_raw;
                    int curr_fs, curr_ss;

                    curr_idx = pfinter->peak_pixels[peak_idx];
                    curr_i_raw = copy[curr_idx];
                    curr_i = curr_i_raw - local_offset;
                    peak_tot_i += curr_i;
                    pk_tot_i_raw += curr_i_raw;

                    // Remember that curr_idx = curr_fs + curr_ss*num_pix_fs
                    curr_fs = curr_idx % num_pix_fs;
                    curr_ss = curr_idx / num_pix_fs;
                    sum_com_fs += curr_i * ((float)curr_fs);
                    sum_com_ss += curr_i * ((float)curr_ss);

                    if ( curr_i_raw > pk_max_i_raw ) pk_max_i_raw = curr_i_raw;
                    if ( curr_i > peak_max_i ) peak_max_i = curr_i;
                }


                // This CAN happen! Better to skip...
                if ( fabs(peak_tot_i) < 1e-10 ) continue;

                peak_com_fs = sum_com_fs / fabs(peak_tot_i);
                peak_com_ss = sum_com_ss / fabs(peak_tot_i);

                // Calculate signal-to-noise and apply SNR criteria
                if ( fabs(local_sigma) > 1e-10 ) {
                    peak_snr = peak_tot_i / local_sigma;
                } else {
                    peak_snr = 0;
                }

                if (peak_snr < min_snr) continue;

                // Is the maximum intensity in the peak enough above intensity in background region to
                // be a peak and not noise? The more pixels there are in the peak, the more relaxed we
                // are about this criterion
                // f_background_thresh = background_max_i - local_offset; //!!! Ofiget'!  If I uncomment
                // if (peak_max_i < f_background_thresh) {               // these lines the result is
                // different!
                if (peak_max_i < background_max_i - local_offset) continue;

                // This is a peak? If so, add info to peak list
                if ( num_pix_in_peak >= min_pix_count
                  && num_pix_in_peak <= max_pix_count ) {

                    // Bragg peaks in the mask
                    for ( peak_idx = 0 ;
                          peak_idx < num_pix_in_peak &&
                          peak_idx < max_pix_count ;
                          peak_idx++ ) {
                        pfinter->pix_in_peak_map[pfinter->peak_pixels[peak_idx]] = 2;
                    }

                    int peak_com_idx;
                    peak_com_idx = (int)rint(peak_com_fs) + (int)rint(peak_com_ss) *
                                        num_pix_fs;
                    // Remember peak information
                    if ( *peak_count < max_n_peaks ) {

                        int pidx;
                        pidx = *peak_count;

                        npix[pidx] = num_pix_in_peak;
                        com_fs[pidx] = peak_com_fs;
                        com_ss[pidx] = peak_com_ss;
                        com_index[pidx] = peak_com_idx;
                        tot_i[pidx] = peak_tot_i;
                        max_i[pidx] = peak_max_i;
                        sigma[pidx] = local_sigma;
                        snr[pidx] = peak_snr;
                    }
                    *peak_count += 1;
                }
            }

            float kk = 0.5;
            // adding pixels below lthreshold to mask as '3' - shadow mask
            // if ( copy[pxidx] < kk*roffset[curr_rad] + (1.-kk)*lthreshold[curr_rad]
            if ( copy[pxidx] < lthreshold[curr_rad]
              && pfinter->pix_in_peak_map[pxidx] == 0
              && mask[pxidx] != 0 ) {
                pfinter->pix_in_peak_map[pxidx] = 3;
            }

        }
    }
    //printf("Time process_panel taken: %.2fs\n", (double)(clock() - tStart)/CLOCKS_PER_SEC);
}

//UPT

static void process_panel_offset(int asic_size_fs, int asic_size_ss, int num_pix_fs,
                          int aiss, int aifs, float *rthreshold,
                          float *lthreshold, float *roffset, int *peak_count,
                          float *copy, struct peakfinder_intern_data *pfinter,
                          int *r_map, char *mask, int *npix, float *com_fs,
                          float *com_ss, int *com_index, float *tot_i,
                          float *max_i, float *sigma, float *snr,
                          int min_pix_count, int max_pix_count,
                          int local_bg_radius, float min_snr, int max_n_peaks)
{
    int pxss, pxfs;
    int num_pix_in_peak;
    //clock_t tStart = clock();

    // Loop over pixels within a module
    for ( pxss=1 ; pxss<asic_size_ss-1 ; pxss++ ) {
        for ( pxfs=1 ; pxfs<asic_size_fs-1 ; pxfs++ ) {

            float curr_thresh;
            int pxidx;
            int curr_rad;

            pxidx = (pxss + aiss * asic_size_ss) * num_pix_fs +
            pxfs + aifs * asic_size_fs;

            curr_rad = r_map[pxidx];
            curr_thresh = rthreshold[curr_rad];

            if ( copy[pxidx] > curr_thresh
              && pfinter->pix_in_peak_map[pxidx] == 0
              && mask[pxidx] != 0 ) {   //??? not sure if needed

                // This might be the start of a new peak - start searching
                float sum_com_fs, sum_com_ss;
                float sum_i;
                float peak_com_fs, peak_com_ss;
                float peak_com_fs_int, peak_com_ss_int;
                float peak_tot_i, pk_tot_i_raw;
                float peak_max_i, pk_max_i_raw;
                float peak_snr;
                float local_sigma, local_offset;
                float background_max_i;
                int lt_num_pix_in_pk;
                int ring_width;
                int peak_idx;
                int com_idx;
                int p;

                pfinter->infs[0] = pxfs;
                pfinter->inss[0] = pxss;
                pfinter->peak_pixels[0] = pxidx;
                num_pix_in_peak = 0; //y 1;

                sum_i = 0;
                sum_com_fs = 0;
                sum_com_ss = 0;

                // Keep looping until the pixel count within this peak does not change
                do {
                    lt_num_pix_in_pk = num_pix_in_peak;

                    // Loop through points known to be within this peak
                    for ( p=0; p<=num_pix_in_peak; p++ ) { //changed from 1 to 0 by O.Y.
                        peak_search_offset(p,
                                    pfinter, copy, mask,
                                    r_map,
                                    rthreshold,
                                    roffset,
                                    &num_pix_in_peak,
                                    asic_size_fs,
                                    asic_size_ss,
                                    aifs, aiss,
                                    num_pix_fs,
                                    &sum_com_fs,
                                    &sum_com_ss,
                                    &sum_i,
                                    max_pix_count);
                    }

                } while ( lt_num_pix_in_pk != num_pix_in_peak );

                // Too many or too few pixels means ignore this 'peak'; move on now
                if ( num_pix_in_peak < min_pix_count || num_pix_in_peak > max_pix_count ) continue;

                // If for some reason sum_i is 0 - it's better to skip
                if ( fabs(sum_i) < 1e-10 ) continue;

                // Calculate center of mass for this peak from initial peak search
                peak_com_fs = sum_com_fs / fabs(sum_i);
                peak_com_ss = sum_com_ss / fabs(sum_i);

                com_idx = (int)rint(peak_com_fs) + (int)rint(peak_com_ss) * num_pix_fs;

                peak_com_fs_int = (int)rint(peak_com_fs) - aifs * asic_size_fs;
                peak_com_ss_int = (int)rint(peak_com_ss) - aiss * asic_size_ss;

                // Calculate the local signal-to-noise ratio and local background in an annulus around
                // this peak (excluding pixels which look like they might be part of another peak)
                local_sigma = 0.0;
                local_offset = 0.0;
                background_max_i = 0.0;

                ring_width = 2 * local_bg_radius;

                search_in_ring_offset(ring_width, peak_com_fs_int,
                               peak_com_ss_int,
                               copy, r_map, rthreshold,
                               roffset,
                               pfinter->pix_in_peak_map,
                               mask, asic_size_fs,
                               asic_size_ss,
                               aifs, aiss,
                               num_pix_fs,
                               &local_sigma,
                               &local_offset,
                               &background_max_i,
                               com_idx, local_bg_radius);

                // Re-integrate (and re-centroid) peak using local background estimates
                peak_tot_i = 0;
                pk_tot_i_raw = 0;
                peak_max_i = 0;
                pk_max_i_raw = 0;
                sum_com_fs = 0;
                sum_com_ss = 0;

                for ( peak_idx = 0 ;
                    peak_idx < num_pix_in_peak && peak_idx < max_pix_count ;
                    peak_idx++ ) {

                    int curr_idx;
                    float curr_i;
                    float curr_i_raw;
                    int curr_fs, curr_ss;

                    curr_idx = pfinter->peak_pixels[peak_idx];
                    curr_i_raw = copy[curr_idx];
                    curr_i = curr_i_raw - local_offset;
                    peak_tot_i += curr_i;
                    pk_tot_i_raw += curr_i_raw;

                    // Remember that curr_idx = curr_fs + curr_ss*num_pix_fs
                    curr_fs = curr_idx % num_pix_fs;
                    curr_ss = curr_idx / num_pix_fs;
                    sum_com_fs += curr_i * ((float)curr_fs);
                    sum_com_ss += curr_i * ((float)curr_ss);

                    if ( curr_i_raw > pk_max_i_raw ) pk_max_i_raw = curr_i_raw;
                    if ( curr_i > peak_max_i ) peak_max_i = curr_i;
                }


                // This CAN happen! Better to skip...
                if ( fabs(peak_tot_i) < 1e-10 ) continue;

                peak_com_fs = sum_com_fs / fabs(peak_tot_i);
                peak_com_ss = sum_com_ss / fabs(peak_tot_i);

                // Calculate signal-to-noise and apply SNR criteria
                if ( fabs(local_sigma) > 1e-10 ) {
                    peak_snr = peak_tot_i / local_sigma;
                } else {
                    peak_snr = 0;
                }

                if (peak_snr < min_snr) continue;

                // Is the maximum intensity in the peak enough above intensity in background region to
                // be a peak and not noise? The more pixels there are in the peak, the more relaxed we
                // are about this criterion
                //f_background_thresh = background_max_i - local_offset; //!!! Ofiget'!  If I uncomment
                // if (peak_max_i < f_background_thresh) {               // these lines the result is
                // different!
                if (peak_max_i < background_max_i - local_offset) continue;

                // This is a peak? If so, add info to peak list
                if ( num_pix_in_peak >= min_pix_count
                  && num_pix_in_peak <= max_pix_count ) {

                    // Bragg peaks in the mask
                    for ( peak_idx = 0 ;
                          peak_idx < num_pix_in_peak &&
                          peak_idx < max_pix_count ;
                          peak_idx++ ) {
                        pfinter->pix_in_peak_map[pfinter->peak_pixels[peak_idx]] = 2;
                    }

                    int peak_com_idx;
                    peak_com_idx = (int)rint(peak_com_fs) + (int)rint(peak_com_ss) *
                                        num_pix_fs;
                    // Remember peak information
                    if ( *peak_count < max_n_peaks ) {

                        int pidx;
                        pidx = *peak_count;

                        npix[pidx] = num_pix_in_peak;
                        com_fs[pidx] = peak_com_fs;
                        com_ss[pidx] = peak_com_ss;
                        com_index[pidx] = peak_com_idx;
                        tot_i[pidx] = peak_tot_i;
                        max_i[pidx] = peak_max_i;
                        sigma[pidx] = local_sigma;
                        snr[pidx] = peak_snr;
                    }
                    *peak_count += 1;
                }
            }

            float kk = 0.5;
            // adding pixels below lthreshold to mask as '3' - shadow mask
//            if ( copy[pxidx] < kk*roffset[curr_rad] + (1.-kk)*lthreshold[curr_rad]
            if ( copy[pxidx] < lthreshold[curr_rad]
              && pfinter->pix_in_peak_map[pxidx] == 0
              && mask[pxidx] != 0 ) {
                pfinter->pix_in_peak_map[pxidx] = 3;
            }

        }
    }
    //printf("Time process_panel taken: %.2fs\n", (double)(clock() - tStart)/CLOCKS_PER_SEC);
}



static int peakfinder8_base(float *roffset, float *rthreshold, float *lthreshold,
                            float *data, char *mask, float *r_map,
                            int asic_size_fs, int num_asics_fs,
                            int asic_size_ss, int num_asics_ss,
                            int max_n_peaks, int *num_found_peaks,
                            int *npix, float *com_fs,
                            float *com_ss, int *com_index, float *tot_i,
                            float *max_i, float *sigma, float *snr,
                            int min_pix_count, int max_pix_count,
                            int local_bg_radius, float min_snr,
                            char* outliersMask)
{

    int num_pix_fs, num_pix_ss, num_pix_tot;
    int aifs, aiss;
    int peak_count;
    struct peakfinder_intern_data *pfinter;

    //clock_t tStart = clock();
    num_pix_fs = asic_size_fs * num_asics_fs;
    num_pix_ss = asic_size_ss * num_asics_ss;
    num_pix_tot = num_pix_fs * num_pix_ss;

    pfinter = allocate_peakfinder_intern_data(num_pix_tot, max_pix_count);
    if ( pfinter == NULL ) {
        return 1;
    }

    peak_count = 0;

    // Loop over modules (nxn array)
    for ( aiss=0 ; aiss<num_asics_ss ; aiss++ ) {
        for ( aifs=0 ; aifs<num_asics_fs ; aifs++ ) {                 // ??? to change to proper panels need
            process_panel(asic_size_fs, asic_size_ss, num_pix_fs, // change copy, mask, r_map
                            aiss, aifs, rthreshold, lthreshold, roffset,
                          &peak_count, data, pfinter, r_map, mask,
                          npix, com_fs, com_ss, com_index, tot_i,
                          max_i, sigma, snr, min_pix_count,
                          max_pix_count, local_bg_radius, min_snr,
                          max_n_peaks);
        }
    }
    *num_found_peaks = peak_count;

    if (outliersMask != NULL) {
        memcpy(outliersMask, pfinter->pix_in_peak_map, num_pix_tot*sizeof(char));
    }

    free_peakfinder_intern_data(pfinter);
    //printf("Time peakfinder8_base taken: %.2fs\n", (double)(clock() - tStart)/CLOCKS_PER_SEC);

    return 0;
}

//UPT
static int peakfinder8_base_offset(float *roffset, float *rthreshold, float *lthreshold,
                            float *data, char *mask, int *r_map,
                            int asic_size_fs, int num_asics_fs,
                            int asic_size_ss, int num_asics_ss,
                            int max_n_peaks, int *num_found_peaks,
                            int *npix, float *com_fs,
                            float *com_ss, int *com_index, float *tot_i,
                            float *max_i, float *sigma, float *snr,
                            int min_pix_count, int max_pix_count,
                            int local_bg_radius, float min_snr,
                            char* outliersMask)
{

    int num_pix_fs, num_pix_ss, num_pix_tot;
    int aifs, aiss;
    int peak_count;
    struct peakfinder_intern_data *pfinter;

    //clock_t tStart = clock();
    num_pix_fs = asic_size_fs * num_asics_fs;
    num_pix_ss = asic_size_ss * num_asics_ss;
    num_pix_tot = num_pix_fs * num_pix_ss;

    pfinter = allocate_peakfinder_intern_data(num_pix_tot, max_pix_count);
    if ( pfinter == NULL ) {
        return 1;
    }

    peak_count = 0;

    // Loop over modules (nxn array)
    for ( aiss=0 ; aiss<num_asics_ss ; aiss++ ) {
        for ( aifs=0 ; aifs<num_asics_fs ; aifs++ ) {                 // ??? to change to proper panels need
            process_panel_offset(asic_size_fs, asic_size_ss, num_pix_fs, // change copy, mask, r_map
                            aiss, aifs, rthreshold, lthreshold, roffset,
                          &peak_count, data, pfinter, r_map, mask,
                          npix, com_fs, com_ss, com_index, tot_i,
                          max_i, sigma, snr, min_pix_count,
                          max_pix_count, local_bg_radius, min_snr,
                          max_n_peaks);
        }
    }
    *num_found_peaks = peak_count;

    if (outliersMask != NULL) {
        memcpy(outliersMask, pfinter->pix_in_peak_map, num_pix_tot*sizeof(char));
    }

    free_peakfinder_intern_data(pfinter);
    //printf("Time peakfinder8_base taken: %.2fs\n", (double)(clock() - tStart)/CLOCKS_PER_SEC);

    return 0;
}


// Cheetah Peakfinder8
// Count peaks by searching for connected pixels above threshold
// Includes modifications during Cherezov December 2014 LE80
// Anton Barty
int peakfinder8(tPeakList *peaklist, float *data, char *mask, float *pix_r,
                long asic_nx, long asic_ny, long nasics_x, long nasics_y,
                float ADCthresh, float hitfinderMinSNR,
                long hitfinderMinPixCount, long hitfinderMaxPixCount,
                long hitfinderLocalBGRadius, char* outliersMask)
{
    struct radial_stats *rstats;
    struct peakfinder_peak_data *pkdata;
    int iterations;
    int num_pix_fs, num_pix_ss;
    int num_pix_tot;
    int max_num_peaks;
    int num_found_peaks;
    int ret;
    int pki;
    int peaks_to_add;
    ////printf("-----Start Peakfinder8-----\n");
    clock_t tStart = clock();

    max_num_peaks = peaklist->nPeaks_max;

    // Derived values
    num_pix_fs = asic_nx * nasics_x;
    num_pix_ss = asic_ny * nasics_y;
    num_pix_tot = num_pix_fs * num_pix_ss;

    // Compute radial statistics as 1 function (O.Y.)
    iterations = 5;

    //clock_t tStart1 = clock();
    rstats = compute_radial_bins(data, mask, num_pix_tot, pix_r,
                                 iterations, hitfinderMinSNR, ADCthresh,
                                 num_pix_fs, num_pix_ss);
    //printf("Time compute_radial_bins in P8 taken: %.2fs\n", (double)(clock() - tStart1)/CLOCKS_PER_SEC);
    
    //tStart1 = clock();
    pkdata = allocate_peak_data(max_num_peaks);
    //printf("Time allocate_peak_data in P8 taken: %.2fs\n", (double)(clock() - tStart1)/CLOCKS_PER_SEC);
    
    if ( pkdata == NULL ) {
        free_radial_stats(rstats);
        return 1;
    }

    num_found_peaks = 0;
    
    //tStart1 = clock();
    ret = peakfinder8_base(rstats->roffset,
                           rstats->rthreshold,
                           rstats->lthreshold,
                           data,
                           mask,
                           pix_r,
                           asic_nx, nasics_x,
                           asic_ny, nasics_y,
                           max_num_peaks  ,
                           &num_found_peaks,
                           pkdata->npix,
                           pkdata->com_fs,
                           pkdata->com_ss,
                           pkdata->com_index,
                           pkdata->tot_i,
                           pkdata->max_i,
                           pkdata->sigma,
                           pkdata->snr,
                           hitfinderMinPixCount,
                           hitfinderMaxPixCount,
                           hitfinderLocalBGRadius,
                           hitfinderMinSNR,
                           outliersMask);
    //printf("Time peakfinder8_base in P8 taken: %.2fs\n", (double)(clock() - tStart1)/CLOCKS_PER_SEC);
    
    if ( ret != 0 ) {
        free_radial_stats(rstats);
        free_peak_data(pkdata);
        return 1;
    }

    peaks_to_add = num_found_peaks;

    if ( num_found_peaks > max_num_peaks ) {
        peaks_to_add = max_num_peaks;
    }

    for ( pki=0 ; pki<peaks_to_add ; pki++ ) {

        peaklist->peak_maxintensity[pki] = pkdata->max_i[pki];
        peaklist->peak_totalintensity[pki] = pkdata->tot_i[pki];
        peaklist->peak_sigma[pki] = pkdata->sigma[pki];
        peaklist->peak_snr[pki] = pkdata->snr[pki];
        peaklist->peak_npix[pki] = pkdata->npix[pki];
        peaklist->peak_com_x[pki] = pkdata->com_fs[pki];
        peaklist->peak_com_y[pki] = pkdata->com_ss[pki];
        peaklist->peak_com_index[pki] = pkdata->com_index[pki];

        ////printf("peak_maxintensity =%f\tpeak_totalintensity =%f\tpeak_sigma =%f\tpeak_snr =%f\n", peaklist->peak_maxintensity[pki], peaklist->peak_totalintensity[pki], peaklist->peak_sigma[pki], peaklist->peak_snr[pki]);
    }

    peaklist->nPeaks = peaks_to_add;

    free_radial_stats(rstats);
    free_peak_data(pkdata);
    ////printf("-----End Peakfinder8-----\n");
    //printf("Time Peakfinder8 taken: %.2fs\n", (double)(clock() - tStart)/CLOCKS_PER_SEC);
    //printf("%.2fs\n", (double)(clock() - tStart)/CLOCKS_PER_SEC);
    return 0;
}



//UPT
// Cheetah Peakfinder8
// Count peaks by searching for connected pixels above threshold
// Includes modifications during Cherezov December 2014 LE80
// Anton Barty
int peakfinder8_offset(tPeakList *peaklist, float *data, char *mask, int *pix_r,
                long asic_nx, long asic_ny, long nasics_x, long nasics_y,
                float ADCthresh, float hitfinderMinSNR,
                long hitfinderMinPixCount, long hitfinderMaxPixCount,
                long hitfinderLocalBGRadius, int maxRad,
                int lenLinearArrayRandomInd, int* LinearArrayRandomInd,
                int* Offset1DArray, char* outliersMask)
{
    struct radial_stats *rstats;
    struct peakfinder_peak_data *pkdata;
    int iterations;
    int num_pix_fs, num_pix_ss;
    int num_pix_tot;
    int max_num_peaks;
    int num_found_peaks;
    int ret;
    int pki;
    int peaks_to_add;
    ////printf("-----Start Peakfinder8-----\n");
    clock_t tStart = clock();

    max_num_peaks = peaklist->nPeaks_max;

    // Derived values
    num_pix_fs = asic_nx * nasics_x;
    num_pix_ss = asic_ny * nasics_y;
    num_pix_tot = num_pix_fs * num_pix_ss;

    // Compute radial statistics as 1 function (O.Y.)
    iterations = 5;

    //clock_t tStart1 = clock();

    rstats = compute_radial_bins_offset(data, mask, num_pix_tot, pix_r,
                                 iterations, hitfinderMinSNR, ADCthresh,
                                 num_pix_fs, num_pix_ss, maxRad,lenLinearArrayRandomInd,
                                 LinearArrayRandomInd, Offset1DArray);
    //printf("Time compute_radial_bins_offset in P8_offset taken: %.2fs\n", (double)(clock() - tStart1)/CLOCKS_PER_SEC);
    
    //tStart1 = clock();
    pkdata = allocate_peak_data(max_num_peaks);
    //printf("Time allocate_peak_data in P8_offset taken: %.2fs\n", (double)(clock() - tStart1)/CLOCKS_PER_SEC);
    
    if ( pkdata == NULL ) {
        free_radial_stats(rstats);
        return 1;
    }

    num_found_peaks = 0;
    
    //tStart1 = clock();
    ret = peakfinder8_base_offset(rstats->roffset,
                           rstats->rthreshold,
                           rstats->lthreshold,
                           data,
                           mask,
                           pix_r,
                           asic_nx, nasics_x,
                           asic_ny, nasics_y,
                           max_num_peaks  ,
                           &num_found_peaks,
                           pkdata->npix,
                           pkdata->com_fs,
                           pkdata->com_ss,
                           pkdata->com_index,
                           pkdata->tot_i,
                           pkdata->max_i,
                           pkdata->sigma,
                           pkdata->snr,
                           hitfinderMinPixCount,
                           hitfinderMaxPixCount,
                           hitfinderLocalBGRadius,
                           hitfinderMinSNR,
                           outliersMask);
    //printf("Time peakfinder8_base in P8_offset taken: %.2fs\n", (double)(clock() - tStart1)/CLOCKS_PER_SEC);
    
    if ( ret != 0 ) {
        free_radial_stats(rstats);
        free_peak_data(pkdata);
        return 1;
    }

    peaks_to_add = num_found_peaks;

    if ( num_found_peaks > max_num_peaks ) {
        peaks_to_add = max_num_peaks;
    }

    for ( pki=0 ; pki<peaks_to_add ; pki++ ) {

        peaklist->peak_maxintensity[pki] = pkdata->max_i[pki];
        peaklist->peak_totalintensity[pki] = pkdata->tot_i[pki];
        peaklist->peak_sigma[pki] = pkdata->sigma[pki];
        peaklist->peak_snr[pki] = pkdata->snr[pki];
        peaklist->peak_npix[pki] = pkdata->npix[pki];
        peaklist->peak_com_x[pki] = pkdata->com_fs[pki];
        peaklist->peak_com_y[pki] = pkdata->com_ss[pki];
        peaklist->peak_com_index[pki] = pkdata->com_index[pki];

        ////printf("peak_maxintensity =%f\tpeak_totalintensity =%f\tpeak_sigma =%f\tpeak_snr =%f\n", peaklist->peak_maxintensity[pki], peaklist->peak_totalintensity[pki], peaklist->peak_sigma[pki], peaklist->peak_snr[pki]);
    }

    peaklist->nPeaks = peaks_to_add;

    free_radial_stats(rstats);
    free_peak_data(pkdata);
    ////printf("-----End Peakfinder8-----\n");
    //printf("Time Peakfinder8_offset taken: %.2fs\n", (double)(clock() - tStart)/CLOCKS_PER_SEC);
    printf("%.2fs\n", (double)(clock() - tStart)/CLOCKS_PER_SEC);
    return 0;
}

//UPT2 MEDIAN

int peakfinder8_offset_median(tPeakList *peaklist, float *data, char *mask, int *pix_r,
                long asic_nx, long asic_ny, long nasics_x, long nasics_y,
                float ADCthresh, float hitfinderMinSNR,
                long hitfinderMinPixCount, long hitfinderMaxPixCount,
                long hitfinderLocalBGRadius, int maxRad,
                int lenLinearArrayRandomInd, int* LinearArrayRandomInd,
                int* Offset1DArray, char* outliersMask)
{
    struct radial_stats *rstats;
    struct peakfinder_peak_data *pkdata;
    int iterations;
    int num_pix_fs, num_pix_ss;
    int num_pix_tot;
    int max_num_peaks;
    int num_found_peaks;
    int ret;
    int pki;
    int peaks_to_add;
    //printf("-----Start Peakfinder8_offset_median-----\n");
    clock_t tStart = clock();

    max_num_peaks = peaklist->nPeaks_max;

    // Derived values
    num_pix_fs = asic_nx * nasics_x;
    num_pix_ss = asic_ny * nasics_y;
    num_pix_tot = num_pix_fs * num_pix_ss;

    // Compute median radial statistics as 1 function (O.Y.)
    
    //clock_t tStart1 = clock();

    rstats = compute_radial_bins_offset_median(data, mask, pix_r,
                                               hitfinderMinSNR, ADCthresh,
                                               maxRad,lenLinearArrayRandomInd,
                                               LinearArrayRandomInd, Offset1DArray);
    //printf("Time compute_radial_bins_offset_median in P8_offset_median taken: %.2fs\n", (double)(clock() - tStart1)/CLOCKS_PER_SEC);
    
    //tStart1 = clock();
    pkdata = allocate_peak_data(max_num_peaks);
    //printf("Time allocate_peak_data in P8_offset taken: %.2fs\n", (double)(clock() - tStart1)/CLOCKS_PER_SEC);
    
    if ( pkdata == NULL ) {
        free_radial_stats(rstats);
        return 1;
    }

    num_found_peaks = 0;
    //for (int i=0; i<maxRad; i++)
	//  printf("%0.5f ",rstats->roffset[i]);
	//printf("\n");
    //tStart1 = clock();
    ret = peakfinder8_base_offset(rstats->roffset,
                           rstats->rthreshold,
                           rstats->lthreshold,
                           data,
                           mask,
                           pix_r,
                           asic_nx, nasics_x,
                           asic_ny, nasics_y,
                           max_num_peaks,
                           &num_found_peaks,
                           pkdata->npix,
                           pkdata->com_fs,
                           pkdata->com_ss,
                           pkdata->com_index,
                           pkdata->tot_i,
                           pkdata->max_i,
                           pkdata->sigma,
                           pkdata->snr,
                           hitfinderMinPixCount,
                           hitfinderMaxPixCount,
                           hitfinderLocalBGRadius,
                           hitfinderMinSNR,
                           outliersMask);
    
    //printf("Time peakfinder8_base in P8_offset taken: %.2fs\n", (double)(clock() - tStart1)/CLOCKS_PER_SEC);
    
    if ( ret != 0 ) {
        free_radial_stats(rstats);
        free_peak_data(pkdata);
        return 1;
    }else{
		printf("ret = %d\n",ret);
	}

    peaks_to_add = num_found_peaks;

    if ( num_found_peaks > max_num_peaks ) {
        peaks_to_add = max_num_peaks;
    }

    for ( pki=0 ; pki<peaks_to_add ; pki++ ) {

        peaklist->peak_maxintensity[pki] = pkdata->max_i[pki];
        peaklist->peak_totalintensity[pki] = pkdata->tot_i[pki];
        peaklist->peak_sigma[pki] = pkdata->sigma[pki];
        peaklist->peak_snr[pki] = pkdata->snr[pki];
        peaklist->peak_npix[pki] = pkdata->npix[pki];
        peaklist->peak_com_x[pki] = pkdata->com_fs[pki];
        peaklist->peak_com_y[pki] = pkdata->com_ss[pki];
        peaklist->peak_com_index[pki] = pkdata->com_index[pki];

        ////printf("peak_maxintensity =%f\tpeak_totalintensity =%f\tpeak_sigma =%f\tpeak_snr =%f\n", peaklist->peak_maxintensity[pki], peaklist->peak_totalintensity[pki], peaklist->peak_sigma[pki], peaklist->peak_snr[pki]);
    }

    peaklist->nPeaks = peaks_to_add;

    free_radial_stats(rstats);
    free_peak_data(pkdata);
    ////printf("-----End Peakfinder8-----\n");
    //printf("Time Peakfinder8_offset_median taken: %.2fs\n", (double)(clock() - tStart)/CLOCKS_PER_SEC);
    //printf("%.2fs\n", (double)(clock() - tStart)/CLOCKS_PER_SEC);
	//printf("%d\n", peaklist->nPeaks);
    return 0;
};

}
