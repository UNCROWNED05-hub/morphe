# vjtihack02

# MORPHE — Complete Problem Statement and Build Brief

## Project
**MORPHE: Memory-Oriented Reconfigurable Plasticity and Hierarchical Evolution**

**Context:** This brief is based on the MORPHE problem statement in the uploaded AIML problem statement PDF, pages 5–6. Implementation recommendations are marked as recommendations rather than official requirements.

---

# 1. What MORPHE Is

MORPHE is an adaptive memory system for AI agents. It changes how stored information is organized and retrieved when the current memory structure is inefficient.

Think of a library:
- A conventional fixed-structure system keeps its shelves largely unchanged as books accumulate.
- MORPHE monitors which shelves are overcrowded, which contain redundant content, and which are often needed together.
- It can split, merge, or connect memory groups.
- It tests whether a structural change helps retrieval.
- It keeps the change if it passes the evaluation criteria and rolls it back if performance deteriorates.

The central idea is not merely to store information or retrieve it with AI. It is to **modify the structure of memory based on measurable retrieval performance and usage patterns**.

The problem statement does not require training a new neural architecture or creating a fully autonomous cognitive system. It allows predefined heuristics and lightweight algorithms.

---

# 2. The Problems MORPHE Addresses

The problem statement describes several issues that can occur as stored information grows:

## 2.1 Overloaded memory modules
A module may contain too many records or unrelated topics, making organization and retrieval inefficient.

**Expected response:** Identify an overloaded module and split it into more suitable groups.

## 2.2 Redundant memory modules
Two modules may contain similar or overlapping information.

**Expected response:** Identify redundant or closely related modules and consider merging them.

## 2.3 Inefficient retrieval pathways
Two modules may frequently be needed together but lack a useful direct connection.

**Expected response:** Create a connection, or shortcut, between frequently co-accessed modules.

## 2.4 Declining retrieval relevance or increased latency
As information grows, retrieval may become less relevant or slower.

**Expected response:** Monitor retrieval relevance and latency, identify structural weaknesses, and test whether adaptations help.

These are potential problems described by the brief, not guaranteed failures in every conventional memory system. A prototype should demonstrate a specific weakness and test whether its adaptation addresses it.

---

# 3. Mandatory Workflow Requirements

The problem statement specifies the following workflow.

## 3.1 Memory ingestion and organization

The system must:
- Accept text-based information.
- Divide it into manageable records.
- Generate embeddings or an equivalent retrieval representation.
- Organize records into memory modules.
- Retain relevant metadata.

Terms:
- **Ingestion:** Taking information into the system.
- **Record/chunk:** A manageable piece of information.
- **Embedding:** A numeric representation of text meaning, used for similarity comparisons.
- **Memory module:** A group of related records.
- **Metadata:** Additional details such as record ID, source, timestamp, topic, and module ID.

Example records:
- M1: “Java supports inheritance and polymorphism.”
- M2: “Python is used for machine learning.”
- M3: “Java classes can implement interfaces.”
- M4: “FAISS supports vector similarity search.”
- M5: “NumPy and pandas are Python libraries.”

Possible initial modules:
- Java: M1 and M3
- Python and ML: M2 and M5
- Retrieval tools: M4

Groups can be formed using rules, similarity thresholds, or clustering. For a small prototype, a lightweight approach is acceptable.

## 3.2 Graph-based memory representation

The system must:
- Represent memory modules as nodes in a graph.
- Represent relationships or retrieval pathways as edges.
- Support graph inspection.
- Support retrieval across relevant modules.
- Use semantic retrieval through a vector index or equivalent retrieval mechanism.

Key distinctions:
- **Node:** A memory module.
- **Edge:** A relationship or retrieval pathway between modules.
- **Embedding:** A representation used to compare semantic similarity.
- **Semantic search:** Finding information by meaning rather than only exact keywords.

Example: If queries frequently require both a Python-tools module and an AI-project module, MORPHE may create a direct edge between them.

The graph must represent the actual structure used by the application. A decorative graph alone does not satisfy the requirement.

## 3.3 Performance monitoring

The brief names four signals:

### A. Retrieval relevance
Measures whether retrieved records are useful for a query.

Possible metrics:
- Precision@K
- Recall@K
- Count or proportion of relevant results found

Example: For “What Java concepts should I study?”, Java-interface records are relevant; unrelated travel records are not.

### B. Module utilization
Tracks how often each module is accessed during retrieval.

A frequently accessed module may be overloaded or central to many queries. A rarely accessed module may be specialized or underused. Low usage alone does not prove that a module is badly organized.

### C. Repeated co-access patterns
Tracks which modules are repeatedly retrieved together.

Example: If the Python-tools and AI-project modules often appear together, a direct connection may be useful.

### D. Retrieval latency
Measures how long retrieval takes, usually in milliseconds.

Compare latency under consistent conditions. Do not claim a speed improvement unless measurements support it.

## 3.4 Adaptive structural reconfiguration

The system must implement all three operations and define criteria that trigger them.

### Operation A: Split an overloaded module
**Purpose:** Break one large or mixed-topic module into more useful groups.

Possible trigger:
- Module exceeds a record-count threshold.
- Its records contain clearly separated topic clusters.

Possible implementation:
- Calculate embeddings for records.
- Cluster records by similarity.
- Split the module when clusters are sufficiently distinct and meet minimum size requirements.

### Operation B: Merge redundant modules
**Purpose:** Combine modules with highly similar or overlapping content.

Possible trigger:
- Similarity between module representations exceeds a threshold.
- The modules have substantial overlapping content.

Possible implementation:
- Calculate cosine similarity between module representations.
- Propose a merge only when the threshold is reached.
- Validate the merged structure before accepting it.

### Operation C: Create a shortcut
**Purpose:** Add a connection between modules that are frequently retrieved together.

Possible trigger:
- Co-access count or rate exceeds a threshold.
- The modules do not already have the relevant direct edge.

Possible implementation:
- Record module IDs retrieved for each query.
- Count pairs that appear together.
- Add an edge when the pair passes the defined threshold.

Threshold values are implementation choices; the brief does not prescribe exact numbers.

**Important:** Adaptation must change the real graph and relevant module assignments or retrieval pathways. A button that only displays “Optimize memory” is insufficient.

## 3.5 Validation, versioning, and rollback

This is a central requirement.

### Validation
- Evaluate proposed structural changes against a consistent set of test queries.
- Use the same labelled evaluation dataset before and after a change.
- Compare retrieval performance.
- Reject or roll back changes that violate defined thresholds.

### Versioning
Maintain architecture versions, for example:
- V1: Initial graph.
- V2: A module was split.
- V3: Two redundant modules were merged.

Record for each version:
- Graph structure
- Memory-to-module assignments
- Operation performed
- Timestamp
- Evaluation metrics
- Whether the version was accepted or rejected

### Rollback
If an adaptation degrades performance beyond the allowed threshold, restore the previous accepted architecture.

Rollback must restore the actual graph and module assignments, not merely change a version label in the UI.

### Example
Suppose Recall@5 is 0.80 before a merge. After the merge, it drops to 0.50. If the defined minimum acceptable score is 0.75, reject the change and restore the previous architecture.

These numbers are illustrative, not measured results.

A robust acceptance rule should protect retrieval quality. Latency may also be monitored, but faster retrieval should not be achieved at the cost of unacceptable relevance.

## 3.6 Visualization and inspection

The brief requires a simple dashboard or API to demonstrate:
- Memory ingestion
- Retrieval
- Graph visualization
- Structural adaptation
- Comparison of the original and adapted architectures
- Inspection of structural changes
- Architecture history

Recommended dashboard areas:
1. **Memory input:** Add text, load sample data, inspect records and module assignments.
2. **Semantic retrieval:** Enter a query and display retrieved records, scores, module IDs, and latency.
3. **Memory graph:** Display actual nodes and edges; allow inspection of module contents and connections.
4. **Adaptation comparison:** Show what changed, why, and how evaluation results changed.
5. **Version history:** Show architecture versions, accepted/rejected changes, metrics, and a working restore function.

The interface is not merely for appearance. It should let a judge verify the system's behavior.

---

# 4. Six Mandatory MVP Requirements

The problem statement explicitly lists these six mandatory items.

1. **Memory Storage and Retrieval:** Text ingestion, embeddings or an equivalent retrieval representation, and semantic search across multiple memory modules.
2. **Memory Graph:** Represent memory modules and their relationships as a graph, supporting graph inspection and retrieval across relevant modules.
3. **Structural Adaptation:** Implement splitting, merging, and shortcut creation, with defined criteria for triggering each operation.
4. **Performance-Based Validation:** Compare performance before and after structural changes using a consistent evaluation dataset; reject or roll back changes that violate defined thresholds.
5. **Versioning and Recovery:** Record architecture versions and structural changes, track associated retrieval metrics, and restore a previous architecture version.
6. **Interactive Demonstration:** Provide a simple dashboard or API demonstrating ingestion, retrieval, graph visualization, structural adaptation, and comparison of the original and adapted architectures.

The MVP must demonstrate a complete adaptation cycle:
1. Identify a structural weakness.
2. Propose and apply a change.
3. Evaluate the outcome.
4. Retain the change or roll it back.

---

# 5. Data and Reference Resources

The brief permits:
- Publicly available text datasets
- Technical documentation
- Synthetic documents
- Generated interaction histories

The evaluation data should contain queries with known relevant documents so that retrieval performance can be measured consistently.

Resources named in the brief:
- NetworkX: graph representation and manipulation
- FAISS: vector similarity search
- Sentence Transformers: pretrained embeddings
- Qdrant: vector search infrastructure
- BEIR: retrieval evaluation framework and datasets

These are suggested resources, not a requirement to use every library. Existing embedding models and vector-search implementations may be used; training from scratch is not required.

## Recommended approach for a short hackathon deadline
Use a small synthetic dataset with labelled questions and known relevant record IDs. For example, create 40–60 memories about Java, Python, machine learning, vector search, and AI projects. Include:
- One oversized mixed-topic group
- Two highly similar groups
- Two groups frequently retrieved together

This gives the system specific structural weaknesses to detect and lets the team demonstrate split, merge, and shortcut operations.

---

# 6. What Will Make MORPHE Stand Out?

The following are implementation recommendations, not additional official requirements.

## 6.1 Evidence-driven adaptation
Do not reorganize memory randomly. Explain the signal and rule behind each change.

Example:
“Module A exceeded its size threshold and contains two distinct topic clusters. Proposed operation: split.”

Display:
- Triggering signal
- Threshold
- Proposed operation
- Result after evaluation

## 6.2 Safe adaptation
Demonstrate that a change can be rejected.

Example:
“The proposed merge reduced Recall@5 below the acceptance threshold. The merge was rejected and the previous architecture restored.”

Show a real rejected operation and successful rollback—not only a rollback button.

## 6.3 Compare against a baseline
Run the same test queries against:
- A conventional fixed memory structure
- The adaptive MORPHE structure

Compare:
- Retrieval relevance
- Latency
- Number of modules accessed, if relevant
- Accepted and rejected structural changes

Do not claim that every existing memory product has a fixed structure. Clearly name the baseline actually tested.

## 6.4 Explainable architecture history
Show a timeline such as V1 → V2 → V3. For each version, display:
- Graph snapshot
- Operation
- Reason for the operation
- Evaluation result
- Accepted/rejected status

## 6.5 Reproducible evaluation
Use the same labelled queries before and after adaptation. Display:
- Test queries
- Expected relevant record IDs
- Actual retrieved record IDs
- Calculated metrics

This makes the result verifiable rather than dependent on a persuasive-looking dashboard.

## Suggested comparison table

| Capability | Fixed-memory baseline | MORPHE prototype |
|---|---|---|
| Store and retrieve memories | Yes | Yes |
| Represent modules as a graph | Optional | Yes |
| Detect structural weaknesses | No automatic adaptation in this baseline | Uses defined monitoring rules |
| Split, merge, and create shortcuts | Fixed structure | Controlled operations |
| Validate against fixed queries | Not necessarily | Yes |
| Reject harmful changes and restore prior version | Not necessarily | Yes |

This describes the proposed experiment, not a universal statement about all memory systems.

---

# 7. How to Prove the Prototype Works

Create a small labelled test dataset.

Example memories:

| ID | Memory |
|---|---|
| M1 | Java supports inheritance. |
| M2 | Java supports interfaces. |
| M3 | Python is used in machine learning. |
| M4 | NumPy provides numerical computing tools for Python. |
| M5 | FAISS supports vector similarity search. |

Test query:
“What Java concepts should I study?”

Known relevant records: M1 and M2.

Run the experiment:
1. Store memories in the initial graph.
2. Run fixed test queries.
3. Record retrieved record IDs, relevance, and latency.
4. Trigger a structural adaptation using a defined rule.
5. Run the exact same queries with the same retrieval settings.
6. Compare results.
7. Accept or reject the change based on a predefined threshold.
8. Show the resulting graph, metrics, and architecture history.

Possible metrics:

**Recall@K**
Recall@K = relevant records found in top K / total known relevant records.

If two records are relevant and the top results include one of them, Recall@K = 1/2 = 0.5.

**Precision@K**
Precision@K = relevant records in top K / number of results returned in top K.

Measure latency under consistent conditions. Report actual results even if there is no improvement.

Important evaluation caution: if the graph does not affect retrieval behavior, changing the graph visualization alone cannot prove that graph adaptation improved retrieval. Ensure the graph/module structure or pathways genuinely affect how candidate memories are retrieved or ranked.

---

# 8. Recommended Technical Architecture

For a short prototype, use a simple stack.

| Component | Recommendation | Reason |
|---|---|---|
| Language | Python | Convenient for ML and graph logic |
| Embeddings | Sentence Transformers `all-MiniLM-L6-v2` | Pretrained semantic representations |
| Graph | NetworkX | Straightforward graph operations |
| Similarity search | NumPy cosine similarity initially | Avoid extra infrastructure |
| Persistence | SQLite or JSON snapshots | Simple storage and recovery |
| Dashboard | Streamlit | Quick local UI |
| Evaluation | Fixed labelled queries and Recall@K | Reproducible comparison |

FAISS or Qdrant can be added later if justified, but they are not necessary for a small prototype.

## Proposed architecture flow
1. Memory ingestion
2. Pretrained embedding model
3. Memory graph and retrieval
4. Monitoring and adaptation engine
5. Evaluation and version control
6. Streamlit dashboard

---

# 9. Suggested Project File Structure

```text
MORPHE/
├── app.py                 # Streamlit UI
├── memory_engine.py       # Memory, graph, retrieval, adaptation
├── requirements.txt
├── sample_data.json
├── test_engine.py
└── README.md
```

## Suggested division for a two-person team

### Person 1 — UI, visualization, and presentation
- Build the Streamlit dashboard.
- Create memory input and query interface.
- Visualize the actual NetworkX graph.
- Display adaptation history and before/after metrics.
- Prepare the live demo and presentation.

Main file: `app.py`

### Person 2 — Memory engine and evaluation
- Implement ingestion and embeddings.
- Create modules and graph edges.
- Implement retrieval and split/merge/shortcut operations.
- Build fixed-query evaluation, versioning, and rollback.
- Test the engine independently.

Main file: `memory_engine.py`

Agree on function names and returned data structures before generating both sides of the code. Work in separate files, integrate early, and use the same sample dataset.

---

# 10. Recommended Build Order

1. **Make semantic retrieval work.** Add sample memories and retrieve relevant ones.
2. **Make the graph real.** Nodes must represent actual modules and edges actual relationships.
3. **Implement split, merge, and shortcut creation.** Define the trigger criteria.
4. **Implement validation and rollback.** Save the prior architecture and compare results against fixed queries.
5. **Build the dashboard around the working engine.** Show what changed, why, and the evaluation result.
6. **Rehearse a complete demonstration.** Show a weakness, proposed change, evaluation, and acceptance or rollback.

Do not spend too long polishing the UI before the core engine works. Integrate early and reserve time for testing.

---

# 11. Common Mistakes to Avoid

| Mistake | Why it hurts | Better approach |
|---|---|---|
| Building only a chatbot | Misses the central adaptation requirement | Prioritize structural adaptation |
| Showing a graph unrelated to retrieval | Makes the graph decorative | Ensure graph changes affect module assignments or retrieval pathways |
| Randomly merging groups | Can destroy useful distinctions | Use similarity criteria and evaluation |
| Reporting only latency | Faster results may be less relevant | Measure relevance and latency |
| Changing test queries | Makes comparisons unfair | Freeze a labelled query set |
| Adding an LLM too early | Increases setup risk | Get retrieval and adaptation working first |
| Displaying invented metrics | Results are unverifiable | Calculate metrics from real tests |
| Fake rollback | Does not demonstrate recovery | Restore the saved graph and assignments |
| Over-polishing the UI | Consumes time without satisfying core requirements | Finish the complete adaptation cycle first |

---

# 12. Likely Judge Questions and Suggested Answers

### Q1. How is MORPHE different from ordinary RAG?
RAG commonly retrieves relevant information from a collection of documents. MORPHE's focus in this implementation is to monitor memory-structure performance, modify its module graph, and validate or reverse those changes.

### Q2. Why use a graph if embeddings already exist?
Embeddings help compare semantic similarity. The graph represents relationships and retrieval pathways between memory modules. They serve different purposes and can work together.

### Q3. How does the system decide when to split or merge?
It uses explicit criteria. For example, module size and topic separation for splitting, similarity thresholds for merging, and repeated co-access counts for adding edges.

### Q4. How do you know adaptation improved performance?
Use the same labelled queries before and after adaptation and compare retrieval metrics under the same settings. Do not assume every change improves results.

### Q5. What happens when adaptation makes performance worse?
The system rejects the change or restores the last accepted architecture version.

### Q6. Did you train your own AI model?
A new neural model is not required. The prototype uses a pretrained embedding model and implements the graph reconfiguration, evaluation, and recovery logic.

### Q7. Is the system fully autonomous?
Describe the actual implementation honestly. It may automatically run controlled heuristic-based adaptation rules, but it is not a general-purpose autonomous cognitive architecture.

---

# 13. Final Summary

The most important idea in MORPHE is not that it uses AI to remember information. It is that the memory structure itself can be measured, changed, evaluated, and restored.

For a successful prototype, demonstrate this complete loop:

**Detect a structural weakness → propose and apply a change → test with fixed queries → keep the change or roll it back.**

Prioritize:
- Real semantic retrieval
- Real memory modules and graph relationships
- All three structural operations: split, merge, shortcut creation
- Consistent before/after evaluation
- Versioning and working rollback
- A dashboard that makes the process inspectable

Use pretrained models and lightweight algorithms rather than training a model from scratch. Make claims only when your actual test results support them.

**Source basis:** Uploaded `AIML PS.pdf`, MORPHE problem statement, pages 5–6. This document preserves the stated requirements and separates implementation recommendations from official requirements.
