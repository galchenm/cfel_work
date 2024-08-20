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
#include <bits/stdc++.h>
#include <cstdio>

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
}


int minShell(int maxRad, int *numPerShell1)
{
  int* tmpnumPerShell1 = (int*)malloc(maxRad*sizeof(int));
  memcpy(tmpnumPerShell1, numPerShell1, maxRad*sizeof(int));


  for(int i=0;i<maxRad; i++){
    if(tmpnumPerShell1[i] <= NumberOfRandomS){
      tmpnumPerShell1[i] = INT_MAX;
    }
  }
  int* minShellN = std::min_element(tmpnumPerShell1, tmpnumPerShell1 + maxRad);
  return *minShellN;
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

void RandomIndexFM(int lenShellR, int* RandomIndex)
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
      RandomIndex[i] = pick_index;
  }
  return;
};


void funcNumPerShellC(int numEl, int maxRad, int* pix_r, int *numPerShell1){
  for (int i=0; i<numEl; ++i){
    if(pix_r[i] <0)
    {
      continue;
    }
    numPerShell1[pix_r[i]]++;
  }
};

void GetIndexForNonNegativeR(int numEl, int maxRad, int* pix_r, int* numPerShell, int*** IndexForEachR)
{
  //int lenNumPerShell1 = (maxRad) * sizeof(int);
  //int* numPerShell1 =  (int*) malloc(lenNumPerShell1);
  //memset(numPerShell1, 0, lenNumPerShell1);

  funcNumPerShellC(numEl, maxRad, pix_r, numPerShell);

  int** _IndexForEachR;

  //2D array where each r > 0 relates to the list if its indexes
  IndexForEachRF(numEl, maxRad, pix_r, numPerShell, &_IndexForEachR);

  *IndexForEachR = _IndexForEachR;
  //*numPerShell = numPerShell1;
};


int fLenArrayForLinearArrayRandomInd(int maxRad, int* numPerShell1){
  int lenShellR;
  int lenLinearArrayRandomInd = 0;
  for(int r=0; r < maxRad; r++)
  {
    lenShellR = numPerShell1[r];
    lenLinearArrayRandomInd += ((lenShellR <= NumberOfRandomS) ? lenShellR : NumberOfRandomS);
  }
  return lenLinearArrayRandomInd;
};

void UptLinearPixRmodifWithArrayOfIndexV2(int numEl, int maxRad, int *pix_r, int lenLinearArrayRandomInd, int* tmpLinearArrayRandomInd, int* tmpOffset1DArray, int *numPerShell1)
{
  int* RIndex = (int*) malloc(NumberOfRandomS*sizeof(int));
  memset(RIndex, 0, NumberOfRandomS*sizeof(int));
  //printf("uptLinearPixRmodifWithArrayOfIndex\n");
  
  //int* tmpDATA = (int*) malloc(numEl * sizeof(int));
  //memset(tmpDATA, 0, numEl * sizeof(int));

  clock_t tStart = clock();
  
  int** _IndexForEachR;
  
  //2D array where each r > 0 relates to the list if its indexes
  GetIndexForNonNegativeR(numEl, maxRad, pix_r, numPerShell1, &_IndexForEachR);

  int lenShellR;

  int indOffset1DArray = 0;
  int indLinearArrayRandomInd = 0;
  int prevOffset = 0;

  for(int r =0; r<maxRad; r++)
  {
    lenShellR = numPerShell1[r];

    //if number of items for this r is less than should be
    //selected, skip it. It means that we selected all items 
    //for this r
    if(lenShellR <= NumberOfRandomS){
      for(int ir = 0; ir <lenShellR; ir++)
      {
        tmpLinearArrayRandomInd[indLinearArrayRandomInd] = _IndexForEachR[r][ir];
        //tmpDATA[_IndexForEachR[r][ir]] = 1;
        indLinearArrayRandomInd++;
      }
      tmpOffset1DArray[indOffset1DArray] = prevOffset;
      prevOffset = indLinearArrayRandomInd;

      indOffset1DArray++;
      continue;
    }

    //get array that includes a list of random indexes for each r
    RandomIndexF(lenShellR, _IndexForEachR[r], RIndex);
    for(int ir = 0; ir<NumberOfRandomS; ir++)
      {
        tmpLinearArrayRandomInd[indLinearArrayRandomInd] = RIndex[ir];
        //tmpDATA[RIndex[ir]] = 1;
        indLinearArrayRandomInd++;
      }
    tmpOffset1DArray[indOffset1DArray] = prevOffset;
    prevOffset = indLinearArrayRandomInd;
    indOffset1DArray++;
  }

  //FILE *stream;
  //stream = fopen("OLEXANDRZANUDA_offset.bin", "wb");
  //for (int i=0; i<numEl; i++){
  //  fwrite(&tmpDATA[i], sizeof(int), 1, stream);
  //}
  
  //fclose(stream);

  printf("Time RANDOM taken: %.4fs\n", (double)(clock() - tStart)/CLOCKS_PER_SEC);
  return;
};



void UptLinearPixRmodifWithArrayOfIndexV3(int numEl, int maxRad, int *pix_r, int lenLinearArrayRandomInd, int* tmpLinearArrayRandomInd, int* tmpOffset1DArray, int *numPerShell1)
{
  int* RIndex = (int*) malloc(NumberOfRandomS*sizeof(int));
  memset(RIndex, 0, NumberOfRandomS*sizeof(int));

  //int* tmpDATA = (int*) malloc(numEl * sizeof(int));
  //memset(tmpDATA, 0, numEl * sizeof(int));

  clock_t tStart = clock();
  
  
  int** _IndexForEachR;
  
  //2D array where each r > 0 relates to the list if its indexes
  GetIndexForNonNegativeR(numEl, maxRad, pix_r, numPerShell1, &_IndexForEachR);

  int minLenShellR = minShell(maxRad, numPerShell1);
  
  RandomIndexFM(minLenShellR, RIndex);


  int lenShellR;

  int indOffset1DArray = 0;
  int indLinearArrayRandomInd = 0;
  int prevOffset = 0;

  for(int r =0; r<maxRad; r++)
  {
    lenShellR = numPerShell1[r];

    int koef = lenShellR / minLenShellR;

    //if number of items for this r is less than should be
    //selected, skip it. It means that we selected all items 
    //for this r
    if(lenShellR <= NumberOfRandomS){
      for(int ir = 0; ir <lenShellR; ir++)
      {
        tmpLinearArrayRandomInd[indLinearArrayRandomInd] = _IndexForEachR[r][ir];
        indLinearArrayRandomInd++;

        //tmpDATA[_IndexForEachR[r][ir]] = 1;
        //printf("index is %i\n", _IndexForEachR[r][ir]);
      }
      tmpOffset1DArray[indOffset1DArray] = prevOffset;
      prevOffset = indLinearArrayRandomInd;

      indOffset1DArray++;
      continue;
    }

    //get array that includes a list of random indexes for each r
    //RandomIndexF(lenShellR, _IndexForEachR[r], RIndex);
    for(int ir = 0; ir<NumberOfRandomS; ir++)
      {
        tmpLinearArrayRandomInd[indLinearArrayRandomInd] = _IndexForEachR[r][RIndex[ir]*koef];
        indLinearArrayRandomInd++;

        //tmpDATA[_IndexForEachR[r][RIndex[ir]*koef]] = 1;
        //printf("index is %i\n", _IndexForEachR[r][RIndex[ir]*koef]);
      }
    tmpOffset1DArray[indOffset1DArray] = prevOffset;
    prevOffset = indLinearArrayRandomInd;
    indOffset1DArray++;
  }


  //FILE *stream;
  //stream = fopen("OLEXANDRZANUDA.bin", "wb");
  //for (int i=0; i<numEl; i++){
  //  fwrite(&tmpDATA[i], sizeof(int), 1, stream);
  //}
  
  //fclose(stream);

  printf("Time RANDOM taken: %.4fs\n", (double)(clock() - tStart)/CLOCKS_PER_SEC);
  return;

};


}