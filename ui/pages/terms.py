import streamlit as st

def render():
    st.title("Terms of Use")
    st.caption("Last updated: October 25, 2026")

    st.markdown("""
### Purpose & Scope
MORPHE is an experimental research prototype for inspecting and evaluating 
adaptive memory graph reconfiguration in AI agent systems. It is provided 
for technical demonstration and academic evaluation.

### Local Execution & Availability
The software executes exclusively on your local host environment. 
No continuous uptime, availability, or operational guarantees are implied.

### Accuracy of Adaptive Decisions
Structural adaptations (splitting, merging, shortcut addition) are proposed 
based on configurable heuristic thresholds and verified against deterministic 
benchmark queries. Performance outcomes depend directly on the structure of the 
evaluation corpus.

### Intellectual Property & Open Source
The code and architecture are subject to the project license in the repository.
""")
