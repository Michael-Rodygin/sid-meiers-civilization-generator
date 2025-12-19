import pandas as pd
import streamlit as st
import numpy as np
import time
import os
import base64
import state_manager
from random_generator import find_odds

def display_table(table, player_flag, player_name, player_index) -> None:
    start, col1, mid, col2, end = st.columns([0.5, 3.5, 1, 12, 3])

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

    # Nation image (outside collapsible card)
    try:
        image_path = 'static/img/' + str(nation) + '.png'
        col1.image(image_path, width='stretch')
    except Exception:
        col1.write("Image not found")

    # Determine Title based on Nation
    nation_titles = {
        'Американцы': 'Президент',
        'Арабы': 'Султан',
        'Ацтеки': 'Тлатоани',
        'Греки': 'Архонт',
        'Египтяне': 'Фараон',
        'Зулусы': 'Инкоси',
        'Испанцы': 'Король',
        'Индийцы': 'Махараджа',
        'Китайцы': 'Хуанди',
        'Монголы': 'Хан',
        'Немцы': 'Канцлер',
        'Римляне': 'Император',
        'Русские': 'Царь',
        'Французы': 'Король',
        'Японцы': 'Сёгун',
        'Англичане': 'Король'
    }
    title = nation_titles.get(nation, 'Лидер')
    full_name = f"{title} {player_name}"

    html_card = f"""
    <div class="player-info-card">
        <div class="player-name">{full_name}</div>
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
    with col2.expander(full_name, expanded=True):
        st.markdown(html_card, unsafe_allow_html=True)

    # Add vertical spacing between players
    st.markdown("<div style='margin-bottom: 3rem;'></div>", unsafe_allow_html=True)


def create_web_page(df1, df2, df3, df4, df5, df6, initial_players):
    # Icon List: 🏛️🕌🛕🌍🏙🏰🏦
    st.set_page_config(
        page_title="Civilization RNG",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Add global styling to give the app a Strategy Game look
    st.markdown("""
        <style>
        /* Import Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');

        html, body, [class*="css"] {
            font-family: 'Crimson Text', serif;
        }

        h1, h2, h3, .stButton > button, .nation-label, .player-name, .seating-header {
            font-family: 'Cinzel', serif;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* Main background - Dark Parchment/Tabletop feel */
        .main {
            background-color: #1a1a1d;
            background-image: 
                linear-gradient(rgba(26, 26, 29, 0.92), rgba(26, 26, 29, 0.95)),
                url("https://www.transparenttextures.com/patterns/aged-paper.png");
            color: #d4c5a3;
        }

        /* Sidebar - Darker Leather/Wood feel */
        [data-testid="stSidebar"] {
            background-color: #0f0f11;
            border-right: 2px solid #3d342b;
        }
        
        [data-testid="stSidebar"] * {
            color: #b0a085;
        }

        /* Headings */
        h1 {
            color: #c9a959; /* Gold */
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
            border-bottom: 2px solid #3d342b;
            padding-bottom: 0.5rem;
        }

        h2 {
            color: #a6916e;
            border-bottom: 1px solid #3d342b;
            padding-bottom: 0.2rem;
        }

        /* Buttons (Reroll, Submit, etc.) - Metallic/Stone */
        .stButton > button {
            background: linear-gradient(to bottom, #4a4a4f, #2c2c30);
            color: #d4c5a3;
            border: 1px solid #6b5c47;
            padding: 0.5rem 1.5rem;
            border-radius: 2px;
            font-weight: 700;
            text-shadow: 0 1px 2px black;
            box-shadow: 0 4px 6px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1);
            transition: all 0.2s ease;
        }

        .stButton > button:hover {
            background: linear-gradient(to bottom, #5a5a60, #3c3c40);
            color: #fff;
            border-color: #c9a959;
            transform: translateY(-1px);
        }

        /* Player Info Card - Parchment Dossier */
        .player-info-card {
            background: transparent;
            color: #2c241b; /* Ink */
            border: none;
            border-radius: 0;
            padding: 1.5rem;
            box-shadow: none;
            position: relative;
            width: 100%;
            margin: 0;
            box-sizing: border-box;
        }
        
        /* Decorative corner flourishes (CSS pseudo-elements could go here, keeping it simple) */

        .player-name {
            font-size: 1.5rem;
            font-weight: 700;
            color: #4a0404; /* Deep Red */
            margin-bottom: 1rem;
            border-bottom: 2px solid #8b4513;
            padding-bottom: 0.5rem;
            text-align: center;
        }

        .info-row {
            display: flex;
            margin-bottom: 0.5rem;
            align-items: baseline;
            border-bottom: 1px dashed #bdaea3;
            padding-bottom: 0.2rem;
            gap: 0.5rem;
        }

        .info-label {
            min-width: 130px;
            font-weight: 600;
            color: #5c4033;
            font-size: 1rem;
            font-variant: small-caps;
        }

        .info-value {
            color: #2c241b;
            flex: 1;
            font-size: 1.1rem;
            font-weight: 600;
            word-wrap: break-word;
            white-space: normal;
        }

        .nation-row {
            margin-top: 1.2rem;
            background: #2c241b;
            padding: 1rem;
            border: 2px solid #c9a959;
            display: flex;
            align-items: center;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
        }

        .nation-label {
            font-weight: 700;
            color: #c9a959;
            margin-right: 1rem;
            font-size: 1.2rem;
        }

        .nation-value {
            color: #fff;
            font-weight: 700;
            font-size: 1.3rem;
            font-family: 'Cinzel', serif;
            text-shadow: 0 0 5px #c9a959;
        }

        /* Images - Framed */
        .stImage > img {
            border: 4px ridge #c9a959;
            box-shadow: 0 5px 15px rgba(0,0,0,0.6);
            border-radius: 2px;
            width: 100% !important;
        }

        /* Seating Plan - Map Table Style */
        .seating-container {
            background: #2c241b;
            border: 8px solid #3d342b;
            border-image: linear-gradient(to bottom right, #5c4033, #3d342b) 1;
            padding: 1rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }

        .seating-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            background: url("https://www.transparenttextures.com/patterns/dark-leather.png");
            padding: 10px;
            border: 1px solid #5c4033;
        }

        .seating-cell {
            aspect-ratio: 1;
            border: 1px solid #5c4033;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Cinzel', serif;
            font-weight: 700;
            font-size: 0.9rem;
            color: #d4c5a3;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
            text-shadow: 1px 1px 2px black;
        }

        .cell-table {
            background: #3e5c76; /* Muted Blue map water/cloth */
            opacity: 0.8;
            border: 1px solid #587999;
        }
        
        .cell-empty {
            background: transparent;
            border: 1px dashed #5c4033;
            opacity: 0.3;
        }

        .cell-player {
             /* Player cells will get specific colors inline, but we add texture here */
             background-image: linear-gradient(rgba(255,255,255,0.1), rgba(0,0,0,0.2));
             border: 2px solid rgba(255,255,255,0.2);
        }

        /* Tables (Dataframes) */
        .stDataFrame {
            border: 2px solid #3d342b !important;
        }
        .stDataFrame table {
             color: #d4c5a3 !important;
        }
        .stDataFrame th {
            background-color: #2c241b !important;
            color: #c9a959 !important;
            font-family: 'Cinzel', serif !important;
            border-bottom: 1px solid #c9a959 !important;
        }
        .stDataFrame td {
            background-color: rgba(44, 36, 27, 0.8) !important;
            border-bottom: 1px solid #3d342b !important;
        }
        
        /* Input Fields */
        .stTextInput > div > div > input {
            background-color: #2c241b;
            color: #d4c5a3;
            border: 1px solid #5c4033;
            font-family: 'Crimson Text', serif;
        }
        .stTextInput > div > div > input:focus {
            border-color: #c9a959;
            box-shadow: 0 0 5px rgba(201, 169, 89, 0.5);
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
            background-color: #1a1a1d;
            background-image: 
                linear-gradient(rgba(26, 26, 29, 0.92), rgba(26, 26, 29, 0.95)),
                url("https://www.transparenttextures.com/patterns/aged-paper.png");
            padding: 0.5rem;
            border-bottom: 2px solid #3d342b;
        }

        .stTabs [data-baseweb="tab-panel"] {
            background: transparent;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: #2c2c30;
            color: #888;
            border: 1px solid #3d342b;
            border-bottom: none;
            border-radius: 4px 4px 0 0;
            padding: 0.5rem 1.5rem;
            font-family: 'Cinzel', serif;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #3d342b;
            color: #c9a959;
            border: 1px solid #c9a959;
            border-bottom: none;
        }

        [data-testid="stExpander"] [data-testid="stExpanderContent"] {
            padding: 0 !important;
        }
        [data-testid="stExpander"] [data-testid="stExpanderContent"] > div {
            padding: 0 !important;
            margin: 0 !important;
        }
        [data-testid="stExpander"] [data-testid="stMarkdownContainer"] {
            padding: 0 !important;
            margin: 0 !important;
        }
        /* Style the expander itself as the parchment card */
        [data-testid="stExpander"] {
            border: 4px double #3d342b !important;
            background: #e3dac3 !important;
            box-shadow: 0 10px 20px rgba(0,0,0,0.5) !important;
        }
        /* Give the header a subtle parchment look */
        [data-testid="stExpander"] div[role="button"] {
            background: #e3dac3 !important;
            border-bottom: 2px solid #8b4513 !important;
            color: #000 !important;
            opacity: 1 !important;
            font-family: 'Cinzel', serif !important;
            letter-spacing: 0.05em !important;
        }
        [data-testid="stExpander"] div[role="button"] * {
            color: #000 !important;
        }

        @media (max-width: 640px) {
            .player-info-card {
                padding: 1rem;
            }
            .info-label {
                min-width: 60px;
                font-size: 0.95rem;
            }
            .info-row {
                padding-bottom: 0.15rem;
                gap: 0.4rem;
            }
            .info-value {
                font-size: 1.05rem;
                line-height: 1.4;
            }
        }

        </style>
    """, unsafe_allow_html=True)

    # Load shared state
    shared_state = state_manager.load_state()
    if shared_state is None:
        # Initialize if not exists
        shared_state = state_manager.initialize_state(initial_players)

    # Track state file modification time for auto-refresh
    try:
        st.session_state.last_mtime = os.path.getmtime(state_manager.STATE_FILE)
    except OSError:
        st.session_state.last_mtime = 0

    players = shared_state['players']
    tables = shared_state['tables']
    player_flags = shared_state['player_flags']
    game_info = shared_state['game_info']
    random_event = shared_state['random_event']

    # Render players
    tab1, tab2 = st.tabs(["🏛️ Civilizations", "🗺️ Strategic Map"])

    with tab1:
        st.header("The Council of Leaders")
        for i, player_name in enumerate(players):
            if i in tables:
                table_i = tables[i]
                if table_i is not None and str(player_name).strip():
                    display_table(table_i, player_flags[i], player_name, i)

    with tab2:
        st.header("Strategic Overview")
        
        # Center the map and restrict width
        col_map_container = st.container()
        
        with col_map_container:
            seating = game_info['seating']
            map_maker_idx = game_info['map_maker']
            first_player_idx = game_info['first_player']
            map_b64 = None
            try:
                with open("static/img/map.png", "rb") as f:
                    map_b64 = base64.b64encode(f.read()).decode()
            except Exception:
                map_b64 = None
             
            # Ensure indices are valid
            map_maker_name = players[map_maker_idx] if map_maker_idx < len(players) else players[0]
            first_player_name = players[first_player_idx] if first_player_idx < len(players) else players[0]
    
            # Strategy seating plan rendering
            st.markdown('<div style="margin-top: 1rem; margin-bottom: 0.5rem; font-weight: 600; color: #a6916e; font-family: Cinzel, serif; font-size: 1.2rem; text-align: center;">Territorial Arrangement</div>', unsafe_allow_html=True)
            
            def get_cell_style(val):
                if val == ' ':
                    return 'cell-table', ''
                if not val or not val.strip():
                    return 'cell-empty', ''
                
                # Player colors - muted/heraldic
                colors = {
                    'Даня': '#8b0000', # Dark Red
                    'Дима': '#cc5500', # Burnt Orange
                    'Папа': '#006400', # Dark Green
                    'Миша': '#00008b', # Dark Blue
                    'Слава': '#4b0082', # Indigo
                }
                bg = colors.get(val, '#696969') # Dim Gray
                return 'cell-player', f'background-color: {bg}; box-shadow: inset 0 0 10px rgba(0,0,0,0.5); border: 2px solid #c9a959;'
    
            # Use max-width to make it smaller and margin auto to center
            seating_html = '<div class="seating-container" style="max-width: 400px; margin: 0 auto;"><div class="seating-grid">'
            
            # Iterate by index to handle merging
            rows = len(seating)
            cols = len(seating.columns)
            
            for r in range(rows):
                for c in range(cols):
                    # Check if this is part of the 2x2 table block (r=1,2 and c=1,2)
                    if r == 1 and c == 1:
                        if map_b64:
                            seating_html += f'<div class="seating-cell cell-table" style="grid-column: span 2; grid-row: span 2; background-image: url(\'data:image/png;base64,{map_b64}\'); background-size: cover; background-position: center;"></div>'
                        else:
                            seating_html += '<div class="seating-cell cell-table" style="grid-column: span 2; grid-row: span 2;"></div>'
                    elif (r == 1 and c == 2) or (r == 2 and c == 1) or (r == 2 and c == 2):
                        # Other parts of the block: Skip
                        continue
                    else:
                        # Normal cell
                        # Get value using iloc
                        val = seating.iloc[r, c]
                        cls, style = get_cell_style(val)
                        seating_html += f'<div class="seating-cell {cls}" style="{style}">{val if val != " " else ""}</div>'
            
            seating_html += '</div></div>'
            st.markdown(seating_html, unsafe_allow_html=True)
    
            st.markdown(f"""
            <div style="margin-top: 1rem; max-width: 400px; margin-left: auto; margin-right: auto; padding: 1rem; background: #2c241b; border: 2px solid #3d342b; border-left: 4px solid #c9a959;">
                <div style="font-size: 1rem; color: #b0a085;">Map Architect: <span style="color: #d4c5a3; font-weight: 700; font-family: Cinzel, serif;">{map_maker_name}</span></div>
                <div style="font-size: 1rem; color: #b0a085; margin-top: 0.5rem;">First Sovereign: <span style="color: #d4c5a3; font-weight: 700; font-family: Cinzel, serif;">{first_player_name}</span></div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # Odds section at the bottom
        if len(players) == 4:
            # Need to pass tables in correct order: 1, 2, 3, 4
            # tables dict keys are 0, 1, 2, 3
            if 0 in tables and 1 in tables and 2 in tables and 3 in tables:
                table, winner = find_odds(tables[0], tables[1], tables[2], tables[3], players)

                st.markdown('<div class="seating-header" style="color: #c9a959; font-size: 1.2rem; margin-bottom: 0.5rem;">Victory Probabilities (Single Type)</div>', unsafe_allow_html=True)
                st.dataframe(table, width='stretch')

                st.markdown('<div class="seating-header" style="color: #c9a959; font-size: 1.2rem; margin-top: 1rem; margin-bottom: 0.5rem;">Overall Victory Odds</div>', unsafe_allow_html=True)
                st.dataframe(winner, column_order=('2', '1', '0'),
                             column_config={'0': 'Probability', '1': 'Victory Type', '2': 'Leader'}, width='stretch')
        else:
             st.info("Victory odds are only available for 4 players.")


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
        
        # New Game button
        if st.button('New Game', key='new_game_top', use_container_width=True):
             state_manager.reset_game(initial_players)
             st.rerun()

        st.divider()
        st.header("Global Event")

        if st.button("Generate Event", key="gen_event_btn", use_container_width=True):
             state_manager.generate_new_event()
             st.rerun()

        event_text = random_event.loc[':', list(random_event)[1]]
        st.info(f"📜 {event_text}")

        st.divider()

        seating = game_info['seating']
        map_maker_idx = game_info['map_maker']
        first_player_idx = game_info['first_player']
        
        # Ensure indices are valid
        map_maker_name = players[map_maker_idx] if map_maker_idx < len(players) else players[0]
        first_player_name = players[first_player_idx] if first_player_idx < len(players) else players[0]

        # Strategy seating plan rendering
        st.markdown('<div style="margin-top: 1rem; margin-bottom: 0.5rem; font-weight: 600; color: #a6916e; font-family: Cinzel, serif; font-size: 1.2rem;">Territorial Arrangement</div>', unsafe_allow_html=True)
        
        def get_cell_style(val):
            if val == ' ':
                return 'cell-table', ''
            if not val or not val.strip():
                return 'cell-empty', ''
            
            # Player colors - muted/heraldic
            colors = {
                'Даня': '#8b0000', # Dark Red
                'Дима': '#cc5500', # Burnt Orange
                'Папа': '#006400', # Dark Green
                'Миша': '#00008b', # Dark Blue
                'Слава': '#4b0082', # Indigo
            }
            bg = colors.get(val, '#696969') # Dim Gray
            return 'cell-player', f'background-color: {bg}; box-shadow: inset 0 0 10px rgba(0,0,0,0.5); border: 2px solid #c9a959;'

        seating_html = '<div class="seating-container"><div class="seating-grid">'
        
        # Iterate rows
        for idx in seating.index:
             for col in seating.columns:
                 val = seating.loc[idx, col]
                 cls, style = get_cell_style(val)
                 seating_html += f'<div class="seating-cell {cls}" style="{style}">{val if val != " " else ""}</div>'
        
        seating_html += '</div></div>'
        st.markdown(seating_html, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="margin-top: 1rem; padding: 0.75rem; background: rgba(30,41,59,0.5); border-radius: 8px; border-left: 3px solid #38bdf8;">
            <div style="font-size: 0.9rem; color: #94a3b8;">Карту раскладывает: <span style="color: #e2e8f0; font-weight: 600;">{map_maker_name}</span></div>
            <div style="font-size: 0.9rem; color: #94a3b8; margin-top: 0.25rem;">Первый Игрок: <span style="color: #e2e8f0; font-weight: 600;">{first_player_name}</span></div>
        </div>
        """, unsafe_allow_html=True)

        if False:
            pass

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
                    new_names.append(st.text_input(label=label, value=val, key=f'player_name_{i}'))
                elif i == 3:
                     # 4th player
                     new_names.append(st.text_input(label=label, value=val, key=f'player_name_{i}'))
                elif i == 4:
                     # 5th player
                     new_names.append(st.text_input(label=label, value=val, key=f'player_name_{i}'))

            col1, col2 = st.columns([1, 1])
            submit_button = col1.form_submit_button(label='Submit')
            remove_button = col2.form_submit_button(label='Remove')

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

    # Continuous file-change sync across clients
    while True:
        time.sleep(2)
        try:
            new_mtime = os.path.getmtime(state_manager.STATE_FILE)
            if new_mtime > st.session_state.last_mtime:
                st.session_state.last_mtime = new_mtime
                st.rerun()
        except OSError:
            pass
