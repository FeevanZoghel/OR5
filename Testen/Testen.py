import pandas as pd
import numpy as np
import random
import math as m
import matplotlib.pyplot as plt

random.seed(42)

testbestand = 'Test01_HappyFlow.xlsx'

df = pd.read_excel(f'Testen/{testbestand}', sheet_name=None)

def only_check_columns(df):
    '''

    Alleen kolommen checken

    return:
        alleen of de kolummen fout zijn of correct

    '''

    fout = False

    columns = df.columns.tolist()
    good_columns = ['Order', 'Surface', 'Colour', 'Deadline', 'Penalty']

    for i in columns:
        if i not in good_columns:
            fout = True
            return False

    if fout is False:
        return True

def check_columns(df):
    """
    
    Checken of de kolommen uit de gegeven dataset correct zijn

    Hij checkt per kolom of die data mist / of er spelfouten in de kolomnamen zitten.

    En print dan ook waar de fout zit


    """
    fout = False

    columns = df.columns.tolist()
    good_columns = ['Order', 'Surface', 'Colour', 'Deadline', 'Penalty']

    if len(columns) != len(good_columns):
        st.error('The number of columns is incorrect')
        fout = True

    else:
        for i in range(len(columns)):
            if columns[i] != good_columns[i]:
                st.error(f'Column "{columns[i]}" is wrong. It should be "{good_columns}".')

    if fout == False:
        return True

def check_all(df): 
    '''
    Check alles
    '''

    kolommen_correct = only_check_columns(df)

    if kolommen_correct is True:
        st.succes('De data is compleet')
    else:
        st.error('Data is incorrect')
        if st.button('klik hier voor details'):
            check_columns(df)
