import json
import datetime

# Configuration
INPUT_FILE = 'finance_events_2026.json'
OUTPUT_FILE = 'finance_calendar_2026.html'

# Role Mapping
ROLES = {
    "Prep": {"role": "Finance Supervisor", "person": "BOM/JPAL"},
    "Review": {"role": "Senior Finance Manager", "person": "RIM"},
    "Approval": {"role": "Finance Director", "person": "CKVC"},
    "Filing": {"role": "Finance Team", "person": "ALL"}
}

def generate_html():
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)

    nodes = []
    
    for i, record in enumerate(data):
        # New format is flat: { "date": ..., "label": ..., "role": ..., "person": ..., "status": ... }
        nodes.append({
            "name": f"{record['date']}-{i}",
            "value": [record['date'], record['value']],
            "label": record['label'],
            "role": record['role'],
            "person": record['person'],
            "status": record['status'],
            "objective": record['objective']
        })

    # Convert to JSON string for embedding
    nodes_json = json.dumps(nodes, indent=2)

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>2026 Finance Closing & Tax Calendar</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        body {{ margin: 0; background-color: #04172b; color: white; font-family: sans-serif; }}
        #main {{ width: 100%; height: 100vh; }}
    </style>
</head>
<body>
    <div id="main"></div>
    <script type="text/javascript">
        var chartDom = document.getElementById('main');
        var myChart = echarts.init(chartDom);
        var option;

        const nodes = {nodes_json};

        const bg = '#04172b';
        const onTrack = '#00C853';
        const atRisk = '#FFAB00';
        const late = '#FF5252';
        const open = '#90caf9'; // Blue for future/open

        function statusColor(status) {{
            if (status === 'late') return late;
            if (status === 'at_risk') return atRisk;
            if (status === 'open') return open;
            return onTrack;
        }}

        const seriesData = nodes.map(n => ({{
            ...n,
            symbolSize: 10,
            itemStyle: {{ color: statusColor(n.status) }},
        }}));

        option = {{
            backgroundColor: bg,
            title: {{
                text: '2026 Finance Closing & Tax Calendar',
                left: 'center',
                top: 20,
                textStyle: {{ color: '#ffffff', fontSize: 24 }}
            }},
            tooltip: {{
                trigger: 'item',
                formatter: params => {{
                    const d = params.data;
                    return `
                        <div style="text-align:left">
                        <b>${{d.value[0]}}</b><br/>
                        ${{d.label}}<br/>
                        ${{d.role}} – ${{d.person}}<br/>
                        Status: ${{d.status}}
                        </div>
                    `;
                }},
            }},
            calendar: {{
                range: '2026',
                cellSize: ['auto', 20],
                top: 100,
                left: 60,
                right: 60,
                bottom: 40,
                yearLabel: {{ show: true, color: '#fff', fontSize: 20 }},
                dayLabel: {{ firstDay: 1, color: '#90a4ae', nameMap: 'en' }},
                monthLabel: {{ color: '#90a4ae', nameMap: 'en' }},
                itemStyle: {{
                    color: '#0b253a',
                    borderColor: '#113550'
                }}
            }},
            series: [
                {{
                    type: 'graph',
                    coordinateSystem: 'calendar',
                    data: seriesData,
                    links: [],
                    edgeSymbol: ['none', 'arrow'],
                    edgeSymbolSize: 6,
                    lineStyle: {{
                        color: '#90caf9',
                        width: 1,
                        opacity: 0.6,
                    }},
                    emphasis: {{ focus: 'adjacency' }},
                }},
            ],
        }};

        option && myChart.setOption(option);
        
        window.addEventListener('resize', function() {{
            myChart.resize();
        }});
    </script>
</body>
</html>
    """

    with open(OUTPUT_FILE, 'w') as f:
        f.write(html_content)
    print(f"Generated {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_html()
