#!/usr/bin/env python3
"""
StrategicKhaos Sovereignty Assessment Validator
Version: 1.0.0
Purpose: Validate assessment submission format and completeness

Usage:
    python validate_assessment.py submission.yaml
"""

import sys
import os
import yaml
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple

class AssessmentValidator:
    """Validates sovereignty assessment submissions"""
    
    REQUIRED_FIELDS = [
        'assessment_submission.candidate_id',
        'assessment_submission.submission_date',
        'assessment_submission.sections',
        'assessment_submission.verification.gpg_key_id',
        'assessment_submission.verification.signature_declaration',
    ]
    
    EXPECTED_SECTIONS = ['A', 'B', 'C', 'D', 'E', 'F', 'META']
    EXPECTED_QUESTIONS = {
        'A': [1, 2, 3, 4, 5, 6],
        'B': [7, 8, 9, 10, 11, 12],
        'C': [13, 14, 15, 16, 17, 18],
        'D': [19, 20, 21, 22, 23, 24],
        'E': [25, 26, 27, 28, 29, 30],
        'F': [31, 32, 33, 34, 35, 36],
        'META': [37]
    }
    
    def __init__(self, submission_path: str):
        self.submission_path = Path(submission_path)
        self.errors = []
        self.warnings = []
        self.data = None
        
    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """Run all validation checks"""
        
        # Check file exists
        if not self.submission_path.exists():
            self.errors.append(f"Submission file not found: {self.submission_path}")
            return False, self.errors, self.warnings
        
        # Load YAML
        if not self._load_yaml():
            return False, self.errors, self.warnings
        
        # Run validation checks
        self._validate_required_fields()
        self._validate_sections()
        self._validate_files()
        self._validate_verification()
        
        # Return results
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def _load_yaml(self) -> bool:
        """Load and parse YAML file"""
        try:
            with open(self.submission_path, 'r') as f:
                self.data = yaml.safe_load(f)
            return True
        except yaml.YAMLError as e:
            self.errors.append(f"Invalid YAML syntax: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return False
    
    def _validate_required_fields(self):
        """Check all required fields are present"""
        for field_path in self.REQUIRED_FIELDS:
            if not self._get_nested_field(field_path):
                self.errors.append(f"Missing required field: {field_path}")
    
    def _validate_sections(self):
        """Validate section structure and completeness"""
        sections = self._get_nested_field('assessment_submission.sections')
        if not sections:
            self.errors.append("No sections found in submission")
            return
        
        submitted_sections = set()
        for section in sections:
            section_id = section.get('section')
            if not section_id:
                self.errors.append("Section missing 'section' field")
                continue
            
            submitted_sections.add(section_id)
            
            # Check questions
            questions = section.get('questions', [])
            expected = self.EXPECTED_QUESTIONS.get(section_id, [])
            
            if set(questions) != set(expected):
                self.errors.append(
                    f"Section {section_id}: Expected questions {expected}, "
                    f"got {questions}"
                )
            
            # Check files
            files = section.get('files', [])
            if len(files) != len(expected):
                self.warnings.append(
                    f"Section {section_id}: Expected {len(expected)} files, "
                    f"got {len(files)}"
                )
        
        # Check all sections present
        missing = set(self.EXPECTED_SECTIONS) - submitted_sections
        if missing:
            self.errors.append(f"Missing sections: {sorted(missing)}")
    
    def _validate_files(self):
        """Check that referenced files exist"""
        sections = self._get_nested_field('assessment_submission.sections')
        if not sections:
            return
        
        base_dir = self.submission_path.parent
        
        for section in sections:
            files = section.get('files', [])
            for file_path in files:
                full_path = base_dir / file_path
                if not full_path.exists():
                    self.errors.append(f"Referenced file not found: {file_path}")
    
    def _validate_verification(self):
        """Validate verification fields"""
        verification = self._get_nested_field('assessment_submission.verification')
        if not verification:
            return
        
        # Check GPG signature file
        sig_file = verification.get('signature_file')
        if sig_file:
            sig_path = self.submission_path.parent / sig_file
            if not sig_path.exists():
                self.errors.append(f"GPG signature file not found: {sig_file}")
        else:
            self.warnings.append("No GPG signature file specified")
        
        # Check timestamp file
        ts_file = verification.get('timestamp_file')
        if ts_file:
            ts_path = self.submission_path.parent / ts_file
            if not ts_path.exists():
                self.errors.append(f"Timestamp file not found: {ts_file}")
        else:
            self.warnings.append("No OpenTimestamps file specified")
        
        # Check declaration
        declaration = verification.get('signature_declaration')
        if declaration != "I agree to the above declaration":
            self.errors.append("Invalid signature declaration")
    
    def _get_nested_field(self, field_path: str):
        """Get a nested field from the data dict using dot notation"""
        parts = field_path.split('.')
        current = self.data
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current


def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: python validate_assessment.py submission.yaml")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    
    print("=" * 70)
    print("StrategicKhaos Sovereignty Assessment Validator")
    print("=" * 70)
    print(f"\nValidating: {submission_file}\n")
    
    validator = AssessmentValidator(submission_file)
    is_valid, errors, warnings = validator.validate()
    
    # Print warnings
    if warnings:
        print("⚠️  WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")
        print()
    
    # Print errors
    if errors:
        print("❌ ERRORS:")
        for error in errors:
            print(f"  - {error}")
        print()
    
    # Print result
    if is_valid:
        print("✅ Validation PASSED")
        print("\nNext steps:")
        print("  1. Sign with GPG: gpg --clearsign submission.yaml")
        print("  2. Create timestamp: ots stamp submission.yaml")
        print("  3. Verify signature: gpg --verify submission.yaml.asc")
        print("  4. Submit to: assessment@strategickhaos.ai")
        sys.exit(0)
    else:
        print("❌ Validation FAILED")
        print("\nPlease fix the errors above and try again.")
        sys.exit(1)


if __name__ == '__main__':
    main()
