import pickle
import os
import json
import pandas as pd
import numpy as np
import random
from read_file import parse_sheet
from random_generator import random_distribution, player_seating, shuffle_slice

STATE_FILE = 'game_state.pkl'
PLAYER_NAMES_FILE = 'player_names.json'

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return None
    return None

def save_state(state):
    with open(STATE_FILE, 'wb') as f:
        pickle.dump(state, f)

def save_player_names(names):
    try:
        with open(PLAYER_NAMES_FILE, 'w', encoding='utf-8') as f:
            json.dump(names, f, ensure_ascii=False)
    except Exception:
        pass

def load_saved_player_names():
    if os.path.exists(PLAYER_NAMES_FILE):
        try:
            with open(PLAYER_NAMES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    return None

def initialize_state(players):
    # Check for saved player names and override if they exist
    saved_names = load_saved_player_names()
    if saved_names:
        players = saved_names

    # Load initial data
    # We need to bypass the st.session_state logic in parse_sheet for the initial load
    # or just use it and extract values.
    # Since parse_sheet relies on st.session_state, we might want to replicate its logic 
    # or just use it if we are in a streamlit context. 
    # However, to be safe and independent, let's replicate the reading logic here 
    # or assume this is called from main where st is available.
    
    # For simplicity, let's just read the excel directly here to get fresh decks
    file_name = 'Civ_bonuses.xlsx'
    my_sheet = 'Sheet1'
    df = pd.read_excel(file_name, header=0, names=['tier', 'bonus', 'cul', 'eco', 'war', 'tech'], index_col=None, sheet_name=my_sheet)
    
    df1 = df[df['tier'] == 1].copy()
    df2 = df[df['tier'] == 2].copy()
    df3 = df[df['tier'] == 3].copy()
    df4 = df[df['tier'] == 4].copy()
    df5 = df[df['tier'] == 5].copy()
    df6 = df[df['tier'] == 6].copy()
    
    # Shuffle players
    players = shuffle_slice(players[:]) # Copy to avoid side effects
    
    # Generate initial tables
    tables = {}
    player_flags = {} # p1, p2, etc.
    
    # We need to handle up to 5 players
    # Using index 0-4
    for i in range(len(players)):
        tables[i] = random_distribution(df1, df2, df3, df4, df5)
        player_flags[i] = False
        
    # Random event
    df6_sample = df6.sample(random_state=np.random.RandomState())
    df6_sample.index = [':']
    
    # Game Info
    seating = player_seating(players)
    map_maker = random.randint(0, len(players) - 1)
    first_player = random.randint(0, len(players) - 1)
    
    state = {
        'players': players,
        'decks': {
            'df1': df1, 'df2': df2, 'df3': df3, 'df4': df4, 'df5': df5, 'df6': df6
        },
        'tables': tables,
        'player_flags': player_flags,
        'random_event': df6_sample,
        'game_info': {
            'seating': seating,
            'map_maker': map_maker,
            'first_player': first_player
        }
    }
    
    save_state(state)
    return state

def reroll_player(player_index):
    state = load_state()
    if not state:
        return None
        
    decks = state['decks']
    
    # Perform reroll
    new_table = random_distribution(decks['df1'], decks['df2'], decks['df3'], decks['df4'], decks['df5'])
    
    if new_table is not None:
        state['tables'][player_index] = new_table
        state['player_flags'][player_index] = True
        save_state(state)
        
    return state

def generate_new_event():
    state = load_state()
    if not state:
        return None
        
    df6 = state['decks']['df6']
    new_event = df6.sample(random_state=np.random.RandomState())
    new_event.index = [':']
    
    state['random_event'] = new_event
    save_state(state)
    return state

def update_player_names(new_players):
    state = load_state()
    if not state:
        return None
        
    # Update names but keep tables? 
    # The original code re-shuffled/re-seated when names changed.
    # "if submit_button: ... state.seating = player_seating(state.players)"
    
    # If the number of players changes, we might need to regenerate everything or handle it gracefully.
    # For now, let's assume we just update the names list and seating.
    
    state['players'] = new_players
    state['game_info']['seating'] = player_seating(new_players)
    
    # Save names persistently
    save_player_names(new_players)
    
    # If player count changed, we might need to add/remove tables
    # But for "renaming", usually count is same. 
    # If count changes (add/remove player), we need to handle that.
    
    # Logic from web_page.py:
    # if submit_button: ... state.players = ... state.seating = ...
    # if remove_button: ... state.players = state.players[:-1] ...
    
    # We should probably regenerate tables if count increases?
    # Original code:
    # if "table4" not in state: ...
    
    current_count = len(state['tables'])
    new_count = len(new_players)
    
    if new_count > current_count:
        # Add new players
        for i in range(current_count, new_count):
            state['tables'][i] = random_distribution(state['decks']['df1'], state['decks']['df2'], state['decks']['df3'], state['decks']['df4'], state['decks']['df5'])
            state['player_flags'][i] = False
    elif new_count < current_count:
        # Remove players (just delete from dict)
        for i in range(new_count, current_count):
            if i in state['tables']:
                del state['tables'][i]
            if i in state['player_flags']:
                del state['player_flags'][i]
                
    # Re-roll random roles if needed?
    # Original code:
    # if remove_button: ... map_maker = random... first_player = random...
    
    # We'll just update seating for now.
    
    save_state(state)
    return state

def reset_game(players):
    # Force fresh start
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    return initialize_state(players)
