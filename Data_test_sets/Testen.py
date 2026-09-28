import streamlit as st

# pylint: disable=no-member

def only_check_columns(df):
    '''
    Controleert of alle vereiste kolommen aanwezig zijn
    en of er geen verkeerde kolommen aanwezig zijn.

    Return:
        True als alle kolommen correct zijn
        False als er iets fout is
    '''

    columns = df.columns.tolist()
    good_columns = ['Order', 'Surface', 'Colour', 'Deadline', 'Penalty']

    if columns == good_columns:
        return True
    else:
        return False


def check_columns(df):
    '''
    Geeft aan welke kolommen ontbreken of verkeerd zijn.
    '''

    columns = df.columns.tolist()
    good_columns = ['Order', 'Surface', 'Colour', 'Deadline', 'Penalty']

    fout = False

    # Ontbrekende kolommen
    for column in good_columns:
        if column not in columns:
            st.error(f'Kolom "{column}" ontbreekt.')
            fout = True

    # Onbekende/verkeerde kolommen
    for column in columns:
        if column not in good_columns:
            st.error(f'Kolom "{column}" is onbekend.')
            fout = True

    if fout is False:
        st.success('Alle kolommen zijn correct.')


def check_all(df):
    '''
    Voert alle controles uit.
    '''

    kolommen_correct = only_check_columns(df)

    if kolommen_correct is True:
        st.success('De data is compleet')
    else:
        st.error('Data is incorrect')

        if st.button('Klik hier voor details'):
            check_columns(df)