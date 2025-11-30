#!/usr/bin/env python3
"""
Script to load CSV data into SQLite database.

Usage:
    python scripts/load_csv.py <path_to_csv>
    python scripts/load_csv.py datasets/new_data_sample.csv
    
Options:
    --clear     Clear existing data before loading
    --help      Show this help message
"""

import sys
import argparse
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from app.database import init_db, insert_sensor_data, clear_session_data, get_data_count
from app.config import DATABASE_PATH


def load_csv_to_db(csv_path: str, clear_existing: bool = False) -> dict:
    """
    Load CSV file into SQLite database.
    
    Args:
        csv_path: Path to CSV file
        clear_existing: Whether to clear existing data first
        
    Returns:
        Dictionary with load statistics
    """
    csv_file = Path(csv_path)
    
    if not csv_file.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    # Initialize database
    init_db()
    
    # Clear existing data if requested
    if clear_existing:
        deleted = clear_session_data()
        print(f"Cleared {deleted} existing records")
    
    # Read CSV
    print(f"Reading CSV file: {csv_path}")
    df = pd.read_csv(csv_file)
    
    print(f"CSV columns: {list(df.columns)}")
    print(f"CSV shape: {df.shape}")
    
    # Expected columns
    expected_cols = ['device_id', 'real_time', 'ch0', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7']
    optional_cols = ['id', 'packet_id']
    
    # Validate required columns
    missing_cols = [col for col in expected_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Prepare data for insertion
    records = []
    for _, row in df.iterrows():
        record = {
            'device_id': int(row['device_id']),
            'packet_id': int(row['packet_id']) if 'packet_id' in df.columns and pd.notna(row.get('packet_id')) else None,
            'real_time': str(row['real_time']),
            'ch0': int(row['ch0']),
            'ch1': int(row['ch1']),
            'ch2': int(row['ch2']),
            'ch3': int(row['ch3']),
            'ch4': int(row['ch4']),
            'ch5': int(row['ch5']),
            'ch6': int(row['ch6']),
            'ch7': int(row['ch7']),
        }
        records.append(record)
    
    # Insert data
    print(f"Inserting {len(records)} records into database...")
    inserted = insert_sensor_data(records)
    
    # Get final counts
    counts = get_data_count()
    
    result = {
        'csv_file': str(csv_file),
        'records_in_csv': len(df),
        'records_inserted': inserted,
        'total_left': counts['left'],
        'total_right': counts['right'],
        'total_records': counts['total'],
        'database_path': str(DATABASE_PATH),
    }
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description='Load CSV data into Smart Insole SQLite database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/load_csv.py datasets/new_data_sample.csv
    python scripts/load_csv.py datasets/new_data_sample.csv --clear
        """
    )
    parser.add_argument('csv_path', help='Path to CSV file to load')
    parser.add_argument('--clear', action='store_true', help='Clear existing data before loading')
    
    args = parser.parse_args()
    
    try:
        result = load_csv_to_db(args.csv_path, args.clear)
        
        print("\n" + "="*50)
        print("Load Complete!")
        print("="*50)
        print(f"CSV File:        {result['csv_file']}")
        print(f"Records in CSV:  {result['records_in_csv']}")
        print(f"Records Added:   {result['records_inserted']}")
        print(f"Total Left Foot: {result['total_left']}")
        print(f"Total Right Foot:{result['total_right']}")
        print(f"Total Records:   {result['total_records']}")
        print(f"Database:        {result['database_path']}")
        print("="*50)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
