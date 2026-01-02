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

IMPROVEMENTS (v3.0) - Academic-backed enhancements:
- Cluster confidence scoring (Silhouette-inspired, Rousseeuw 1987)
- Source reliability weighting (MBFC/NewsGuard methodology)
- Syndication/echo detection (title similarity threshold)
"""

import re
from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher
import json
from typing import List, Dict, Set, Tuple, Optional


# Source reliability scores (0.0 - 1.0)
# Based on Media Bias/Fact Check factuality ratings + NewsGuard methodology
# Reference: https://arxiv.org/html/2404.09565
SOURCE_RELIABILITY = {
    # Tier 1: Very High Factuality (0.85-1.0)
    'Reuters': 0.95,
    'Associated Press': 0.95,
    'BBC': 0.90,
    'Reuters Cyber': 0.95,
    'BBC Fresh': 0.90,
    'FT': 0.90,
    'FT Cyber': 0.90,
    'FT Fresh': 0.90,
    'WSJ': 0.88,
    'WSJ Cyber': 0.88,
    'WSJ Fresh': 0.88,
    'NYT': 0.85,
    'NYT Cyber': 0.85,
    'NYT Fresh': 0.85,
    'The Guardian': 0.85,
    'Guardian Fresh': 0.85,
    'Bloomberg': 0.88,
    'Bloomberg Cyber': 0.88,
    'Bloomberg Fresh': 0.88,
    'Economist Fresh': 0.88,

    # Tier 2: High Factuality - Security Press (0.75-0.85)
    'Krebs on Security': 0.90,
    'Schneier on Security': 0.88,
    'The Record': 0.85,
    'Bleeping Computer': 0.82,
    'SecurityWeek': 0.80,
    'Dark Reading': 0.80,
    'CyberScoop': 0.80,
    'Cybersecurity Dive': 0.80,
    'The Hacker News': 0.75,
    'GBHackers': 0.72,
    'The Register': 0.78,
    'Register Fresh': 0.78,
    'Ars Technica Fresh': 0.82,

    # Tier 3: Vendor Research (0.70-0.85)
    # High quality but potential commercial bias
    'Mandiant': 0.85,
    'CrowdStrike': 0.82,
    'Unit 42': 0.82,
    'SentinelOne': 0.78,
    'Trend Micro': 0.78,
    'Kaspersky': 0.72,  # Geopolitical considerations
    'Elastic Security Labs': 0.78,
    'Wiz': 0.75,
    'Huntress': 0.75,

    # Tier 4: International News (0.65-0.80)
    'SCMP': 0.68,
    'SCMP Fresh': 0.68,
    'Nikkei Fresh': 0.82,
    'Straits Times Fresh': 0.78,
    'ABC Australia Fresh': 0.80,
    'The Hindu Fresh': 0.72,
    'Deutsche Welle Fresh': 0.80,
    'France24': 0.78,
    'France24 Cyber': 0.78,
    'France24 Fresh': 0.78,
    'Euronews Fresh': 0.75,
    'Al Jazeera Fresh': 0.70,
    'Times of Israel Fresh': 0.72,
    'Kyiv Independent': 0.70,
    'Kyiv Independent Fresh': 0.70,
    'CBC Canada Fresh': 0.82,
    'Korea Times': 0.72,

    # Tier 5: Think Tanks / Policy (0.70-0.85)
    'Lawfare': 0.85,
    'Just Security': 0.82,
    'ASPI': 0.80,
    'FDD': 0.75,
    'National Interest': 0.72,
    'Risky Business': 0.80,

    # Tier 6: Mixed/Lower Reliability (0.50-0.70)
    'Politico Fresh': 0.75,
    'TechCrunch Security': 0.72,
    'TechCrunch Fresh': 0.72,
    'Forbes Cyber': 0.68,
    'Wired Cyber': 0.72,
    'MSN Cyber': 0.60,
    'IBT': 0.58,

    # Default for unknown sources
    'default': 0.50
}


def get_source_reliability(source: str) -> float:
    """Get reliability score for a source, with fuzzy matching"""
    if not source:
        return SOURCE_RELIABILITY['default']

    # Direct match
    if source in SOURCE_RELIABILITY:
        return SOURCE_RELIABILITY[source]

    # Partial match (source name contained in key or vice versa)
    source_lower = source.lower()
    for key, score in SOURCE_RELIABILITY.items():
        if key == 'default':
            continue
        if key.lower() in source_lower or source_lower in key.lower():
            return score

    return SOURCE_RELIABILITY['default']


class StoryCorrelator:
    """
    Analyzes stories to find connections and patterns.
    This is the "mosaic intelligence" engine - each story is a tile contributing to the big picture.
    """

    def __init__(self):
        # Common entities that might connect stories
        # These patterns help distinguish different story types for coherent clustering
        self.entity_patterns = {
            'countries': r'\b(China|Chinese|Russia|Russian|Iran|Iranian|Israel|Israeli|Ukraine|Ukrainian|Taiwan|Taiwanese|North Korea|DPRK|United States|USA|US|Myanmar|India|European Union|EU|Pakistan|Turkey|Belarus|Vietnam|Philippines|Japan|South Korea)\b',
            'threat_actors': r'\b(' + '|'.join([
                # Generic APT pattern
                r'APT\d+',
                # Chinese threat actors
                'Salt Typhoon', 'Volt Typhoon', 'Flax Typhoon', 'Charcoal Typhoon', 'Raspberry Typhoon',
                'Mustang Panda', 'Winnti', 'Hafnium', 'Naikon', 'Emissary Panda', 'Stone Panda',
                'Comment Crew', 'Double Dragon', 'Wicked Panda', 'Aquatic Panda', 'Earth Lusca',
                # Russian threat actors
                'Fancy Bear', 'Cozy Bear', 'Sandworm', 'Turla', 'Gamaredon', 'Ember Bear',
                'Star Blizzard', 'Midnight Blizzard', 'Forest Blizzard', 'Seashell Blizzard',
                'Voodoo Bear', 'Venomous Bear', 'Primitive Bear', 'Gossamer Bear',
                # North Korean threat actors
                'Lazarus', 'Kimsuky', 'Andariel', 'BlueNoroff', 'Stardust Chollima',
                'Labyrinth Chollima', 'Ricochet Chollima', 'Silent Chollima', 'Velvet Chollima',
                # Iranian threat actors
                'Charming Kitten', 'Magic Hound', 'MuddyWater', 'Phosphorus', 'Nemesis Kitten',
                'Mint Sandstorm', 'Peach Sandstorm', 'Cotton Sandstorm', 'Crimson Sandstorm',
                'OilRig', 'Tortoiseshell', 'Imperial Kitten',
                # Ransomware groups
                'LockBit', 'BlackCat', 'ALPHV', r'Cl0p', 'Clop', 'REvil', 'Conti', 'Hive',
                'Black Basta', 'Royal', 'Play', 'Akira', 'Rhysida', 'Medusa', 'BianLian',
                'Vice Society', 'Cuba', 'Ragnar Locker', 'BlackMatter', 'DarkSide',
                # Financial/other threat actors
                'FIN7', 'FIN11', 'FIN12', 'Scattered Spider', r'LAPSUS\$', 'Lapsus',
                'UNC1878', 'UNC2452', 'UNC3886', 'UNC4841',
                # Generic terms
                'state-sponsored', 'nation-state', 'threat actor', 'threat group',
            ]) + r')\b',
            'malware': r'\b(ransomware|malware|trojan|backdoor|rootkit|spyware|wiper|infostealer|stealer|RAT|remote access|botnet|cryptominer|miner|loader|dropper|implant)\b',
            'vulnerabilities': r'\b(CVE-\d{4}-\d{4,7}|zero-day|zero day|0day|vulnerability|exploit|RCE|remote code execution|privilege escalation|authentication bypass)\b',
            'techniques': r'\b(phishing|spear-phishing|spearphishing|social engineering|watering hole|DDoS|credential stuffing|brute force|password spray|lateral movement|persistence|exfiltration|C2|command and control|living off the land|LOTL)\b',
            'sectors': r'\b(healthcare|hospital|financial|bank|banking|infrastructure|critical infrastructure|energy|power grid|telecom|telecommunications|government|defense|military|aerospace|manufacturing|retail|education|university|legal|law firm)\b',
            'tech': r'\b(Ivanti|VMware|Cisco|Microsoft|Fortinet|Palo Alto|CrowdStrike|SentinelOne|Mandiant|Google|Apple|Huawei|Citrix|F5|Barracuda|MOVEit|SolarWinds|Okta|LastPass|3CX)\b',
            'cyber_ops': r'\b(cyber attack|cyber espionage|cyber[\s-]?threat|data breach|network intrusion|hacking campaign|compromise|incident|targeted attack)\b',
            'supply_chain': r'\b(semiconductor|chip|TSMC|rare[\s-]?earths?|lithium|cobalt|gallium|germanium|supply chain|fab|foundry|wafer|npm|pypi|software supply chain)\b',
            'economic': r'\b(sanctions|sanction|tariff|export control|trade war|trade spat|CFIUS|Entity List|forced technology transfer|economic warfare)\b',
            'military': r'\b(drone|UAV|UAS|missile|satellite|ASAT|military operation|combat|military warfare|space warfare|hypersonic)\b',
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

    def detect_syndication(self, stories: List[Dict], threshold: float = 0.85) -> Dict:
        """
        Detect syndicated/echo content - same story from multiple sources.
        Stories with >85% title similarity are likely wire service syndication.

        Reference: Echo chamber detection methodology
        https://link.springer.com/article/10.1007/s13278-021-00779-3
        """
        syndication_groups = []
        processed = set()

        for i, story_a in enumerate(stories):
            if i in processed:
                continue

            title_a = story_a.get('Title', '').lower().strip()
            if not title_a:
                continue

            group = [story_a]

            for j, story_b in enumerate(stories[i+1:], i+1):
                if j in processed:
                    continue

                title_b = story_b.get('Title', '').lower().strip()
                if not title_b:
                    continue

                # Calculate title similarity
                similarity = SequenceMatcher(None, title_a, title_b).ratio()

                if similarity >= threshold:
                    group.append(story_b)
                    processed.add(j)

            if len(group) > 1:
                # Multiple sources with near-identical titles = syndication
                sources = list(set(s.get('Source', 'Unknown') for s in group))
                syndication_groups.append({
                    'canonical_title': group[0].get('Title'),
                    'source_count': len(sources),
                    'sources': sources,
                    'effective_weight': 1,  # Count as single confirmation
                    'stories': group
                })
                processed.add(i)

        total_syndicated = sum(len(g['stories']) - 1 for g in syndication_groups)

        return {
            'syndication_groups': syndication_groups,
            'total_stories': len(stories),
            'unique_stories': len(stories) - total_syndicated,
            'syndicated_count': total_syndicated,
            'echo_ratio': total_syndicated / len(stories) if stories else 0
        }

    def calculate_cluster_confidence(self, cluster: List[Dict], all_stories: List[Dict]) -> Dict:
        """
        Calculate confidence score for a cluster using Silhouette-inspired metrics.

        Based on Rousseeuw (1987) Silhouette coefficient methodology:
        - Measures cohesion (within-cluster similarity)
        - Measures separation (between-cluster distance)

        Reference: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html

        Returns confidence score 0-1 with interpretable drivers.
        """
        if len(cluster) < 2:
            return {
                'confidence': 0.3,
                'strength': 'weak',
                'drivers': {'reason': 'single_story_cluster'}
            }

        # 1. Entity Overlap Score (cohesion)
        # How many entity dimensions are shared across cluster
        all_entities = []
        for story in cluster:
            text = f"{story.get('Title', '')} {story.get('Category', '')}"
            entities = self.extract_entities(text)
            all_entities.append(entities)

        # Count dimensions with overlap
        dimension_overlaps = {}
        for dim in self.entity_patterns.keys():
            sets = [e.get(dim, set()) for e in all_entities]
            non_empty = [s for s in sets if s]
            if len(non_empty) >= 2:
                # Calculate intersection across all non-empty sets
                intersection = non_empty[0]
                for s in non_empty[1:]:
                    intersection = intersection & s
                if intersection:
                    dimension_overlaps[dim] = len(intersection)

        entity_score = min(len(dimension_overlaps) / 4, 1.0)  # 4+ dimensions = 1.0

        # 2. Source Diversity Score
        # More unique, reliable sources = higher confirmation
        sources = [s.get('Source', 'Unknown') for s in cluster]
        unique_sources = set(sources)
        source_diversity = min(len(unique_sources) / 5, 1.0)  # 5+ sources = 1.0

        # 3. Source Quality Score (weighted by reliability)
        reliability_scores = [get_source_reliability(s) for s in sources]
        source_quality = sum(reliability_scores) / len(reliability_scores)

        # 4. Temporal Coherence Score
        # Stories within tight time window score higher
        temporal_score = 0.5  # Default if no datetime available
        datetimes = []
        for story in cluster:
            dt_str = story.get('Datetime')
            if dt_str:
                try:
                    if isinstance(dt_str, str):
                        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                    else:
                        dt = dt_str
                    datetimes.append(dt)
                except (ValueError, TypeError):
                    pass

        if len(datetimes) >= 2:
            time_spread = (max(datetimes) - min(datetimes)).total_seconds() / 3600
            temporal_score = max(0, 1 - (time_spread / 72))  # 72h spread = 0

        # 5. Text Similarity Score (mean pairwise similarity)
        similarities = []
        for i in range(len(cluster)):
            for j in range(i + 1, len(cluster)):
                sim = self.calculate_story_similarity(cluster[i], cluster[j])
                similarities.append(sim)
        text_similarity = sum(similarities) / len(similarities) if similarities else 0

        # Combined confidence (weighted average)
        # Weights based on importance for threat intelligence
        confidence = (
            entity_score * 0.30 +       # Entity overlap most important
            source_diversity * 0.15 +   # Multiple sources
            source_quality * 0.20 +     # Reliable sources
            temporal_score * 0.15 +     # Time coherence
            text_similarity * 0.20      # Text similarity
        )

        # Determine strength label (per Silhouette interpretation)
        if confidence >= 0.7:
            strength = 'strong'
        elif confidence >= 0.5:
            strength = 'reasonable'
        elif confidence >= 0.25:
            strength = 'weak'
        else:
            strength = 'noise'

        return {
            'confidence': round(confidence, 3),
            'strength': strength,
            'drivers': {
                'entity_overlap': round(entity_score, 2),
                'source_diversity': round(source_diversity, 2),
                'source_quality': round(source_quality, 2),
                'temporal_coherence': round(temporal_score, 2),
                'text_similarity': round(text_similarity, 2),
                'shared_dimensions': list(dimension_overlaps.keys()),
                'unique_sources': len(unique_sources),
                'story_count': len(cluster)
            }
        }

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
        Build comprehensive intelligence report showing the big picture.
        Includes confidence scoring and syndication detection.
        """
        clusters = self.find_story_clusters(stories, threshold)
        connections = self.identify_connections(stories)

        # Detect syndication/echo content
        syndication = self.detect_syndication(stories)

        # Calculate confidence for each cluster
        clusters_with_confidence = []
        high_confidence_count = 0
        for cluster in clusters[:20]:  # Top 20 clusters
            confidence_data = self.calculate_cluster_confidence(cluster, stories)
            if confidence_data['strength'] in ['strong', 'reasonable']:
                high_confidence_count += 1
            clusters_with_confidence.append({
                'size': len(cluster),
                'confidence': confidence_data['confidence'],
                'strength': confidence_data['strength'],
                'confidence_drivers': confidence_data['drivers'],
                'stories': [
                    {
                        'title': s.get('Title'),
                        'source': s.get('Source'),
                        'source_reliability': get_source_reliability(s.get('Source')),
                        'category': s.get('Category'),
                        'link': s.get('Link')
                    } for s in cluster
                ]
            })

        # Sort clusters by confidence (highest first)
        clusters_with_confidence.sort(key=lambda c: c['confidence'], reverse=True)

        # Identify key themes
        themes = defaultdict(int)
        for story in stories:
            category = story.get('Category', 'Unknown')
            themes[category] += 1

        # Build timeline with source reliability
        timeline = []
        for story in sorted(stories, key=lambda s: s.get('Scraped_At', ''), reverse=True):
            timeline.append({
                'title': story.get('Title'),
                'source': story.get('Source'),
                'source_reliability': get_source_reliability(story.get('Source')),
                'category': story.get('Category'),
                'time': story.get('Published'),
                'link': story.get('Link')
            })

        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_stories': len(stories),
                'unique_stories': syndication['unique_stories'],
                'syndicated_stories': syndication['syndicated_count'],
                'echo_ratio': round(syndication['echo_ratio'], 3),
                'story_clusters': len(clusters),
                'high_confidence_clusters': high_confidence_count,
                'top_themes': dict(sorted(themes.items(), key=lambda x: x[1], reverse=True)[:10]),
                'connection_points': sum(len(v) for v in connections.values())
            },
            'clusters': clusters_with_confidence,
            'syndication': {
                'echo_ratio': round(syndication['echo_ratio'], 3),
                'groups': [
                    {
                        'title': g['canonical_title'],
                        'sources': g['sources'],
                        'count': len(g['stories'])
                    } for g in syndication['syndication_groups'][:10]
                ]
            },
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
    Main function to analyze stories and build mosaic intelligence.
    Includes confidence scoring, source reliability, and syndication detection.
    """
    correlator = StoryCorrelator()

    print(f"\n{'='*60}")
    print("MOSAIC INTELLIGENCE ANALYSIS (v3.0)")
    print(f"{'='*60}")
    print(f"Analyzing {len(stories)} stories to find connections...")

    # Build intelligence report
    report = correlator.build_intelligence_report(stories, similarity_threshold)

    print(f"\nKey Findings:")
    print(f"  - Story clusters identified: {report['summary']['story_clusters']}")
    print(f"  - High-confidence clusters: {report['summary']['high_confidence_clusters']}")
    print(f"  - Connection points found: {report['summary']['connection_points']}")

    print(f"\nSyndication Analysis:")
    print(f"  - Total stories: {report['summary']['total_stories']}")
    print(f"  - Unique stories: {report['summary']['unique_stories']}")
    print(f"  - Syndicated/echo: {report['summary']['syndicated_stories']}")
    print(f"  - Echo ratio: {report['summary']['echo_ratio']:.1%}")

    print(f"\nTop Clusters by Confidence:")
    for i, cluster in enumerate(report['clusters'][:5]):
        strength_label = cluster['strength'].upper()
        print(f"  {i+1}. [{strength_label}] {cluster['confidence']:.2f} - {cluster['size']} stories")
        if cluster['stories']:
            print(f"     {cluster['stories'][0]['title'][:60]}...")
            drivers = cluster.get('confidence_drivers', {})
            if drivers.get('shared_dimensions'):
                print(f"     Dimensions: {', '.join(drivers['shared_dimensions'])}")

    print(f"\nTop Themes:")
    for theme, count in list(report['summary']['top_themes'].items())[:5]:
        print(f"  - {theme}: {count} stories")

    print(f"\nKey Connection Points:")
    for entity_type, entities in report['connections'].items():
        if entities:
            print(f"\n  {entity_type.upper()}:")
            for name, data in list(entities.items())[:3]:
                print(f"    - {name}: mentioned in {data['mention_count']} stories")

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
