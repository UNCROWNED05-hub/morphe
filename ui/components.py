import streamlit as st

GRAPH_HTML = """
<div class="morphe-graph-root" tabindex="0">
  <div class="graph-toolbar">
    <div class="toolbar-info" id="graph-summary">Loading graph topology...</div>
    <div class="toolbar-actions">
      <button type="button" class="tool-btn" id="btn-zoom-reset" aria-label="Reset Zoom">Reset Zoom</button>
    </div>
  </div>
  <div class="canvas-wrapper">
    <svg id="morphe-svg" width="100%" height="520" viewBox="0 0 800 500" role="img" aria-label="MORPHE Network Topology Graph"></svg>
  </div>
</div>
"""

GRAPH_CSS = """
:root {
  --canvas-bg: #090E1A;
  --surface: #101728;
  --surface-2: #192238;
  --border: rgba(255, 255, 255, 0.08);
  --ink: #F8FAFC;
  --ink-soft: #94A3B8;
  --primary: #6366F1;
  --change: #F59E0B;
}

.morphe-graph-root {
  width: 100%;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  outline: none;
  font-family: 'Atkinson Hyperlegible', sans-serif;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
}

.morphe-graph-root:focus-visible {
  border-color: var(--primary);
}

.graph-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 18px;
  background: linear-gradient(180deg, #131B2E 0%, #101728 100%);
  border-bottom: 1px solid var(--border);
  font-size: 13px;
  color: var(--ink-soft);
}

.toolbar-info {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 12px;
  color: #CBD5E1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tool-btn {
  background: var(--surface-2);
  border: 1px solid var(--border);
  color: var(--ink);
  padding: 5px 14px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 140ms ease-out;
}
.tool-btn:hover {
  background: #23304E;
  border-color: rgba(255, 255, 255, 0.2);
  color: #FFFFFF;
  transform: translateY(-1px);
}

.canvas-wrapper {
  width: 100%;
  height: 520px;
  position: relative;
  background: var(--canvas-bg);
  background-image: radial-gradient(rgba(99, 102, 241, 0.16) 1.4px, transparent 1.4px);
  background-size: 24px 24px;
  overflow: hidden;
}

svg {
  display: block;
  width: 100%;
  height: 100%;
  cursor: grab;
}

svg:active {
  cursor: grabbing;
}

/* Edge styles */
.edge-semantic {
  stroke: #38BDF8;
  stroke-width: 1.8px;
  opacity: 0.45;
  transition: stroke 200ms ease-out, stroke-width 200ms ease-out, opacity 200ms ease-out;
}
.edge-semantic:hover {
  stroke: #38BDF8;
  stroke-width: 3.5px;
  opacity: 0.95;
  cursor: pointer;
}

.edge-shortcut {
  stroke: var(--change);
  stroke-width: 2.5px;
  stroke-dasharray: 6 3;
  opacity: 0.95;
  filter: drop-shadow(0 0 5px rgba(245, 158, 11, 0.6));
  transition: stroke-width 200ms ease-out;
}
.edge-shortcut:hover {
  stroke-width: 4px;
  cursor: pointer;
}

/* Node styles */
.graph-node {
  cursor: pointer;
  outline: none;
  transition: transform 180ms ease-out;
}

.graph-node circle.main-circle {
  stroke: var(--canvas-bg);
  stroke-width: 2.5px;
  filter: drop-shadow(0 4px 10px rgba(0, 0, 0, 0.5));
  transition: stroke 180ms ease-out, stroke-width 180ms ease-out, filter 180ms ease-out;
}

.graph-node:hover circle.main-circle {
  stroke: #FFFFFF;
  stroke-width: 3.5px;
  filter: drop-shadow(0 0 14px rgba(99, 102, 241, 0.8));
}

.graph-node:focus-visible circle.main-circle,
.graph-node.is-selected circle.main-circle {
  stroke: #FFFFFF;
  stroke-width: 4px;
  filter: drop-shadow(0 0 16px rgba(99, 102, 241, 0.9));
}

.changed-ring {
  fill: none;
  stroke: var(--change);
  stroke-width: 2.5px;
  stroke-dasharray: 5 3;
  filter: drop-shadow(0 0 8px rgba(245, 158, 11, 0.7));
}

.node-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  fill: #E2E8F0;
  text-anchor: middle;
  pointer-events: none;
  user-select: none;
  filter: drop-shadow(0 1px 4px rgba(0, 0, 0, 0.9));
}

.node-count {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  font-weight: 700;
  fill: #FFFFFF;
  text-anchor: middle;
  dominant-baseline: central;
  pointer-events: none;
  user-select: none;
  filter: drop-shadow(0 1px 3px rgba(0, 0, 0, 0.8));
}
"""

GRAPH_JS = """
export default function(component) {
  const { data, setTriggerValue, setStateValue, parentElement } = component;
  const svg = parentElement.querySelector('#morphe-svg');
  const summaryEl = parentElement.querySelector('#graph-summary');
  const resetBtn = parentElement.querySelector('#btn-zoom-reset');

  if (!data || !data.nodes) return;

  if (summaryEl && data.summary) {
    summaryEl.textContent = data.summary;
  }
  if (svg && data.summary) {
    svg.setAttribute('aria-label', data.summary);
  }

  // Clear previous contents
  svg.innerHTML = '';

  const gMain = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  gMain.id = 'viewport-group';
  svg.appendChild(gMain);

  // Group for edges
  const gEdges = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  gMain.appendChild(gEdges);

  // Group for nodes
  const gNodes = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  gMain.appendChild(gNodes);

  // Node coordinate lookup
  const nodeCoords = {};
  data.nodes.forEach(n => {
    nodeCoords[n.id] = { x: n.x, y: n.y, r: n.r };
  });

  // Render edges
  data.edges.forEach(e => {
    const p1 = nodeCoords[e.source];
    const p2 = nodeCoords[e.target];
    if (!p1 || !p2) return;

    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', p1.x);
    line.setAttribute('y1', p1.y);
    line.setAttribute('x2', p2.x);
    line.setAttribute('y2', p2.y);
    line.setAttribute('class', e.kind === 'shortcut' ? 'edge-shortcut' : 'edge-semantic');
    line.setAttribute('data-source', e.source);
    line.setAttribute('data-target', e.target);
    line.setAttribute('data-kind', e.kind);
    line.setAttribute('data-weight', e.weight);
    line.setAttribute('tabindex', '0');
    line.onclick = () => {
      setTriggerValue('selected_edge', { source: e.source, target: e.target, kind: e.kind, weight: e.weight, co_access: e.co_access });
    };
    gEdges.appendChild(line);
  });

  // Render nodes
  data.nodes.forEach(n => {
    const nodeG = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    nodeG.setAttribute('class', 'graph-node');
    nodeG.setAttribute('data-id', n.id);
    nodeG.setAttribute('tabindex', '0');
    nodeG.setAttribute('role', 'button');
    nodeG.setAttribute('aria-label', `Module ${n.label}, ${n.record_count} records`);

    // Amber ring if changed
    if (n.changed) {
      const ring = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      ring.setAttribute('cx', n.x);
      ring.setAttribute('cy', n.y);
      ring.setAttribute('r', n.r + 5);
      ring.setAttribute('class', 'changed-ring');
      nodeG.appendChild(ring);
    }

    // Main Circle
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', n.x);
    circle.setAttribute('cy', n.y);
    circle.setAttribute('r', n.r);
    circle.setAttribute('fill', n.fill);
    circle.setAttribute('class', 'main-circle');
    nodeG.appendChild(circle);

    // Record count inside node
    const countText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    countText.setAttribute('x', n.x);
    countText.setAttribute('y', n.y);
    countText.setAttribute('class', 'node-count');
    countText.textContent = n.record_count;
    nodeG.appendChild(countText);

    // Label below node
    const labelText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    labelText.setAttribute('x', n.x);
    labelText.setAttribute('y', n.y + n.r + 14);
    labelText.setAttribute('class', 'node-label');
    labelText.textContent = n.id;
    nodeG.appendChild(labelText);

    // Click & Keyboard interactions
    const selectNode = () => {
      parentElement.querySelectorAll('.graph-node').forEach(el => el.classList.remove('is-selected'));
      nodeG.classList.add('is-selected');
      setTriggerValue('selected_node', n.id);
    };

    nodeG.onclick = selectNode;
    nodeG.onkeydown = (evt) => {
      if (evt.key === 'Enter' || evt.key === ' ') {
        evt.preventDefault();
        selectNode();
      }
    };

    gNodes.appendChild(nodeG);
  });

  // Pan & Zoom logic
  let isPanning = false;
  let startX = 0, startY = 0;
  let translateX = 0, translateY = 0;
  let scale = 1.0;

  const updateTransform = () => {
    gMain.setAttribute('transform', `translate(${translateX}, ${translateY}) scale(${scale})`);
  };

  svg.onmousedown = (e) => {
    if (e.target.tagName === 'circle' || e.target.tagName === 'text') return;
    isPanning = true;
    startX = e.clientX - translateX;
    startY = e.clientY - translateY;
  };

  window.onmousemove = (e) => {
    if (!isPanning) return;
    translateX = e.clientX - startX;
    translateY = e.clientY - startY;
    updateTransform();
  };

  window.onmouseup = () => {
    isPanning = false;
  };

  svg.onwheel = (e) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
    scale = Math.min(Math.max(0.4, scale * zoomFactor), 3.0);
    updateTransform();
  };

  if (resetBtn) {
    resetBtn.onclick = () => {
      translateX = 0;
      translateY = 0;
      scale = 1.0;
      updateTransform();
    };
  }

  // Escape key closes selection
  const handleKeydown = (e) => {
    if (e.key === 'Escape') {
      parentElement.querySelectorAll('.graph-node').forEach(el => el.classList.remove('is-selected'));
      setTriggerValue('closed_drawer', true);
    }
  };
  window.addEventListener('keydown', handleKeydown);

  return () => {
    window.removeEventListener('keydown', handleKeydown);
    window.onmousemove = null;
    window.onmouseup = null;
  };
}
"""

import json
import streamlit.components.v1 as _components

def morphe_graph_component(data, key=None, **kwargs):
    """Renders interactive NetworkX memory topology SVG graph canvas via Streamlit components.v1."""
    if not data or not data.get("nodes"):
        st.info("No nodes in current graph topology.")
        return None

    payload_json = json.dumps(data)
    clean_js = GRAPH_JS.replace("export default function(component) {", "function mountGraph() {").replace("const { data, setTriggerValue, setStateValue, parentElement } = component;", "")
    
    full_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    {GRAPH_CSS}
  </style>
</head>
<body style="margin: 0; padding: 0; background: transparent; overflow: hidden;">
  {GRAPH_HTML}
  <script>
    (function() {{
      const data = {payload_json};
      const parentElement = document.body;
      function setTriggerValue(key, val) {{
        console.log('Graph event:', key, val);
      }}
      {clean_js}
      mountGraph();
    }})();
  </script>
</body>
</html>
"""
    _components.html(full_html, height=540)
    return None

