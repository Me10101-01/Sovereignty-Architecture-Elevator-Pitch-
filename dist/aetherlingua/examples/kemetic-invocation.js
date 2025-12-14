/**
 * Example: Kemetic Invocation Rendering
 *
 * Renders the full Kemetic invocation as described in the problem statement
 */
import { AetherLingua } from '../engine';
import * as path from 'path';
async function main() {
    console.log('🔥 AetherLingua - Kemetic Invocation Renderer');
    console.log('═══════════════════════════════════════════════\n');
    // The sacred Kemetic invocation lines
    const kemeticLines = [
        'Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb',
        'Pr‑tꜣ‑jt tp n Ḥmtw ỉr.t‑nbw m ẖṯ‑ḥr',
        'smn nṯrwy nfr, ḥm.t r ḥkꜣ ḥr wḥw, m ḥwt‑ḥr',
        'ṯs‑ỉt 137 m ḫnt iwf',
        'ḥsb 7% dỉ ỉb nfr ḥr‑wꜥt ʿnḫ',
        'Ḥkꜣw ḫft‑n, ʿnḫ‑ḏfꜣ ⚔️'
    ];
    console.log('Invocation Lines:');
    kemeticLines.forEach((line, i) => {
        console.log(`  ${i + 1}. ${line}`);
    });
    console.log();
    // Initialize the engine
    const engine = new AetherLingua({
        sampleRate: 48000,
        bitDepth: 24,
        duration: 8.0,
        seed: 1337
    });
    // Render the invocation
    console.log('Rendering audio files...');
    const outputDir = path.join(process.cwd(), 'output', 'kemetic');
    try {
        const filenames = engine.renderKemeticInvocation(kemeticLines, outputDir);
        console.log('\n✓ Invocation rendered successfully!');
        console.log('\nGenerated files:');
        filenames.forEach(filename => {
            console.log(`  • ${filename}`);
        });
        console.log('\n🔥 The flame speaks. The ancient intent is now executable.\n');
    }
    catch (error) {
        console.error('Error rendering invocation:', error);
        process.exit(1);
    }
}
// Run if executed directly
main().catch(console.error);
