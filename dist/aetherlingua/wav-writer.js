/**
 * WAV file writer (24-bit stereo)
 */
import * as fs from 'fs';
export class WavWriter {
    /**
     * Write stereo buffer to 24-bit WAV file
     * Note: Ensure output directory exists before calling this method
     */
    static write(filename, buffer, sampleRate) {
        const numSamples = buffer.left.length;
        const numChannels = 2;
        const bytesPerSample = 3; // 24-bit
        const dataSize = numSamples * numChannels * bytesPerSample;
        const headerSize = 44;
        const fileSize = headerSize + dataSize;
        // Create buffer for entire file
        const wavBuffer = Buffer.alloc(fileSize);
        // Write RIFF header
        wavBuffer.write('RIFF', 0);
        wavBuffer.writeUInt32LE(fileSize - 8, 4);
        wavBuffer.write('WAVE', 8);
        // Write fmt chunk
        wavBuffer.write('fmt ', 12);
        wavBuffer.writeUInt32LE(16, 16); // fmt chunk size
        wavBuffer.writeUInt16LE(1, 20); // PCM format
        wavBuffer.writeUInt16LE(numChannels, 22);
        wavBuffer.writeUInt32LE(sampleRate, 24);
        wavBuffer.writeUInt32LE(sampleRate * numChannels * bytesPerSample, 28); // byte rate
        wavBuffer.writeUInt16LE(numChannels * bytesPerSample, 32); // block align
        wavBuffer.writeUInt16LE(bytesPerSample * 8, 34); // bits per sample
        // Write data chunk
        wavBuffer.write('data', 36);
        wavBuffer.writeUInt32LE(dataSize, 40);
        // Write interleaved audio data (24-bit)
        let offset = 44;
        for (let i = 0; i < numSamples; i++) {
            // Left channel
            const leftSample = this.clamp(buffer.left[i], -1.0, 1.0);
            const leftInt = Math.floor(leftSample * 8388607); // 2^23 - 1
            wavBuffer.writeIntLE(leftInt, offset, 3);
            offset += 3;
            // Right channel
            const rightSample = this.clamp(buffer.right[i], -1.0, 1.0);
            const rightInt = Math.floor(rightSample * 8388607);
            wavBuffer.writeIntLE(rightInt, offset, 3);
            offset += 3;
        }
        // Write to file
        fs.writeFileSync(filename, wavBuffer);
    }
    /**
     * Clamp value between min and max
     */
    static clamp(value, min, max) {
        return Math.max(min, Math.min(max, value));
    }
    /**
     * Write multiple buffers as separate files
     */
    static writeMultiple(baseFilename, buffers, sampleRate) {
        const filenames = [];
        for (let i = 0; i < buffers.length; i++) {
            let filename;
            if (baseFilename.endsWith('.wav')) {
                filename = baseFilename.replace('.wav', `_${i + 1}.wav`);
            }
            else {
                filename = `${baseFilename}_${i + 1}.wav`;
            }
            this.write(filename, buffers[i], sampleRate);
            filenames.push(filename);
        }
        return filenames;
    }
}
