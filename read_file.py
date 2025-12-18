import pandas as pd
import streamlit as st


def parse_sheet():
    pd.set_option('display.max_colwidth', None)
    pd.options.mode.chained_assignment = None

    my_sheet = 'Sheet1'
    file_name = 'Civ_bonuses.xlsx'

    df = pd.read_excel(file_name, header=0, names=['tier', 'bonus', 'cul', 'eco', 'war', 'tech'], index_col=None,
                       sheet_name=my_sheet)
    # df.style.set_properties(**{'text-align': 'right'})

    df1 = df[df['tier'] == 1]
    df2 = df[df['tier'] == 2]
    df3 = df[df['tier'] == 3]
    df4 = df[df['tier'] == 4]
    df5 = df[df['tier'] == 5]
    df6 = df[df['tier'] == 6]

    state = st.session_state

    if "df1" not in state:
        state.df1 = df1
    if "df2" not in state:
        state.df2 = df2
    if "df3" not in state:
        state.df3 = df3
    if "df5" not in state:
        state.df5 = df5

    return state.df1, state.df2, state.df3, df4, state.df5, df6
