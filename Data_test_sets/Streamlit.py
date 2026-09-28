#URL:
#https://totestdataset.streamlit.app/

# pylint: disable=no-member

from test_data import check_all

import streamlit as st
import pandas as pd

st.header('Data check')

bestand = st.file_uploader('Upload een planning', type=['xlsx'])

if bestand is not None:
    df = pd.read_excel(bestand)

    check_all(df)
