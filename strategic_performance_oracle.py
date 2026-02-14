#!/usr/bin/env python3
"""
strategic_performance_oracle.py
Advanced Performance Oracle - Creates "something the world has never seen"
Real-time system and Docker container correlation analysis with AI-powered insights
"""

import json
import time
import psutil
import subprocess
import threading
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import logging
import os
import signal
import sys

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    print("Warning: Docker library not available. Install with: pip install docker")
    DOCKER_AVAILABLE = False

@dataclass
class SystemMetrics:
    timestamp: str
    cpu_percent: float
    cpu_count: int
    memory_percent: float
    memory_available_gb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    load_average: List[float]
    processes_count: int
    boot_time: str

@dataclass
class ContainerMetrics:
    name: str
    cpu_percent: float
    memory_usage_mb: float
    memory_percent: float
    network_io_mb: float
    block_io_mb: float
    status: str
    image: str
    created: str

@dataclass
class PerformanceAnalysis:
    timestamp: str
    system: SystemMetrics
    containers: List[ContainerMetrics]
    correlations: Dict[str, Any]
    recommendations: List[str]
    health_score: float
    trend_analysis: Dict[str, str]
    resmon_equivalent: Dict[str, Any]

class StrategicPerformanceOracle:
    """
    The world's first AI-powered Docker ecosystem performance oracle
    Correlates system metrics with container performance for unprecedented insights
    """
    
    def __init__(self, log_dir: str = "./logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Setup enhanced logging
        log_format = '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(f"{log_dir}/strategic_oracle.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("StrategicOracle")
        
        # Docker client (optional)
        self.docker_client = None
        if DOCKER_AVAILABLE:
            try:
                self.docker_client = docker.from_env()
                self.logger.info("✅ Docker client initialized")
            except Exception as e:
                self.logger.warning(f"Docker not available: {e}")
        
        # Performance history
        self.history: List[PerformanceAnalysis] = []
        self.max_history = 500
        
        # Baseline metrics
        self.baseline: Optional[PerformanceAnalysis] = None
        self.running = True
        
        # Performance counters baseline
        self.last_disk_io = None
        self.last_network_io = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Graceful shutdown handler"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        sys.exit(0)
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect comprehensive system metrics (resmon-style analysis)"""
        try:
            # CPU metrics with more detail
            cpu_percent = psutil.cpu_percent(interval=0.1, percpu=False)
            cpu_count = psutil.cpu_count(logical=True)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Disk I/O with delta calculation
            disk_io = psutil.disk_io_counters()
            if disk_io and self.last_disk_io:
                disk_io_read_mb = (disk_io.read_bytes - self.last_disk_io.read_bytes) / (1024**2)
                disk_io_write_mb = (disk_io.write_bytes - self.last_disk_io.write_bytes) / (1024**2)
            else:
                disk_io_read_mb = disk_io.read_bytes / (1024**2) if disk_io else 0
                disk_io_write_mb = disk_io.write_bytes / (1024**2) if disk_io else 0
            self.last_disk_io = disk_io
            
            # Network I/O with delta calculation
            net_io = psutil.net_io_counters()
            if net_io and self.last_network_io:
                network_sent_mb = (net_io.bytes_sent - self.last_network_io.bytes_sent) / (1024**2)
                network_recv_mb = (net_io.bytes_recv - self.last_network_io.bytes_recv) / (1024**2)
            else:
                network_sent_mb = net_io.bytes_sent / (1024**2) if net_io else 0
                network_recv_mb = net_io.bytes_recv / (1024**2) if net_io else 0
            self.last_network_io = net_io
            
            # Load average (Unix-like systems)
            try:
                load_average = list(os.getloadavg())
            except (AttributeError, OSError):
                # Windows approximation
                load_average = [cpu_percent / 100 * cpu_count, cpu_percent / 100 * cpu_count, cpu_percent / 100 * cpu_count]
            
            # Process count
            processes_count = len(psutil.pids())
            
            # Boot time
            boot_time = datetime.fromtimestamp(psutil.boot_time()).isoformat()
            
            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                cpu_count=cpu_count,
                memory_percent=memory_percent,
                memory_available_gb=memory_available_gb,
                disk_io_read_mb=max(0, disk_io_read_mb),  # Ensure non-negative
                disk_io_write_mb=max(0, disk_io_write_mb),
                network_sent_mb=max(0, network_sent_mb),
                network_recv_mb=max(0, network_recv_mb),
                load_average=load_average,
                processes_count=processes_count,
                boot_time=boot_time
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return self._get_fallback_metrics()
    
    def _get_fallback_metrics(self) -> SystemMetrics:
        """Fallback metrics when collection fails"""
        return SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=0, cpu_count=1, memory_percent=0, memory_available_gb=0,
            disk_io_read_mb=0, disk_io_write_mb=0, network_sent_mb=0, network_recv_mb=0,
            load_average=[0, 0, 0], processes_count=0, boot_time=""
        )
    
    def collect_container_metrics(self) -> List[ContainerMetrics]:
        """Collect Docker container metrics with error handling"""
        containers = []
        
        if not self.docker_client:
            return containers
        
        try:
            for container in self.docker_client.containers.list(all=True):
                try:
                    # Skip if container is not running
                    if container.status != 'running':
                        containers.append(ContainerMetrics(
                            name=container.name,
                            cpu_percent=0,
                            memory_usage_mb=0,
                            memory_percent=0,
                            network_io_mb=0,
                            block_io_mb=0,
                            status=container.status,
                            image=container.image.tags[0] if container.image.tags else "unknown",
                            created=container.attrs['Created'][:19]
                        ))
                        continue
                    
                    # Get container stats (non-blocking)
                    stats = container.stats(stream=False, decode=True)
                    
                    # Calculate CPU percentage
                    cpu_percent = self._calculate_container_cpu(stats)
                    
                    # Memory calculations
                    memory_usage = stats['memory_stats'].get('usage', 0)
                    memory_limit = stats['memory_stats'].get('limit', 1)
                    memory_usage_mb = memory_usage / (1024**2)
                    memory_percent = (memory_usage / memory_limit) * 100 if memory_limit > 0 else 0
                    
                    # Network I/O
                    network_io_mb = self._calculate_container_network_io(stats)
                    
                    # Block I/O
                    block_io_mb = self._calculate_container_block_io(stats)
                    
                    containers.append(ContainerMetrics(
                        name=container.name,
                        cpu_percent=cpu_percent,
                        memory_usage_mb=memory_usage_mb,
                        memory_percent=min(100, memory_percent),  # Cap at 100%
                        network_io_mb=network_io_mb,
                        block_io_mb=block_io_mb,
                        status=container.status,
                        image=container.image.tags[0] if container.image.tags else "unknown",
                        created=container.attrs['Created'][:19]
                    ))
                    
                except Exception as e:
                    self.logger.warning(f"Error collecting stats for container {container.name}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error accessing Docker containers: {e}")
        
        return containers
    
    def _calculate_container_cpu(self, stats: dict) -> float:
        """Calculate container CPU percentage with error handling"""
        try:
            cpu_stats = stats.get('cpu_stats', {})
            precpu_stats = stats.get('precpu_stats', {})
            
            cpu_usage = cpu_stats.get('cpu_usage', {})
            precpu_usage = precpu_stats.get('cpu_usage', {})
            
            cpu_delta = cpu_usage.get('total_usage', 0) - precpu_usage.get('total_usage', 0)
            system_cpu_delta = cpu_stats.get('system_cpu_usage', 0) - precpu_stats.get('system_cpu_usage', 0)
            
            if system_cpu_delta > 0 and cpu_delta >= 0:
                cpu_count = len(cpu_usage.get('percpu_usage', [1]))
                cpu_percent = (cpu_delta / system_cpu_delta) * cpu_count * 100
                return min(100 * cpu_count, max(0, cpu_percent))  # Reasonable bounds
            
            return 0.0
            
        except (KeyError, ZeroDivisionError, TypeError) as e:
            return 0.0
    
    def _calculate_container_network_io(self, stats: dict) -> float:
        """Calculate container network I/O in MB"""
        try:
            networks = stats.get('networks', {})
            total_io = 0
            
            for network_stats in networks.values():
                rx_bytes = network_stats.get('rx_bytes', 0)
                tx_bytes = network_stats.get('tx_bytes', 0)
                total_io += rx_bytes + tx_bytes
            
            return total_io / (1024**2)
            
        except (KeyError, TypeError):
            return 0.0
    
    def _calculate_container_block_io(self, stats: dict) -> float:
        """Calculate container block I/O in MB"""
        try:
            blkio_stats = stats.get('blkio_stats', {})
            io_service_bytes = blkio_stats.get('io_service_bytes_recursive', [])
            
            total_io = 0
            for io_stat in io_service_bytes:
                total_io += io_stat.get('value', 0)
            
            return total_io / (1024**2)
            
        except (KeyError, TypeError):
            return 0.0
    
    def analyze_correlations(self, system: SystemMetrics, containers: List[ContainerMetrics]) -> Dict[str, Any]:
        """Advanced correlation analysis - the secret sauce"""
        correlations = {}
        
        try:
            # CPU Analysis
            total_container_cpu = sum(c.cpu_percent for c in containers)
            cpu_efficiency = (total_container_cpu / (system.cpu_percent * system.cpu_count * 100)) * 100 if system.cpu_percent > 0 else 0
            
            correlations['cpu_analysis'] = {
                "system_cpu_percent": system.cpu_percent,
                "total_container_cpu": total_container_cpu,
                "cpu_efficiency": min(100, cpu_efficiency),
                "unaccounted_cpu": max(0, system.cpu_percent - (total_container_cpu / system.cpu_count)),
                "cpu_pressure": "high" if system.cpu_percent > 80 else "medium" if system.cpu_percent > 60 else "low"
            }
            
            # Memory Analysis
            total_container_memory = sum(c.memory_usage_mb for c in containers)
            system_memory_gb = (100 - system.memory_percent) / 100 * (psutil.virtual_memory().total / (1024**3))
            
            correlations['memory_analysis'] = {
                "system_memory_percent": system.memory_percent,
                "total_container_memory_mb": total_container_memory,
                "memory_available_gb": system.memory_available_gb,
                "container_memory_efficiency": (total_container_memory / 1024) / system_memory_gb * 100 if system_memory_gb > 0 else 0,
                "memory_pressure": "critical" if system.memory_percent > 90 else "high" if system.memory_percent > 80 else "medium" if system.memory_percent > 60 else "low"
            }
            
            # I/O Analysis
            total_container_network = sum(c.network_io_mb for c in containers)
            total_container_disk = sum(c.block_io_mb for c in containers)
            
            correlations['io_analysis'] = {
                "system_disk_read_mb": system.disk_io_read_mb,
                "system_disk_write_mb": system.disk_io_write_mb,
                "system_network_sent_mb": system.network_sent_mb,
                "system_network_recv_mb": system.network_recv_mb,
                "container_network_io_mb": total_container_network,
                "container_disk_io_mb": total_container_disk,
                "io_intensity": (system.disk_io_read_mb + system.disk_io_write_mb + system.network_sent_mb + system.network_recv_mb)
            }
            
            # Load Analysis (resmon-style)
            if len(system.load_average) >= 3:
                correlations['load_analysis'] = {
                    "load_1m": system.load_average[0],
                    "load_5m": system.load_average[1],
                    "load_15m": system.load_average[2],
                    "load_trend": self._determine_load_trend(system.load_average),
                    "load_per_core": system.load_average[0] / system.cpu_count,
                    "system_saturation": "critical" if system.load_average[0] > system.cpu_count * 2 else "high" if system.load_average[0] > system.cpu_count else "normal"
                }
            
            # Container Health Analysis
            running_containers = len([c for c in containers if c.status == 'running'])
            total_containers = len(containers)
            
            correlations['container_health'] = {
                "total_containers": total_containers,
                "running_containers": running_containers,
                "container_availability": (running_containers / total_containers * 100) if total_containers > 0 else 100,
                "high_cpu_containers": len([c for c in containers if c.cpu_percent > 50]),
                "high_memory_containers": len([c for c in containers if c.memory_percent > 80])
            }
            
        except Exception as e:
            self.logger.error(f"Error in correlation analysis: {e}")
            correlations['error'] = str(e)
        
        return correlations
    
    def _determine_load_trend(self, load_avg: List[float]) -> str:
        """Determine load average trend"""
        if len(load_avg) < 3:
            return "unknown"
        
        if load_avg[0] > load_avg[1] > load_avg[2]:
            return "increasing"
        elif load_avg[0] < load_avg[1] < load_avg[2]:
            return "decreasing"
        else:
            return "stable"
    
    def generate_intelligent_recommendations(self, analysis: PerformanceAnalysis) -> List[str]:
        """Generate AI-powered recommendations"""
        recommendations = []
        
        try:
            system = analysis.system
            containers = analysis.containers
            corr = analysis.correlations
            
            # CPU Recommendations
            if 'cpu_analysis' in corr:
                cpu_data = corr['cpu_analysis']
                if cpu_data['cpu_pressure'] == 'high':
                    recommendations.append("🚨 HIGH CPU PRESSURE: Consider scaling down services or optimizing container resource limits")
                
                if cpu_data['unaccounted_cpu'] > 25:
                    recommendations.append(f"🔍 SYSTEM ANALYSIS: {cpu_data['unaccounted_cpu']:.1f}% CPU usage outside containers - investigate host processes")
                
                if cpu_data['cpu_efficiency'] < 40:
                    recommendations.append("⚡ EFFICIENCY ALERT: Low container CPU efficiency - consider workload optimization")
            
            # Memory Recommendations
            if 'memory_analysis' in corr:
                mem_data = corr['memory_analysis']
                if mem_data['memory_pressure'] in ['critical', 'high']:
                    recommendations.append(f"🧠 MEMORY {mem_data['memory_pressure'].upper()}: {system.memory_percent:.1f}% usage - risk of OOM conditions")
                
                if mem_data['container_memory_efficiency'] > 90:
                    recommendations.append("📈 MEMORY OPTIMIZATION: Containers using high memory ratio - consider memory limits")
            
            # Load Recommendations
            if 'load_analysis' in corr:
                load_data = corr['load_analysis']
                if load_data['system_saturation'] == 'critical':
                    recommendations.append(f"⚡ CRITICAL OVERLOAD: Load {load_data['load_1m']:.2f} >> {system.cpu_count} cores - immediate action required")
                elif load_data['system_saturation'] == 'high':
                    recommendations.append(f"⚠️ HIGH LOAD: Load {load_data['load_1m']:.2f} > {system.cpu_count} cores - monitor closely")
            
            # Container-specific recommendations
            if 'container_health' in corr:
                health_data = corr['container_health']
                if health_data['container_availability'] < 90:
                    recommendations.append(f"🐋 CONTAINER HEALTH: Only {health_data['running_containers']}/{health_data['total_containers']} containers running")
                
                if health_data['high_cpu_containers'] > 0:
                    high_cpu_names = [c.name for c in containers if c.cpu_percent > 50]
                    recommendations.append(f"🔥 HIGH CPU CONTAINERS: {', '.join(high_cpu_names[:3])} - investigate workload")
                
                if health_data['high_memory_containers'] > 0:
                    high_mem_names = [c.name for c in containers if c.memory_percent > 80]
                    recommendations.append(f"💾 HIGH MEMORY CONTAINERS: {', '.join(high_mem_names[:3])} - check for leaks")
            
            # I/O Recommendations
            if 'io_analysis' in corr:
                io_data = corr['io_analysis']
                total_io = io_data.get('io_intensity', 0)
                if total_io > 100:  # > 100MB/s total I/O
                    recommendations.append(f"💽 HIGH I/O ACTIVITY: {total_io:.1f}MB/s - potential bottleneck")
            
            # Performance Optimization
            if len(self.history) > 5:
                recent_health = [h.health_score for h in self.history[-5:]]
                if all(score < 70 for score in recent_health):
                    recommendations.append("📉 PERFORMANCE DEGRADATION: Consistent low health scores - system optimization needed")
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            recommendations.append(f"⚠️ Analysis Error: {e}")
        
        return recommendations
    
    def calculate_health_score(self, analysis: PerformanceAnalysis) -> float:
        """Calculate comprehensive health score (0-100)"""
        try:
            score = 100.0
            system = analysis.system
            containers = analysis.containers
            
            # CPU Health (30% weight)
            if system.cpu_percent > 95:
                score -= 25
            elif system.cpu_percent > 85:
                score -= 15
            elif system.cpu_percent > 75:
                score -= 10
            elif system.cpu_percent > 65:
                score -= 5
            
            # Memory Health (25% weight)
            if system.memory_percent > 95:
                score -= 20
            elif system.memory_percent > 85:
                score -= 12
            elif system.memory_percent > 75:
                score -= 8
            elif system.memory_percent > 65:
                score -= 4
            
            # Load Average Health (20% weight)
            if len(system.load_average) > 0:
                load_ratio = system.load_average[0] / system.cpu_count
                if load_ratio > 3:
                    score -= 20
                elif load_ratio > 2:
                    score -= 15
                elif load_ratio > 1.5:
                    score -= 10
                elif load_ratio > 1:
                    score -= 5
            
            # Container Health (15% weight)
            if containers:
                running_ratio = len([c for c in containers if c.status == 'running']) / len(containers)
                if running_ratio < 0.7:
                    score -= 15
                elif running_ratio < 0.9:
                    score -= 8
                elif running_ratio < 0.95:
                    score -= 4
            
            # I/O Health (10% weight)
            total_io = system.disk_io_read_mb + system.disk_io_write_mb + system.network_sent_mb + system.network_recv_mb
            if total_io > 500:  # Very high I/O
                score -= 10
            elif total_io > 200:  # High I/O
                score -= 5
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            self.logger.error(f"Error calculating health score: {e}")
            return 50.0  # Neutral score on error
    
    def create_resmon_equivalent_analysis(self, analysis: PerformanceAnalysis) -> Dict[str, Any]:
        """Create analysis equivalent to Windows Resource Monitor"""
        try:
            system = analysis.system
            correlations = analysis.correlations
            
            return {
                "overview": {
                    "cpu_usage_percent": system.cpu_percent,
                    "memory_usage_percent": system.memory_percent,
                    "disk_activity_mb_per_sec": system.disk_io_read_mb + system.disk_io_write_mb,
                    "network_activity_mb_per_sec": system.network_sent_mb + system.network_recv_mb
                },
                "cpu_analysis": {
                    "logical_processors": system.cpu_count,
                    "current_usage": system.cpu_percent,
                    "load_distribution": system.load_average,
                    "processes_count": system.processes_count
                },
                "memory_analysis": {
                    "physical_memory_usage_percent": system.memory_percent,
                    "available_memory_gb": system.memory_available_gb,
                    "container_memory_allocation": correlations.get('memory_analysis', {}).get('total_container_memory_mb', 0)
                },
                "disk_analysis": {
                    "read_activity_mb": system.disk_io_read_mb,
                    "write_activity_mb": system.disk_io_write_mb,
                    "total_activity_mb": system.disk_io_read_mb + system.disk_io_write_mb
                },
                "network_analysis": {
                    "sent_mb": system.network_sent_mb,
                    "received_mb": system.network_recv_mb,
                    "total_activity_mb": system.network_sent_mb + system.network_recv_mb
                },
                "system_health": {
                    "overall_score": analysis.health_score,
                    "status": "excellent" if analysis.health_score > 85 else "good" if analysis.health_score > 70 else "fair" if analysis.health_score > 50 else "poor"
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error creating resmon equivalent: {e}")
            return {"error": str(e)}
    
    def perform_comprehensive_analysis(self) -> PerformanceAnalysis:
        """Perform the comprehensive performance analysis"""
        # Collect all metrics
        system_metrics = self.collect_system_metrics()
        container_metrics = self.collect_container_metrics()
        
        # Analyze correlations
        correlations = self.analyze_correlations(system_metrics, container_metrics)
        
        # Create preliminary analysis
        analysis = PerformanceAnalysis(
            timestamp=datetime.now().isoformat(),
            system=system_metrics,
            containers=container_metrics,
            correlations=correlations,
            recommendations=[],
            health_score=0.0,
            trend_analysis={},
            resmon_equivalent={}
        )
        
        # Generate intelligent recommendations
        analysis.recommendations = self.generate_intelligent_recommendations(analysis)
        
        # Calculate health score
        analysis.health_score = self.calculate_health_score(analysis)
        
        # Create resmon-equivalent analysis
        analysis.resmon_equivalent = self.create_resmon_equivalent_analysis(analysis)
        
        # Trend analysis (if history available)
        if len(self.history) > 2:
            analysis.trend_analysis = self.analyze_performance_trends()
        
        # Store in history
        self.history.append(analysis)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        # Set baseline if not set
        if self.baseline is None:
            self.baseline = analysis
            self.logger.info("📊 Performance baseline established")
        
        return analysis
    
    def analyze_performance_trends(self) -> Dict[str, str]:
        """Analyze performance trends over recent history"""
        if len(self.history) < 3:
            return {"status": "insufficient_data"}
        
        try:
            recent = self.history[-5:]  # Last 5 measurements
            
            # CPU trend
            cpu_values = [h.system.cpu_percent for h in recent]
            cpu_trend = "increasing" if cpu_values[-1] > cpu_values[0] + 5 else "decreasing" if cpu_values[-1] < cpu_values[0] - 5 else "stable"
            
            # Memory trend
            memory_values = [h.system.memory_percent for h in recent]
            memory_trend = "increasing" if memory_values[-1] > memory_values[0] + 5 else "decreasing" if memory_values[-1] < memory_values[0] - 5 else "stable"
            
            # Health trend
            health_values = [h.health_score for h in recent]
            health_trend = "improving" if health_values[-1] > health_values[0] + 5 else "degrading" if health_values[-1] < health_values[0] - 5 else "stable"
            
            # Load trend
            load_values = [h.system.load_average[0] if h.system.load_average else 0 for h in recent]
            load_trend = "increasing" if load_values[-1] > load_values[0] + 0.5 else "decreasing" if load_values[-1] < load_values[0] - 0.5 else "stable"
            
            return {
                "cpu_trend": cpu_trend,
                "memory_trend": memory_trend,
                "health_trend": health_trend,
                "load_trend": load_trend,
                "analysis_window": f"Last {len(recent)} measurements",
                "trend_confidence": "high" if len(recent) >= 5 else "medium"
            }
            
        except Exception as e:
            self.logger.error(f"Error in trend analysis: {e}")
            return {"error": str(e)}
    
    def save_analysis_report(self, analysis: PerformanceAnalysis):
        """Save comprehensive analysis report"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.log_dir}/strategic_analysis_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(asdict(analysis), f, indent=2, default=str)
            
            self.logger.info(f"📄 Analysis report saved: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving analysis report: {e}")
    
    def display_oracle_analysis(self, analysis: PerformanceAnalysis):
        """Display the analysis in spectacular format"""
        print("\n" + "="*90)
        print("🧠 STRATEGIC PERFORMANCE ORACLE - REAL-TIME INTELLIGENCE ANALYSIS 🧠")
        print("="*90)
        print(f"📅 Analysis Time: {analysis.timestamp}")
        print(f"🎯 Health Score: {analysis.health_score:.1f}/100 " + 
              ("🟢 EXCELLENT" if analysis.health_score > 85 else 
               "🟡 GOOD" if analysis.health_score > 70 else 
               "🟠 FAIR" if analysis.health_score > 50 else "🔴 POOR"))
        
        # System Overview
        s = analysis.system
        print(f"\n📊 SYSTEM PERFORMANCE OVERVIEW")
        print(f"  💻 CPU: {s.cpu_percent:.1f}% ({s.cpu_count} cores)")
        print(f"  🧠 Memory: {s.memory_percent:.1f}% ({s.memory_available_gb:.2f}GB available)")
        print(f"  ⚡ Load: {s.load_average[0]:.2f}, {s.load_average[1]:.2f}, {s.load_average[2]:.2f}")
        print(f"  🔄 Processes: {s.processes_count}")
        print(f"  💽 Disk I/O: {s.disk_io_read_mb:.2f}MB R, {s.disk_io_write_mb:.2f}MB W")
        print(f"  🌐 Network: {s.network_sent_mb:.2f}MB ↑, {s.network_recv_mb:.2f}MB ↓")
        
        # Container Overview
        if analysis.containers:
            print(f"\n🐋 CONTAINER ECOSYSTEM ({len(analysis.containers)} containers)")
            running_containers = [c for c in analysis.containers if c.status == 'running']
            print(f"  ✅ Running: {len(running_containers)}/{len(analysis.containers)}")
            
            if running_containers:
                for container in sorted(running_containers, key=lambda x: x.cpu_percent, reverse=True)[:5]:
                    cpu_bar = "█" * min(20, int(container.cpu_percent / 5)) if container.cpu_percent > 0 else ""
                    mem_bar = "█" * min(10, int(container.memory_percent / 10)) if container.memory_percent > 0 else ""
                    print(f"    {container.name}: CPU {container.cpu_percent:.1f}% {cpu_bar:20s} | RAM {container.memory_percent:.1f}% {mem_bar:10s}")
        
        # Correlation Analysis
        if 'cpu_analysis' in analysis.correlations:
            cpu_corr = analysis.correlations['cpu_analysis']
            print(f"\n🔍 INTELLIGENT CORRELATION ANALYSIS")
            print(f"  🖥️  System CPU: {cpu_corr['system_cpu_percent']:.1f}%")
            print(f"  🐋 Container CPU: {cpu_corr['total_container_cpu']:.1f}%")
            print(f"  ❓ Unaccounted: {cpu_corr['unaccounted_cpu']:.1f}%")
            print(f"  ⚡ Efficiency: {cpu_corr['cpu_efficiency']:.1f}%")
            print(f"  📊 Pressure Level: {cpu_corr['cpu_pressure'].upper()}")
        
        if 'load_analysis' in analysis.correlations:
            load_corr = analysis.correlations['load_analysis']
            print(f"  🏋️  Load per Core: {load_corr['load_per_core']:.2f}")
            print(f"  🚨 Saturation: {load_corr['system_saturation'].upper()}")
        
        # Trends
        if analysis.trend_analysis and 'cpu_trend' in analysis.trend_analysis:
            print(f"\n📈 PERFORMANCE TRENDS")
            print(f"  CPU: {analysis.trend_analysis['cpu_trend']} | " +
                  f"Memory: {analysis.trend_analysis['memory_trend']} | " +
                  f"Health: {analysis.trend_analysis['health_trend']}")
        
        # Recommendations
        if analysis.recommendations:
            print(f"\n💡 INTELLIGENT RECOMMENDATIONS")
            for i, rec in enumerate(analysis.recommendations[:7], 1):  # Limit to 7
                print(f"  {i}. {rec}")
        
        # Resmon Equivalent Summary
        if 'overview' in analysis.resmon_equivalent:
            overview = analysis.resmon_equivalent['overview']
            print(f"\n📋 RESMON-EQUIVALENT SUMMARY")
            print(f"  CPU: {overview['cpu_usage_percent']:.1f}% | " +
                  f"Memory: {overview['memory_usage_percent']:.1f}% | " +
                  f"Disk: {overview['disk_activity_mb_per_sec']:.2f}MB/s | " +
                  f"Network: {overview['network_activity_mb_per_sec']:.2f}MB/s")
        
        print("="*90)
    
    def run_continuous_monitoring(self, interval: int = 30):
        """Run continuous performance monitoring"""
        self.logger.info(f"🚀 Starting Strategic Performance Oracle (interval: {interval}s)")
        
        try:
            while self.running:
                # Perform comprehensive analysis
                analysis = self.perform_comprehensive_analysis()
                
                # Display results
                self.display_oracle_analysis(analysis)
                
                # Save report
                self.save_analysis_report(analysis)
                
                # Wait for next iteration
                if self.running:
                    print(f"\n⏱️  Next analysis in {interval} seconds... (Ctrl+C to stop)")
                    time.sleep(interval)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Oracle monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Fatal error in monitoring: {e}")
        finally:
            print("\n💾 Saving final analysis...")
            if self.history:
                self.save_final_summary()
    
    def save_final_summary(self):
        """Save final summary of the monitoring session"""
        try:
            if not self.history:
                return
            
            summary = {
                "session_summary": {
                    "start_time": self.history[0].timestamp,
                    "end_time": self.history[-1].timestamp,
                    "total_analyses": len(self.history),
                    "average_health_score": sum(h.health_score for h in self.history) / len(self.history)
                },
                "peak_metrics": {
                    "max_cpu": max(h.system.cpu_percent for h in self.history),
                    "max_memory": max(h.system.memory_percent for h in self.history),
                    "min_health_score": min(h.health_score for h in self.history),
                    "max_health_score": max(h.health_score for h in self.history)
                },
                "final_analysis": asdict(self.history[-1])
            }
            
            filename = f"{self.log_dir}/strategic_session_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            self.logger.info(f"📊 Session summary saved: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving session summary: {e}")

def main():
    """Main execution - The Oracle Awakens"""
    print("="*90)
    print("🧠 STRATEGICKHAOS PERFORMANCE ORACLE INITIALIZING... 🧠")
    print("Creating something the world has never seen...")
    print("="*90)
    
    oracle = StrategicPerformanceOracle()
    
    try:
        # Check if we should run single analysis or continuous monitoring
        import argparse
        parser = argparse.ArgumentParser(description='Strategic Performance Oracle')
        parser.add_argument('--once', action='store_true', help='Run single analysis')
        parser.add_argument('--interval', type=int, default=30, help='Monitoring interval in seconds')
        
        args = parser.parse_args()
        
        if args.once:
            # Single analysis
            analysis = oracle.perform_comprehensive_analysis()
            oracle.display_oracle_analysis(analysis)
            oracle.save_analysis_report(analysis)
        else:
            # Continuous monitoring
            oracle.run_continuous_monitoring(args.interval)
        
    except Exception as e:
        print(f"❌ Oracle initialization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()