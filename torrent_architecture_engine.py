#!/usr/bin/env python3
"""
🌱 TORRENT ARCHITECTURE ENGINE v1.0
Advanced P2P Network Analysis & Distributed Data System
Creates custom torrents for monitoring data and analyzes peer networks
"""

import hashlib
import bencodepy
import socket
import threading
import time
import json
import struct
import random
import urllib.parse
import requests
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import os
import mimetypes

@dataclass
class TorrentInfo:
    info_hash: str
    name: str
    length: int
    piece_length: int
    pieces_count: int
    announce_url: str
    creation_date: datetime
    created_by: str
    comment: str

@dataclass
class PeerInfo:
    ip: str
    port: int
    peer_id: str
    client: str
    country: Optional[str] = None
    upload_speed: Optional[int] = None
    download_speed: Optional[int] = None
    completed: Optional[bool] = None
    last_seen: Optional[datetime] = None

@dataclass
class TrackerResponse:
    interval: int
    peers: List[PeerInfo]
    seeders: int
    leechers: int
    downloaded: int
    tracker_url: str
    response_time: float

class TorrentArchitectureEngine:
    def __init__(self, tracker_urls: List[str] = None):
        self.tracker_urls = tracker_urls or [
            'http://tracker.openbittorrent.com:80/announce',
            'udp://tracker.openbittorrent.com:80/announce',
            'http://tracker.opentrackr.org:1337/announce',
            'udp://tracker.opentrackr.org:1337/announce'
        ]
        self.created_torrents = []
        self.peer_database = {}
        self.tracker_responses = []
        
    def create_advanced_torrent(self, 
                               file_path: str = None,
                               data: bytes = None,
                               name: str = None,
                               comment: str = "Sovereignty Architecture Data",
                               private: bool = False,
                               piece_size: int = 524288) -> TorrentInfo:
        """Create advanced torrent with custom metadata and multi-tracker support"""
        
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                file_data = f.read()
            torrent_name = name or os.path.basename(file_path)
        elif data:
            file_data = data
            torrent_name = name or f"sovereignty_data_{int(time.time())}.bin"
        else:
            raise ValueError("Either file_path or data must be provided")
        
        # Calculate pieces
        pieces = []
        for i in range(0, len(file_data), piece_size):
            piece = file_data[i:i + piece_size]
            pieces.append(hashlib.sha1(piece).digest())
        
        # Create torrent info dictionary
        info = {
            'name': torrent_name.encode('utf-8'),
            'length': len(file_data),
            'piece length': piece_size,
            'pieces': b''.join(pieces)
        }
        
        if private:
            info['private'] = 1
        
        # Create full torrent dictionary
        torrent_dict = {
            'announce': self.tracker_urls[0],
            'announce-list': [[url] for url in self.tracker_urls],
            'info': info,
            'comment': comment,
            'created by': 'Sovereignty Architecture Engine v1.0',
            'creation date': int(time.time()),
            'encoding': 'UTF-8'
        }
        
        # Add custom sovereignty metadata
        torrent_dict['sovereignty-metadata'] = {
            'generator': 'TorrentArchitectureEngine',
            'version': '1.0',
            'classification': 'network-monitoring',
            'encryption-capable': True,
            'peer-exchange': True,
            'fast-resume': True
        }
        
        # Encode torrent
        torrent_bytes = bencodepy.encode(torrent_dict)
        
        # Calculate info hash
        info_hash = hashlib.sha1(bencodepy.encode(info)).hexdigest()
        
        # Save torrent file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        torrent_filename = f"sovereignty_{torrent_name}_{timestamp}.torrent"
        
        with open(torrent_filename, 'wb') as f:
            f.write(torrent_bytes)
        
        # Create TorrentInfo object
        torrent_info = TorrentInfo(
            info_hash=info_hash,
            name=torrent_name,
            length=len(file_data),
            piece_length=piece_size,
            pieces_count=len(pieces),
            announce_url=self.tracker_urls[0],
            creation_date=datetime.now(),
            created_by='Sovereignty Architecture Engine v1.0',
            comment=comment
        )
        
        self.created_torrents.append({
            'info': torrent_info,
            'filename': torrent_filename,
            'file_data': file_data
        })
        
        return torrent_info
    
    def parse_torrent_file(self, torrent_path: str) -> Dict:
        """Parse existing torrent file and extract detailed information"""
        try:
            with open(torrent_path, 'rb') as f:
                torrent_data = bencodepy.decode(f.read())
            
            # Extract info hash
            info_hash = hashlib.sha1(bencodepy.encode(torrent_data[b'info'])).hexdigest()
            
            # Parse torrent structure
            parsed = {
                'info_hash': info_hash,
                'announce': torrent_data.get(b'announce', b'').decode('utf-8', errors='ignore'),
                'announce_list': [],
                'name': torrent_data[b'info'][b'name'].decode('utf-8', errors='ignore'),
                'length': torrent_data[b'info'].get(b'length', 0),
                'piece_length': torrent_data[b'info'][b'piece length'],
                'pieces_count': len(torrent_data[b'info'][b'pieces']) // 20,
                'comment': torrent_data.get(b'comment', b'').decode('utf-8', errors='ignore'),
                'created_by': torrent_data.get(b'created by', b'').decode('utf-8', errors='ignore'),
                'creation_date': datetime.fromtimestamp(torrent_data.get(b'creation date', 0)),
                'private': torrent_data[b'info'].get(b'private', 0) == 1,
                'files': []
            }
            
            # Parse announce list
            if b'announce-list' in torrent_data:
                for tier in torrent_data[b'announce-list']:
                    tier_urls = [url.decode('utf-8', errors='ignore') for url in tier]
                    parsed['announce_list'].append(tier_urls)
            
            # Parse files (multi-file torrent)
            if b'files' in torrent_data[b'info']:
                for file_info in torrent_data[b'info'][b'files']:
                    file_path = '/'.join([p.decode('utf-8', errors='ignore') for p in file_info[b'path']])
                    parsed['files'].append({
                        'path': file_path,
                        'length': file_info[b'length']
                    })
            
            return parsed
            
        except Exception as e:
            return {'error': str(e)}
    
    async def analyze_tracker_network(self, info_hash: str, max_trackers: int = 10) -> List[TrackerResponse]:
        """Analyze tracker network and gather peer information"""
        responses = []
        
        # Generate random peer ID
        peer_id = self._generate_peer_id()
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            tasks = []
            
            for tracker_url in self.tracker_urls[:max_trackers]:
                task = self._query_tracker(session, tracker_url, info_hash, peer_id)
                tasks.append(task)
            
            # Execute tracker queries concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, TrackerResponse):
                    responses.append(result)
                    self.tracker_responses.append(result)
        
        return responses
    
    async def _query_tracker(self, session: aiohttp.ClientSession, tracker_url: str, 
                           info_hash: str, peer_id: str) -> Optional[TrackerResponse]:
        """Query individual tracker for peer information"""
        try:
            start_time = time.time()
            
            # Prepare tracker parameters
            params = {
                'info_hash': bytes.fromhex(info_hash),
                'peer_id': peer_id.encode(),
                'port': 6881,
                'uploaded': 0,
                'downloaded': 0,
                'left': 1000000,  # Fake remaining bytes
                'compact': 1,
                'event': 'started'
            }
            
            if tracker_url.startswith('http'):
                # HTTP tracker
                response = await self._query_http_tracker(session, tracker_url, params)
            elif tracker_url.startswith('udp'):
                # UDP tracker
                response = await self._query_udp_tracker(tracker_url, params)
            else:
                return None
            
            response_time = time.time() - start_time
            
            if response:
                return TrackerResponse(
                    interval=response.get('interval', 1800),
                    peers=response.get('peers', []),
                    seeders=response.get('complete', 0),
                    leechers=response.get('incomplete', 0),
                    downloaded=response.get('downloaded', 0),
                    tracker_url=tracker_url,
                    response_time=response_time
                )
                
        except Exception as e:
            print(f"Tracker query failed for {tracker_url}: {e}")
            return None
    
    async def _query_http_tracker(self, session: aiohttp.ClientSession, 
                                 tracker_url: str, params: Dict) -> Optional[Dict]:
        """Query HTTP/HTTPS tracker"""
        try:
            # URL encode parameters
            query_params = {}
            for key, value in params.items():
                if isinstance(value, bytes):
                    query_params[key] = value
                else:
                    query_params[key] = str(value)
            
            async with session.get(tracker_url, params=query_params) as response:
                if response.status == 200:
                    data = await response.read()
                    parsed = bencodepy.decode(data)
                    
                    # Parse response
                    result = {
                        'interval': parsed.get(b'interval', 1800),
                        'complete': parsed.get(b'complete', 0),
                        'incomplete': parsed.get(b'incomplete', 0),
                        'downloaded': parsed.get(b'downloaded', 0),
                        'peers': []
                    }
                    
                    # Parse peers
                    if b'peers' in parsed:
                        peers_data = parsed[b'peers']
                        if isinstance(peers_data, bytes):
                            # Compact format
                            result['peers'] = self._parse_compact_peers(peers_data)
                        elif isinstance(peers_data, list):
                            # Dictionary format
                            result['peers'] = self._parse_dict_peers(peers_data)
                    
                    return result
                    
        except Exception as e:
            return None
    
    async def _query_udp_tracker(self, tracker_url: str, params: Dict) -> Optional[Dict]:
        """Query UDP tracker (simplified implementation)"""
        try:
            # Parse UDP tracker URL
            parsed_url = urllib.parse.urlparse(tracker_url)
            host = parsed_url.hostname
            port = parsed_url.port or 80
            
            # Create UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(10)
            
            # Connection request
            transaction_id = random.randint(0, 2**32 - 1)
            connect_packet = struct.pack('!QII', 0x41727101980, 0, transaction_id)
            
            sock.sendto(connect_packet, (host, port))
            response, _ = sock.recvfrom(16)
            
            if len(response) >= 16:
                action, ret_transaction_id, connection_id = struct.unpack('!IIQ', response)
                
                if action == 0 and ret_transaction_id == transaction_id:
                    # Announce request
                    announce_packet = struct.pack(
                        '!QII20s20sQQQIIIiH',
                        connection_id, 1, transaction_id,
                        bytes.fromhex(params['info_hash'].hex()),
                        params['peer_id'],
                        params['downloaded'], params['left'], params['uploaded'],
                        2, 0, 0, -1, params['port']
                    )
                    
                    sock.sendto(announce_packet, (host, port))
                    response, _ = sock.recvfrom(1024)
                    
                    if len(response) >= 20:
                        action, ret_transaction_id, interval, leechers, seeders = struct.unpack('!IIIII', response[:20])
                        
                        if action == 1 and ret_transaction_id == transaction_id:
                            peers_data = response[20:]
                            peers = self._parse_compact_peers(peers_data)
                            
                            sock.close()
                            return {
                                'interval': interval,
                                'incomplete': leechers,
                                'complete': seeders,
                                'downloaded': 0,
                                'peers': peers
                            }
            
            sock.close()
            return None
            
        except Exception as e:
            return None
    
    def _parse_compact_peers(self, peers_data: bytes) -> List[PeerInfo]:
        """Parse compact peer format (6 bytes per peer)"""
        peers = []
        for i in range(0, len(peers_data), 6):
            if i + 6 <= len(peers_data):
                ip_bytes = peers_data[i:i+4]
                port_bytes = peers_data[i+4:i+6]
                
                ip = socket.inet_ntoa(ip_bytes)
                port = struct.unpack('!H', port_bytes)[0]
                
                peer = PeerInfo(
                    ip=ip,
                    port=port,
                    peer_id=f"unknown_{ip}_{port}",
                    client="Unknown",
                    last_seen=datetime.now()
                )
                peers.append(peer)
                
                # Store in peer database
                peer_key = f"{ip}:{port}"
                self.peer_database[peer_key] = peer
        
        return peers
    
    def _parse_dict_peers(self, peers_list: List) -> List[PeerInfo]:
        """Parse dictionary peer format"""
        peers = []
        for peer_dict in peers_list:
            ip = peer_dict.get(b'ip', b'').decode('utf-8')
            port = peer_dict.get(b'port', 0)
            peer_id = peer_dict.get(b'peer id', b'').decode('utf-8', errors='ignore')
            
            peer = PeerInfo(
                ip=ip,
                port=port,
                peer_id=peer_id,
                client=self._identify_client(peer_id),
                last_seen=datetime.now()
            )
            peers.append(peer)
            
            # Store in peer database
            peer_key = f"{ip}:{port}"
            self.peer_database[peer_key] = peer
        
        return peers
    
    def _identify_client(self, peer_id: str) -> str:
        """Identify BitTorrent client from peer ID"""
        if not peer_id or len(peer_id) < 8:
            return "Unknown"
        
        # Common client identification patterns
        client_patterns = {
            '-AZ': 'Azureus/Vuze',
            '-UT': 'µTorrent',
            '-TR': 'Transmission',
            '-DE': 'Deluge',
            '-qB': 'qBittorrent',
            '-LT': 'libtorrent',
            '-RT': 'rTorrent',
            '-PC': 'CacheLogic WebSeeder',
            '-BC': 'BitComet'
        }
        
        for pattern, client in client_patterns.items():
            if peer_id.startswith(pattern):
                return client
        
        return "Unknown"
    
    def _generate_peer_id(self) -> str:
        """Generate random peer ID for tracker queries"""
        client_id = "-SV1000-"  # Sovereignty v1.0.0
        random_part = ''.join(random.choices('0123456789ABCDEF', k=12))
        return client_id + random_part
    
    def analyze_peer_network_topology(self) -> Dict:
        """Analyze peer network topology and patterns"""
        if not self.peer_database:
            return {'error': 'No peer data available'}
        
        analysis = {
            'total_peers': len(self.peer_database),
            'ip_ranges': {},
            'port_distribution': {},
            'client_distribution': {},
            'geographic_distribution': {},
            'network_patterns': []
        }
        
        # Analyze IP ranges
        ip_ranges = {}
        for peer_key, peer in self.peer_database.items():
            ip_parts = peer.ip.split('.')
            if len(ip_parts) >= 2:
                subnet = f"{ip_parts[0]}.{ip_parts[1]}.x.x"
                ip_ranges[subnet] = ip_ranges.get(subnet, 0) + 1
        
        analysis['ip_ranges'] = dict(sorted(ip_ranges.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Analyze port distribution
        port_dist = {}
        for peer_key, peer in self.peer_database.items():
            port_dist[peer.port] = port_dist.get(peer.port, 0) + 1
        
        analysis['port_distribution'] = dict(sorted(port_dist.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Analyze client distribution
        client_dist = {}
        for peer_key, peer in self.peer_database.items():
            client_dist[peer.client] = client_dist.get(peer.client, 0) + 1
        
        analysis['client_distribution'] = dict(sorted(client_dist.items(), key=lambda x: x[1], reverse=True))
        
        # Identify network patterns
        patterns = []
        
        # Check for suspicious port concentrations
        common_ports = [6881, 6969, 8080, 51413]
        for port in common_ports:
            count = port_dist.get(port, 0)
            if count > 0:
                patterns.append(f"Port {port}: {count} peers (common BitTorrent port)")
        
        # Check for IP clustering
        for subnet, count in list(analysis['ip_ranges'].items())[:5]:
            if count > 10:
                patterns.append(f"IP cluster in {subnet}: {count} peers (possible datacenter/VPN)")
        
        analysis['network_patterns'] = patterns
        
        return analysis
    
    def create_monitoring_data_torrent(self, monitoring_data: Dict) -> TorrentInfo:
        """Create torrent specifically for network monitoring data"""
        # Serialize monitoring data
        data_json = json.dumps(monitoring_data, indent=2, default=str)
        data_bytes = data_json.encode('utf-8')
        
        # Add metadata
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"network_monitoring_{timestamp}.json"
        comment = f"Network Sovereignty Monitoring Data - {len(monitoring_data.get('events', []))} events"
        
        return self.create_advanced_torrent(
            data=data_bytes,
            name=name,
            comment=comment,
            private=True,  # Keep monitoring data private
            piece_size=262144  # Smaller pieces for faster distribution
        )
    
    def generate_torrent_analysis_report(self) -> str:
        """Generate comprehensive torrent network analysis report"""
        peer_analysis = self.analyze_peer_network_topology()
        
        report = f"""
🌱 TORRENT ARCHITECTURE ANALYSIS REPORT
Generated: {datetime.now().isoformat()}

=== TORRENT CREATION SUMMARY ===
Total Torrents Created: {len(self.created_torrents)}
Active Trackers: {len(self.tracker_urls)}
Tracker Responses: {len(self.tracker_responses)}

"""
        
        for i, torrent in enumerate(self.created_torrents, 1):
            info = torrent['info']
            report += f"""
Torrent #{i}: {info.name}
• Info Hash: {info.info_hash}
• Size: {info.length:,} bytes
• Pieces: {info.pieces_count}
• Created: {info.creation_date.strftime('%Y-%m-%d %H:%M:%S')}
• File: {torrent['filename']}
"""
        
        report += f"""
=== PEER NETWORK ANALYSIS ===
"""
        
        if peer_analysis.get('error'):
            report += f"Error: {peer_analysis['error']}\n"
        else:
            report += f"""
Total Peers Discovered: {peer_analysis['total_peers']}

Top IP Ranges:
"""
            for subnet, count in list(peer_analysis['ip_ranges'].items())[:5]:
                report += f"• {subnet}: {count} peers\n"
            
            report += f"""
Common Ports:
"""
            for port, count in list(peer_analysis['port_distribution'].items())[:5]:
                report += f"• Port {port}: {count} peers\n"
            
            report += f"""
Client Distribution:
"""
            for client, count in peer_analysis['client_distribution'].items():
                report += f"• {client}: {count} peers\n"
            
            if peer_analysis['network_patterns']:
                report += f"""
Network Patterns:
"""
                for pattern in peer_analysis['network_patterns']:
                    report += f"• {pattern}\n"
        
        report += f"""
=== TRACKER PERFORMANCE ===
"""
        
        if self.tracker_responses:
            avg_response_time = sum(r.response_time for r in self.tracker_responses) / len(self.tracker_responses)
            total_seeders = sum(r.seeders for r in self.tracker_responses)
            total_leechers = sum(r.leechers for r in self.tracker_responses)
            
            report += f"""
Average Response Time: {avg_response_time:.2f} seconds
Total Seeders: {total_seeders}
Total Leechers: {total_leechers}
Active Trackers: {len(set(r.tracker_url for r in self.tracker_responses))}

Tracker Details:
"""
            for response in self.tracker_responses[:10]:  # Limit to top 10
                report += f"• {response.tracker_url}: {len(response.peers)} peers, {response.response_time:.2f}s\n"
        else:
            report += "No tracker responses recorded\n"
        
        report += f"""
=== SOVEREIGNTY CAPABILITIES ===
✅ Advanced torrent creation with multi-tracker support
✅ Real-time peer network analysis and topology mapping
✅ Monitoring data distribution via P2P network
✅ Client identification and network pattern detection
✅ Private torrent creation for sensitive monitoring data

=== RECOMMENDATIONS ===
1. Use private torrents for sensitive monitoring data
2. Implement peer verification for security
3. Set up dedicated tracker for internal sovereignty network
4. Create automated monitoring data distribution schedules
5. Correlate peer networks with performance monitoring

=== NEXT STEPS ===
• Integrate with X.com Intelligence Parser for web scraping distribution
• Create Obsidian knowledge graph from torrent network topology
• Implement real-time peer monitoring and alerts
• Set up distributed computing using torrent peer network
"""
        
        return report

async def main():
    """Main execution function with async support"""
    print("🌱 TORRENT ARCHITECTURE ENGINE")
    print("=" * 50)
    
    engine = TorrentArchitectureEngine()
    
    # Create sample monitoring data
    sample_monitoring_data = {
        'events': [
            {
                'timestamp': datetime.now().isoformat(),
                'event_type': 'NETWORK_SCAN',
                'target': 'sovereignty.network',
                'status': 'SUCCESS',
                'details': {'ports_open': [80, 443, 6881], 'response_time': 0.15}
            }
        ],
        'metadata': {
            'generator': 'NetworkSovereigntyMonitor',
            'version': '1.0',
            'classification': 'network-intelligence'
        }
    }
    
    # Create torrent from monitoring data
    print("\n🌱 Creating Monitoring Data Torrent...")
    torrent_info = engine.create_monitoring_data_torrent(sample_monitoring_data)
    print(f"Torrent Created: {torrent_info.name}")
    print(f"Info Hash: {torrent_info.info_hash}")
    print(f"Pieces: {torrent_info.pieces_count}")
    
    # Analyze tracker network
    print("\n🔍 Analyzing Tracker Network...")
    try:
        tracker_responses = await engine.analyze_tracker_network(torrent_info.info_hash, max_trackers=5)
        print(f"Tracker Responses: {len(tracker_responses)}")
        
        for response in tracker_responses:
            print(f"• {response.tracker_url}: {len(response.peers)} peers, {response.response_time:.2f}s")
    except Exception as e:
        print(f"Tracker analysis error: {e}")
    
    # Analyze peer network
    print("\n📊 Analyzing Peer Network...")
    peer_analysis = engine.analyze_peer_network_topology()
    
    if not peer_analysis.get('error'):
        print(f"Total Peers: {peer_analysis['total_peers']}")
        print(f"IP Ranges: {len(peer_analysis['ip_ranges'])}")
        print(f"Client Types: {len(peer_analysis['client_distribution'])}")
    else:
        print(f"Peer analysis: {peer_analysis['error']}")
    
    # Generate comprehensive report
    print("\n📋 Generating Torrent Analysis Report...")
    report = engine.generate_torrent_analysis_report()
    print(report)
    
    # Save report
    report_filename = f"torrent_analysis_report_{int(time.time())}.txt"
    with open(report_filename, 'w') as f:
        f.write(report)
    
    print(f"\n✅ Report saved to: {report_filename}")
    
    # List created files
    print(f"✅ Created files:")
    for torrent in engine.created_torrents:
        print(f"   • {torrent['filename']} ({torrent['info'].info_hash})")

if __name__ == "__main__":
    # Run with asyncio
    asyncio.run(main())