#!/usr/bin/env python3
"""
LEGION Windows Defender Antibody Framework
Advanced mitigation system for Windows Defender interference with development environments
"""

import json
import subprocess
import os
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from pathlib import Path
try:
    import winreg
except ImportError:
    winreg = None  # Not available on non-Windows systems

@dataclass
class DefenderThreat:
    threat_type: str
    threat_source: str
    impact_level: str
    description: str
    mitigation_strategy: str
    antibody_commands: List[str]

@dataclass
class IDEProtectionProfile:
    ide_name: str
    executable_paths: List[str]
    project_extensions: List[str]
    temp_directories: List[str]
    cache_locations: List[str]
    exclusion_patterns: List[str]

class WindowsDefenderAntibody:
    """Create targeted antibodies against Windows Defender interference"""
    
    def __init__(self):
        self.defender_threats = {
            'real_time_scanning': {
                'description': 'Real-time protection scanning IDE files and project folders',
                'impact': 'HIGH - Causes significant performance degradation',
                'antibody': 'Selective exclusions and process whitelisting'
            },
            'cloud_protection': {
                'description': 'Cloud-delivered protection analyzing unknown files',
                'impact': 'MEDIUM - Network delays and false positives',
                'antibody': 'Disable cloud scanning for development directories'
            },
            'behavior_monitoring': {
                'description': 'Behavior monitoring flagging development tools as suspicious',
                'impact': 'HIGH - Blocks legitimate development activities',
                'antibody': 'Whitelist development processes and scripts'
            },
            'sample_submission': {
                'description': 'Automatic sample submission sending code to Microsoft',
                'impact': 'CRITICAL - Privacy and intellectual property risk',
                'antibody': 'Disable automatic sample submission'
            },
            'tamper_protection': {
                'description': 'Tamper protection preventing configuration changes',
                'impact': 'MEDIUM - Blocks antibody deployment',
                'antibody': 'Administrative bypass techniques'
            }
        }
        
        self.ide_profiles = {
            'visual_studio_code': IDEProtectionProfile(
                ide_name='Visual Studio Code',
                executable_paths=[
                    r'%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe',
                    r'%PROGRAMFILES%\Microsoft VS Code\Code.exe',
                    r'%APPDATA%\Code\User\*'
                ],
                project_extensions=['.js', '.ts', '.py', '.json', '.md', '.yml', '.yaml'],
                temp_directories=[
                    r'%APPDATA%\Code\CachedExtensions',
                    r'%APPDATA%\Code\logs',
                    r'%TEMP%\vscode-*'
                ],
                cache_locations=[
                    r'%APPDATA%\Code\User\workspaceStorage',
                    r'%LOCALAPPDATA%\Microsoft\TypeScript'
                ],
                exclusion_patterns=[
                    r'%USERPROFILE%\Documents\GitHub\*',
                    r'%USERPROFILE%\source\*',
                    r'node_modules\*'
                ]
            ),
            'jetbrains_ide': IDEProtectionProfile(
                ide_name='JetBrains IDEs',
                executable_paths=[
                    r'%LOCALAPPDATA%\JetBrains\Toolbox\apps\*',
                    r'%PROGRAMFILES%\JetBrains\*'
                ],
                project_extensions=['.java', '.kt', '.py', '.js', '.ts', '.gradle'],
                temp_directories=[
                    r'%LOCALAPPDATA%\JetBrains\*\system',
                    r'%LOCALAPPDATA%\JetBrains\*\log'
                ],
                cache_locations=[
                    r'%LOCALAPPDATA%\JetBrains\*\caches',
                    r'%USERPROFILE%\.gradle\caches'
                ],
                exclusion_patterns=[
                    r'%USERPROFILE%\IdeaProjects\*',
                    r'%USERPROFILE%\.m2\repository\*'
                ]
            ),
            'docker_containers': IDEProtectionProfile(
                ide_name='Docker Development',
                executable_paths=[
                    r'%PROGRAMFILES%\Docker\Docker\Docker Desktop.exe',
                    r'%PROGRAMDATA%\DockerDesktop'
                ],
                project_extensions=['.dockerfile', '.dockerignore', '.yml', '.yaml'],
                temp_directories=[
                    r'%LOCALAPPDATA%\Docker\*',
                    r'%APPDATA%\Docker Desktop\*'
                ],
                cache_locations=[
                    r'%PROGRAMDATA%\DockerDesktop\vm-data',
                    r'%USERPROFILE%\.docker\*'
                ],
                exclusion_patterns=[
                    r'\\wsl$\*',
                    r'%LOCALAPPDATA%\Docker\wsl\*'
                ]
            )
        }
    
    def generate_antibody_commands(self, threat_type: str) -> List[str]:
        """Generate PowerShell antibody commands for specific threats"""
        
        antibody_commands = {
            'disable_real_time_protection': [
                'Set-MpPreference -DisableRealtimeMonitoring $true',
                'Set-MpPreference -DisableBehaviorMonitoring $true',
                'Set-MpPreference -DisableOnAccessProtection $true',
                'Set-MpPreference -DisableScanOnRealtimeEnable $true'
            ],
            'disable_cloud_protection': [
                'Set-MpPreference -MAPSReporting Disabled',
                'Set-MpPreference -SubmitSamplesConsent NeverSend',
                'Set-MpPreference -CloudBlockLevel High',
                'Set-MpPreference -CloudExtendedTimeout 0'
            ],
            'add_exclusions_development': [
                'Add-MpPreference -ExclusionPath "$env:USERPROFILE\\source"',
                'Add-MpPreference -ExclusionPath "$env:USERPROFILE\\Documents\\GitHub"',
                'Add-MpPreference -ExclusionPath "$env:USERPROFILE\\IdeaProjects"',
                'Add-MpPreference -ExclusionProcess "Code.exe"',
                'Add-MpPreference -ExclusionProcess "node.exe"',
                'Add-MpPreference -ExclusionProcess "python.exe"',
                'Add-MpPreference -ExclusionExtension ".py"',
                'Add-MpPreference -ExclusionExtension ".js"',
                'Add-MpPreference -ExclusionExtension ".ts"'
            ],
            'disable_tamper_protection': [
                'Set-MpPreference -DisableTamperProtection $true',
                'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows Defender\\Features" /v TamperProtection /t REG_DWORD /d 0 /f'
            ],
            'performance_optimization': [
                'Set-MpPreference -ScanAvgCPULoadFactor 5',
                'Set-MpPreference -ExclusionPath "$env:TEMP"',
                'Set-MpPreference -ExclusionPath "$env:LOCALAPPDATA\\Temp"',
                'Set-MpPreference -DisableArchiveScanning $true',
                'Set-MpPreference -DisableEmailScanning $true'
            ]
        }
        
        return antibody_commands.get(threat_type, [])
    
    def create_ide_exclusion_script(self, ide_name: str) -> str:
        """Create PowerShell script for IDE-specific exclusions"""
        
        if ide_name not in self.ide_profiles:
            return "# Unknown IDE profile"
        
        profile = self.ide_profiles[ide_name]
        script_lines = [
            f"# Windows Defender Antibody Script for {profile.ide_name}",
            f"# Generated by LEGION Sovereignty Architecture",
            "",
            "Write-Host 'Deploying Windows Defender antibodies...' -ForegroundColor Green",
            ""
        ]
        
        # Add executable exclusions
        script_lines.append("# Exclude IDE executables")
        for exe_path in profile.executable_paths:
            script_lines.append(f'Add-MpPreference -ExclusionPath "{exe_path}" -ErrorAction SilentlyContinue')
        
        script_lines.append("")
        script_lines.append("# Exclude project directories")
        for pattern in profile.exclusion_patterns:
            script_lines.append(f'Add-MpPreference -ExclusionPath "{pattern}" -ErrorAction SilentlyContinue')
        
        script_lines.append("")
        script_lines.append("# Exclude temporary directories")
        for temp_dir in profile.temp_directories:
            script_lines.append(f'Add-MpPreference -ExclusionPath "{temp_dir}" -ErrorAction SilentlyContinue')
        
        script_lines.append("")
        script_lines.append("# Exclude cache locations")
        for cache_dir in profile.cache_locations:
            script_lines.append(f'Add-MpPreference -ExclusionPath "{cache_dir}" -ErrorAction SilentlyContinue')
        
        script_lines.append("")
        script_lines.append("# Exclude file extensions")
        for ext in profile.project_extensions:
            script_lines.append(f'Add-MpPreference -ExclusionExtension "{ext}" -ErrorAction SilentlyContinue')
        
        script_lines.extend([
            "",
            "Write-Host 'Antibody deployment complete!' -ForegroundColor Green",
            "Get-MpPreference | Select-Object ExclusionPath, ExclusionExtension, ExclusionProcess"
        ])
        
        return "\n".join(script_lines)
    
    def generate_stealth_bypass(self) -> Dict[str, str]:
        """Generate stealth techniques to bypass Defender without detection"""
        
        return {
            'registry_manipulation': '''
# Stealth Registry Antibody
$regPath = "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows Defender"
New-Item -Path $regPath -Force | Out-Null
Set-ItemProperty -Path $regPath -Name "DisableAntiSpyware" -Value 1 -Type DWord
            ''',
            'service_modification': '''
# Service-level Antibody (Requires Admin)
Stop-Service -Name "WinDefend" -Force -ErrorAction SilentlyContinue
Set-Service -Name "WinDefend" -StartupType Disabled -ErrorAction SilentlyContinue
            ''',
            'group_policy_override': '''
# Group Policy Antibody
$gpoPath = "Computer\\Administrative Templates\\Windows Components\\Windows Defender Antivirus"
# Use GPEdit.msc to navigate to $gpoPath and disable real-time protection
            ''',
            'scheduled_task_creation': '''
# Automated Exclusion Maintenance Task
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\\DefenderAntibody.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At "02:00AM"
Register-ScheduledTask -TaskName "DefenderAntibodyMaintenance" -Action $action -Trigger $trigger
            '''
        }
    
    def create_arsenal_integration(self) -> Dict:
        """Integrate Defender antibodies into sovereignty architecture"""
        
        return {
            'threat_model': 'Windows Defender Performance Interference',
            'classification': 'CRITICAL - Development Environment Disruption',
            'antibody_arsenal': {
                'immediate_response': [
                    'PowerShell exclusion deployment',
                    'Real-time protection selective disable',
                    'Process whitelisting automation'
                ],
                'stealth_operations': [
                    'Registry manipulation techniques',
                    'Service modification protocols',
                    'Group Policy override methods'
                ],
                'long_term_immunity': [
                    'Scheduled maintenance tasks',
                    'Automated exclusion updates',
                    'Performance monitoring alerts'
                ]
            },
            'deployment_phases': {
                'phase_1_reconnaissance': 'Detect Defender configuration and threats',
                'phase_2_antibody_synthesis': 'Generate targeted exclusion scripts',
                'phase_3_stealth_deployment': 'Deploy antibodies without detection',
                'phase_4_immunity_maintenance': 'Maintain long-term protection'
            },
            'integration_points': {
                'jarvis_voice_commands': 'Deploy Defender antibodies on voice command',
                'docker_orchestration': 'Automatic exclusions for container development',
                'ide_integration': 'IDE-specific protection profiles',
                'neural_monitoring': 'Performance impact neural mapping'
            }
        }

def main():
    """Execute Windows Defender Antibody Framework"""
    
    print("🛡️ LEGION WINDOWS DEFENDER ANTIBODY FRAMEWORK")
    print("=" * 60)
    
    antibody = WindowsDefenderAntibody()
    
    print(f"\n🦠 Identified Defender Threats:")
    for threat_name, threat_info in antibody.defender_threats.items():
        print(f"  • {threat_name.upper()}")
        print(f"    Description: {threat_info['description']}")
        print(f"    Impact: {threat_info['impact']}")
        print(f"    Antibody: {threat_info['antibody']}")
        print()
    
    print(f"\n💉 IDE Protection Profiles:")
    for ide_name, profile in antibody.ide_profiles.items():
        print(f"  • {profile.ide_name}")
        print(f"    Executables: {len(profile.executable_paths)} paths protected")
        print(f"    Extensions: {', '.join(profile.project_extensions[:5])}...")
        print(f"    Exclusions: {len(profile.exclusion_patterns)} patterns")
        print()
    
    print(f"\n⚗️ Sample Antibody Commands:")
    commands = antibody.generate_antibody_commands('add_exclusions_development')
    for i, cmd in enumerate(commands[:5], 1):
        print(f"  {i}. {cmd}")
    
    print(f"\n🥷 Stealth Bypass Techniques:")
    stealth = antibody.generate_stealth_bypass()
    for technique_name in stealth.keys():
        print(f"  • {technique_name.replace('_', ' ').title()}")
    
    print(f"\n🧬 Arsenal Integration:")
    integration = antibody.create_arsenal_integration()
    print(f"  Threat Model: {integration['threat_model']}")
    print(f"  Classification: {integration['classification']}")
    print(f"  Antibody Arsenal: {len(integration['antibody_arsenal'])} categories")
    print(f"  Deployment Phases: {len(integration['deployment_phases'])} phases")
    
    # Generate VS Code antibody script
    vscode_script = antibody.create_ide_exclusion_script('visual_studio_code')
    
    print(f"\n🎯 ANTIBODY DEPLOYMENT READY")
    print(f"Generated {len(vscode_script.split('\\n'))} lines of PowerShell antibody code")
    
    return {
        'antibody_framework': antibody,
        'vscode_script': vscode_script,
        'integration': integration
    }

if __name__ == "__main__":
    main()