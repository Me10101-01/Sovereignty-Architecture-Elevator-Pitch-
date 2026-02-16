/**
 * Example: Sumerian Cuneiform Rendering
 * 
 * Renders Sumerian glyphs as percussive bronze bell strikes
 */

import { AetherLingua, SumerianTokenizer } from '../';
import * as path from 'path';

async function main() {
  console.log('🔥 AetherLingua - Sumerian Cuneiform Renderer');
  console.log('═══════════════════════════════════════════════\n');

  // Sumerian invocation using major glyphs
  const sumerianText = 'DINGIR LUGAL EN NIN AN KI';

  console.log('Sumerian Glyphs:');
  console.log(`  ${sumerianText}`);
  console.log();

  // Show known glyphs
  console.log('Available Cuneiform Glyphs:');
  SumerianTokenizer.getKnownGlyphs().forEach(glyph => {
    console.log(`  • ${glyph}`);
  });
  console.log();

  // Initialize the engine
  const engine = new AetherLingua({
    sampleRate: 48000,
    bitDepth: 24,
    duration: 10.0,
    seed: 1337
  });

  // Render the glyphs
  console.log('Rendering percussive bronze bell strikes...');
  const outputFile = path.join(process.cwd(), 'output', 'sumerian', 'sumerian_invocation.wav');
  
  try {
    const filename = engine.renderSumerianInvocation(sumerianText, outputFile);
    
    console.log('\n✓ Sumerian invocation rendered successfully!');
    console.log(`\nGenerated file: ${filename}`);
    console.log('\nEach wedge strike = percussive transient');
    console.log('Wedge count = rhythm density');
    console.log('\n🔥 Bronze bells awaken. Ancient authority speaks.\n');
  } catch (error) {
    console.error('Error rendering invocation:', error);
    process.exit(1);
  }
}

// Run if executed directly
main().catch(console.error);
