#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from PIL import Image
import numpy as np
import pandas as pd
import os
from tqdm import tqdm
from pyproj import Transformer
from datetime import datetime


# In[2]:


# function to return the dictionary required to convert the image
def dictionary_loader(ID):
    
    # Switch case for each type of data present
    switcher = {
        'BZC': "dict_bzc.csv",
        'CZC': "dict_czc.csv",
        'LZC': "dict_lzc.csv",
        'RZC': "dict_rzc.csv"
    }
    
    #Obtain the correct dictionary name based on ID passed to function
    file_name = switcher.get(ID, "Error")
    
    #Load the dictionary into a dataframe
    df_dict = pd.read_csv(file_name, names = ['key','value'])
    
    #Return the dataframe as an array
    return dict(np.asarray(df_dict))
    
    


# In[3]:


# function which returns the folder names containing 'BZC' or 'CZC' or 'LZC' or 'RZC'
def identify_folders(data_directory):
        
    #Obtain all the folders in the current directory
    all_folders = os.listdir(data_directory)

    #Create a list to contain the folders we want to iterate over
    target_folders = []
    
    #Loop all the folders to add the relevant folders
    for f_name in all_folders:
        
        #Do not add folder names with zip or csv
        if(not('zip' in f_name or 'csv' in f_name)):
            if('BZC' in f_name or 
               'CZC' in f_name or
               'LZC' in f_name or
               'RZC' in f_name):

                #Add the folder name to the list
                target_folders.append(f_name)

    #Return the list with the correct folders specified
    return target_folders


# In[10]:


#Function to compute the csv for the parsed folder directory
def compute_csv(folder_directory):
    
    #Obtain all the files in the current directory
    files = os.listdir(folder_directory)
    
    #Loop all the files to only select gif files
    for file in files:
        #If 'gif' is not in the file
        if(not('gif' in file)):
            #Remove the file from the list
            files.remove(file)
            
    #Progress bar for the images computed
    pbar = tqdm(total=len(files),position = 0, desc = folder_directory)
    
    #Declare an empty list to add the data contained in the folder
    output = []
    
    #Loop all the images in the files list
    for image in files:
        #Compute the array of the image
        image_array = list(compute_array(folder_directory,image))
        
        #If the list is not empty
        if(not(image_array == [])):
            #Add the computed array to the output
            output = output + image_array
        
        #Release the memory storing image_array
        image_array = None
        
        #Update the progress bar
        pbar.update(1)
    
    #Split the location into list
    save_location = folder_directory.split('/')
    #Add name of folder that will store the extracted radar data
    save_location.insert(2,'Extracted Radar Data')
    #location of folder which will contain data
    create_folder_path = "/".join(save_location[:len(save_location)-1])
    #set location for the saving of the csv file
    save_location = "/".join(save_location)
    
    #If the 'Extracted Data' folder does not yet exist
    if(not(os.path.exists(create_folder_path))):
        #Create the 'Extracted Data' folder in the folder
        os.mkdir(create_folder_path)
    
    #Open a csv file at the save location to write to
    f = open(save_location + '.csv', "w")

    #Save the output to the location specified
    np.savetxt(f,np.array(output),delimiter=',')
    
    #Close the csv file, which saves it correctly
    f.close()
    
    #Close the progress bar
    pbar.close()


# In[5]:


#Function to compute the location and value of the points in the image
#points returned depend on the dictionary of the type of image
def compute_array(location, image):
    
    #Open the image
    img = Image.open(location + "/" + image)

    #Convert the gif grayscale to rgb
    rgb_img = img.convert('RGB')

    #Load the dictionary into memory
    dictionary = dictionary_loader(image[0:3])
    
    #Declare an empty array which will 
    img_values = []
    
    #Store the location of the image in a local variable
    image_location = location + "/" + image
    
    #If the image conists of just two colors it either contains no information or is an error
    if(len(rgb_img.getcolors()) <= 2):
        #Return empty array
        return img_values
    else:

        #Load the timestamp, which is determined from the image name
        timestamp = timestamp_loader(image_location)
        
        #Get the rgb colors contained in the image
        img_rgb_colors = np.asarray(rgb_img.getcolors()).T[1]
        
        #Declare an empty list to store rgb values
        rgb_list = []
        #Loop all the rgb colors in the image
        for i in range(0,len(img_rgb_colors)):
            #Add the rgb value to the list
            rgb_list.append(str(img_rgb_colors[i]))
        
        #Transform list to an array
        img_rgb_colors = np.array(rgb_list)
        
        #Free memory of rgb_list
        rgb_list = None

        #Load the keys of the dictionary
        keys = np.array(list(dictionary.keys()))

        #Perform an intersect to find the colors that are in the image and in the dictionary
        colors_in_dict = np.intersect1d(img_rgb_colors, keys)
        
        #If there are no colors in the image that are also in the dictionary
        if(len(colors_in_dict) == 0):
            #Return an empty array
            return []

        #Declare an empty list to store the colors
        colors = []

        #Loop all the colors in the dictionary
        for color in colors_in_dict:
            #Split the rgb values from the color string
            rgb_values = color.split('(')[1].split(')')[0].split(',')
            #Convert the string to int64
            rgb_color = np.array(rgb_values).astype('int64')
            #Add the array to the colors list
            colors.append(rgb_color)

        #Transform the list to a np array
        colors = np.array(colors)

        #Declare an empty list for the coordinates
        coordinates = []

        #Declare an empty list for the value column that forms part of the output
        value_col = []
        
        #Transform to an array
        rgb_img_np = np.array(rgb_img)

        #Loop all the colors
        for n in range(0,len(colors)):

            #Load the value of the corresponding rgb in the dictionary
            value = dictionary[colors_in_dict[n]]

            #Find the pixels where the current color is present
            pixels = np.where(rgb_img_np == colors[n])

            #Declare an empty list to contain pixels which have 012 sequence in pixels[2]
            list_012 = []

            #Loop all the found pixels to search 012 sequence
            for i in range(0,len(pixels[2])-2):
                #Check whether the 012 is present
                if(pixels[2][i] == 0 and pixels[2][i+1] == 1 and pixels[2][i+2] == 2):
                    #Add the pixel to the list if it is the case
                    list_012.append(i)

            #Loop all the pixels which have 012 sequence
            for j in list_012:
                #Check if the 3 pixel values are the same coordinate 
                if(pixels[0][j] == pixels[0][j+1] == pixels[0][j+2] and 
                   pixels[1][j] == pixels[1][j+1] == pixels[1][j+2]):
                    #Add the coordinate to coordinates list
                    coordinates.append([pixels[1][j],pixels[0][j]])
                    #Add a value entry to the value column list
                    value_col.append([value])

        #Transform the found coordinates to epsg 4326
        coord_cols = transform_coord(coordinates,image_location)

        #Transform to an array
        value_col = np.array(value_col)

        #Create an array for the time column
        time_col = np.ones((len(coord_cols),1))*timestamp

        #Append the coordinates to time_col
        time_coord_cols = np.append(time_col,coord_cols,axis=1)

        #Append value column for the final output
        img_values = np.append(time_coord_cols,value_col,axis=1)
        
        #Return the array with the 4 columns
        #[timestamp, xCoord, yCoord, value]
        return img_values
    


# In[15]:


def timestamp_loader(image_name):
    
    #Split to obtain name of image
    gif_name = image_name.split('.')[0]
    
    #Split to obtain name of image
    gif_name = gif_name.split('/')[-1]
    
    #Load year, day, hour, and minute from gif_name
    year = gif_name[3:5]
    day = gif_name[5:8]
    hour = gif_name[8:10]
    minute = gif_name[10:12]
    
    #Merge the extracted strings into date format
    date_string = " ".join([year,day,hour,minute])
    
    #Return the timestamp of the corresponding date
    return datetime.strptime(date_string,'%y %j %H %M').timestamp()


# In[14]:


#Function to get the offset values of NW corner
def NW_corner_loader(image_location):
    
    #Load the image into a local variable
    img = Image.open(image_location)
    
    #Split the description of the image
    info_list = img.info['comment'].decode().split()
    
    #Loop every element in the description of the image
    for row in info_list:
        
        #Split the element in half
        split_entry = row.split('=')
        
        #If the first half is equal to 'CHXNW'
        if(split_entry[0] == 'CHXNW'):
            #Set the corresponding local variable
            CHXNW = int(split_entry[1])
        
        #If the first half is equal to 'CHYNW'
        if(split_entry[0] == 'CHYNW'):
            #Set the corresponding local variable
            CHYNW = int(split_entry[1])
    
    #Check whether both CHXNW and CHYNW have been loaded
    if(CHXNW == None or CHYNW == None):
        #Print the error code and exit
        print("CHXNW or CHYNW was not found in the description of the file")
        sys.exit(1)
    else:
        #Return the coordinates of the north west corner
        return(np.array([CHYNW,CHXNW]))
    


# In[12]:


#Function to transform EPSG:21781 to EPSG:4326 of a certain image
def transform_coord(coordinates,image_location):
    
    #If coordinates list is empty
    if(coordinates == []):
        #Return an empty array
        return []
    
    #Transform the coordinates list to an array
    np_coord = np.array(coordinates)
    
    #Load the offset values from the image
    xOffset,yOffset = (NW_corner_loader(image_location)*1000)
    
    #Add 500 or subtract 500 to obtain the center of the pixel
    xOffset += 500
    yOffset -= 500
    
    #Create a transformer from epsg 21781 to epsg 4326
    transformer = Transformer.from_crs("epsg:21781","epsg:4326")
    
    #Transform the parsed data using the offset
    transformation = transformer.transform(xOffset+np_coord.T[0]*1000,yOffset-np_coord.T[1]*1000)
    
    #Return the transformation in [x1,y1],[x2,y2] format
    return np.array(transformation).T


# In[13]:


#Set the directory of the unzipped files, should include the dictionary files for each
data_directory = 'D:/Master Project/'

#Obtain a list of the relevant folders using the identify_folders method
relevant_folders = identify_folders(data_directory)

#Loop all the folders
for folder in relevant_folders:
    
    #If there isn't already a csv for this folder
    if(not(os.path.isfile(data_directory + 'Extracted Radar Data/' + folder + '.csv'))):
        #Compute the relevant radar data and export to a csv
        compute_csv(data_directory + folder)


# In[ ]:





# In[ ]:




