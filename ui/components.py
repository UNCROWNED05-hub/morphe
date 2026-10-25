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
  --canvas-bg: #0D0E10;
  --surface: #151619;
  --surface-2: #1C1E22;
  --border: #262930;
  --ink: #ECEFF2;
  --ink-soft: #8F96A3;
  --primary: #5E6AD2;
  --change: #C98A2C;
}

.morphe-graph-root {
  width: 100%;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  outline: none;
  font-family: 'Atkinson Hyperlegible', sans-serif;
}

.morphe-graph-root:focus-visible {
  border-color: var(--primary);
}

.graph-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  font-size: 13px;
  color: var(--ink-soft);
}

.toolbar-info {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 12px;
  color: var(--ink-soft);
  display: flex;
  align-items: center;
  gap: 8px;
}

.tool-btn {
  background: var(--surface-2);
  border: 1px solid var(--border);
  color: var(--ink);
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 120ms ease-out;
}
.tool-btn:hover {
  background: #25282F;
  border-color: #383D47;
  color: #FFFFFF;
}

.canvas-wrapper {
  width: 100%;
  height: 520px;
  position: relative;
  background: var(--canvas-bg);
  background-image: radial-gradient(#262930 1.2px, transparent 1.2px);
  background-size: 20px 20px;
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
  stroke: #3A404D;
  stroke-width: 1.5px;
  opacity: 0.65;
  transition: stroke 140ms ease-out, stroke-width 140ms ease-out, opacity 140ms ease-out;
}
.edge-semantic:hover {
  stroke: #5E6AD2;
  stroke-width: 2.5px;
  opacity: 1;
  cursor: pointer;
}

.edge-shortcut {
  stroke: var(--change);
  stroke-width: 2px;
  stroke-dasharray: 5 3;
  opacity: 0.9;
  transition: stroke-width 140ms ease-out;
}
.edge-shortcut:hover {
  stroke-width: 3px;
  cursor: pointer;
}

/* Node styles */
.graph-node {
  cursor: pointer;
  outline: none;
  transition: transform 140ms ease-out;
}

.graph-node circle.main-circle {
  stroke: var(--surface);
  stroke-width: 2px;
  transition: stroke 140ms ease-out, stroke-width 140ms ease-out;
}

.graph-node:hover circle.main-circle {
  stroke: #FFFFFF;
  stroke-width: 3px;
}

.graph-node:focus-visible circle.main-circle,
.graph-node.is-selected circle.main-circle {
  stroke: #FFFFFF;
  stroke-width: 3px;
}

.changed-ring {
  fill: none;
  stroke: var(--change);
  stroke-width: 2px;
  stroke-dasharray: 4 2;
}

.node-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  font-weight: 500;
  fill: var(--ink-soft);
  text-anchor: middle;
  pointer-events: none;
  user-select: none;
}

.node-count {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  font-weight: 600;
  fill: #FFFFFF;
  text-anchor: middle;
  dominant-baseline: central;
  pointer-events: none;
  user-select: none;
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

