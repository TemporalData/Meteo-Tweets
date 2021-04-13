#!/usr/bin/env python
# coding: utf-8

# In[20]:


import pandas as pd
import csv


# In[101]:


#Function to load the array from the dat file into a dictionary
def load_dictionary(Id, file_name):

    #Read the file into a pandas dataframe
    levels = pd.read_csv(file_name,header=None)
    
    #Rename the column to 'lines' for simplicity
    levels.columns = ['lines']

    #Boolean variable to record when the array has started
    array = False
    #Empty dictionary which will be filled and returned
    dictionary = {}
    
    #Counter for the rows seen from the array
    row_counter = 0
    
    #Loop all the rows from the array that has been read
    for row in levels['lines'][:len(levels['lines'])-1]:
        
        #If the line is part of the array
        if(array):
            #Do not add rows that have 'reserved' in the value column
            if(not(row.split()[4] == 'reserved')):
                #Add the RGB values and value to the dictionary
                dictionary[(int(row.split()[1]),
                            int(row.split()[2]),
                            int(row.split()[3]))] = float(row.split()[4])
                
        #If the first string is a 0 the array has started
        #Skip the first row if 'CZC' or 'RZC'
        if(row.split()[0] == "0" and (Id == 'bzc' or Id == 'lcz')):
            #Set the boolean to True to input the following rows
            array = True
        
        if(row.split()[0] == "1"):
            array = True
            
            
        
    return(dictionary)


# In[102]:


#Function to create the csv with the dictionary
def create_csv(Id,file_name):
    
    #Load the dictionary into memory
    dict = load_dictionary(Id, file_name)
    #Open a csv file with 'w' (write)
    f = open("dict_" + Id + ".csv", "w")
    #Use csv writer for this opened file
    w = csv.writer(f)
    #Loop all the keys in the dictionary and add them to the csv
    for key, val in dict.items():
        w.writerow([key, val])
    #Close the file, which correctly saves the file
    f.close()


# In[103]:


# BZC
create_csv("bzc","RGB_datalevels_bzc.dat")

# CZC
create_csv("czc","RGB_datalevels256_czc.dat")

# LZC
create_csv("lzc","RGB_datalevels256_lzc.dat")

# RZC
create_csv("rzc","RGB_datalevels256_rzc.dat")


# In[ ]:





# In[108]:


f = open("test.csv", "w")
np.savetxt(f,[0,0,0,0],delimiter=',')
f.close()


# In[107]:


import numpy as np


# In[ ]:




