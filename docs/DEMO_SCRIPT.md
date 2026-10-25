# MORPHE Live Demonstration Script

Run-of-show for a 5-minute technical evaluation walkthrough on localhost (http://localhost:8501).

---

## 1. Pre-Flight Checklist
- [ ] Ensure local virtual environment is active and dependencies are installed.
- [ ] Confirm Streamlit dashboard is running at `http://localhost:8501`.
- [ ] Pre-warm the embedding model so query latencies reflect true in-memory retrieval.
- [ ] Verify offline capability: model weights cached in local directory.
- [ ] Set browser zoom to 110% for crisp display visibility.
- [ ] Silence operating system and browser notifications.
- [ ] Click **Memory** -> **Reset demo state** to start from a clean baseline (V1).

---

## 2. Five-Minute Step-by-Step Run of Show

### Step 1: Introduction and Problem Overview (0:00 - 0:45)
- **Action:** Open `http://localhost:8501` to the **Overview** page.
- **Say:** "Conventional memory architectures keep graph modules static as knowledge accumulates, causing retrieval degradation. MORPHE dynamically reconfigures memory modules using measured retrieval signals and rolls back changes if performance drops."
- **Visible:** Clean live ledger showing 60 knowledge chunks across 7 module nodes and 9 pathway edges, active version V1, and acceptance gate tick at 0.70.
- **Fallback:** If metrics do not show immediately, click "Load corpus (synthetic)".

### Step 2: Semantic Memory Retrieval (0:45 - 1:30)
- **Action:** Navigate to **Retrieve**. Click the one-click chip: `"What Java concepts should I study?"`. Click **Search**.
- **Say:** "MORPHE routes the query via centroid similarity, traverses one hop to adjacent modules, and retrieves relevant records with measured execution latency."
- **Visible:** Summary strip: "Retrieved 4 records from 1 module in X ms". Below, the traversal path highlights touched modules with amber pulse rings, displaying ranked records with true similarity scores.
- **Fallback:** If the chip is not pre-populated, type "What Java concepts should I study?" into the query box.

### Step 3: Structural Weakness Detection (1:30 - 2:15)
- **Action:** Navigate to **Adapt**. Inspect Section 1 (Detect) and Section 2 (Propose).
- **Say:** "The engine monitors three structural signals against heuristic thresholds: module overload via bi-modal cluster silhouette, module redundancy via centroid cosine similarity, and co-access frequency."
- **Visible:** Telemetry ledger displaying `MOD_MIXED_CORE` triggered for SPLIT (measured silhouette 0.283 > 0.20 threshold) and `MOD_VECTOR_INDEX` + `MOD_EMBEDDING_RETRIEVAL` triggered for MERGE (similarity 0.912 > 0.88).
- **Fallback:** Review the threshold table parameters in the config summary.

### Step 4: Guarded Adaptation and Automated Rollback (2:15 - 3:30)
- **Action:** Select candidate proposal `SPLIT on MOD_MIXED_CORE`. Click **Run adaptation cycle**.
- **Say:** "MORPHE applies the split, re-evaluates all 16 frozen benchmark queries, verifies that recall increased, and accepts the change into version V2."
- **Visible:** Decision tag reads `ACCEPTED`. Delta Recall reads "+0.0469" with green tag.
- **Action:** Now demonstrate safety by triggering an unviable split or tight threshold.
- **Say:** "When an adaptation violates the minimum recall threshold or allowed epsilon drop, the guardrail rejects it and rolls back the graph automatically."
- **Visible:** Status tag displays `REJECTED`, followed by "Rolled back to previous version: Graph restored."
- **Fallback:** Reference the decision ledger row recording the rollback event.

### Step 5: Version History, Baseline Comparison, and Restore (3:30 - 5:00)
- **Action:** Navigate to **History**. Show the version progression chart and side-by-side comparison.
- **Say:** "Every architectural snapshot is immutable and verifiable. We compare the adapted graph against a flat vector search baseline and can restore any previous version in one click."
- **Action:** Click "Restore V1" and confirm in the dialog.
- **Say:** "Restoring V1 reconstitutes the initial graph topology and module assignments in memory."
- **Visible:** Active version updates to V1; graph canvas reflects initial 7-node baseline structure.
- **Fallback:** Use the table view in Graph to inspect node counts directly.
