import streamlit as st
from ui.adapter import EngineAdapter
from ui.models import EngineContractError

def render():
    st.title("Memory Management")
    st.write("Memory input and records ledger.")

render()
