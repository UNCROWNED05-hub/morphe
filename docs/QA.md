# MORPHE Judge Questions and Verified Technical Answers

Technical defense reference based on BRIEF Section 12 and measured data in `docs/results.json`.

---

### Q1. How is MORPHE different from ordinary RAG?
Ordinary Retrieval-Augmented Generation (RAG) retrieves chunks from a static collection of documents or vector index where indexing geometry never alters based on usage. 

MORPHE is an adaptive structural memory architecture. It continuously monitors memory topology via retrieval telemetry (access frequency, centroid similarity, query co-access), identifies structural weaknesses (overloaded groups, redundant modules, missing associative links), applies structural mutations (Split, Merge, Shortcut), and validates every mutation against frozen benchmark queries. If a mutation harms recall, MORPHE rolls it back automatically.

---

### Q2. Why use a graph if embeddings already exist?
Embeddings quantify point-to-point semantic similarity in high-dimensional space. The NetworkX graph represents topological retrieval pathways between modular memory groups.

Centroid routing allows MORPHE to direct searches to the most relevant module first, then traverse 1-hop pathways to adjacent connected modules. This enables cross-domain associative recall (such as connecting data preparation in Python to neural network training in PyTorch via a shortcut edge) while maintaining clean modular isolation, which flat vector search lacks.

---

### Q3. How does the system decide when to split or merge?
Decisions are driven by explicit heuristic monitoring rules defined in `engine/config.py`:
1. **Split Trigger:** When a module contains >= 8 records (`SPLIT_MIN_MODULE_SIZE`) and bi-modal K-Means clustering yields a silhouette score > 0.12 (`SPLIT_MIN_SILHOUETTE`) with both clusters having at least 3 records. In our benchmark, `MOD_MIXED_CORE` (combining Java OOP and Linear Algebra) triggered a split with 14 records and silhouette 0.283.
2. **Merge Trigger:** When centroid cosine similarity between two modules exceeds 0.78 (`MERGE_COSINE_SIM_THRESHOLD`). `MOD_VECTOR_INDEX` and `MOD_EMBEDDING_RETRIEVAL` triggered this with similarity 0.912.
3. **Shortcut Trigger:** When two unconnected modules appear together in top query hits >= 3 times (`SHORTCUT_MIN_CO_ACCESS`). `MOD_PYTHON_DATA` and `MOD_ML_MODELS` triggered this after repeated co-access.

---

### Q4. How do you know adaptation improved performance?
We evaluate the memory graph against 16 frozen benchmark queries before and after every structural change under identical top-k retrieval conditions (Top K = 4).

In our measured benchmark (`docs/results.json`):
- Baseline (V1) achieved Recall@4 of 0.7969 and Precision@4 of 0.5469 across the 16 queries.
- Adding the shortcut between `MOD_PYTHON_DATA` and `MOD_ML_MODELS` (V4) increased Recall@4 to 0.8281 (+0.0312 gain) and Precision@4 to 0.5625 (+0.0156 gain).
- Performance claims are based strictly on these empirical measurements.

---

### Q5. What happens when adaptation makes performance worse?
MORPHE enforces an automated guardrail before committing any adaptation to the version history.
1. The post-mutation Recall@K must satisfy the minimum acceptable threshold (0.60).
2. The recall drop compared to the previous accepted snapshot must not exceed an allowed epsilon (0.05).

If either condition fails, the mutation is classified as `REJECTED`, the transaction is aborted, and the graph and module records immediately roll back to the previous accepted snapshot.

---

### Q6. Did you train your own AI model?
No. The brief explicitly allows pretrained embedding models. We use `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense vectors) running locally. Our engineering focus is on structural memory plasticity: graph representations, heuristic weakness detection, guarded validation, and rollback mechanics.

---

### Q7. Is the system fully autonomous?
No. MORPHE is an evidence-driven adaptive memory system operating on deterministic heuristic rules and threshold gates. It is not an unconstrained, self-directing artificial general intelligence. It demonstrates that an AI agent's memory topology can be systematically measured, mutated, verified, and restored based on empirical retrieval performance.
