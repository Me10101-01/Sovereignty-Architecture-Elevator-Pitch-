/**
 * Example: War Room Synthesizer Integration
 * Demonstrates how to integrate the War Room Synthesizer into your application
 */

import { WarRoomSynthesizer, type OverrideProtocolConfig } from '../src/war-room-synthesizer';

/**
 * Example 1: Basic execution with default configuration
 */
async function basicExecution() {
  console.log('Example 1: Basic Execution\n');

  const config: OverrideProtocolConfig = {
    overrideCode: 'DOM_010101',
    scope: ['strategic-khaos'],
    nodeCount: 895,
    distributionTargets: ['cluster-primary']
  };

  const warRoom = new WarRoomSynthesizer(config);

  const overridePhrase = `
    EXECUTIVE AUTONOMOUS OVERRIDE: DOM_010101 // NEUROSPIKE ASCENSION
    INITIATE WAR ROOM SYNTHESIZER — THREAT MODEL 2025
    RED TEAM: FULL OFFENSIVE SIMULATION
    PURPLE TEAM: REAL-TIME COLLABORATIVE HARDENING
    BLUE TEAM: DEFEND THE SWARM AT ALL COSTS
  `;

  await warRoom.executeOverride(overridePhrase);

  const status = warRoom.getStatus();
  console.log('\nStatus:', status);
}

/**
 * Example 2: Custom scope with multiple repositories
 */
async function multiRepoExecution() {
  console.log('\nExample 2: Multi-Repository Execution\n');

  const config: OverrideProtocolConfig = {
    overrideCode: 'DOM_010101',
    scope: [
      'strategic-khaos',
      'sovereignty-architecture',
      'valoryield-engine',
      'quantum-symbolic-emulator'
    ],
    nodeCount: 1200, // Expanded node count
    distributionTargets: [
      'cluster-primary',
      'cluster-staging',
      'cluster-production-east',
      'cluster-production-west'
    ]
  };

  const warRoom = new WarRoomSynthesizer(config);

  const overridePhrase = `
    EXECUTIVE AUTONOMOUS OVERRIDE: DOM_010101 // NEUROSPIKE ASCENSION
    INITIATE WAR ROOM SYNTHESIZER — THREAT MODEL 2025
  `;

  await warRoom.executeOverride(overridePhrase);
}

/**
 * Example 3: Status monitoring and reporting
 */
async function statusMonitoring() {
  console.log('\nExample 3: Status Monitoring\n');

  const config: OverrideProtocolConfig = {
    overrideCode: 'DOM_010101',
    scope: ['strategic-khaos'],
    nodeCount: 895,
    distributionTargets: ['cluster-dev']
  };

  const warRoom = new WarRoomSynthesizer(config);

  const overridePhrase = `
    EXECUTIVE AUTONOMOUS OVERRIDE: DOM_010101 // NEUROSPIKE ASCENSION
    INITIATE WAR ROOM SYNTHESIZER — THREAT MODEL 2025
  `;

  await warRoom.executeOverride(overridePhrase);

  // Get detailed status
  const status = warRoom.getStatus();

  console.log('War Room Status Report:');
  console.log('─'.repeat(50));
  console.log(`Active: ${status.active}`);
  console.log('\nRed Team:');
  console.log(`  Findings: ${status.redTeam.findingsCount}`);
  console.log(`  Critical: ${status.redTeam.criticalFindings}`);
  console.log(`  High: ${status.redTeam.highFindings}`);
  console.log('\nBlue Team:');
  console.log(`  Active Defenses: ${status.blueTeam.activeDefenses}`);
  console.log(`  Total Defenses: ${status.blueTeam.totalDefenses}`);
  console.log(`  Effectiveness: ${status.blueTeam.averageEffectiveness.toFixed(1)}%`);
  console.log('\nPurple Team:');
  console.log(`  Total Analyses: ${status.purpleTeam.totalAnalyses}`);
  console.log(`  Mitigated: ${status.purpleTeam.mitigatedThreats}`);
  console.log(`  Hotfixes Deployed: ${status.purpleTeam.hotfixesDeployed}`);
  console.log('\nVault:');
  console.log(`  Generated: ${status.vaultGenerated ? '✅' : '❌'}`);
  console.log(`  Distributed: ${status.distributionComplete ? '✅' : '❌'}`);
}

/**
 * Example 4: Error handling and graceful shutdown
 */
async function errorHandling() {
  console.log('\nExample 4: Error Handling\n');

  const config: OverrideProtocolConfig = {
    overrideCode: 'DOM_010101',
    scope: ['strategic-khaos'],
    nodeCount: 895,
    distributionTargets: ['cluster-primary']
  };

  const warRoom = new WarRoomSynthesizer(config);

  try {
    // Try with invalid override phrase
    await warRoom.executeOverride('INVALID OVERRIDE PHRASE');
  } catch (error) {
    console.log('✅ Invalid override correctly rejected:', (error as Error).message);
  }

  // Now execute with valid phrase
  const validPhrase = `
    EXECUTIVE AUTONOMOUS OVERRIDE: DOM_010101 // NEUROSPIKE ASCENSION
    INITIATE WAR ROOM SYNTHESIZER — THREAT MODEL 2025
  `;

  try {
    await warRoom.executeOverride(validPhrase);
    console.log('✅ Valid override executed successfully');

    // Graceful shutdown
    await warRoom.shutdown();
    console.log('✅ System shutdown completed');
  } catch (error) {
    console.error('❌ Error during execution:', error);
    await warRoom.shutdown();
  }
}

/**
 * Run all examples
 */
async function runExamples() {
  console.log('═══════════════════════════════════════════════════════════════');
  console.log('  War Room Synthesizer - Integration Examples');
  console.log('═══════════════════════════════════════════════════════════════\n');

  // Run error handling example as demonstration
  await errorHandling();

  console.log('\n═══════════════════════════════════════════════════════════════');
  console.log('  Examples Complete');
  console.log('═══════════════════════════════════════════════════════════════');
}

// Execute examples
if (import.meta.url === `file://${process.argv[1]}`) {
  runExamples().catch(console.error);
}

export {
  basicExecution,
  multiRepoExecution,
  statusMonitoring,
  errorHandling
};
