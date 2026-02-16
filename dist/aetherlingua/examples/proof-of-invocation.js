/**
 * Example: Proof of Invocation
 *
 * Demonstrates cryptographic hash generation and VFASP seed creation
 */
import { AetherLingua, AudioSynthesizer } from '../';
async function main() {
    console.log('🔥 AetherLingua - Proof of Invocation');
    console.log('═══════════════════════════════════════\n');
    const engine = new AetherLingua({
        sampleRate: 48000,
        bitDepth: 24,
        duration: 8.0,
        seed: 1337
    });
    // Render a line with special motifs
    const line = 'ḥsb 7% dỉ ỉb nfr ḥr‑wꜥt ʿnḫ';
    console.log(`Text: ${line}`);
    console.log(`  ↳ Contains 7% charity motif\n`);
    const carrier = AudioSynthesizer.getLineCarrier(0);
    const buffer = AudioSynthesizer.renderLine(line, carrier, {
        sampleRate: 48000,
        bitDepth: 24,
        duration: 8.0,
        seed: 1337
    });
    // Generate cryptographic hash
    console.log('Generating cryptographic hash...');
    const hash = await engine.getAudioHash(buffer);
    console.log(`  SHA-256: ${hash}\n`);
    // Generate VFASP seed
    console.log('Generating VFASP speculation seed...');
    const seed = engine.generateVFASPSeed(hash);
    console.log(`  Seed: ${seed}\n`);
    console.log('✓ Proof of invocation generated');
    console.log('\nThis hash is:');
    console.log('  • Immutable — cannot be changed');
    console.log('  • Beautiful — deterministic from ancient text');
    console.log('  • On-chain verifiable — can be stored in treasury');
    console.log('\nThe rendered sound becomes proof.');
    console.log('Intent becomes executable sovereignty. 🔥\n');
}
main().catch(console.error);
