import cairosvg

def generate_chart(members):
    # Размеры прямоугольника узла
    node_width = 150
    node_height = 50
    
    # Размеры холста
    canvas_width = 800
    canvas_height = 600
    
    # Радиус узла (для закругленных прямоугольников)
    node_radius = 10
    
    # Цвета
    background_color = "#F2F2F2"
    node_color = "#EFEFEF"
    node_stroke_color = "#999"
    node_text_color = "#333"
    line_color = "#CCC"
    
    # Список строк SVG-кода
    svg_lines = []
    
    # Рассчитываем координаты для каждого узла
    coordinates = {}
    for member in members:
        x = member['x']
        y = member['y']
        coordinates[member['id']] = {'x': x, 'y': y}
    
    # Рисуем линии-связи между узлами
    for member in members:
        member_id = member['id']
        x1 = coordinates[member_id]['x'] * node_width + node_width / 2
        y1 = coordinates[member_id]['y'] * node_height + node_height / 2
        for parent_id in member['parents']:
            x2 = coordinates[parent_id]['x'] * node_width + node_width / 2
            y2 = coordinates[parent_id]['y'] * node_height + node_height / 2
            svg_lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{line_color}" stroke-width="2"/>')
    
    # Рисуем узлы
    for member in members:
        member_id = member['id']
        x = coordinates[member_id]['x'] * node_width
        y = coordinates[member_id]['y'] * node_height
        
        # Рисуем фоновый прямоугольник
        svg_lines.append(f'<rect x="{x}" y="{y}" width="{node_width}" height="{node_height}" rx="{node_radius}" fill="{node_color}" stroke="{node_stroke_color}" stroke-width="2"/>')
        
        # Добавляем текст в центр узла
        member_name = member['name'][:16]
        text_x = x + node_width / 2
        text_y = y + node_height / 2
        svg_lines.append(f'<text x="{text_x}" y="{text_y}" text-anchor="middle" dominant-baseline="central" font-size="16" fill="{node_text_color}">{member_name}</text>')
    
    # Создаем SVG-код
    svg = f'<svg viewBox="0 0 {canvas_width} {canvas_height}" xmlns="http://www.w3.org/2000/svg" style="background-color:{background_color};">'
    for line in svg_lines:
        svg += line
    svg += '</svg>'
    # конвертировать SVG в PNG
    png_data = cairosvg.svg2png(bytestring=svg_data)
    return png_data
