"""
Story Correlation Engine - Mosaic Intelligence
Connects related stories to build the bigger picture

IMPROVEMENTS (v2.0):
- Multi-dimensional entity matching: Requires stories to align on 2+ dimensions
  (e.g., country + technique, or actor + sector) to prevent overly broad clustering
- Cluster size limits: Maximum 15 stories per cluster for focused groupings
- Enhanced entity patterns: Better distinction between cyber ops, supply chain,
  economic warfare, and military intelligence topics
- Narrative coherence: Stories about "China scams" and "China rare earths" no longer
  cluster together just because they mention the same country
"""

import re
from collections import defaultdict
from datetime import datetime
import json
from typing import List, Dict, Set, Tuple


class StoryCorrelator:
    """
    Analyzes stories to find connections and patterns.
    This is the "mosaic intelligence" engine - each story is a tile contributing to the big picture.
    """

    def __init__(self):
        # Common entities that might connect stories
        # These patterns help distinguish different story types for coherent clustering
        self.entity_patterns = {
            'countries': r'\b(China|Chinese|Russia|Russian|Iran|Iranian|Israel|Ukraine|Taiwan|North Korea|DPRK|United States|USA|US|Myanmar|India|European Union|EU)\b',
            'threat_actors': r'\b(APT\d*|Lazarus|Cozy Bear|Fancy Bear|Salt Typhoon|Volt Typhoon|Sandworm|Kimsuky|state-sponsored|nation-state)\b',
            'malware': r'\b(ransomware|malware|trojan|backdoor|rootkit|spyware|wiper)\b',
            'vulnerabilities': r'\b(CVE-\d{4}-\d{4,7}|zero-day|zero day|0day|vulnerability|exploit)\b',
            'techniques': r'\b(phishing|spear-phishing|social engineering|watering hole|DDoS|credential stuffing|attack|breach|hack|intrusion)\b',
            'sectors': r'\b(healthcare|financial|infrastructure|energy|telecom|telecommunications|government|defense|military)\b',
            'tech': r'\b(Ivanti|VMware|Cisco|Microsoft|Google|Apple|Huawei|5G|AI)\b',
            'cyber_ops': r'\b(cyber attack|cyber espionage|cyber[\s-]?threat|data breach|network intrusion|hacking campaign|compromise)\b',
            'supply_chain': r'\b(semiconductor|chip|TSMC|rare[\s-]?earths?|lithium|cobalt|gallium|germanium|supply chain|fab|foundry|wafer)\b',
            'economic': r'\b(sanctions|sanction|tariff|export control|trade war|trade spat|CFIUS|Entity List|forced technology transfer|economic warfare)\b',
            'military': r'\b(drone|UAV|UAS|missile|satellite|ASAT|military operation|combat|military warfare|space warfare)\b',
        }

        # Cyber campaign indicators
        self.campaign_indicators = [
            'attack', 'breach', 'hack', 'exploit', 'compromise', 'intrusion',
            'espionage', 'operation', 'campaign', 'vulnerability'
        ]

    def extract_entities(self, text: str) -> Dict[str, Set[str]]:
        """Extract named entities from text using regex patterns"""
        entities = {}

        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Normalize entities to improve matching
                normalized = set()
                for match in matches:
                    # Convert to uppercase and normalize variations
                    normalized_match = match.upper()
                    # Normalize rare earth variations
                    normalized_match = re.sub(r'RARE[\s-]?EARTHS?', 'RARE EARTH', normalized_match)
                    # Remove hyphens and extra spaces
                    normalized_match = re.sub(r'[\s-]+', ' ', normalized_match).strip()
                    normalized.add(normalized_match)
                entities[entity_type] = normalized

        return entities

    def calculate_story_similarity(self, story1: Dict, story2: Dict) -> float:
        """
        Calculate similarity between two stories based on:
        - Multi-dimensional entity matches (require multiple dimensions to align)
        - Topic overlap
        - Narrative coherence

        This prevents grouping unrelated stories that only share common entities like "China"
        """
        # Extract entities from both stories
        text1 = f"{story1.get('Title', '')} {story1.get('Category', '')}"
        text2 = f"{story2.get('Title', '')} {story2.get('Category', '')}"

        entities1 = self.extract_entities(text1)
        entities2 = self.extract_entities(text2)

        # Check dimensional matches - stories must align on multiple dimensions
        dimensions_matched = 0
        dimension_scores = []

        # Critical dimensions that define narrative coherence
        critical_dimensions = ['threat_actors', 'malware', 'vulnerabilities', 'techniques', 'sectors']

        for entity_type in self.entity_patterns.keys():
            set1 = entities1.get(entity_type, set())
            set2 = entities2.get(entity_type, set())

            if set1 and set2:
                shared = len(set1 & set2)
                total = len(set1 | set2)
                if shared > 0:
                    dimensions_matched += 1
                    dimension_score = shared / total
                    dimension_scores.append(dimension_score)

        # Calculate word overlap (simple TF)
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))

        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                      'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during'}
        words1 -= stop_words
        words2 -= stop_words

        word_overlap = len(words1 & words2) / max(len(words1 | words2), 1)

        # Require at least 2 dimensional matches for coherent clustering
        # Exception: Allow 1 dimension if word overlap is very high (>0.5) indicating same specific topic
        # Stories about "China scams" and "China rare earths" only share 1 dimension (country) + low word overlap
        # Stories about "China APT phishing" and "China APT malware" share 3 dimensions (country, threat_actors, techniques)
        if dimensions_matched < 2:
            # Allow clustering if word overlap is exceptionally high (same specific topic)
            if word_overlap < 0.5:
                return 0.0  # Not enough dimensional overlap for coherent clustering

        # Calculate average dimensional similarity
        entity_similarity = sum(dimension_scores) / len(dimension_scores) if dimension_scores else 0

        # Combine similarities (weighted)
        similarity = (entity_similarity * 0.7) + (word_overlap * 0.3)

        return similarity

    def find_story_clusters(self, stories: List[Dict], threshold: float = 0.3, max_cluster_size: int = 15) -> List[List[Dict]]:
        """
        Group related stories into clusters (the "mosaic tiles")
        Returns list of story clusters

        Args:
            stories: List of story dictionaries
            threshold: Similarity threshold for clustering
            max_cluster_size: Maximum stories per cluster (prevents oversized groupings)
        """
        if not stories:
            return []

        # Build similarity matrix
        n = len(stories)
        clusters = []
        assigned = set()

        for i in range(n):
            if i in assigned:
                continue

            # Start new cluster
            cluster = [stories[i]]
            assigned.add(i)

            # Find similar stories (with size limit)
            for j in range(i + 1, n):
                if j in assigned:
                    continue

                # Stop if cluster is getting too large
                if len(cluster) >= max_cluster_size:
                    break

                similarity = self.calculate_story_similarity(stories[i], stories[j])
                if similarity >= threshold:
                    cluster.append(stories[j])
                    assigned.add(j)

            clusters.append(cluster)

        # Sort clusters by size (larger clusters = bigger stories)
        clusters.sort(key=lambda c: len(c), reverse=True)

        # Split any oversized clusters that slipped through
        refined_clusters = []
        for cluster in clusters:
            if len(cluster) > max_cluster_size:
                # Split into smaller sub-clusters with higher threshold
                sub_clusters = self._split_large_cluster(cluster, threshold + 0.1, max_cluster_size)
                refined_clusters.extend(sub_clusters)
            else:
                refined_clusters.append(cluster)

        return refined_clusters

    def _split_large_cluster(self, cluster: List[Dict], higher_threshold: float, max_size: int) -> List[List[Dict]]:
        """
        Split an oversized cluster into smaller, more coherent sub-clusters
        Uses a higher similarity threshold to ensure tighter grouping
        """
        if len(cluster) <= max_size:
            return [cluster]

        # Re-cluster with higher threshold for better coherence
        sub_clusters = []
        assigned = set()

        for i in range(len(cluster)):
            if i in assigned:
                continue

            sub_cluster = [cluster[i]]
            assigned.add(i)

            for j in range(i + 1, len(cluster)):
                if j in assigned:
                    continue

                if len(sub_cluster) >= max_size:
                    break

                similarity = self.calculate_story_similarity(cluster[i], cluster[j])
                if similarity >= higher_threshold:
                    sub_cluster.append(cluster[j])
                    assigned.add(j)

            sub_clusters.append(sub_cluster)

        return sub_clusters

    def identify_connections(self, stories: List[Dict]) -> Dict:
        """
        Identify key connections between stories to build the intelligence picture
        """
        # Extract all entities across all stories
        entity_map = defaultdict(list)  # entity -> list of stories

        for story in stories:
            text = f"{story.get('Title', '')} {story.get('Category', '')}"
            entities = self.extract_entities(text)

            for entity_type, entity_set in entities.items():
                for entity in entity_set:
                    entity_map[f"{entity_type}:{entity}"].append(story)

        # Find entities mentioned in multiple stories (connection points)
        connections = {}
        for entity, story_list in entity_map.items():
            if len(story_list) > 1:  # Entity appears in multiple stories
                entity_type, entity_name = entity.split(':', 1)
                if entity_type not in connections:
                    connections[entity_type] = {}
                connections[entity_type][entity_name] = {
                    'count': len(story_list),
                    'stories': story_list
                }

        return connections

    def build_intelligence_report(self, stories: List[Dict], threshold: float = 0.3) -> Dict:
        """
        Build comprehensive intelligence report showing the big picture
        """
        clusters = self.find_story_clusters(stories, threshold)
        connections = self.identify_connections(stories)

        # Identify key themes
        themes = defaultdict(int)
        for story in stories:
            category = story.get('Category', 'Unknown')
            themes[category] += 1

        # Build timeline
        timeline = []
        for story in sorted(stories, key=lambda s: s.get('Scraped_At', ''), reverse=True):
            timeline.append({
                'title': story.get('Title'),
                'source': story.get('Source'),
                'category': story.get('Category'),
                'time': story.get('Published'),
                'link': story.get('Link')
            })

        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_stories': len(stories),
                'story_clusters': len(clusters),
                'top_themes': dict(sorted(themes.items(), key=lambda x: x[1], reverse=True)[:10]),
                'connection_points': sum(len(v) for v in connections.values())
            },
            'clusters': [
                {
                    'size': len(cluster),
                    'stories': [
                        {
                            'title': s.get('Title'),
                            'source': s.get('Source'),
                            'category': s.get('Category'),
                            'link': s.get('Link')
                        } for s in cluster
                    ]
                } for cluster in clusters[:20]  # Top 20 clusters
            ],
            'connections': {
                entity_type: {
                    name: {
                        'mention_count': data['count'],
                        'story_titles': [s.get('Title') for s in data['stories'][:5]]
                    }
                    for name, data in sorted(entities.items(), key=lambda x: x[1]['count'], reverse=True)[:10]
                }
                for entity_type, entities in connections.items()
            },
            'timeline': timeline[:50]  # Most recent 50 stories
        }

        return report

    def generate_graph_data(self, stories: List[Dict], threshold: float = 0.3) -> Dict:
        """
        Generate network graph data for visualization
        Nodes = stories, edges = connections
        """
        nodes = []
        edges = []

        # Create nodes
        for i, story in enumerate(stories):
            nodes.append({
                'id': i,
                'label': story.get('Title', '')[:50] + '...',
                'category': story.get('Category'),
                'source': story.get('Source'),
                'link': story.get('Link'),
                'full_title': story.get('Title')
            })

        # Create edges based on similarity
        for i in range(len(stories)):
            for j in range(i + 1, len(stories)):
                similarity = self.calculate_story_similarity(stories[i], stories[j])
                if similarity >= threshold:
                    edges.append({
                        'from': i,
                        'to': j,
                        'weight': similarity
                    })

        return {
            'nodes': nodes,
            'edges': edges
        }


def analyze_stories(stories: List[Dict], similarity_threshold: float = 0.3) -> Dict:
    """
    Main function to analyze stories and build mosaic intelligence
    """
    correlator = StoryCorrelator()

    print(f"\n{'='*60}")
    print("MOSAIC INTELLIGENCE ANALYSIS")
    print(f"{'='*60}")
    print(f"Analyzing {len(stories)} stories to find connections...")

    # Build intelligence report
    report = correlator.build_intelligence_report(stories, similarity_threshold)

    print(f"\nKey Findings:")
    print(f"  • Story clusters identified: {report['summary']['story_clusters']}")
    print(f"  • Connection points found: {report['summary']['connection_points']}")
    print(f"\nTop Themes:")
    for theme, count in list(report['summary']['top_themes'].items())[:5]:
        print(f"  • {theme}: {count} stories")

    print(f"\nKey Connection Points:")
    for entity_type, entities in report['connections'].items():
        if entities:
            print(f"\n  {entity_type.upper()}:")
            for name, data in list(entities.items())[:3]:
                print(f"    • {name}: mentioned in {data['mention_count']} stories")

    # Generate graph data for visualization
    graph_data = correlator.generate_graph_data(stories, similarity_threshold)
    report['graph'] = graph_data

    return report


if __name__ == "__main__":
    # Test with sample data
    sample_stories = [
        {"Title": "China-linked APT group targets US critical infrastructure", "Category": "China Cyber", "Source": "Reuters"},
        {"Title": "New APT campaign discovered targeting energy sector", "Category": "Critical Infrastructure", "Source": "WSJ"},
        {"Title": "Russia-based hackers exploit zero-day vulnerability", "Category": "Russian Cyber", "Source": "BBC"},
    ]

    report = analyze_stories(sample_stories)
    print("\n" + json.dumps(report, indent=2))
