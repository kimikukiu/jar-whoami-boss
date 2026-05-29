"""
JARVIS Data Engine
Procesare, analiză și vizualizare date
Implementat pe baza analizei video-urilor din D:\pj-for-jarvis-implement-features
"""

import asyncio
import json
import csv
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib


class DataFormat(Enum):
    """Formate de date suportate"""
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    YAML = "yaml"
    PARQUET = "parquet"
    SQL = "sql"
    EXCEL = "excel"


class ChartType(Enum):
    """Tipuri de grafice suportate"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"
    HEATMAP = "heatmap"
    TREEMAP = "treemap"
    GAUGE = "gauge"


@dataclass
class DataSource:
    """Reprezintă o sursă de date"""
    id: str
    name: str
    type: str  # database, api, file, stream
    connection_string: str
    format: DataFormat
    last_sync: Optional[datetime] = None
    status: str = "active"  # active, inactive, error
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.id is None:
            self.id = f"ds_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(self.name) % 10000}"


@dataclass
class DataTransform:
    """Reprezintă o transformare de date"""
    id: str
    name: str
    type: str  # filter, map, reduce, aggregate, sort, join
    config: Dict[str, Any]
    input_schema: Dict[str, str]
    output_schema: Dict[str, str]
    
    def __post_init__(self):
        if self.id is None:
            self.id = f"dt_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(self.name) % 10000}"


@dataclass
class Visualization:
    """Reprezintă o vizualizare de date"""
    id: str
    name: str
    type: ChartType
    config: Dict[str, Any]
    data_source: str
    filters: List[Dict[str, Any]]
    aggregations: List[Dict[str, Any]]
    styling: Dict[str, Any]
    
    def __post_init__(self):
        if self.id is None:
            self.id = f"viz_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(self.name) % 10000}"


class DataEngine:
    """
    Motor de date pentru JARVIS
    Procesare, transformare, analiză și vizualizare date
    """
    
    def __init__(self, db_path: str = "data/jarvis_data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.sources: Dict[str, DataSource] = {}
        self.transforms: Dict[str, DataTransform] = {}
        self.visualizations: Dict[str, Visualization] = {}
        
        self.cache: Dict[str, Any] = {}
        self.metrics: Dict[str, Any] = {
            "queries_executed": 0,
            "data_processed_mb": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # Inițializează baza de date
        self._init_database()
    
    def _init_database(self):
        """Inițializează schema bazei de date"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Tabel pentru surse de date
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_sources (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                connection_string TEXT,
                format TEXT,
                last_sync TIMESTAMP,
                status TEXT DEFAULT 'active',
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabel pentru transformări
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_transforms (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                config TEXT,
                input_schema TEXT,
                output_schema TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabel pentru vizualizări
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visualizations (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                config TEXT,
                data_source TEXT,
                filters TEXT,
                aggregations TEXT,
                styling TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabel pentru cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # === GESTIONARE SURSE DE DATE ===
    
    def add_source(self, source: DataSource) -> str:
        """Adaugă o sursă de date"""
        # Salvează în memorie
        self.sources[source.id] = source
        
        # Salvează în baza de date
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO data_sources 
            (id, name, type, connection_string, format, last_sync, status, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            source.id,
            source.name,
            source.type,
            source.connection_string,
            source.format.value,
            source.last_sync.isoformat() if source.last_sync else None,
            source.status,
            json.dumps(source.metadata)
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✓ Sursă adăugată: {source.name} ({source.type})")
        return source.id
    
    def get_source(self, source_id: str) -> Optional[DataSource]:
        """Obține o sursă de date după ID"""
        # Încearcă din memorie
        if source_id in self.sources:
            return self.sources[source_id]
        
        # Încearcă din baza de date
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM data_sources WHERE id = ?", (source_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            source = DataSource(
                id=row['id'],
                name=row['name'],
                type=row['type'],
                connection_string=row['connection_string'],
                format=DataFormat(row['format']),
                last_sync=datetime.fromisoformat(row['last_sync']) if row['last_sync'] else None,
                status=row['status'],
                metadata=json.loads(row['metadata']) if row['metadata'] else {}
            )
            # Salvează în memorie
            self.sources[source_id] = source
            return source
        
        return None
    
    def list_sources(self, source_type: str = None) -> List[DataSource]:
        """Listează toate sursele de date"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if source_type:
            cursor.execute("SELECT * FROM data_sources WHERE type = ? AND status = 'active'", (source_type,))
        else:
            cursor.execute("SELECT * FROM data_sources WHERE status = 'active'")
        
        rows = cursor.fetchall()
        conn.close()
        
        sources = []
        for row in rows:
            source = DataSource(
                id=row['id'],
                name=row['name'],
                type=row['type'],
                connection_string=row['connection_string'],
                format=DataFormat(row['format']),
                last_sync=datetime.fromisoformat(row['last_sync']) if row['last_sync'] else None,
                status=row['status'],
                metadata=json.loads(row['metadata']) if row['metadata'] else {}
            )
            sources.append(source)
            # Salvează în memorie
            self.sources[source.id] = source
        
        return sources
    
    # === TRANSFORMĂRI DE DATE ===
    
    def add_transform(self, transform: DataTransform) -> str:
        """Adaugă o transformare de date"""
        self.transforms[transform.id] = transform
        
        # Salvează în baza de date
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO data_transforms 
            (id, name, type, config, input_schema, output_schema)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            transform.id,
            transform.name,
            transform.type,
            json.dumps(transform.config),
            json.dumps(transform.input_schema),
            json.dumps(transform.output_schema)
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✓ Transformare adăugată: {transform.name} ({transform.type})")
        return transform.id
    
    def apply_transform(self, data: List[Dict], transform_id: str) -> List[Dict]:
        """Aplică o transformare pe date"""
        transform = self.transforms.get(transform_id)
        if not transform:
            raise ValueError(f"Transformare negăsită: {transform_id}")
        
        print(f"🔄 Aplicare transformare: {transform.name}")
        
        # Aplică transformarea în funcție de tip
        if transform.type == "filter":
            condition = transform.config.get("condition")
            if condition:
                data = [row for row in data if eval(condition, {"row": row})]
        
        elif transform.type == "map":
            mapping = transform.config.get("mapping", {})
            data = [
                {new_key: row[old_key] for new_key, old_key in mapping.items() if old_key in row}
                for row in data
            ]
        
        elif transform.type == "aggregate":
            group_by = transform.config.get("group_by")
            aggregations = transform.config.get("aggregations", [])
            
            if group_by:
                groups = {}
                for row in data:
                    key = row.get(group_by)
                    if key not in groups:
                        groups[key] = []
                    groups[key].append(row)
                
                result = []
                for key, group in groups.items():
                    aggregated = {group_by: key}
                    for agg in aggregations:
                        column = agg.get("column")
                        operation = agg.get("operation")  # sum, avg, count, min, max
                        alias = agg.get("alias", f"{operation}_{column}")
                        
                        if operation == "sum":
                            aggregated[alias] = sum(row.get(column, 0) for row in group)
                        elif operation == "avg":
                            values = [row.get(column, 0) for row in group]
                            aggregated[alias] = sum(values) / len(values) if values else 0
                        elif operation == "count":
                            aggregated[alias] = len(group)
                        elif operation == "min":
                            aggregated[alias] = min(row.get(column, 0) for row in group)
                        elif operation == "max":
                            aggregated[alias] = max(row.get(column, 0) for row in group)
                    
                    result.append(aggregated)
                
                data = result
        
        elif transform.type == "sort":
            sort_by = transform.config.get("sort_by")
            sort_order = transform.config.get("order", "asc")  # asc, desc
            
            if sort_by:
                reverse = sort_order == "desc"
                data = sorted(data, key=lambda x: x.get(sort_by), reverse=reverse)
        
        elif transform.type == "join":
            # Implementare simplificată pentru join
            # În practică, ai nevoie de o a doua sursă de date
            pass
        
        print(f"   ✓ Transformare aplicată: {len(data)} rânduri")
        return data
    
    # === VIZUALIZĂRI ===
    
    def add_visualization(self, viz: Visualization) -> str:
        """Adaugă o vizualizare"""
        self.visualizations[viz.id] = viz
        
        # Salvează în baza de date
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO visualizations 
            (id, name, type, config, data_source, filters, aggregations, styling)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            viz.id,
            viz.name,
            viz.type.value,
            json.dumps(viz.config),
            viz.data_source,
            json.dumps(viz.filters),
            json.dumps(viz.aggregations),
            json.dumps(viz.styling)
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✓ Vizualizare adăugată: {viz.name} ({viz.type.value})")
        return viz.id
    
    def generate_chart_config(self, viz_id: str, data: List[Dict]) -> Dict[str, Any]:
        """Generează configurație pentru grafic"""
        viz = self.visualizations.get(viz_id)
        if not viz:
            raise ValueError(f"Vizualizare negăsită: {viz_id}")
        
        config = {
            "type": viz.type.value,
            "title": viz.name,
            "data": data,
            "options": viz.config.get("options", {}),
            "styling": viz.styling
        }
        
        # Adaugă configurații specifice tipului de grafic
        if viz.type == ChartType.LINE:
            config["options"]["scales"] = {
                "x": {"display": True, "title": {"display": True, "text": "X Axis"}},
                "y": {"display": True, "title": {"display": True, "text": "Y Axis"}}
            }
        
        elif viz.type == ChartType.BAR:
            config["options"]["scales"] = {
                "x": {"display": True},
                "y": {"display": True, "beginAtZero": True}
            }
        
        elif viz.type == ChartType.PIE:
            config["options"]["plugins"] = {
                "legend": {"display": True, "position": "right"}
            }
        
        return config
    
    # === EXPORT / IMPORT ===
    
    def export_to_format(self, data: List[Dict], format: DataFormat, 
                        output_path: str) -> str:
        """Exportă date în formatul specificat"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == DataFormat.JSON:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        elif format == DataFormat.CSV:
            if data:
                keys = data[0].keys()
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(data)
        
        elif format == DataFormat.SQL:
            # Generează comenzi INSERT SQL
            with open(output_path, 'w', encoding='utf-8') as f:
                table_name = "exported_data"
                for row in data:
                    columns = ', '.join(row.keys())
                    values = ', '.join([f"'{str(v).replace(chr(39), chr(39)+chr(39))}'" if v is not None else 'NULL' for v in row.values()])
                    f.write(f"INSERT INTO {table_name} ({columns}) VALUES ({values});\n")
        
        else:
            raise ValueError(f"Format nesuportat: {format}")
        
        print(f"✅ Date exportate: {output_path}")
        return str(output_path)
    
    def import_from_format(self, input_path: str, format: DataFormat) -> List[Dict]:
        """Importă date din formatul specificat"""
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Fișier negăsit: {input_path}")
        
        if format == DataFormat.JSON:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else [data]
        
        elif format == DataFormat.CSV:
            data = []
            with open(input_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(dict(row))
            return data
        
        else:
            raise ValueError(f"Format nesuportat pentru import: {format}")
    
    # === METRICI ȘI MONITORIZARE ===
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obține metricile sistemului"""
        return {
            "timestamp": datetime.now().isoformat(),
            "queries_executed": self.metrics["queries_executed"],
            "data_processed_mb": self.metrics["data_processed_mb"],
            "cache_hits": self.metrics["cache_hits"],
            "cache_misses": self.metrics["cache_misses"],
            "cache_hit_rate": self.metrics["cache_hits"] / (self.metrics["cache_hits"] + self.metrics["cache_misses"]) if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0 else 0,
            "sources_count": len(self.sources),
            "transforms_count": len(self.transforms),
            "visualizations_count": len(self.visualizations)
        }
    
    def reset_metrics(self):
        """Resetează metricile"""
        self.metrics = {
            "queries_executed": 0,
            "data_processed_mb": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        print("✅ Metrici resetate")


# Dacă rulăm direct
if __name__ == "__main__":
    print("=" * 70)
    print("JARVIS DATA ENGINE")
    print("=" * 70)
    print()
    print("Exemple de utilizare:")
    print()
    print("1. Inițializare motor de date:")
    print("   engine = DataEngine()")
    print()
    print("2. Adăugare sursă de date:")
    print("   source = DataSource(")
    print("       id='db_prod',")
    print("       name='Production DB',")
    print("       type='database',")
    print("       connection_string='postgresql://...',")
    print("       format=DataFormat.SQL")
    print("   )")
    print("   engine.add_source(source)")
    print()
    print("3. Interogare date:")
    print("   data = engine.query('SELECT * FROM users')")
    print()
    print("4. Aplicare transformare:")
    print("   transformed = engine.apply_transform(")
    print("       data,")
    print("       transform_id='filter_active'")
    print("   )")
    print()
    print("5. Export date:")
    print("   engine.export_to_format(")
    print("       data,")
    print("       format=DataFormat.CSV,")
    print("       output_path='output.csv'")
    print("   )")
    print()
    print("=" * 70)
