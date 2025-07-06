#!/usr/bin/env python3
"""
Comprehensive Metrics Dashboard Generator for Bob's Brief
Creates an HTML dashboard showing all metrics, sources, and query performance
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

def generate_metrics_dashboard():
    """Generate comprehensive HTML dashboard with all metrics"""
    
    # Load all metrics data
    data_files = {
        'metrics': Path("data/metrics_tracking.json"),
        'sources': Path("data/source_statistics.json"),
        'categories': Path("data/category_performance.json"),
        'queries': Path("data/search_query_stats.json")
    }
    
    # Load data with fallbacks
    metrics_data = load_data_safe(data_files['metrics'], {"sessions": {}, "totals": {}})
    source_data = load_data_safe(data_files['sources'], {"sources": {}, "sessions": {}})
    category_data = load_data_safe(data_files['categories'], {"categories": {}, "sessions": {}})
    query_data = load_data_safe(data_files['queries'], {"queries": {}, "sessions": {}})
    
    # Generate timestamp
    current_time = datetime.now()
    timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S')
    
    # Calculate key statistics
    total_sessions = len(metrics_data.get('sessions', {}))
    total_articles = metrics_data.get('totals', {}).get('total_articles', 0)
    total_sources = len(source_data.get('sources', {}))
    total_categories = len(category_data.get('categories', {}))
    
    # Get recent performance
    recent_sessions = get_recent_sessions(metrics_data.get('sessions', {}), 7)
    avg_articles_recent = sum(s.get('total_articles', 0) for s in recent_sessions) / len(recent_sessions) if recent_sessions else 0
    
    # Top sources
    top_sources = sorted(
        source_data.get('sources', {}).items(),
        key=lambda x: x[1].get('total_articles', 0),
        reverse=True
    )[:10]
    
    # Category performance
    category_performance = []
    for cat, data in category_data.get('categories', {}).items():
        hit_rate = 0
        if data.get('total_sessions', 0) > 0:
            hit_rate = (data.get('times_hit_target', 0) / data['total_sessions']) * 100
        
        category_performance.append({
            'name': cat,
            'total_articles': data.get('total_articles', 0),
            'hit_rate': hit_rate,
            'avg_per_session': data.get('average_per_session', 0)
        })
    
    category_performance.sort(key=lambda x: x['hit_rate'], reverse=True)
    
    # Query performance
    top_queries = []
    failing_queries = []
    
    for query_key, data in query_data.get('queries', {}).items():
        query_info = {
            'category': data.get('search_name', 'Unknown'),
            'query': data.get('query', ''),
            'success_rate': data.get('success_rate', 0),
            'total_uses': data.get('total_uses', 0),
            'avg_articles': data.get('average_articles', 0)
        }
        
        if query_info['success_rate'] >= 70:
            top_queries.append(query_info)
        elif query_info['success_rate'] < 30 and query_info['total_uses'] >= 3:
            failing_queries.append(query_info)
    
    top_queries.sort(key=lambda x: x['success_rate'], reverse=True)
    failing_queries.sort(key=lambda x: x['success_rate'])
    
    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bob's Brief - Metrics Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #007acc, #0056b3);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2.5em;
        }}
        
        .header p {{
            margin: 0;
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        
        .metric-card {{
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .metric-card h3 {{
            margin: 0 0 15px 0;
            color: #007acc;
            font-size: 1.3em;
            border-bottom: 2px solid #007acc;
            padding-bottom: 8px;
        }}
        
        .big-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #007acc;
            margin: 10px 0;
        }}
        
        .metric-label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 8px;
            background-color: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }}
        
        .source-list {{
            max-height: 300px;
            overflow-y: auto;
        }}
        
        .source-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        .source-name {{
            font-weight: 500;
            flex: 1;
        }}
        
        .source-count {{
            background-color: #007acc;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-left: 10px;
        }}
        
        .category-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        .category-name {{
            font-weight: 500;
            flex: 1;
        }}
        
        .category-stats {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        
        .hit-rate {{
            font-weight: bold;
        }}
        
        .hit-rate.good {{ color: #28a745; }}
        .hit-rate.medium {{ color: #ffc107; }}
        .hit-rate.poor {{ color: #dc3545; }}
        
        .query-item {{
            background: #f8f9fa;
            border-radius: 6px;
            padding: 12px;
            margin: 8px 0;
            border-left: 4px solid #007acc;
        }}
        
        .query-category {{
            font-weight: bold;
            color: #007acc;
            font-size: 0.9em;
        }}
        
        .query-text {{
            font-family: monospace;
            background: #e9ecef;
            padding: 4px 8px;
            border-radius: 4px;
            margin: 5px 0;
            font-size: 0.85em;
        }}
        
        .query-stats {{
            display: flex;
            gap: 15px;
            font-size: 0.85em;
            color: #666;
        }}
        
        .warning-card {{
            border-left: 4px solid #dc3545;
            background: #fff5f5;
        }}
        
        .success-card {{
            border-left: 4px solid #28a745;
            background: #f8fff8;
        }}
        
        .info-card {{
            border-left: 4px solid #17a2b8;
            background: #f0f9ff;
        }}
        
        .tabs {{
            display: flex;
            border-bottom: 1px solid #e0e0e0;
            margin: 20px 30px 0 30px;
        }}
        
        .tab {{
            padding: 12px 24px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            color: #666;
            font-weight: 500;
        }}
        
        .tab.active {{
            color: #007acc;
            border-bottom-color: #007acc;
        }}
        
        .tab-content {{
            padding: 30px;
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .timestamp {{
            text-align: center;
            color: #666;
            font-size: 0.9em;
            padding: 20px;
            border-top: 1px solid #e0e0e0;
        }}
        
        @media (max-width: 768px) {{
            .dashboard-grid {{
                grid-template-columns: 1fr;
                padding: 20px;
            }}
            
            .tabs {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Bob's Brief Metrics Dashboard</h1>
            <p>Comprehensive analytics for automated cyber intelligence collection</p>
        </div>
        
        <div class="tabs">
            <div class="tab active" onclick="showTab('overview')">Overview</div>
            <div class="tab" onclick="showTab('sources')">Sources</div>
            <div class="tab" onclick="showTab('categories')">Categories</div>
            <div class="tab" onclick="showTab('queries')">Query Performance</div>
        </div>
        
        <div id="overview" class="tab-content active">
            <div class="dashboard-grid">
                <div class="metric-card">
                    <h3>📈 Collection Overview</h3>
                    <div class="big-number">{total_articles:,}</div>
                    <div class="metric-label">Total Articles Collected</div>
                    <hr>
                    <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                        <div>
                            <div style="font-size: 1.5em; font-weight: bold;">{total_sessions}</div>
                            <div class="metric-label">Total Sessions</div>
                        </div>
                        <div>
                            <div style="font-size: 1.5em; font-weight: bold;">{avg_articles_recent:.1f}</div>
                            <div class="metric-label">Avg/Session (7d)</div>
                        </div>
                    </div>
                </div>
                
                <div class="metric-card">
                    <h3>🌐 Source Diversity</h3>
                    <div class="big-number">{total_sources}</div>
                    <div class="metric-label">Unique News Sources</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {min(100, (total_sources / 50) * 100)}%"></div>
                    </div>
                    <div style="font-size: 0.8em; color: #666;">Target: 50+ sources</div>
                </div>
                
                <div class="metric-card">
                    <h3>📂 Category Coverage</h3>
                    <div class="big-number">{total_categories}</div>
                    <div class="metric-label">Categories Monitored</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {min(100, (total_categories / 25) * 100)}%"></div>
                    </div>
                    <div style="font-size: 0.8em; color: #666;">Target: 25+ categories</div>
                </div>
                
                <div class="metric-card">
                    <h3>🎯 Recent Performance</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div>
                            <div style="font-size: 1.3em; font-weight: bold; color: #28a745;">{len([s for s in recent_sessions if s.get('total_articles', 0) >= 100])}</div>
                            <div class="metric-label">High Sessions (100+)</div>
                        </div>
                        <div>
                            <div style="font-size: 1.3em; font-weight: bold; color: #ffc107;">{len([s for s in recent_sessions if s.get('total_articles', 0) < 50])}</div>
                            <div class="metric-label">Low Sessions (&lt;50)</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="sources" class="tab-content">
            <div class="dashboard-grid">
                <div class="metric-card">
                    <h3>🏆 Top News Sources</h3>
                    <div class="source-list">"""
