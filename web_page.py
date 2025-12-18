import pandas as pd
import streamlit as st
import numpy as np
import time
import state_manager
from random_generator import find_odds

def display_table(table, player_flag, player_name, player_index) -> None:
    start, col1, mid, col2, end = st.columns([0.5, 2.5, 1, 12, 3])

    # Reroll button
    # Logic: disabled=False if state else False -> always False (enabled).
    # If the intention was to disable after reroll, we should check player_flag.
    # But current code seems to allow infinite rerolls or at least doesn't disable.
    # We'll keep it enabled.
    
    click = end.button("Reroll", key=f"reroll_{player_index}")

    if click:
        state_manager.reroll_player(player_index)
        st.rerun()

    # If table is None (e.g. error), return
    if table is None:
        return

    final = table.drop(columns=['cul', 'eco', 'war', 'tech'], axis=1)
    final = final.rename(columns={"bonus": player_name})
    
    # Image
    try:
        nation_name = table.loc['Нация: ', list(table)[0]]
        image_path = 'static/img/' + nation_name + '.png'
        col1.image(image_path, width='stretch')
    except Exception:
        col1.write("Image not found")

    # Extract values for custom rendering
    try:
        bonus1 = final.loc['Бонус 1: ', player_name]
        bonus2 = final.loc['Бонус 2: ', player_name]
        bonus3 = final.loc['Бонус 3: ', player_name]
        tech = final.loc['Технология: ', player_name]
        nation = final.loc['Нация: ', player_name]
    except KeyError:
        # Fallback
        col2.table(final)
        st.markdown("<div style='margin-bottom: 3rem;'></div>", unsafe_allow_html=True)
        return

    html_card = f"""
    <div class="player-info-card">
        <div class="player-name">{player_name}</div>
        <div class="info-row">
            <span class="info-label">Бонус 1:</span>
            <span class="info-value">{bonus1}</span>
        </div>
        <div class="info-row">
            <span class="info-label">Бонус 2:</span>
            <span class="info-value">{bonus2}</span>
        </div>
        <div class="info-row">
            <span class="info-label">Бонус 3:</span>
            <span class="info-value">{bonus3}</span>
        </div>
        <div class="info-row">
            <span class="info-label">Технология:</span>
            <span class="info-value">{tech}</span>
        </div>
        <div class="nation-row">
            <span class="nation-label">Нация:</span>
            <span class="nation-value">{nation}</span>
        </div>
    </div>
    """
    col2.markdown(html_card, unsafe_allow_html=True)

    # Add vertical spacing between players
    st.markdown("<div style='margin-bottom: 3rem;'></div>", unsafe_allow_html=True)


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


def create_web_page(df1, df2, df3, df4, df5, df6, initial_players):
    # Icon List: 🏛️🕌🛕🌍🏙🏰🏦
    st.set_page_config(
        page_title="Civilization RNG",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Add global styling to give the app a modern look
    st.markdown("""
        <style>
        /* Modern font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }

        /* Main background */
        .main {
            background: radial-gradient(circle at top left, #1e293b 0, #020617 55%, #000000 100%);
            color: #e5e7eb;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #020617 0%, #111827 100%);
            border-right: 1px solid rgba(148, 163, 184, 0.4);
        }

        /* Headings */
        h1, h2, h3 {
            color: #f9fafb;
            letter-spacing: 0.03em;
        }

        h1 {
            font-size: 2.1rem;
        }

        h2 {
            font-size: 1.5rem;
        }

        /* Buttons (Reroll, Submit, etc.) */
        .stButton > button {
            background: linear-gradient(90deg, #6366f1, #ec4899);
            color: #f9fafb;
            border: none;
            padding: 0.4rem 1.1rem;
            border-radius: 999px;
            font-weight: 600;
            letter-spacing: 0.05em;
            box-shadow: 0 10px 25px rgba(15, 23, 42, 0.7);
            transition: all 0.18s ease-out;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 14px 35px rgba(15, 23, 42, 0.9);
            filter: brightness(1.02);
        }

        .stButton > button:focus {
            outline: none;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.7);
        }

        /* Tables & dataframes as glassmorphism cards */
        .stTable, .stDataFrame {
            background: radial-gradient(circle at top left, rgba(15, 23, 42, 0.95), rgba(15, 23, 42, 0.9));
            border-radius: 14px;
            border: 1px solid rgba(148, 163, 184, 0.3);
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.95);
            overflow: hidden;
        }

        .stTable table, .stDataFrame table {
            color: #e5e7eb;
            background-color: transparent;
        }

        .stTable th, .stTable td,
        .stDataFrame th, .stDataFrame td {
            border-color: rgba(55, 65, 81, 0.6) !important;
        }

        /* Make images fill their container and scale nicely */
        .stImage {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        .stImage > img {
            width: 100% !important;
            max-width: 100% !important;
            height: auto !important;
            object-fit: contain !important;
            object-position: center !important;
            border-radius: 999px;
            box-shadow: 0 18px 40px rgba(15, 23, 42, 0.95);
        }

        /* Columns behave more like cards in a grid */
        div[data-testid="column"] {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        /* Player Info Card */
        .player-info-card {
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 12px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }

        .player-name {
            font-size: 1.25rem;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 1rem;
            border-bottom: 1px solid rgba(148, 163, 184, 0.2);
            padding-bottom: 0.5rem;
        }

        .info-row {
            display: flex;
            margin-bottom: 0.75rem;
            align-items: baseline;
        }

        .info-label {
            min-width: 120px;
            font-weight: 600;
            color: #94a3b8;
            font-size: 0.95rem;
        }

        .info-value {
            color: #e2e8f0;
            flex: 1;
            font-size: 0.95rem;
        }

        .nation-row {
            margin-top: 1rem;
            background: rgba(99, 102, 241, 0.1);
            padding: 0.75rem;
            border-radius: 8px;
            border: 1px solid rgba(99, 102, 241, 0.3);
            display: flex;
            align-items: center;
        }

        .nation-label {
            font-weight: 600;
            color: #818cf8;
            margin-right: 1rem;
        }

        .nation-value {
            color: #c7d2fe;
            font-weight: 700;
            font-size: 1.1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Load shared state
    shared_state = state_manager.load_state()
    if shared_state is None:
        # Initialize if not exists
        shared_state = state_manager.initialize_state(initial_players)

    players = shared_state['players']
    tables = shared_state['tables']
    player_flags = shared_state['player_flags']
    game_info = shared_state['game_info']
    random_event = shared_state['random_event']

    # Render players
    for i, player_name in enumerate(players):
        if i in tables:
            display_table(tables[i], player_flags[i], player_name, i)

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

        st.write(random_event.loc[':', list(random_event)[1]])

        st.divider()

        seating = game_info['seating']
        map_maker_idx = game_info['map_maker']
        first_player_idx = game_info['first_player']
        
        # Ensure indices are valid
        map_maker_name = players[map_maker_idx] if map_maker_idx < len(players) else players[0]
        first_player_name = players[first_player_idx] if first_player_idx < len(players) else players[0]

        col1, col2 = st.columns([1, 1])
        col1.write('Расположение игроков: ')
        col1.write('Карту раскладывает: ' + map_maker_name)
        col1.write('Первый Игрок: ' + first_player_name)
        col1.write('(GM - Game Master)')

        col2.dataframe(
            seating.style.map(
               color_vowel, subset=(['1', '2', '3', '4'], slice(None))
            ),
            hide_index=True
        )

        if len(players) == 4:
            st.divider()
            # Need to pass tables in correct order: 1, 2, 3, 4
            # tables dict keys are 0, 1, 2, 3
            if 0 in tables and 1 in tables and 2 in tables and 3 in tables:
                table, winner = find_odds(tables[0], tables[1], tables[2], tables[3], players)

                st.header('Вероятности победы, все идут по одному виду победы: ')
                st.dataframe(table, width='stretch')

                st.header('Вероятности победы, общие: ')
                st.dataframe(winner, column_order=('2', '1', '0'),
                             column_config={'0': 'Вероятность', '1': 'Вид победы', '2': 'Игрок'}, width='stretch')

        st.divider()
        st.header("Имена игроков: ")
        
        # Form to update players
        with st.form(key='my_form'):
            # Pre-fill with current names
            new_names = []
            for i in range(5):
                val = players[i] if i < len(players) else ""
                label = f'Введите имя игрока {i+1}: '
                if i < 3: # First 3 mandatory-ish in UI logic?
                    new_names.append(st.text_input(label=label, value=val))
                elif i == 3:
                     # 4th player
                     new_names.append(st.text_input(label=label, value=val))
                elif i == 4:
                     # 5th player
                     new_names.append(st.text_input(label=label, value=val))

            col1, col2 = st.columns([1, 1])
            submit_button = col1.form_submit_button(label='Submit')
            remove_button = col2.form_submit_button(label='Remove')
            reset_button = st.form_submit_button(label='Hard Reset Game')

            if submit_button:
                # Filter empty names
                valid_names = [n for n in new_names if n.strip()]
                # Enforce minimum? The original code had fixed logic. 
                # Let's just pass what we have, but maybe ensure at least 3?
                # Original: if submit... state.players = [t1, t2, t3, t4]...
                
                # Logic to match original strictly:
                # text_input1..4 are always rendered.
                # If we want to support dynamic 3-5, we should check what user entered.
                # Let's trust the valid_names list.
                
                if len(valid_names) < 3:
                     valid_names = valid_names + [f"Player {i+1}" for i in range(len(valid_names), 3)]
                
                state_manager.update_player_names(valid_names)
                st.rerun()

            if remove_button:
                # Remove last player
                if len(players) > 0:
                    new_list = players[:-1]
                    state_manager.update_player_names(new_list)
                    st.rerun()
                    
            if reset_button:
                state_manager.reset_game(initial_players)
                st.rerun()
