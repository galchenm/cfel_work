#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <math.h>
#include <ctype.h>
#include <stdarg.h>
#include <stdint.h>
#include <stddef.h>
#include <limits.h>
#include <string.h>
#include <ctype.h>
#include <algorithm>
#include <iostream>

const int NumberOfRandomS = 100;

extern "C"{
void IndexForEachRF(int numEl, int maxRad, int* pix_r, int* numPerShell1, int*** IndexForEachR){
  
  int** IndexForEachRtmp = new int*[maxRad];
  for(int i=0; i<maxRad; i++)
  {
    IndexForEachRtmp[i] = new int[numPerShell1[i]];
    for(int j=0; j<numPerShell1[i]; j++)
    {
      IndexForEachRtmp[i][j] = 0;
    }
  }
  for (int i=0; i<maxRad; i++)
    numPerShell1[i] = 0;
  // actual forming of the 2D array
  for (int i=0; i<numEl; i++)
  { 
    if(pix_r[i]<0)
    {
      continue;
    }
    IndexForEachRtmp[pix_r[i]][numPerShell1[pix_r[i]]] = i;
    numPerShell1[pix_r[i]]++;
  }
  *IndexForEachR = IndexForEachRtmp;
  return;
};

void RandomIndexF(int lenShellR, int* currentR, int* RandomIndex)
{
  //generate random indexes without repetiotion that should be selected from currentR
  srand(time(NULL));
  int value [NumberOfRandomS];
  for (int i=0;i<NumberOfRandomS;++i)
  {
      int check; //variable to check or index is already used for this r
      int pick_index; //variable to store the random index in
      do
      {
      pick_index = rand() % lenShellR;
      //check or index is already used for this r:
      check=1;
      for (int j=0;j<i;++j)
          if (pick_index == value[j]) //if index is already used
          {
              check=0; //set check to false
              break; //no need to check the other elements of value[]
          }
      } while (check == 0); //loop until new, unique index is found
      value[i]=pick_index; //store the generated index in the array
      RandomIndex[i] = currentR[pick_index];
  }
  return;
};

void NegativeSetRoUtOfRanIndex(int lenShellR, int* currentR, int* RandomIndex, int *pix_r)
{
  for(int i=0; i<lenShellR;i++)
  {
    int *end = RandomIndex + NumberOfRandomS;
    // find the value
    int *result = std::find(RandomIndex, end, currentR[i]);
    if (result != end) {
      continue;
    }else{
      pix_r[currentR[i]] = -1;
    }
  }
};

void GetIndexForNonNegativeR(int numEl, int maxRad, int* pix_r, int** numPerShell, int*** IndexForEachR)
{
  int lenNumPerShell1 = (maxRad) * sizeof(int);
  int* numPerShell1 =  (int*) malloc(lenNumPerShell1);
  memset(numPerShell1, 0, lenNumPerShell1);

  for (int i=0; i<numEl; ++i){
    if(pix_r[i] <0)
    {
      continue;
    }
    numPerShell1[pix_r[i]]++;
  }

  int** _IndexForEachR;

  //2D array where each r > 0 relates to the list if its indexes
  IndexForEachRF(numEl, maxRad, pix_r, numPerShell1, &_IndexForEachR);

  *IndexForEachR = _IndexForEachR;
  *numPerShell = numPerShell1;
};

int pixRmodifWithArrayOfIndex(int numEl, int *pix_r, int** numPerShellF, int*** Array2DpixRwithInd)
{
  int* RIndex = (int*) malloc(NumberOfRandomS*sizeof(int));
  memset(RIndex, 0, NumberOfRandomS*sizeof(int));
  
  

  int maxRad = 0;
  for(int i =0; i<numEl;i++){
    maxRad = pix_r[i] > maxRad ? pix_r[i] : maxRad;
  }
  maxRad +=1;

  int** _IndexForEachR;
  int* numPerShell1;

  //2D array where each r > 0 relates to the list if its indexes
  GetIndexForNonNegativeR(numEl, maxRad, pix_r, &numPerShell1, &_IndexForEachR);
  
  for(int r =0; r<maxRad; r++)
  {
    int lenShellR = numPerShell1[r];

    //if number of items for this r is less than should be
    //selected, skip it. It means that we selected all items 
    //for this r
    if(lenShellR <= NumberOfRandomS){
      continue;
    }

    //get array that includes a list of random indexes for each r
    RandomIndexF(lenShellR, _IndexForEachR[r], RIndex);

    //set to -1 all items with indexes that are out of a list of random indexes
    NegativeSetRoUtOfRanIndex(lenShellR, _IndexForEachR[r], RIndex, pix_r); 
    
  }

  int** _IndexForEachR2;
  int* numPerShell2;

  //2D array where each r > 0 relates to the list if its indexes
  GetIndexForNonNegativeR(numEl, maxRad, pix_r, &numPerShell2, &_IndexForEachR2);

  *Array2DpixRwithInd=_IndexForEachR2;
  *numPerShellF=numPerShell2;

  return maxRad;
};


void LinearPixRmodifWithArrayOfIndex(int numEl, int maxRad, int *pix_r, int* Array1DpixRwithInd)
{
  int* RIndex = (int*) malloc(NumberOfRandomS*sizeof(int));
  memset(RIndex, 0, NumberOfRandomS*sizeof(int));
  //printf("LinearPixRmodifWithArrayOfIndex\n");
  

  //int maxRad = 0;
  //for(int i =0; i<numEl;i++){
  //  maxRad = pix_r[i] > maxRad ? pix_r[i] : maxRad;
  //}
  //maxRad +=1;

  int** _IndexForEachR;
  int* numPerShell1;

  //2D array where each r > 0 relates to the list if its indexes
  GetIndexForNonNegativeR(numEl, maxRad, pix_r, &numPerShell1, &_IndexForEachR);
  
  for(int r =0; r<maxRad; r++)
  {
    int lenShellR = numPerShell1[r];

    //if number of items for this r is less than should be
    //selected, skip it. It means that we selected all items 
    //for this r
    if(lenShellR <= NumberOfRandomS){
      continue;
    }

    //get array that includes a list of random indexes for each r
    RandomIndexF(lenShellR, _IndexForEachR[r], RIndex);

    //set to -1 all items with indexes that are out of a list of random indexes
    NegativeSetRoUtOfRanIndex(lenShellR, _IndexForEachR[r], RIndex, pix_r); 
    
  }

  int** _IndexForEachR2;
  int* numPerShell2;

  //2D array where each r > 0 relates to the list if its indexes
  GetIndexForNonNegativeR(numEl, maxRad, pix_r, &numPerShell2, &_IndexForEachR2);
  
  int ind=0;
  for(int k=0; k < maxRad; k++)
  {
    for(int j=0;j<numPerShell2[k];j++){
      Array1DpixRwithInd[k*NumberOfRandomS + j] = _IndexForEachR2[k][j];
      //printf("r = %i; index is %i\n",k, _IndexForEachR2[k][j]);
      ind++;
    }
  }

  return;
};
}