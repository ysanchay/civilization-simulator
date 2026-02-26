"""Export utilities for simulation data."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


class Exporter:
    """Export simulation data in various formats."""
    
    def __init__(self, export_dir: str = "exports"):
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def export_json(self, data: Dict[str, Any], name: str) -> str:
        """Export data as JSON."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = self.export_dir / f"{name}_{timestamp}.json"
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        return str(path)
    
    def export_csv(self, data: List[Dict[str, Any]], name: str) -> str:
        """Export data as CSV."""
        import csv
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = self.export_dir / f"{name}_{timestamp}.csv"
        
        if not data:
            return str(path)
        
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        return str(path)
    
    def export_replay(self, history: List[Dict], name: str) -> str:
        """Export simulation replay."""
        return self.export_json({'replay': history}, f"replay_{name}")