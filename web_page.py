import pandas as pd
import streamlit as st
import numpy as np
import time
from random_generator import random_distribution, find_odds, player_seating, shuffle_slice
import random


def display_table(table, state, player, df1, df2, df3, df4, df5) -> tuple:
    start, col1, mid, col2, end = st.columns([1, 1, 3.5, 14, 4])

    click = end.button("Reroll", key=player, disabled=False if state else False)

    if click:
        df_player = random_distribution(df1, df2, df3, df4, df5)
        table = df_player if df_player is not None else table
        state = True
        time.sleep(1)

    final = table.drop(columns=['cul', 'eco', 'war', 'tech'], axis=1)
    final = final.rename(columns={"bonus": player})
    image_path = 'static/img/' + table.loc['Нация: ', list(table)[0]] + '.png'
    col1.image(image_path, width=250)
    col2.table(final)

    return table, state


def color_vowel(value):
    if value == ' ':
        return f"background-color: CornFlowerBlue;"
    if value == 'Даня':
        return f"background-color: Red;"
    if value == 'Дима':
        return f"background-color: Orange;"
    if value == 'Папа':
        return f"background-color: Green;"
    if value == 'Миша':
        return f"background-color: RoyalBlue;"
    if value == 'Слава':
        return f"background-color: MediumOrchid;"

    return None


def create_web_page(df1, df2, df3, df4, df5, df6, players):
    # Icon List: 🏛️🕌🛕🌍🏙🏰🏦
    st.set_page_config(
        page_title="Civilization RNG",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    state = st.session_state

    if "players" not in state:
        players = shuffle_slice(players)
        state.players = players

    # Player 1

    if "table1" not in state:
        df_player1 = random_distribution(df1, df2, df3, df4, df5)
        state.table1 = df_player1
    if "p1" not in state:
        state.p1 = False

    state.table1, state.p1 = display_table(state.table1, state.p1, state.players[0], df1, df2, df3, df4, df5)

    # Player 2

    if "table2" not in state:
        df_player2 = random_distribution(df1, df2, df3, df4, df5)
        state.table2 = df_player2
    if "p2" not in state:
        state.p2 = False

    state.table2, state.p2 = display_table(state.table2, state.p2, state.players[1], df1, df2, df3, df4, df5)

    # Player 3

    if "table3" not in state:
        df_player3 = random_distribution(df1, df2, df3, df4, df5)
        state.table3 = df_player3
    if "p3" not in state:
        state.p3 = False

    state.table3, state.p3 = display_table(state.table3, state.p3, state.players[2], df1, df2, df3, df4, df5)

    # Player 4
    if len(state.players) > 3:
        if "table4" not in state:
            df_player4 = random_distribution(df1, df2, df3, df4, df5)
            state.table4 = df_player4
        if "p4" not in state:
            state.p4 = False

        state.table4, state.p4 = display_table(state.table4, state.p4, state.players[3], df1, df2, df3, df4, df5)

    # Player 5
    if len(state.players) == 5:

        if "table5" not in state:
            df_player5 = random_distribution(df1, df2, df3, df4, df5)
            state.table5 = df_player5
        if "p5" not in state:
            state.p5 = False

        state.table5, state.p5 = display_table(state.table5, state.p5, state.players[4], df1, df2, df3, df4, df5)

    # Sidebar content

    with st.sidebar.container():
        st.markdown("""
          <style>
            .st-emotion-cache-1mi2ry5.eczjsme9 {
              margin-top: -75px;
            }
          </style>
        """, unsafe_allow_html=True)

        st.image('static/img/logo.png')

        st.divider()
        st.header("Случайное событие: ")

        if "df6" not in state:
            state.df6 = df6.sample(random_state=np.random.RandomState())
            state.df6.index = [':']

        st.write(state.df6.loc[':', list(state.df6)[1]])

        st.divider()

        if "seating" not in state:
            seating = player_seating(state.players)
            state.seating = seating
        if "map_maker" not in state:
            state.map_maker = random.randint(0, len(state.players) - 1)
        if "first_player" not in state:
            state.first_player = random.randint(0, len(state.players) - 1)

        col1, col2 = st.columns([1, 1])
        col1.write('Расположение игроков: ')
        col1.write('Карту раскладывает: ' + state.players[state.map_maker])
        col1.write('Первый Игрок: ' + state.players[state.first_player])
        col1.write('(GM - Game Master)')

        col2.dataframe(
            state.seating.style.map(
               color_vowel, subset=(['1', '2', '3', '4'], slice(None))
            ),
            hide_index=True
        )

        if len(state.players) == 4:
            st.divider()
            table, winner = find_odds(state.table1, state.table2, state.table3, state.table4, state.players)

            st.header('Вероятности победы, все идут по одному виду победы: ')
            st.dataframe(table, use_container_width=True)

            st.header('Вероятности победы, общие: ')
            st.dataframe(winner, column_order=('2', '1', '0'),
                         column_config={'0': 'Вероятность', '1': 'Вид победы', '2': 'Игрок'}, use_container_width=True)

        st.divider()
        st.header("Имена игроков: ")
        with st.form(key='my_form'):
            text_input1 = st.text_input(label='Введите имя игрока 1: ', value=state.players[0])
            text_input2 = st.text_input(label='Введите имя игрока 2: ', value=state.players[1])
            text_input3 = st.text_input(label='Введите имя игрока 3: ', value=state.players[2])
            if len(state.players) > 3:
                text_input4 = st.text_input(label='Введите имя игрока 4: ', value=state.players[3])
            if len(state.players) == 5:
                text_input5 = st.text_input(label='Введите имя игрока 5: ', value=state.players[4])

            col1, col2 = st.columns([1, 1])
            submit_button = col1.form_submit_button(label='Submit')
            remove_button = col2.form_submit_button(label='Remove')

            if submit_button:
                state.players = [text_input1, text_input2, text_input3, text_input4]
                if len(state.players) > 3:
                    state.players.append(text_input4)
                if len(state.players) == 5:
                    state.players.append(text_input5)
                state.seating = player_seating(state.players)

            if remove_button:
                state.players = state.players[:-1]
                state.seating = player_seating(state.players)
                state.map_maker = random.randint(0, len(state.players) - 1)
                state.first_player = random.randint(0, len(state.players) - 1)

                st.rerun()
