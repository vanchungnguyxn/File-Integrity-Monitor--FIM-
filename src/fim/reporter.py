"""Report generation for File Integrity Monitor."""

from pathlib import Path
from typing import List, Dict
from collections import Counter
import jinja2

from .models import Event


def render_report(events: List[Event], output_path: Path) -> None:
    """
    Render HTML report from events.
    
    Args:
        events: List of Event objects
        output_path: Path to save HTML report
    """
    # Get template directory
    template_dir = Path(__file__).parent / 'templates'
    
    # Setup Jinja2 environment
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        autoescape=jinja2.select_autoescape(['html', 'xml'])
    )
    
    template = env.get_template('report.html.j2')
    
    # Count events by type
    event_counts = Counter(event.type for event in events)
    
    # Prepare chart data
    chart_data = {
        'labels': ['ADDED', 'MODIFIED', 'DELETED'],
        'data': [
            event_counts.get('ADDED', 0),
            event_counts.get('MODIFIED', 0),
            event_counts.get('DELETED', 0)
        ]
    }
    
    # Render template
    html_content = template.render(
        events=events,
        chart_data=chart_data,
        total_events=len(events)
    )
    
    # Save report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Report saved to {output_path}")
