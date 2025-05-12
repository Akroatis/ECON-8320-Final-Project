import streamlit as st
import pandas as pd
import os
import numpy as np
import plotly.express as px
import datetime as dt


# Uniquely, I encountered a substantial issue using .xlsx on Mac.  To ensure that this works on any computer,
# I've chosen to just use a csv file. This is a limitation, but thankfully a very, very easy one to overcome,
# As you can literally just save an Excel sheet as a .csv file using the 'Save As' function within Excel
dataset = "https://raw.githubusercontent.com/Akroatis/ECON-8320-Final-Project/refs/heads/main/Data%20Set.csv"

df = pd.DataFrame(pd.read_csv(dataset)) 

# The next step is to individually clean columns in such a way that any *new* data will not cause a python conniption
# First, make sure none of these numbers have spaces anywhere
df['Patient ID#'] = df['Patient ID#'].replace(' ', '')

# Next, a quick conversion of the Grant Req Date column to datetime format and a removal of any spaces (just in case)
df['Grant Req Date'] = df['Grant Req Date'].replace(' ', '')
df['Grant Req Date'] = pd.to_datetime(df['Grant Req Date'], errors = 'coerce')
df['Grant Req Date'] = pd.to_datetime(df['Grant Req Date'], '%Y-%m-%d')
#
# DATE FORMAT IS NOW YYYY-MM-DD
#

# The " Remaining Balance " column (those extra spaces are truly a bane) has a few details that really make me scratch my head
# These include punctuation (makes sense) and using a dash whenever a remaining balance is 0 (bro why, like actually)
# Thankfully they're pretty simple to solve as we go in and swap things for what we want them to be, then turn the whole
# set of numbers into real numbers (good old 2 point floats) instead of strings

# This translation function effectively takes all the weird punctuation and swaps it for what I want it to be
# As long as I don't need regex for anything, this will swap individual characters easily.
df[' Remaining Balance '] = df[' Remaining Balance '].str.translate(str.maketrans({'$' : '', ',': '', '-': '0', '(': '-', ')': ''}))
df[' Remaining Balance '] = df[' Remaining Balance '].astype(float).round(2) #And now to make sure it's a real number.

# A fun tidbit on the above two lines is that the float conversion served as a validator/error test 
# for the line above it, since it would lead to an error if all punctuation hadn't been caught

# A simple check to ensure capitalization and spacing is consistent in Request Status
df['Request Status'] = df['Request Status'].str.title() #Capitalizes first letter of every continuous string
df['Request Status'] = df['Request Status'].str.strip() #Removes trailing spaces.  Notably it also breaks numbers, so strings only use case


# Payment Submitted is an interesting column that blends dates with boolean values
# We don't want data loss, but we can't use the date info that's there in any form save boolean
# So, we go with a classic approach, we make a clean boolean version and tack it on as a
# separate column that replaces the old one.  We then save the old one under a new name (not in this order, though)
# Basically what I've done is cast everything into one form (uppercase for consistency throughout project) 

df['Payment Submitted?'] = df['Payment Submitted?'].str.title()
df['Payment Submitted?'] = df['Payment Submitted?'].str.strip()
df['Payment Submitted? Boolean'] = df['Payment Submitted?']
df['Payment Submitted?'] = pd.to_datetime(df['Payment Submitted?'], errors = 'coerce')
df['Payment Submitted?'] = pd.to_datetime(df['Payment Submitted?'], '%Y-%m-%d')

df['Payment Submitted? Boolean'] = df['Payment Submitted? Boolean'].replace('^0-9.*', True, regex = True)
df['Payment Submitted? Boolean'] = df['Payment Submitted? Boolean'].replace('No', False)
df['Payment Submitted? Boolean'] = df['Payment Submitted? Boolean'].replace('Yes', True)

# For the cities, opting to simply remove punctuation and cast as uppercase.  Also replacing missing values with blanks.

df['Pt City'] = df['Pt City'].str.translate(str.maketrans({'.': '', ',': '', '(': '', '?': '', ')': ''}))
df['Pt City'] = df['Pt City'].str.title()
df['Pt City'] = df['Pt City'].str.strip()
df['Pt City'] = df['Pt City'].replace('Missing', np.nan)

# For states, we have to somehow figure out a way to convert full names to abbreviations or vice versa.
# The following function 'state_abbrev_mapping()' is *not* an original of my own design but rather a publicly available version 
# from Medium.com published by Jason C. in April 21, 2023, link below:
# https://medium.com/@jason_the_data_scientist/python-mapping-state-abbreviations-to-state-and-vice-versa-in-pandas-e4cd24edefb0


def state_abbrev_mapping(df, col, output_abbr = False, add_new_col = False, new_col = None,  case = None):
    #df =  the Pandas dataframe.
    #col = String. The column with the state name or abbreviation you wish to use
    #output_abbr = True/False. Do you want to the output to the the state abbreviation? The other option is the state full name.
    #add_new_col = True/False. Do you want to add a new column? The new column will overwrite the inputted column if not.
    #new_col = String. Name of new column you wish to add.
    #case = 'upper', 'lower', or None. Do you want to specify a letter-case for the data?
 
 
    #List of states
    state2abbrev = {
        'Alaska': 'AK',
        'Alabama': 'AL',
        'Arkansas': 'AR',
        'Arizona': 'AZ',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'District of Columbia': 'DC',
        'Delaware': 'DE',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Hawaii': 'HI',
        'Iowa': 'IA',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Massachusetts': 'MA',
        'Maryland': 'MD',
        'Maine': 'ME',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Missouri': 'MO',
        'Mississippi': 'MS',
        'Montana': 'MT',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Nebraska': 'NE',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'Nevada': 'NV',
        'New York': 'NY',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Virginia': 'VA',
        'Vermont': 'VT',
        'Washington': 'WA',
        'Wisconsin': 'WI',
        'West Virginia': 'WV',
        'Wyoming': 'WY',
        'Puerto Rico': 'PR',
        'Virigin Islands': 'VI'
    }
 
    #List of states
    abbrev2state = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming',
        'PR': 'Puerto Rico',
        'VI': 'Virigin Islands'
    }
     
    #If user wants to add a new column
    if add_new_col == False:
         
        #Is the output an abbreviation?
        if output_abbr == True:
            df[col] = df[col].str.strip().replace(state2abbrev)
        else:
            df[col] = df[col].str.strip().replace(abbrev2state)
             
        #Does the user want a specific case sensitivity?
        if case == 'upper':
            df[col] = df[col].str.upper()
        elif case == 'lower':
            df[col] = df[col].str.lower()
             
    #If user not want to add a new column       
    if add_new_col == True:
         
        #If new column name is missing
        if new_col == None:
            #Prompt user to enter a new column name
            print("Error: You requested to add a new column but did not specify a new column name. Please add a column name with new_col = ''")
            return()
         
        #Is the output an abbreviation?
        if output_abbr == True:
            df[new_col] = df[col].str.strip().replace(state2abbrev)
        else:
            df[new_col] = df[col].str.strip().replace(abbrev2state)
 
        #Does the user want a specific case sensitivity?
        if case == 'upper':
            df[new_col] = df[new_col].str.upper()
        elif case == 'lower':
            df[new_col] = df[new_col].str.lower()
 
    return(df)

df['Pt State'] = df['Pt State'].str.title()
df['Pt State'] = df['Pt State'].str.strip()
state_abbrev_mapping(df, 'Pt State')

# With the above function having run, we now have a consistent format for states as their respective names. 
# Now we replace any case of the "Missing" value with blank ones.  We can alter the blanks later if needed, but this is consistent for now.
df['Pt State'] = df['Pt State'].replace('(?i)missing', np.nan, regex = True)

# Someone entered 698863 incorrectly.  Took a manual look at the city and found the zipcode error with a quick Google search
df['Pt Zip'] = df['Pt Zip'].str.replace(" ", "")
df['Pt Zip'] = df['Pt Zip'].replace('698863', '68863')
df['Pt Zip'] = df['Pt Zip'].replace('(?i)missing', np.nan, regex = True)
df['Pt Zip'] = df['Pt Zip'][0:4] # Just the first five digits of the zip code


# Language data cleaning
df['Language'] = df['Language'].str.title()
df['Language'] = df['Language'].str.strip()
df['Language'] = df['Language'].replace('(?i)missing', np.nan, regex = True)
df['Language'] = df['Language'].replace("Karen", np.nan) # I don't know what this was supposed to be.  Instinct says 'Korean', but without proof, this entry must be invalidated
df['Language'] = df['Language'].replace('English, Spanish', 'English') # Keeping things simple at one language


# DOB data cleaning
df['DOB'] = df['DOB'].replace('(?i)missing', np.nan, regex = True)

df['DOB'] = pd.to_datetime(df['DOB'], errors = 'coerce')
df['DOB'] = pd.to_datetime(df['DOB'], '%Y-%m-%d') # Notably some of these are birth year only, so that's the only thing we can really use
df.loc[df['DOB'] > pd.Timestamp.today(), 'DOB'] = pd.NaT # Some people were apparently from the future so I disabled time traveling
df['YOB'] = df['DOB'].dt.year # YOB column for the sake of some data preservation

# Marital Status data cleaning (Yes, I know I had all those fancy descriptions earlier. Truth is, though, https://tenor.com/cZESrBQb5Qu.gif)

df['Marital Status'] = df['Marital Status'].str.title()
df['Marital Status'] = df['Marital Status'].str.strip()
df['Marital Status'] = df['Marital Status'].replace("Seperated", 'Separated')
df['Marital Status'] = df['Marital Status'].replace('(?i)missing', np.nan, regex = True)

# Gender data cleaning
df['Gender'] = df['Gender'].str.title()
df['Gender'] = df['Gender'].str.strip()
df['Gender'] = df['Gender'].replace('Missing', np.nan)


# Race data cleaning
df['Race'] = df['Race'].str.title()
df['Race'] = df['Race'].str.strip()
df['Race'] = df['Race'].replace('(?i)whiate', 'white', regex = True)
df['Race'] = df['Race'].apply(lambda x: "American Indian or Alaskan Native" if "Indian Or" in str(x) else x)
df['Race'] = df['Race'].replace('(?i)decline to answer', np.nan, regex = True)
df['Race'] = df['Race'].replace('(?i)missing', np.nan, regex = True)
df['Race'] = df['Race'].replace('(?i)hispanic', 'Other', regex = True)
df['Race'] = df['Race'].replace('(?i)two or more races', 'Other', regex = True)

# Hispanic or Latino data cleaning.
df['Hispanic/Latino'] = df['Hispanic/Latino'].str.title()
df['Hispanic/Latino'] = df['Hispanic/Latino'].str.strip()
df['Hispanic/Latino'] = df['Hispanic/Latino'].replace('^No.*', False, regex = True)
df['Hispanic/Latino'] = df['Hispanic/Latino'].replace('^His.*', True, regex = True)
df['Hispanic/Latino'] = df['Hispanic/Latino'].replace('Yes', True)
df['Hispanic/Latino'] = df['Hispanic/Latino'].replace('(?i)decline to answer', np.nan, regex = True)
df['Hispanic/Latino'] = df['Hispanic/Latino'].replace('(?i)missing', np.nan, regex = True)

# Sexual Orientation data cleaning.
df['Sexual Orientation'] = df['Sexual Orientation'].str.title()
df['Sexual Orientation'] = df['Sexual Orientation'].str.strip()
df['Sexual Orientation'] = df['Sexual Orientation'].replace('(?i)d.*', np.nan, regex = True)
df['Sexual Orientation'] = df['Sexual Orientation'].replace('(?i)st.*', 'Heterosexual', regex = True)
df['Sexual Orientation'] = df['Sexual Orientation'].replace('(?i)missing', np.nan, regex = True)
df['Sexual Orientation'] = df['Sexual Orientation'].replace('(?i)gay or lesbian', 'Homosexual', regex = True)
df['Sexual Orientation'] = df['Sexual Orientation'].replace('(?i)female', np.nan, regex = True)
df['Sexual Orientation'] = df['Sexual Orientation'].replace('(?i)male', np.nan, regex = True)

# Insuramce Type data cleaning.  It took me this long to realize I could have cast 
# so many other lines with .str.title() *before* approaching for data consistency 
# Wouldn't have even needed any regex had I done that.  Time to go back and fix that.  I guess you live and learn.
df['Insurance Type'] = df['Insurance Type'].str.title()
df['Insurance Type'] = df['Insurance Type'].str.strip()
df['Insurance Type'] = df['Insurance Type'].replace('(?i)uni.*', "Uninsured", regex = True)
df['Insurance Type'] = df['Insurance Type'].replace('Unknown', np.nan)
df['Insurance Type'] = df['Insurance Type'].replace('Missing', np.nan)
df['Insurance Type'] = df['Insurance Type'].replace('Heathcare.gov', np.nan) # This person is insured, but Healthcare.gov is a marketplace to get *any* kind of insurance
df['Insurance Type'] = df['Insurance Type'].replace('Medicaid & Medicare', 'Medicare & Medicaid') # Consistency
df['Insurance Type'] = df['Insurance Type'].replace('Medicare & Other')

# Household Size data cleaning

df['Household Size'] = df['Household Size'].replace(' ','')
df['Household Size'] = df['Household Size'].replace('(?i)missing', np.nan, regex = True)
df['Household Size'] = df['Household Size'].astype(float).round(1)
df.loc[df['Household Size'] > 15] = np.nan # Is 15 totally arbitrary?  Yes, absolutely.  Does it take care of the entry that was over 4,000?  Also yes.

# Household Income data cleaning

df[' Total Household Gross Monthly Income '] = df[' Total Household Gross Monthly Income '].replace(' ', '')
df[' Total Household Gross Monthly Income '] = df[' Total Household Gross Monthly Income '].str.translate(str.maketrans({'$' : '', ',': '', '-': '0', '(': '-', ')': ''}))
df[' Total Household Gross Monthly Income '] = df[' Total Household Gross Monthly Income '].replace('(?i)missing', np.nan, regex = True)
df[' Total Household Gross Monthly Income '] = df[' Total Household Gross Monthly Income '].replace('[.].*[.].*', np.nan, regex = True)
df[' Total Household Gross Monthly Income '] = df[' Total Household Gross Monthly Income '].astype(float).round(2)

# Distance roundtrip data cleaning.  Based on dataset, this one was conveniently super straightforward

df['Distance roundtrip/Tx'] = pd.to_numeric(df['Distance roundtrip/Tx'], errors = 'coerce')

# Referral Source Data cleaning.  These are arguably too much to reliably sift as many new sources could be added.
# To keep things straightforward, I'm opting to simply capitalize everything and remove trailing spaces and
# missing values as a precaution.  What I wish I could have done was used NLP to detect names, match them, and then coerce,
# but my attempt at this failed miserably and I didn't have the time to fix it in the slightest.  Might mess around with this
# in the summer if I really want to push through with the data analytics concentration.  Could use the added practice.

df['Referral Source'] = df['Referral Source'].str.upper()
df['Referral Source'] = df['Referral Source'].str.strip()
df['Referral Source'] = df['Referral Source'].replace('MISSING', np.nan)

# Referred By: data cleaning.  Similar story here as Referral Source.

df['Referred By:'] = df['Referred By:'].str.strip()
df['Referred By:'] = df['Referred By:'].str.upper()
df['Referred By:'] = df['Referred By:'].replace('MISSING', np.nan)

# Type of Assistance data cleaning

df['Type of Assistance (CLASS)'] = df['Type of Assistance (CLASS)'].str.strip()
df['Type of Assistance (CLASS)'] = df['Type of Assistance (CLASS)'].str.title()
df['Type of Assistance (CLASS)'] = df['Type of Assistance (CLASS)'].replace('Multiple', 'Other')
df['Type of Assistance (CLASS)'] = df['Type of Assistance (CLASS)'].replace('Missing', np.nan)

# Amount data cleaning.  At this stage it occurred to me I probably could have just made
# Specific functions that cleaned specific data types, like "Dollar data clean" or "String data clean."
# Hindsight may be 20/20, but boy does it make you feel really stupid sometimes.

df[' Amount '] = df[' Amount '].str.translate(str.maketrans({' ': '', '$' : '', ',': '', '-': '0', '(': '-', ')': ''}))
df[' Amount '] = pd.to_numeric(df[' Amount '], errors = 'coerce')

# Payment Method data cleaning

df['Payment Method Original'] = df['Payment Method'].str.upper() # data preservation
df['Payment Method'] = df['Payment Method'].str.upper()
df['Payment Method'] = df['Payment Method'].replace('.*[C][K].*', 'CK', regex = True)
df['Payment Method'] = df['Payment Method'].replace('.*[C][C].*', 'CC', regex = True)
df['Payment Method'] = df['Payment Method'].replace('.*[G][C].*', 'GC', regex = True)
df['Payment Method'] = df['Payment Method'].replace('.*[J].*[E].*', 'JE', regex = True)
df['Payment Method'] = df['Payment Method'].replace('BANK TRANSACTION', 'OTHER') # Bruteforcing this bothered me, but I was rushing too much the last few days
df['Payment Method'] = df['Payment Method'].replace('NCS DUE TO/FROM', 'OTHER')
df['Payment Method'] = df['Payment Method'].replace('CASH', 'OTHER')
df['Payment Method'] = df['Payment Method'].replace('ACH', 'OTHER')
df['Payment Method'] = df['Payment Method'].replace('EFT', 'OTHER')
df['Payment Method'] = df['Payment Method'].replace('1575.86', 'OTHER')
df['Payment Method'] = df['Payment Method'].replace('?', np.nan)
df['Payment Method'] = df['Payment Method'].replace('MISSING', np.nan)
df['Payment Method'] = df['Payment Method'].replace('PENDING', np.nan)

# Payable to: data cleaning

df['Payable to:'] = df['Payable to:'].str.strip()
df['Payable to:'] = df['Payable to:'].replace('(?i)missing', np.nan, regex = True)

# Patient Letter Notified? data cleaning

df['Patient Letter Notified? (Directly/Indirectly through rep)'] = df['Patient Letter Notified? (Directly/Indirectly through rep)'].replace('[0-9].*', True, regex = True)
df['Patient Letter Notified? (Directly/Indirectly through rep)'] = df['Patient Letter Notified? (Directly/Indirectly through rep)'].str.upper()
df['Patient Letter Notified? (Directly/Indirectly through rep)'] = df['Patient Letter Notified? (Directly/Indirectly through rep)'].str.strip()
df['Patient Letter Notified? (Directly/Indirectly through rep)'] = df['Patient Letter Notified? (Directly/Indirectly through rep)'].replace('', np.nan)
df['Patient Letter Notified? (Directly/Indirectly through rep)'] = df['Patient Letter Notified? (Directly/Indirectly through rep)'].replace('MISSING', np.nan)
df['Patient Letter Notified? (Directly/Indirectly through rep)'] = df['Patient Letter Notified? (Directly/Indirectly through rep)'].replace('NA', np.nan)
df['Patient Letter Notified? (Directly/Indirectly through rep)'] = df['Patient Letter Notified? (Directly/Indirectly through rep)'].replace('HOLD', np.nan)
df['Patient Letter Notified? (Directly/Indirectly through rep)'] = df['Patient Letter Notified? (Directly/Indirectly through rep)'].replace('YES', True)
df['Patient Letter Notified? (Directly/Indirectly through rep)'] = df['Patient Letter Notified? (Directly/Indirectly through rep)'].replace('NO', False)


# Application Signed? data cleaning

df['Application Signed?'] = df['Application Signed?'].str.title()
df['Application Signed?'] = df['Application Signed?'].str.strip()
df['Application Signed?'] = df['Application Signed?'].replace('Missing', np.nan)
df['Application Signed?'] = df['Application Signed?'].replace('Yes', True)
df['Application Signed?'] = df['Application Signed?'].replace('No', False)


# Write to new and squeaky clean file
df.to_csv('Cleaned Data Set.csv')


# Well. . . That was exhausting and terribly inefficient.  Time to make the dashboard