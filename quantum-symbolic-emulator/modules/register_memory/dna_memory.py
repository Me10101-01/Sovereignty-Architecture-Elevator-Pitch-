"""
Register Memory - DNA Transcription & NFT Provenance
Implements memory system based on DNA encoding with blockchain-style provenance

Combines biological-inspired memory with cryptographic verification.
"""

import hashlib
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class MemoryCell:
    """Individual memory cell with DNA encoding"""
    address: int
    data: str
    dna_sequence: str
    timestamp: float
    provenance_hash: str
    parent_hash: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class DNAMemory:
    """
    Memory system using DNA transcription for storage
    Each memory cell is encoded as DNA and verified with NFT-style hashing
    """
    
    # DNA codon table for transcription
    DNA_CODONS = {
        '0': 'ATG', '1': 'TGA', '2': 'GCT', '3': 'TAG',
        '4': 'CAT', '5': 'ACG', '6': 'GTA', '7': 'CGA',
        '8': 'TAC', '9': 'CGT', 'A': 'GAT', 'B': 'TCA',
        'C': 'GCA', 'D': 'ATC', 'E': 'CTG', 'F': 'AGC',
        ' ': 'AAA', '.': 'TTT', ',': 'GGG', '!': 'CCC'
    }
    
    def __init__(self, capacity: int = 256):
        """
        Initialize DNA memory system
        
        Args:
            capacity: Number of memory cells
        """
        self.capacity = capacity
        self.memory: Dict[int, MemoryCell] = {}
        self.provenance_chain: List[str] = []
        self.genesis_hash = self._create_genesis_hash()
        
    def _create_genesis_hash(self) -> str:
        """Create genesis hash for provenance chain"""
        genesis_data = {
            'type': 'genesis',
            'timestamp': time.time(),
            'capacity': self.capacity
        }
        return hashlib.sha256(json.dumps(genesis_data).encode()).hexdigest()
    
    def _encode_to_dna(self, data: str) -> str:
        """
        Encode data to DNA sequence
        
        Args:
            data: Data string to encode
            
        Returns:
            DNA sequence
        """
        dna_sequence = []
        for char in data.upper():
            if char in self.DNA_CODONS:
                dna_sequence.append(self.DNA_CODONS[char])
            else:
                # Use ASCII value for unmapped characters
                ascii_val = ord(char)
                codon = f"X{ascii_val:02X}"
                dna_sequence.append(codon)
        return ''.join(dna_sequence)
    
    def _decode_from_dna(self, dna_sequence: str) -> str:
        """
        Decode DNA sequence back to data
        
        Args:
            dna_sequence: DNA sequence
            
        Returns:
            Decoded data string
        """
        # Create reverse mapping
        reverse_codons = {v: k for k, v in self.DNA_CODONS.items()}
        
        decoded = []
        i = 0
        while i < len(dna_sequence):
            codon = dna_sequence[i:i+3]
            if codon in reverse_codons:
                decoded.append(reverse_codons[codon])
                i += 3
            elif codon.startswith('X'):
                # Custom encoded character
                ascii_val = int(dna_sequence[i+1:i+4], 16)
                decoded.append(chr(ascii_val))
                i += 4
            else:
                i += 1
        
        return ''.join(decoded)
    
    def _compute_provenance_hash(self, address: int, dna_sequence: str, 
                                  parent_hash: Optional[str] = None) -> str:
        """
        Compute NFT-style provenance hash
        
        Args:
            address: Memory address
            dna_sequence: DNA encoded data
            parent_hash: Hash of parent cell (for chain)
            
        Returns:
            Blake2b provenance hash
        """
        provenance_data = {
            'address': address,
            'dna_sequence': dna_sequence,
            'timestamp': time.time(),
            'parent_hash': parent_hash or self.genesis_hash
        }
        data_bytes = json.dumps(provenance_data, sort_keys=True).encode()
        return hashlib.blake2b(data_bytes).hexdigest()
    
    def write(self, address: int, data: str) -> bool:
        """
        Write data to memory with DNA encoding
        
        Args:
            address: Memory address (0 to capacity-1)
            data: Data to write
            
        Returns:
            True if write successful
        """
        if address < 0 or address >= self.capacity:
            return False
        
        # Get parent hash if cell exists
        parent_hash = None
        if address in self.memory:
            parent_hash = self.memory[address].provenance_hash
        
        # Encode to DNA
        dna_sequence = self._encode_to_dna(data)
        
        # Compute provenance hash
        provenance_hash = self._compute_provenance_hash(address, dna_sequence, parent_hash)
        
        # Create memory cell
        cell = MemoryCell(
            address=address,
            data=data,
            dna_sequence=dna_sequence,
            timestamp=time.time(),
            provenance_hash=provenance_hash,
            parent_hash=parent_hash
        )
        
        # Store cell
        self.memory[address] = cell
        self.provenance_chain.append(provenance_hash)
        
        return True
    
    def read(self, address: int) -> Optional[str]:
        """
        Read data from memory
        
        Args:
            address: Memory address
            
        Returns:
            Data string or None if not found
        """
        if address not in self.memory:
            return None
        
        return self.memory[address].data
    
    def read_dna(self, address: int) -> Optional[str]:
        """
        Read DNA sequence from memory
        
        Args:
            address: Memory address
            
        Returns:
            DNA sequence or None if not found
        """
        if address not in self.memory:
            return None
        
        return self.memory[address].dna_sequence
    
    def verify_provenance(self, address: int) -> bool:
        """
        Verify provenance hash of memory cell
        
        Args:
            address: Memory address
            
        Returns:
            True if provenance is valid
        """
        if address not in self.memory:
            return False
        
        cell = self.memory[address]
        
        # Recompute hash
        expected_hash = self._compute_provenance_hash(
            cell.address,
            cell.dna_sequence,
            cell.parent_hash
        )
        
        return expected_hash == cell.provenance_hash
    
    def get_provenance_chain(self, address: int) -> List[str]:
        """
        Get full provenance chain for memory cell
        
        Args:
            address: Memory address
            
        Returns:
            List of provenance hashes in chain
        """
        if address not in self.memory:
            return []
        
        chain = []
        current_hash = self.memory[address].provenance_hash
        
        while current_hash:
            chain.append(current_hash)
            
            # Find parent
            found = False
            for cell in self.memory.values():
                if cell.provenance_hash == current_hash:
                    current_hash = cell.parent_hash
                    found = True
                    break
            
            if not found or current_hash == self.genesis_hash:
                break
        
        return chain
    
    def export_cell(self, address: int) -> Optional[Dict[str, Any]]:
        """
        Export memory cell as dictionary
        
        Args:
            address: Memory address
            
        Returns:
            Cell data dictionary or None
        """
        if address not in self.memory:
            return None
        
        return self.memory[address].to_dict()
    
    def get_memory_usage(self) -> float:
        """
        Get memory usage percentage
        
        Returns:
            Percentage of capacity used
        """
        return (len(self.memory) / self.capacity) * 100
    
    def clear(self) -> None:
        """Clear all memory (except genesis)"""
        self.memory.clear()
        self.provenance_chain = [self.genesis_hash]


def main():
    """Demonstration of DNA Memory"""
    print("="*60)
    print("Register Memory - DNA Transcription & NFT Provenance")
    print("="*60)
    print()
    
    # Initialize memory
    memory = DNAMemory(capacity=256)
    
    print(f"Genesis Hash: {memory.genesis_hash[:32]}...")
    print()
    
    # Write data
    print("Writing data to memory:")
    data_samples = [
        (0, "HELLO"),
        (1, "WORLD"),
        (2, "DNA123"),
        (3, "SAGCO")
    ]
    
    for address, data in data_samples:
        success = memory.write(address, data)
        print(f"  Address {address}: {data} -> {'OK' if success else 'FAIL'}")
    print()
    
    # Read and display
    print("Reading memory cells:")
    for address, _ in data_samples:
        data = memory.read(address)
        dna = memory.read_dna(address)
        print(f"  Address {address}:")
        print(f"    Data: {data}")
        print(f"    DNA:  {dna}")
        print(f"    Hash: {memory.memory[address].provenance_hash[:32]}...")
    print()
    
    # Verify provenance
    print("Verifying provenance:")
    for address, _ in data_samples:
        valid = memory.verify_provenance(address)
        print(f"  Address {address}: {'✓ VALID' if valid else '✗ INVALID'}")
    print()
    
    # Update a cell
    print("Updating cell at address 0:")
    memory.write(0, "HELLO2")
    chain = memory.get_provenance_chain(0)
    print(f"  Provenance chain length: {len(chain)}")
    print(f"  Current hash: {chain[0][:32]}...")
    print(f"  Parent hash:  {chain[1][:32]}..." if len(chain) > 1 else "  (no parent)")
    print()
    
    # Memory usage
    print(f"Memory Usage: {memory.get_memory_usage():.2f}%")
    print()
    
    print("="*60)


if __name__ == "__main__":
    main()
