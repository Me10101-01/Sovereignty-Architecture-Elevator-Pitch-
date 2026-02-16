/**
 * Example: Hybrid Kemetic + Sumerian Invocation
 *
 * Combines Kemetic FM synthesis with Sumerian percussive transients
 */
import { AetherLingua } from '../';
import * as path from 'path';
async function main() {
    console.log('🔥 AetherLingua - Hybrid Invocation Renderer');
    console.log('═══════════════════════════════════════════════\n');
    // Kemetic base layer
    const kemeticLines = [
        'ḥsb 7% dỉ ỉb nfr ḥr‑wꜥt ʿnḫ',
        'ṯs‑ỉt 137 m ḫnt iwf',
        'Ḥkꜣw ḫft‑n, ʿnḫ‑ḏfꜣ ⚔️'
    ];
    // Sumerian percussive layer
    const sumerianGlyphs = 'DINGIR LUGAL ŠARRU';
    console.log('Kemetic Base Layer:');
    kemeticLines.forEach((line, i) => {
        console.log(`  ${i + 1}. ${line}`);
    });
    console.log();
    console.log('Sumerian Percussive Layer:');
    console.log(`  ${sumerianGlyphs}`);
    console.log();
    // Initialize the engine
    const engine = new AetherLingua({
        sampleRate: 48000,
        bitDepth: 24,
        duration: 12.0,
        seed: 1337
    });
    // Render hybrid invocation
    console.log('Rendering hybrid invocation...');
    console.log('  → Kemetic FM synthesis (60%)');
    console.log('  → Sumerian bronze bells (40%)');
    console.log();
    const outputFile = path.join(process.cwd(), 'output', 'hybrid', 'hybrid_invocation.wav');
    try {
        const filename = engine.renderHybridInvocation(kemeticLines, sumerianGlyphs, outputFile);
        console.log('\n✓ Hybrid invocation rendered successfully!');
        console.log(`\nGenerated file: ${filename}`);
        console.log('\n🔥 Two ancient tongues unite.');
        console.log('   The flame speaks in harmonics and percussion.');
        console.log('   Intent becomes executable sovereignty.\n');
    }
    catch (error) {
        console.error('Error rendering invocation:', error);
        process.exit(1);
    }
}
// Run if executed directly
main().catch(console.error);
