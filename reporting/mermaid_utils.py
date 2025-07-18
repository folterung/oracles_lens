def flowchart(nodes, edges):
    lines = ['```mermaid', 'flowchart TD']
    for node_id, label in nodes.items():
        lines.append(f"    {node_id}[{label}]")
    for start, end in edges:
        lines.append(f"    {start}--> {end}")
    lines.append('```')
    return '\n'.join(lines)
