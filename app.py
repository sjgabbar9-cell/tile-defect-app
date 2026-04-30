
# Streamlit Defect Analysis App
import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Defect Analysis", layout="wide")

if 'page' not in st.session_state:
    st.session_state.page='home'
if 'defects' not in st.session_state:
    st.session_state.defects={}
if 'basic' not in st.session_state:
    st.session_state.basic={}

st.image('logo.png', width=180)
st.markdown("## Welcome to **Defect Analysis Report**")

if st.session_state.page=='home':
    if st.button('➕ Add New Defect Report'):
        st.session_state.page='basic'

elif st.session_state.page=='basic':
    st.session_state.basic['SKU']=st.text_input('SKU')
    st.session_state.basic['Batch']=st.text_input('Batch')
    if st.button('Continue'):
        st.session_state.page='summary'

elif st.session_state.page=='summary':
    tiles=st.number_input('Tiles in Batch',1)
    defects=st.number_input('Defect Tiles',0)
    if tiles>0:
        st.metric('Defect / Tile', round(defects/tiles,4))
    if st.button('Save'):
        df=pd.DataFrame([{
            'Date':datetime.now(),
            **st.session_state.basic,
            'Tiles':tiles,
            'Defects':defects
        }])
        os.makedirs('data', exist_ok=True)
        file='data/defect_log.csv'
        if os.path.exists(file):
            df.to_csv(file, mode='a', header=False, index=False)
        else:
            df.to_csv(file, index=False)
        st.success('Saved')
