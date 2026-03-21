def generate_heap_html(heap: list) -> str:
    if not heap:
        return """
        <div style='text-align:center; padding:40px; color:#6c7086;
                    background:#1e1e2e; border-radius:12px; font-family:sans-serif;'>
            <h3>🌳 Heap is empty</h3>
            <p>Add tasks to see the live heap tree</p>
        </div>"""

    sorted_heap = sorted(heap)
    nodes = []
    for i, (priority, _, task) in enumerate(sorted_heap):
        nodes.append({
            "id": i,
            "priority": priority,
            "name": task.name,
            "deadline": task.deadline or "None",
            "category": task.category,
            "created_at": task.created_at,
            "left": 2 * i + 1 if 2 * i + 1 < len(sorted_heap) else None,
            "right": 2 * i + 2 if 2 * i + 2 < len(sorted_heap) else None,
        })

    import json
    nodes_json = json.dumps(nodes)

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: #1e1e2e;
    font-family: 'Segoe UI', sans-serif;
    overflow-x: hidden;
  }}
  svg {{ width: 100%; display: block; }}

  .node circle {{
    stroke-width: 3px;
    cursor: pointer;
    transition: all 0.2s;
    filter: drop-shadow(0 0 6px rgba(0,0,0,0.5));
  }}
  .node circle:hover {{
    stroke-width: 5px;
    filter: drop-shadow(0 0 12px rgba(255,255,255,0.3));
    transform: scale(1.1);
  }}
  .node text {{
    font-size: 11px;
    font-weight: 700;
    fill: #1e1e2e;
    pointer-events: none;
    text-anchor: middle;
  }}
  .node .task-name {{
    font-size: 9px;
    font-weight: 500;
  }}
  .node .index-label {{
    font-size: 9px;
    fill: #6c7086;
  }}
  .node .root-label {{
    font-size: 10px;
    fill: #cba6f7;
    font-weight: 800;
  }}
  .link {{
    fill: none;
    stroke: #45475a;
    stroke-width: 2px;
  }}

  /* Tooltip */
  .tooltip {{
    position: fixed;
    background: #313244;
    border: 1px solid #45475a;
    border-radius: 10px;
    padding: 12px 16px;
    color: #cdd6f4;
    font-size: 12px;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.2s;
    z-index: 999;
    min-width: 180px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
  }}
  .tooltip.visible {{ opacity: 1; }}
  .tooltip .t-title {{
    font-weight: 700;
    font-size: 13px;
    color: #cba6f7;
    margin-bottom: 6px;
  }}
  .tooltip .t-row {{
    display: flex;
    justify-content: space-between;
    gap: 12px;
    margin: 3px 0;
    font-size: 11px;
  }}
  .tooltip .t-key {{ color: #6c7086; }}
  .tooltip .t-val {{ color: #cdd6f4; font-weight: 600; }}

  /* Legend */
  .legend {{
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    padding: 10px 16px;
    background: #181825;
    border-top: 1px solid #313244;
  }}
  .legend-item {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    color: #cdd6f4;
  }}
  .legend-dot {{
    width: 12px;
    height: 12px;
    border-radius: 50%;
  }}

  /* Array view */
  .array-view {{
    padding: 10px 16px;
    background: #181825;
    border-top: 1px solid #313244;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    align-items: center;
  }}
  .array-label {{
    font-size: 11px;
    color: #6c7086;
    margin-right: 4px;
  }}
  .array-cell {{
    background: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 10px;
    color: #cdd6f4;
    transition: all 0.3s;
    cursor: default;
  }}
  .array-cell:hover {{
    background: #45475a;
    border-color: #cba6f7;
    color: #cba6f7;
  }}
  .array-cell.root {{ border-color: #cba6f7; color: #cba6f7; }}
</style>
</head>
<body>

<div id="chart"></div>
<div class="legend" id="legend"></div>
<div class="array-view" id="arrayview"></div>
<div class="tooltip" id="tooltip"></div>

<script>
const nodes = {nodes_json};

const COLORS = {{
  1: "#f38ba8",
  2: "#fab387",
  3: "#f9e2af",
  4: "#89b4fa",
  5: "#a6e3a1"
}};
const LABELS = {{
  1: "Critical", 2: "High", 3: "Medium", 4: "Low", 5: "Minimal"
}};

// ── Build tree layout ─────────────────────────────────────
const n = nodes.length;
const depth = Math.floor(Math.log2(n + 1)) + 1;
const W = Math.max(700, Math.pow(2, depth) * 60);
const nodeR = Math.max(28, Math.min(38, 340 / n));
const levelH = Math.max(80, Math.min(100, 400 / depth));
const H = depth * levelH + 60;

function getPos(i) {{
  const level = Math.floor(Math.log2(i + 1));
  const nodesInLevel = Math.pow(2, level);
  const posInLevel = i - (nodesInLevel - 1);
  const totalWidth = Math.pow(2, depth) * nodeR * 1.8;
  const spacing = totalWidth / (nodesInLevel + 1);
  return {{
    x: spacing * (posInLevel + 1),
    y: level * levelH + nodeR + 30
  }};
}}

// ── SVG setup ─────────────────────────────────────────────
const svg = d3.select("#chart")
  .append("svg")
  .attr("viewBox", `0 0 ${{W}} ${{H}}`)
  .attr("height", H);

const tooltip = d3.select("#tooltip");

// ── Draw edges ────────────────────────────────────────────
nodes.forEach((node, i) => {{
  const pos = getPos(i);
  [node.left, node.right].forEach(childIdx => {{
    if (childIdx !== null && childIdx < n) {{
      const cpos = getPos(childIdx);
      svg.append("line")
        .attr("class", "link")
        .attr("x1", pos.x).attr("y1", pos.y)
        .attr("x2", pos.x).attr("y2", pos.y)   // start collapsed
        .transition().duration(600).delay(i * 80)
        .attr("x2", cpos.x).attr("y2", cpos.y);
    }}
  }});
}});

// ── Draw nodes ────────────────────────────────────────────
nodes.forEach((node, i) => {{
  const pos = getPos(i);
  const color = COLORS[node.priority] || "#cdd6f4";
  const g = svg.append("g")
    .attr("class", "node")
    .attr("transform", `translate(${{pos.x}}, ${{pos.y}}) scale(0)`)  // start at 0
    .style("opacity", 0);

  // Animate in
  g.transition().duration(500).delay(i * 100)
    .attr("transform", `translate(${{pos.x}}, ${{pos.y}}) scale(1)`)
    .style("opacity", 1);

  // Circle
  g.append("circle")
    .attr("r", nodeR)
    .attr("fill", color)
    .attr("stroke", i === 0 ? "#cba6f7" : "#1e1e2e");

  // Priority label
  g.append("text")
    .attr("dy", "-4px")
    .attr("class", "priority-text")
    .text(`P${{node.priority}}`);

  // Task name
  const shortName = node.name.length > 9 ? node.name.slice(0, 9) + "…" : node.name;
  g.append("text")
    .attr("dy", "10px")
    .attr("class", "task-name")
    .text(shortName);

  // Index above node
  svg.append("text")
    .attr("class", "index-label")
    .attr("x", pos.x)
    .attr("y", pos.y - nodeR - 6)
    .attr("text-anchor", "middle")
    .style("opacity", 0)
    .text(`[${{i}}]`)
    .transition().duration(400).delay(i * 100 + 300)
    .style("opacity", 1);

  // ROOT label
  if (i === 0) {{
    svg.append("text")
      .attr("class", "root-label")
      .attr("x", pos.x)
      .attr("y", pos.y - nodeR - 18)
      .attr("text-anchor", "middle")
      .style("opacity", 0)
      .text("▲ ROOT (Min)")
      .transition().duration(400).delay(200)
      .style("opacity", 1);
  }}

  // Tooltip interaction
  g.on("mousemove", function(event) {{
    tooltip
      .classed("visible", true)
      .style("left", (event.clientX + 16) + "px")
      .style("top", (event.clientY - 10) + "px")
      .html(`
        <div class="t-title">${{node.name}}</div>
        <div class="t-row"><span class="t-key">Priority</span><span class="t-val">${{node.priority}} — ${{LABELS[node.priority]}}</span></div>
        <div class="t-row"><span class="t-key">Category</span><span class="t-val">${{node.category}}</span></div>
        <div class="t-row"><span class="t-key">Deadline</span><span class="t-val">${{node.deadline}}</span></div>
        <div class="t-row"><span class="t-key">Added</span><span class="t-val">${{node.created_at}}</span></div>
        <div class="t-row"><span class="t-key">Heap index</span><span class="t-val">[${{i}}]</span></div>
      `);
  }})
  .on("mouseleave", function() {{
    tooltip.classed("visible", false);
  }});
}});

// ── Legend ─────────────────────────────────────────────────
const legendDiv = d3.select("#legend");
legendDiv.append("span")
  .attr("class", "array-label")
  .text("Priority: ");

Object.entries(COLORS).forEach(([p, c]) => {{
  const item = legendDiv.append("div").attr("class", "legend-item");
  item.append("div").attr("class", "legend-dot").style("background", c);
  item.append("span").text(`P${{p}} ${{LABELS[p]}}`);
}});

// ── Array view ─────────────────────────────────────────────
const arrayDiv = d3.select("#arrayview");
arrayDiv.append("span")
  .attr("class", "array-label")
  .text("Heap Array → ");

nodes.forEach((node, i) => {{
  arrayDiv.append("div")
    .attr("class", `array-cell${{i === 0 ? " root" : ""}}`)
    .attr("title", node.name)
    .text(`[${{i}}] P${{node.priority}}`)
    .style("opacity", 0)
    .transition().duration(300).delay(i * 80 + 400)
    .style("opacity", 1);
}});

</script>
</body>
</html>
"""