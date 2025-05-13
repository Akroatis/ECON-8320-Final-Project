import streamlit as st
import os
import plotly.express as px
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

df = pd.read_csv("Cleaned Data Set.csv", index_col = 0)
df = df.drop('Payment Submitted? Boolean', axis = 1) # Removing columns that exist solely for data preservation
dfYOB = df
df = df.drop('YOB', axis = 1)
df = df.drop('Payment Method Original', axis = 1)

# Some columns are apparently placeholders produced by some of the cleaning code,
# This code removes those placeholder columns after loading the data in
df = df.loc[:, ~df.columns.str.contains('^Unnamed', regex = True)]

# Initial formatting
st.set_page_config(
    page_title = "Nebraska Cancer Specialists Hope Foundation Grant Information Dashboard",
    layout = 'wide'
)

st.title("Nebraska Cancer Specialists Hope Foundation Grant Information Dashboard")
st.logo(
    image = "https://www.bricksrus.com/donorsite/images/logo-NCSHF.png",
    icon_image = "https://ncshopefoundation.org/wp-content/uploads/2023/05/sun.webp"
)


# The following are pages within the dashboard

# First page for checking on Application Status.  Admittedly quite barebones.  Only added feature is the ability
# To toggle if an unknown signature status should be treated as unsigned.
def appsReadyForReview():
    with st.form(key = "stat_and_sig_form"):
        appStatus = ["Pending", "Approved", "Denied"]
        sigStatus = [True, False]

        st.title("Application Status")
        statusSelection = st.selectbox("Select Application Status", appStatus)
        sigSelection = st.selectbox("Application Signed?", sigStatus)
        coerceNaToNo = st.checkbox(label = 'Treat unknown Signature Status as Unsigned?')


        st.form_submit_button(label = "Filter by Selection")

        if coerceNaToNo == True:
            dfrr = df
            dfrr['Application Signed?'] = dfrr['Application Signed?'].fillna(False)
        else:
            dfrr = df

        dfrr = dfrr.loc[(df['Request Status'] == statusSelection) & (df['Application Signed?'] == sigSelection)]

        st.data_editor(dfrr)
   

# Second page.  Basically this makes a different bar graph based on the selection.

#BUT FIRST. . . A function.  This keeps my displays nice and tidy and shows an average and total support bar graph for each
def demoSelectionDisplay(column = str, demographic = str):
    st.header(f"Average support per grant based on {demographic}")
    st.bar_chart(df.groupby(column)[' Amount '].mean())
    st.header(f"Total support based on {demographic}")
    st.bar_chart(df.groupby(column)[' Amount '].sum())

def supportGiven():
    with st.form(key = "support_given_form"):
        demographics = ['State', 'Gender', 'Monthly Income', 'Insurance Type', 'Age', 'Type of Assistance', 'Hispanic/Latino?', 'Sexual Orientation']

        st.title("Support Given by Demographic")
        demoSelection = st.selectbox("Select Demographic", demographics)
        st.form_submit_button(label = "Filter by Demographic")

        if demoSelection == 'State':
            demoSelectionDisplay('Pt State', 'State')
        
        elif demoSelection == 'Gender':
            demoSelectionDisplay('Gender', 'Gender')
        
        elif demoSelection == 'Monthly Income':
            demoSelectionDisplay(' Total Household Gross Monthly Income ', 'Monthly Income')
        
        elif demoSelection == 'Insurance Type':
            demoSelectionDisplay('Insurance Type', 'Insurance Type')

        elif demoSelection == 'Age':
            df['Age'] = datetime.today().year - dfYOB['YOB']
            demoSelectionDisplay('Age', 'Age')

        elif demoSelection == 'Type of Assistance':
            demoSelectionDisplay('Type of Assistance (CLASS)', 'Type of Assistance')

        elif demoSelection == 'Hispanic/Latino?':
            demoSelectionDisplay('Hispanic/Latino', 'if Hispanic/Latino')

        elif demoSelection == 'Sexual Orientation':
            demoSelectionDisplay('Sexual Orientation', 'Sexual Orientation')

            

def supportWait():

    st.title("Time Between Request and Payment")
    st.write("Note that any entries missing a specific grant request date or payment date are not included in this data.")

    dft = df

    dft = dft.dropna(axis = 0, subset = 'Grant Req Date')
    dft = dft.dropna(axis = 0, subset = 'Payment Submitted?')

    dft['Days Between Request and Payment'] = (pd.to_datetime(dft['Payment Submitted?'], errors = 'coerce') - pd.to_datetime(dft['Grant Req Date'], errors = 'coerce')).dt.days.round(2)
    dft = dft.dropna(axis = 0, subset = 'Days Between Request and Payment')
    
    # Notably the sorting on streamlit for a timedelta is super scuffed and not at all accurate, so without casting the above into days
    # you really get an incorrect sort.

    st.bar_chart(dft['Days Between Request and Payment'].value_counts().sort_index())

# Page 4.  Thankfully a straightforward one, albeit I could have added so much more if I had the time.
def grantBreakdown():
    

    
    dfg = df.loc[(df[' Remaining Balance '] > 0)]


    st.header("Average support per grant based on type of assistance")
    st.bar_chart(df.groupby('Type of Assistance (CLASS)')[' Amount '].mean())

    st.header("Dataframe of all grants not fully used")
    st.write(f"The number of Requestors who did not use their full grant at least once is {dfg["Patient ID#"].nunique()}")
    st.data_editor(dfg)

    # I realized after I had done this and did not have the time that this particular problem is way, way more complicated
    # than this code gives credit.  To actually solve this, one would have to find the last entry from each requestor in a 
    # given grant year, then see if this value is positive and store all entries into a new column or frame.  This code 
    # most certainly *does not* do that, but alas, I was out of both time and ideas.

def execSummary():

    st.title("Executive Summary")
    dfe = df
    datetime.today().year() - 1
    st.dataframe(df)

pageToFunc = {
    "Application Status": appsReadyForReview,
    "Support Given": supportGiven,
    "Waiting Time": supportWait,
    "Grant Usage": grantBreakdown,
    "Executive Summary": execSummary
}

selectedPage = st.sidebar.selectbox("Menu", options = pageToFunc.keys())

pageToFunc[selectedPage]()
