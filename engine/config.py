"""
MORPHE Engine Configuration and Trigger Thresholds
"""

# Text Ingestion
CHUNK_SIZE_WORDS = 25
CHUNK_OVERLAP_WORDS = 5
INGEST_NEW_MODULE_SIM_THRESHOLD = 0.55  # If similarity to best centroid < 0.55, create new module

# Reconfiguration Trigger Rules
SPLIT_MIN_MODULE_SIZE = 8               # Module must have at least N records
SPLIT_MIN_CLUSTER_SIZE = 3              # Each sub-cluster must have at least min_size records
SPLIT_MIN_SILHOUETTE = 0.12             # Silhouette score must be > s to ensure distinct clusters
SPLIT_KMEANS_RANDOM_STATE = 42
SPLIT_KMEANS_N_INIT = 10

MERGE_COSINE_SIM_THRESHOLD = 0.78       # Module centroids with cosine similarity > t are flagged

SHORTCUT_MIN_CO_ACCESS = 3             # Co-access count >= c without an existing direct edge

# Validation & Guardrails
MIN_ACCEPTABLE_RECALL = 0.60            # Absolute minimum allowable Recall@K
MAX_ALLOWABLE_RECALL_DROP = 0.02        # Epsilon: max allowed drop vs previous accepted version
LATENCY_BENCHMARK_RUNS = 3              # Number of runs to average latency (after 1 warm-up run)

# Persistence
HISTORY_PERSISTENCE_PATH = "data/morphe_state.json"
DATASET_PATH = "data/benchmark_data.json"
