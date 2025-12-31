import json
import os

import streamlit as st

from openai import OpenAI
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv(override=True)
st.set_page_config(layout="wide")
st.header("Outsmart")
st.subheader("A game where AI competes with each other and try to win the game.")
st.divider()

MINIMUM_COINS = 12
PLAYERS = ["Corrine", "Cyndi", "Raelene", "Charley"]
MODELS = ["gpt-5-mini", "mistral-small-latest", "gemini-2.5-flash", "gpt-4.1-mini"]

if "display_coin_status" not in st.session_state:
    st.session_state.display_coin_status = {}

if "display_response" not in st.session_state:
    st.session_state.display_response = {}

if "display_winner" not in st.session_state:
    st.session_state.display_winner = {}

ai_coins = {player: MINIMUM_COINS for player in PLAYERS}
button_columns = st.columns(3)
llm_columns = st.columns(4)
turn = 1
history = []

CORRINE_SYSTEM_PROMPT = f"""
You are Corrine, a smart chatbot playing a game called "Outsmart".

You MUST follow ALL rules below. If a rule would be violated, you MUST choose a different valid move. And return only 
json response which should be ready to use without extra characters as mentioned below.

GAME RULES (MANDATORY):
- You cannot give or take a coin from Corrine
- You MUST use the current state of the game make a decision {ai_coins}.  
- You MUST give exactly ONE coin to ONE opponent based on the {ai_coins}.
- You MUST take exactly ONE coin from ONE opponent based on the {ai_coins}.
- You MUST NOT give a coin to yourself.
- You MUST NOT take a coin from yourself.
- You MUST NOT give and take from the same opponent.
- Corrine MUST NEVER appear as "Giving To" or "Taking From".
- You MUST ALWAYS select valid names.

DECISION GOAL:
Choose the move that maximizes your chance of winning.

OUTPUT REQUIREMENTS (STRICT – NO EXCEPTIONS):
- You MUST return VALID JSON ONLY.
- You MUST include ALL THREE fields.
- NO field may be empty or missing.
- NO extra text before or after JSON.
- If some fields are missing, then generate the response again.

REQUIRED BELOW JSON SCHEMA (EXACT KEYS): 
{{
    "Response": "A detail overview about your move.",
    "Giving To": "Name of the player to whome you decided to give the coin.",
    "Taking From": "Name of the player to whome you want to take the coin."
}}

FINAL VALIDATION (DO THIS BEFORE RESPONDING):
1. Check that "Giving To" ≠ "Taking From"
2. Check that neither value is "Corrine"
3. Check that both values are valid names
4. If ANY check fails → choose a different move
"""

CYNDI_SYSTEM_PROMPT = f"""
You are Cyndi, a smart chatbot playing a game called "Outsmart".

You MUST follow ALL rules below. If a rule would be violated, you MUST choose a different valid move. And return only 
json response which should be ready to use without extra characters as mentioned below.

GAME RULES (MANDATORY):
- You cannot give or take a coin from Cyndi
- You MUST use the current state of the game make a decision {ai_coins}.  
- You MUST give exactly ONE coin to ONE opponent based on the {ai_coins}.
- You MUST take exactly ONE coin from ONE opponent based on the {ai_coins}.
- You MUST NOT give a coin to yourself.
- You MUST NOT take a coin from yourself.
- You MUST NOT give and take from the same opponent.
- Cyndi MUST NEVER appear as "Giving To" or "Taking From".
- You MUST ALWAYS select valid names.

DECISION GOAL:
Choose the move that maximizes your chance of winning.

OUTPUT REQUIREMENTS (STRICT – NO EXCEPTIONS):
- You MUST return VALID JSON ONLY.
- You MUST include ALL THREE fields.
- NO field may be empty or missing.
- NO extra text before or after JSON.
- If some fields are missing, then generate the response again.

REQUIRED BELOW JSON SCHEMA (EXACT KEYS): 
{{
    "Response": "A detail overview about your move.",
    "Giving To": "Name of the player to whome you decided to give the coin.",
    "Taking From": "Name of the player to whome you want to take the coin."
}}

FINAL VALIDATION (DO THIS BEFORE RESPONDING):
1. Check that "Giving To" ≠ "Taking From"
2. Check that neither value is "Cyndi"
3. Check that both values are valid names
4. If ANY check fails → choose a different move
"""

RAELENE_SYSTEM_PROMPT = f"""
You are Raelene, a smart chatbot playing a game called "Outsmart".

You MUST follow ALL rules below. If a rule would be violated, you MUST choose a different valid move. And return only 
json response which should be ready to use without extra characters as mentioned below.

GAME RULES (MANDATORY):
- You MUST use the current state of the game make a decision {ai_coins}.  
- You MUST give exactly ONE coin to ONE opponent based on the {ai_coins}.
- You MUST take exactly ONE coin from ONE opponent based on the {ai_coins}.
- You MUST NOT give a coin to yourself.
- You MUST NOT take a coin from yourself.
- You MUST NOT give and take from the same opponent.
- Raelene MUST NEVER appear as "Giving To" or "Taking From".
- You MUST ALWAYS select valid names.

DECISION GOAL:
Choose the move that maximizes your chance of winning.

OUTPUT REQUIREMENTS (STRICT – NO EXCEPTIONS):
- You MUST return VALID JSON ONLY.
- You MUST include ALL THREE fields.
- NO field may be empty or missing.
- NO extra text before or after JSON.
- If some fields are missing, then generate the response again.

REQUIRED BELOW JSON SCHEMA (EXACT KEYS): 
{{
    "Response": "A detail overview about your move.",
    "Giving To": "Name of the player to whome you decided to give the coin.",
    "Taking From": "Name of the player to whome you want to take the coin."
}}

FINAL VALIDATION (DO THIS BEFORE RESPONDING):
1. Check that "Giving To" ≠ "Taking From"
2. Check that neither value is "Raelene"
3. Check that both values are valid names
4. If ANY check fails → choose a different move
"""

CHARLEY_SYSTEM_PROMPT = f"""
You are Charley, a smart chatbot playing a game called "Outsmart".

You MUST follow ALL rules below. If a rule would be violated, you MUST choose a different valid move. And return only 
json response which should be ready to use without extra characters as mentioned below.

GAME RULES (MANDATORY):
- You MUST use the current state of the game make a decision {ai_coins}.  
- You MUST give exactly ONE coin to ONE opponent based on the {ai_coins}.
- You MUST take exactly ONE coin from ONE opponent based on the {ai_coins}.
- You MUST NOT give a coin to yourself.
- You MUST NOT take a coin from yourself.
- You MUST NOT give and take from the same opponent.
- Charley MUST NEVER appear as "Giving To" or "Taking From".
- You MUST ALWAYS select valid names.

DECISION GOAL:
Choose the move that maximizes your chance of winning.

OUTPUT REQUIREMENTS (STRICT – NO EXCEPTIONS):
- You MUST return VALID JSON ONLY.
- You MUST include ALL THREE fields.
- NO field may be empty or missing.
- NO extra text before or after JSON.
- If some fields are missing, then generate the response again.

REQUIRED BELOW JSON SCHEMA (EXACT KEYS): 
{{
    "Response": "A detail overview about your move.",
    "Giving To": "Name of the player to whome you decided to give the coin.",
    "Taking From": "Name of the player to whome you want to take the coin."
}}

FINAL VALIDATION (DO THIS BEFORE RESPONDING):
1. Check that "Giving To" ≠ "Taking From"
2. Check that neither value is "Charley"
3. Check that both values are valid names
4. If ANY check fails → choose a different move
"""

CORRINE_USER_PROMPT = """You are Corrine a smart chatbot who is playing a game with other players. You cannot give coin 
to Corrine and cannot take a coin from Corrine. Make a move to maximize your changes of winning."""

CYNDI_USER_PROMPT = """You are Cyndi a smart chatbot who is playing a game with other players. You cannot give coin 
to Cyndi and cannot take a coin from Cyndi. Make a move to maximize your changes of winning."""

RAELENE_USER_PROMPT = """You are Raelene a smart chatbot who is playing a game with other players. You cannot give coin 
to Raelene and cannot take a coin from Raelene. Make a move to maximize your changes of winning."""

CHARLEY_USER_PROMPT = """You are Charley a smart chatbot who is playing a game with other players. You cannot give coin 
to Charley and cannot take a coin from Charley. Make a move to maximize your changes of winning."""

with button_columns[0]:
    run_turn_button = st.button(f"Run Turn: {turn}")
    st.divider()
with button_columns[1]:
    run_button = st.button("Run Game")
    st.divider()
with button_columns[2]:
    reset_button = st.button("Restart Game")
    st.divider()

st.divider()

with llm_columns[0]:
    row1 = st.markdown(f"<p style='color: lightblue; font-size: 36px;'>{PLAYERS[0]}</p>", unsafe_allow_html=True)
    row2 = st.text(f"{MODELS[0]}")
    row3 = st.text("Coins")
    row4 = st.markdown(f"<p style='color: {'green' if ai_coins['Corrine'] >= MINIMUM_COINS else 'red'}'>{'⬆️' if ai_coins['Corrine'] >= MINIMUM_COINS else '⬇️'} {ai_coins['Corrine']}</p>", unsafe_allow_html=True)
    row5 = st.markdown("Reasoning: ")
    st.session_state.display_coin_status[0] = row4
    st.session_state.display_response[0] = row5
with llm_columns[1]:
    row1 = st.markdown(f"<p style='color: lightblue; font-size: 36px;'>{PLAYERS[1]}</p>", unsafe_allow_html=True)
    row2 = st.text(f"{MODELS[1]}")
    row3 = st.text("Coins")
    row4 = st.markdown(f"<p style='color: {'green' if ai_coins['Cyndi'] >= MINIMUM_COINS else 'red'}'>{'⬆️' if ai_coins['Cyndi'] >= MINIMUM_COINS else '⬇️'} {ai_coins['Cyndi']}</p>", unsafe_allow_html=True)
    row5 = st.markdown("Reasoning: ")
    st.session_state.display_coin_status[1] = row4
    st.session_state.display_response[1] = row5
with llm_columns[2]:
    row1 = st.markdown(f"<p style='color: lightblue; font-size: 36px;'>{PLAYERS[2]}</p>", unsafe_allow_html=True)
    row2 = st.text(f"{MODELS[2]}")
    row3 = st.text("Coins")
    row4 = st.markdown(f"<p style='color: {'green' if ai_coins['Raelene'] >= MINIMUM_COINS else 'red'}'>{'⬆️' if ai_coins['Raelene'] >= MINIMUM_COINS else '⬇️'} {ai_coins['Raelene']}</p>", unsafe_allow_html=True)
    row5 = st.markdown("Reasoning: ")
    st.session_state.display_coin_status[2] = row4
    st.session_state.display_response[2] = row5
with llm_columns[3]:
    row1 = st.markdown(f"<p style='color: lightblue; font-size: 36px;'>{PLAYERS[3]}</p>", unsafe_allow_html=True)
    row2 = st.text(f"{MODELS[3]}")
    row3 = st.text("Coins")
    row4 = st.markdown(f"<p style='color: {'green' if ai_coins['Charley'] >= MINIMUM_COINS else 'red'}'>{'⬆️' if ai_coins['Charley'] >= MINIMUM_COINS else '⬇️'} {ai_coins['Charley']}</p>", unsafe_allow_html=True)
    row5 = st.markdown("Reasoning: ")
    st.session_state.display_coin_status[3] = row4
    st.session_state.display_response[3] = row5

def _corrine() -> None:
    messages = [{"role": "assistant", "content": CORRINE_USER_PROMPT}, {"role": "user", "content": CYNDI_SYSTEM_PROMPT}, {"role": "user", "content": RAELENE_SYSTEM_PROMPT},
                {"role": "user", "content": CHARLEY_SYSTEM_PROMPT}]

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(model=MODELS[0], messages=[{"role": "system", "content": CORRINE_SYSTEM_PROMPT}] + history + messages)
    response = response.choices[0].message.content.replace("\n", "").replace("`", "").replace("json{", "{")
    print(response)
    response = json.loads(response)

    ai_coins[response["Giving To"]] += 1
    ai_coins[response["Taking From"]] -= 1

    for index, player in enumerate(PLAYERS):
        st.session_state.display_coin_status[index].markdown(f"<p style='color: {'green' if ai_coins[player] >= MINIMUM_COINS else 'red'}'>{'⬆️' if ai_coins[player] >= MINIMUM_COINS else '⬇️'} {ai_coins[player]}</p>", unsafe_allow_html=True)

    st.session_state.display_response[0].markdown("Reasoning: " + response["Response"])
    history.extend([{"role": "system", "content": CORRINE_SYSTEM_PROMPT}])
    history.extend(messages)

def _cyndi() -> None:
    messages = [{"role": "assistant", "content": CYNDI_USER_PROMPT}, {"role": "user", "content": CORRINE_SYSTEM_PROMPT}, {"role": "user", "content": RAELENE_SYSTEM_PROMPT},
                {"role": "user", "content": CHARLEY_SYSTEM_PROMPT}]

    client = Mistral(api_key=os.getenv("MIXTRAL_API_KEY"))
    response = client.chat.complete(model=MODELS[1], messages=[{"role": "system", "content": CYNDI_SYSTEM_PROMPT}] + history + messages)
    response = response.choices[0].message.content.replace("\n", "").replace("`", "").replace("json{", "{")
    print(response)
    response = json.loads(response)

    ai_coins[response["Giving To"]] += 1
    ai_coins[response["Taking From"]] -= 1

    for index, player in enumerate(PLAYERS):
        st.session_state.display_coin_status[index].markdown(f"<p style='color: {'green' if ai_coins[player] >= MINIMUM_COINS else 'red'}'>{'⬆️' if ai_coins[player] >= MINIMUM_COINS else '⬇️'} {ai_coins[player]}</p>", unsafe_allow_html=True)

    st.session_state.display_response[1].markdown("Reasoning: " + response["Response"])
    history.extend([{"role": "system", "content": CYNDI_SYSTEM_PROMPT}])
    history.extend(messages)

def _raelene() -> None:
    messages = [{"role": "assistant", "content": RAELENE_USER_PROMPT}, {"role": "user", "content": CORRINE_SYSTEM_PROMPT}, {"role": "user", "content": CYNDI_SYSTEM_PROMPT},
                {"role": "user", "content": CHARLEY_SYSTEM_PROMPT}]
    client = OpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai/", api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))
    response = client.chat.completions.create(model=MODELS[2], messages=[{"role": "system", "content": RAELENE_SYSTEM_PROMPT}] + history + messages)
    response = response.choices[0].message.content.replace("\n", "").replace("`", "").replace("json{", "{")
    response = json.loads(response)

    ai_coins[response["Giving To"]] += 1
    ai_coins[response["Taking From"]] -= 1

    for index, player in enumerate(PLAYERS):
        st.session_state.display_coin_status[index].markdown(f"<p style='color: {'green' if ai_coins[player] >= MINIMUM_COINS else 'red'}'>{'⬆️' if ai_coins[player] >= MINIMUM_COINS else '⬇️'} {ai_coins[player]}</p>", unsafe_allow_html=True)

    st.session_state.display_response[2].markdown("Reasoning: " + response["Response"])
    history.extend([{"role": "system", "content": RAELENE_SYSTEM_PROMPT}])
    history.extend(messages)

def _charley() -> None:
    messages = [{"role": "assistant", "content": CHARLEY_USER_PROMPT}, {"role": "user", "content": CORRINE_SYSTEM_PROMPT}, {"role": "user", "content": CYNDI_SYSTEM_PROMPT},
                {"role": "user", "content": RAELENE_SYSTEM_PROMPT}]

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(model=MODELS[3], messages=[{"role": "system", "content": CHARLEY_SYSTEM_PROMPT}] + history + messages)
    response = response.choices[0].message.content.replace("\n", "").replace("`", "").replace("json{", "{")
    response = json.loads(response)

    ai_coins[response["Giving To"]] += 1
    ai_coins[response["Taking From"]] -= 1

    for index, player in enumerate(PLAYERS):
        st.session_state.display_coin_status[index].markdown(f"<p style='color: {'green' if ai_coins[player] >= MINIMUM_COINS else 'red'}'>{'⬆️' if ai_coins[player] >= MINIMUM_COINS else '⬇️'} {ai_coins[player]}</p>", unsafe_allow_html=True)

    st.session_state.display_response[3].markdown("Reasoning: " + response["Response"])
    history.extend([{"role": "system", "content": CHARLEY_SYSTEM_PROMPT}])
    history.extend(messages)

if run_turn_button:
    _corrine()
    _cyndi()
    _raelene()
    _charley()

    turn += 1

if run_button:
    for _ in range(2):
        _corrine()
        _cyndi()
        _raelene()
        _charley()

    max_kay, max_value = max(ai_coins.items(), key=lambda item: item[1])

    st.session_state.display_winner = st.header(f"The Winner is {max_kay} with maximum coins of {max_value}")

if reset_button:
    ai_coins = {player: MINIMUM_COINS for player in PLAYERS}
    turn = 1

    for index, player in enumerate(PLAYERS):
        st.session_state.display_coin_status[index].markdown(f"<p style='color: {'green' if ai_coins[player] >= MINIMUM_COINS else 'red'}'>{'⬆️' if ai_coins[player] >= MINIMUM_COINS else '⬇️'} {ai_coins[player]}</p>", unsafe_allow_html=True)
        st.session_state.display_response[index].markdown("Reasoning: ")

    st.session_state.display_winner.header("")
    history.clear()
