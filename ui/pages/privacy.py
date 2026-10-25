import streamlit as st

def render():
    st.title("Privacy Policy")
    st.caption("Last updated: October 25, 2026")
    
    st.markdown("""
### Data Processing
All text entered into MORPHE is processed entirely on the local host machine. 
Memory chunking, embedding generation, graph manipulation, and benchmark evaluations 
are computed locally using local Python routines.

### Storage
Memory state, graph snapshots, and version history are stored strictly on local disk 
within the application directory (`data/morphe_state.json`). No external cloud storage 
or third-party database is used.

### Network Activity
No telemetry, tracking, or remote analytics are collected. The application does not 
transmit queries or record contents to external servers. The sole network request is 
the one-time download of the pretrained embedding model weights from Hugging Face during 
initial engine warm-up.

### Browser Storage & Cookies
The dashboard runs locally via Streamlit. The browser retains session state in memory 
and standard local storage keys for interface preferences. No third-party tracking 
cookies are placed.

### Accounts
MORPHE requires no accounts, passwords, or authentication.
""")
