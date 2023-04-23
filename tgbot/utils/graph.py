# Define SVG code generation function with member_id parameter
def generate_chart(members, member_id = None):
    if not member_id:
        member_id = members[0]['id']
    # Define some constants for layout
    node_radius = 30
    node_spacing = 80
    node_y = 100
    parent_y_offset = 50
    child_y_offset = 150
    
    # Find the specified member and its descendants
    member = None
    descendants = set()
    for m in members:
        if m["id"] == member_id:
            member = m
            descendants.add(member_id)
            break
    
    stack = member["children"].copy()
    while stack:
        child_id = stack.pop()
        descendants.add(child_id)
        for m in members:
            if m["id"] == child_id:
                stack.extend(m["children"])
                break

    # Define the x position for each member
    x_positions = {}
    x_positions[member_id] = 0
    for i, m in enumerate(members):
        if m["id"] in descendants:
            x_positions[m["id"]] = (i * node_spacing) + node_radius
    
    # Start building the SVG code
    svg_width = (len(descendants) * node_spacing) + (2 * node_radius)
    svg_height = 200
    svg_code = f'<svg width="{svg_width}" height="{svg_height}">'
    
    # Generate nodes and names for each descendant
    for m in members:
        if m["id"] in descendants:
            node_x = x_positions[m["id"]]
            node_code = f'<circle cx="{node_x}" cy="{node_y}" r="{node_radius}" stroke="black" stroke-width="2" fill="white"/>'
            name_code = f'<text x="{node_x}" y="{node_y}" font-size="16" text-anchor="middle">{m["name"]}</text>'
            svg_code += node_code + name_code
            
            # Generate links to parent nodes
            for parent_id in m["parents"]:
                if parent_id in descendants:
                    parent_x = x_positions[parent_id]
                    link_code = f'<line x1="{node_x}" y1="{node_y - parent_y_offset}" x2="{parent_x}" y2="{node_y}" stroke="black" stroke-width="2"/>'
                    svg_code += link_code
            
            # Generate links to child nodes
            for child_id in m["children"]:
                if child_id in descendants:
                    child_x = x_positions[child_id]
                    link_code = f'<line x1="{node_x}" y1="{node_y + child_y_offset}" x2="{child_x}" y2="{node_y}" stroke="black" stroke-width="2"/>'
                    svg_code += link_code
    
    # Finish the SVG code
    svg_code += '</svg>'
    
    return svg_code.encode('utf-8')