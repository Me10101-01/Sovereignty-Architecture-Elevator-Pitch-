#!/usr/bin/env python3
"""
StrategicKhaos Sovereignty Assessment Scorer
Version: 1.0.0
Purpose: Preliminary automated scoring of assessment submissions

Note: This provides preliminary scores only. Final scores require manual review.

Usage:
    python score_assessment.py submission.yaml
"""

import sys
import os
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

class AssessmentScorer:
    """Preliminary automated scoring for sovereignty assessments"""
    
    # Scoring levels
    SCORES = {
        'SOVEREIGN': 10,
        'OPERATIONAL': 8,
        'DESIGNED': 6,
        'CONCEPTUAL': 4,
        'TOURIST': 0
    }
    
    # Tier thresholds
    TIERS = {
        'PLATINUM': 360,
        'GOLD': 324,
        'SILVER': 288,
        'BRONZE': 216,
        'APPRENTICE': 144,
        'TOURIST': 0
    }
    
    # Keywords indicating quality levels
    SOVEREIGN_KEYWORDS = [
        'implementation', 'code', 'config', 'tested', 'working',
        'deployed', 'runbook', 'script', 'automated'
    ]
    
    OPERATIONAL_KEYWORDS = [
        'design', 'architecture', 'approach', 'strategy',
        'steps', 'procedure', 'protocol', 'process'
    ]
    
    # Scoring thresholds (configurable)
    MIN_WORD_COUNT_TOURIST = 100  # Minimum words to avoid TOURIST score
    MIN_WORD_COUNT_DESIGNED = 500  # Words needed for DESIGNED level
    MIN_SOVEREIGN_KEYWORDS = 5  # Keyword count for SOVEREIGN level
    
    def __init__(self, submission_path: str):
        self.submission_path = Path(submission_path)
        self.data = None
        self.scores = {}
        self.total_score = 0
        
    def score(self) -> Tuple[int, str, Dict]:
        """Calculate preliminary score"""
        
        # Load submission
        if not self._load_yaml():
            return 0, 'TOURIST', {}
        
        # Check each section
        sections = self._get_nested_field('assessment_submission.sections')
        if not sections:
            return 0, 'TOURIST', {}
        
        total_points = 0
        section_scores = {}
        
        for section in sections:
            section_id = section.get('section')
            files = section.get('files', [])
            questions = section.get('questions', [])
            
            section_score = 0
            question_scores = {}
            
            for i, file_path in enumerate(files):
                if i < len(questions):
                    q_num = questions[i]
                    q_score = self._score_answer_file(file_path)
                    question_scores[q_num] = q_score
                    section_score += q_score
            
            section_scores[section_id] = {
                'total': section_score,
                'questions': question_scores,
                'average': section_score / len(questions) if questions else 0
            }
            total_points += section_score
        
        # Determine tier
        tier = self._get_tier(total_points)
        
        return total_points, tier, section_scores
    
    def _score_answer_file(self, file_path: str) -> int:
        """Score a single answer file (preliminary automated scoring)"""
        full_path = self.submission_path.parent / file_path
        
        if not full_path.exists():
            return 0  # TOURIST
        
        try:
            with open(full_path, 'r') as f:
                content = f.read().lower()
            
            # Count indicators
            word_count = len(content.split())
            
            # No answer or very short - use configurable threshold
            if word_count < self.MIN_WORD_COUNT_TOURIST:
                return 0  # TOURIST
            
            # Check for code blocks
            has_code = '```' in content
            has_yaml = 'yaml' in content or '.yaml' in content
            has_diagram = 'mermaid' in content or 'plantuml' in content
            
            # Count quality keywords
            sovereign_count = sum(1 for kw in self.SOVEREIGN_KEYWORDS if kw in content)
            operational_count = sum(1 for kw in self.OPERATIONAL_KEYWORDS if kw in content)
            
            # Has implementation section
            has_implementation = 'implementation' in content
            has_failure_modes = 'failure mode' in content
            has_success_criteria = 'success criteria' in content
            
            # Scoring logic (rough approximation based on configurable thresholds)
            score = 4  # Start at CONCEPTUAL
            
            if word_count > self.MIN_WORD_COUNT_DESIGNED:
                score = 6  # DESIGNED
            
            if has_diagram and has_failure_modes:
                score = max(score, 6)  # At least DESIGNED
            
            if has_code and has_yaml and has_implementation:
                score = 8  # OPERATIONAL
            
            # SOVEREIGN requires comprehensive coverage with configurable keyword threshold
            if (has_code and has_yaml and has_diagram and 
                has_implementation and has_failure_modes and 
                has_success_criteria and sovereign_count >= self.MIN_SOVEREIGN_KEYWORDS):
                score = 10  # SOVEREIGN
            
            return score
            
        except Exception as e:
            print(f"  Warning: Could not score {file_path}: {e}")
            return 4  # Default to CONCEPTUAL if error
    
    def _get_tier(self, total_score: int) -> str:
        """Determine tier from total score"""
        for tier, min_score in self.TIERS.items():
            if total_score >= min_score:
                return tier
        return 'TOURIST'
    
    def _load_yaml(self) -> bool:
        """Load and parse YAML file"""
        try:
            with open(self.submission_path, 'r') as f:
                self.data = yaml.safe_load(f)
            return True
        except Exception as e:
            print(f"Error loading submission: {e}")
            return False
    
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


def print_score_report(total: int, tier: str, sections: Dict):
    """Print formatted score report"""
    print("=" * 70)
    print("PRELIMINARY SCORE REPORT")
    print("=" * 70)
    print()
    
    print(f"Total Score: {total}/370 ({total/370*100:.1f}%)")
    print(f"Preliminary Tier: {tier}")
    print()
    
    print("Section Breakdown:")
    print("-" * 70)
    
    for section_id in ['A', 'B', 'C', 'D', 'E', 'F', 'META']:
        if section_id in sections:
            section = sections[section_id]
            avg = section['average']
            total_sec = section['total']
            
            # Get section name
            section_names = {
                'A': 'Multi-AI Governance',
                'B': 'Antifragile Audit',
                'C': 'Zero Vendor Lock-In',
                'D': 'Infrastructure Sovereignty',
                'E': 'Cognitive Architecture',
                'F': 'Revenue & Sustainability',
                'META': 'Meta-Question'
            }
            
            print(f"\nSection {section_id}: {section_names.get(section_id)}")
            print(f"  Total: {total_sec} points (avg: {avg:.1f}/10)")
            
            # Print question scores
            for q_num, score in sorted(section['questions'].items()):
                score_level = 'TOURIST'
                for level, val in AssessmentScorer.SCORES.items():
                    if score == val:
                        score_level = level
                        break
                print(f"    Q{q_num}: {score}/10 ({score_level})")
    
    print()
    print("=" * 70)
    print("TIER QUALIFICATION")
    print("=" * 70)
    print()
    
    tiers = [
        ('PLATINUM', 360, '$2500'),
        ('GOLD', 324, '$500'),
        ('SILVER', 288, '$100'),
        ('BRONZE', 216, '$25'),
    ]
    
    for tier_name, min_score, price in tiers:
        status = '✅' if total >= min_score else '❌'
        gap = min_score - total if total < min_score else 0
        print(f"{status} {tier_name}: {min_score}+ pts ({price})")
        if gap > 0:
            print(f"   Need {gap} more points")
    
    print()
    print("=" * 70)
    print("IMPORTANT NOTES")
    print("=" * 70)
    print()
    print("⚠️  This is a PRELIMINARY score based on automated analysis.")
    print("⚠️  Final scores require manual review by domain experts.")
    print("⚠️  Your actual score may be higher or lower based on:")
    print("    - Quality of implementation details")
    print("    - Completeness of failure mode analysis")
    print("    - Practical viability of solutions")
    print("    - Sovereignty and antifragility alignment")
    print()
    print("Next steps:")
    print("  1. Review sections with lower scores")
    print("  2. Add more implementation details, code, configs")
    print("  3. Ensure all failure modes are addressed")
    print("  4. Include diagrams for architectural questions")
    print("  5. Submit when confident in your answers")
    print()


def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: python score_assessment.py submission.yaml")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    
    print("\nScoring assessment submission...\n")
    
    scorer = AssessmentScorer(submission_file)
    total, tier, sections = scorer.score()
    
    print_score_report(total, tier, sections)


if __name__ == '__main__':
    main()
