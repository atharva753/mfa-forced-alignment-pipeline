"""
Alignment Quality Checker
==========================

This script analyzes TextGrid alignments to identify potential errors:
- Suspiciously short phonemes (< 20ms)
- Suspiciously long phonemes (> 300ms) 
- Timing gaps/overlaps
- Missing phonemes
- Unusual phoneme sequences

Author: Research Assistant
Date: November 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json


class AlignmentQualityChecker:
    """
    Checks forced alignment quality and identifies potential errors
    """
    
    def __init__(self, phoneme_csv, word_csv):
        """
        Initialize the quality checker
        
        Args:
            phoneme_csv (str): Path to phoneme_measurements.csv
            word_csv (str): Path to word_measurements.csv
        """
        self.phoneme_df = pd.read_csv(phoneme_csv)
        self.word_df = pd.read_csv(word_csv)
        
        # Expected duration ranges (in seconds) for phoneme types
        self.duration_thresholds = {
            'vowel_min': 0.030,      # 30ms minimum for vowels
            'vowel_max': 0.400,      # 400ms maximum for vowels
            'consonant_min': 0.020,  # 20ms minimum for consonants
            'consonant_max': 0.250,  # 250ms maximum for consonants
            'silence_max': 2.000     # 2s maximum for silence
        }
        
        print("=" * 60)
        print("ALIGNMENT QUALITY CHECKER")
        print("=" * 60)
        print(f"Loaded {len(self.phoneme_df)} phonemes")
        print(f"Loaded {len(self.word_df)} words")
        print("=" * 60)
    
    def check_duration_anomalies(self):
        """
        Find phonemes with suspiciously short or long durations
        
        Returns:
            dict: Anomalies by category
        """
        print("\n" + "=" * 60)
        print("CHECKING DURATION ANOMALIES")
        print("=" * 60)
        
        anomalies = {
            'too_short_vowels': [],
            'too_long_vowels': [],
            'too_short_consonants': [],
            'too_long_consonants': []
        }
        
        for idx, row in self.phoneme_df.iterrows():
            duration = row['duration']
            phoneme = row['phoneme']
            is_vowel = row.get('is_vowel', False)
            
            if is_vowel:
                if duration < self.duration_thresholds['vowel_min']:
                    anomalies['too_short_vowels'].append({
                        'file': row['file'],
                        'phoneme': phoneme,
                        'duration': duration,
                        'start': row['start_time'],
                        'end': row['end_time']
                    })
                elif duration > self.duration_thresholds['vowel_max']:
                    anomalies['too_long_vowels'].append({
                        'file': row['file'],
                        'phoneme': phoneme,
                        'duration': duration,
                        'start': row['start_time'],
                        'end': row['end_time']
                    })
            else:  # Consonant
                if duration < self.duration_thresholds['consonant_min']:
                    anomalies['too_short_consonants'].append({
                        'file': row['file'],
                        'phoneme': phoneme,
                        'duration': duration,
                        'start': row['start_time'],
                        'end': row['end_time']
                    })
                elif duration > self.duration_thresholds['consonant_max']:
                    anomalies['too_long_consonants'].append({
                        'file': row['file'],
                        'phoneme': phoneme,
                        'duration': duration,
                        'start': row['start_time'],
                        'end': row['end_time']
                    })
        
        # Print summary
        print(f"\n⚠ Too short vowels: {len(anomalies['too_short_vowels'])}")
        if anomalies['too_short_vowels']:
            for item in anomalies['too_short_vowels'][:5]:
                print(f"  - {item['file']}: {item['phoneme']} = {item['duration']*1000:.1f}ms at {item['start']:.2f}s")
            if len(anomalies['too_short_vowels']) > 5:
                print(f"  ... and {len(anomalies['too_short_vowels']) - 5} more")
        
        print(f"\n⚠ Too long vowels: {len(anomalies['too_long_vowels'])}")
        if anomalies['too_long_vowels']:
            for item in anomalies['too_long_vowels'][:5]:
                print(f"  - {item['file']}: {item['phoneme']} = {item['duration']*1000:.1f}ms at {item['start']:.2f}s")
        
        print(f"\n⚠ Too short consonants: {len(anomalies['too_short_consonants'])}")
        if anomalies['too_short_consonants']:
            for item in anomalies['too_short_consonants'][:5]:
                print(f"  - {item['file']}: {item['phoneme']} = {item['duration']*1000:.1f}ms at {item['start']:.2f}s")
            if len(anomalies['too_short_consonants']) > 5:
                print(f"  ... and {len(anomalies['too_short_consonants']) - 5} more")
        
        print(f"\n⚠ Too long consonants: {len(anomalies['too_long_consonants'])}")
        if anomalies['too_long_consonants']:
            for item in anomalies['too_long_consonants'][:5]:
                print(f"  - {item['file']}: {item['phoneme']} = {item['duration']*1000:.1f}ms at {item['start']:.2f}s")
        
        return anomalies
    
    def check_timing_gaps(self):
        """
        Check for gaps or overlaps between consecutive phonemes
        
        Returns:
            dict: Timing issues found
        """
        print("\n" + "=" * 60)
        print("CHECKING TIMING CONTINUITY")
        print("=" * 60)
        
        gaps = []
        overlaps = []
        
        # Group by file
        for file_name in self.phoneme_df['file'].unique():
            file_phonemes = self.phoneme_df[self.phoneme_df['file'] == file_name].sort_values('start_time')
            
            # Check each consecutive pair
            for i in range(len(file_phonemes) - 1):
                current = file_phonemes.iloc[i]
                next_phoneme = file_phonemes.iloc[i + 1]
                
                current_end = current['end_time']
                next_start = next_phoneme['start_time']
                
                gap = next_start - current_end
                
                if gap > 0.001:  # Gap > 1ms
                    gaps.append({
                        'file': file_name,
                        'after_phoneme': current['phoneme'],
                        'before_phoneme': next_phoneme['phoneme'],
                        'gap_ms': gap * 1000,
                        'time': current_end
                    })
                elif gap < -0.001:  # Overlap > 1ms
                    overlaps.append({
                        'file': file_name,
                        'phoneme1': current['phoneme'],
                        'phoneme2': next_phoneme['phoneme'],
                        'overlap_ms': abs(gap) * 1000,
                        'time': current_end
                    })
        
        print(f"\n⚠ Gaps found: {len(gaps)}")
        if gaps:
            for gap in gaps[:5]:
                print(f"  - {gap['file']}: {gap['gap_ms']:.1f}ms gap after '{gap['after_phoneme']}' at {gap['time']:.2f}s")
            if len(gaps) > 5:
                print(f"  ... and {len(gaps) - 5} more")
        
        print(f"\n⚠ Overlaps found: {len(overlaps)}")
        if overlaps:
            for overlap in overlaps[:5]:
                print(f"  - {overlap['file']}: {overlap['overlap_ms']:.1f}ms overlap between '{overlap['phoneme1']}' and '{overlap['phoneme2']}' at {overlap['time']:.2f}s")
            if len(overlaps) > 5:
                print(f"  ... and {len(overlaps) - 5} more")
        
        return {'gaps': gaps, 'overlaps': overlaps}
    
    def check_phoneme_distribution(self):
        """
        Analyze phoneme duration distributions to identify outliers
        
        Returns:
            dict: Statistical outliers
        """
        print("\n" + "=" * 60)
        print("CHECKING PHONEME DURATION DISTRIBUTIONS")
        print("=" * 60)
        
        outliers = []
        
        # Group by phoneme type
        for phoneme in self.phoneme_df['phoneme'].unique():
            phoneme_data = self.phoneme_df[self.phoneme_df['phoneme'] == phoneme]['duration']
            
            if len(phoneme_data) < 3:
                continue
            
            mean = phoneme_data.mean()
            std = phoneme_data.std()
            
            # Find outliers (> 3 standard deviations)
            for idx, row in self.phoneme_df[self.phoneme_df['phoneme'] == phoneme].iterrows():
                duration = row['duration']
                z_score = abs((duration - mean) / std) if std > 0 else 0
                
                if z_score > 3:
                    outliers.append({
                        'file': row['file'],
                        'phoneme': phoneme,
                        'duration': duration,
                        'mean_duration': mean,
                        'z_score': z_score,
                        'time': row['start_time']
                    })
        
        print(f"\n⚠ Statistical outliers: {len(outliers)}")
        if outliers:
            outliers_sorted = sorted(outliers, key=lambda x: x['z_score'], reverse=True)
            for item in outliers_sorted[:10]:
                print(f"  - {item['file']}: {item['phoneme']} = {item['duration']*1000:.1f}ms "
                      f"(expected ~{item['mean_duration']*1000:.1f}ms, z={item['z_score']:.2f}) at {item['time']:.2f}s")
        
        return outliers
    
    def check_word_phoneme_consistency(self):
        """
        Check if word durations match sum of their phoneme durations
        
        Returns:
            list: Mismatches found
        """
        print("\n" + "=" * 60)
        print("CHECKING WORD-PHONEME CONSISTENCY")
        print("=" * 60)
        
        mismatches = []
        
        for idx, word in self.word_df.iterrows():
            file_name = word['file']
            word_start = word['start_time']
            word_end = word['end_time']
            word_duration = word['duration']
            
            # Find phonemes within this word
            phonemes_in_word = self.phoneme_df[
                (self.phoneme_df['file'] == file_name) &
                (self.phoneme_df['start_time'] >= word_start - 0.001) &
                (self.phoneme_df['end_time'] <= word_end + 0.001)
            ]
            
            if len(phonemes_in_word) == 0:
                mismatches.append({
                    'file': file_name,
                    'word': word['word'],
                    'issue': 'no_phonemes',
                    'time': word_start
                })
                continue
            
            phoneme_duration_sum = phonemes_in_word['duration'].sum()
            difference = abs(word_duration - phoneme_duration_sum)
            
            # Allow 10ms tolerance
            if difference > 0.010:
                mismatches.append({
                    'file': file_name,
                    'word': word['word'],
                    'issue': 'duration_mismatch',
                    'word_duration': word_duration,
                    'phoneme_sum': phoneme_duration_sum,
                    'difference_ms': difference * 1000,
                    'time': word_start
                })
        
        print(f"\n⚠ Word-phoneme mismatches: {len(mismatches)}")
        if mismatches:
            for item in mismatches[:5]:
                if item['issue'] == 'no_phonemes':
                    print(f"  - {item['file']}: '{item['word']}' has no phonemes at {item['time']:.2f}s")
                else:
                    print(f"  - {item['file']}: '{item['word']}' duration mismatch: "
                          f"{item['difference_ms']:.1f}ms difference at {item['time']:.2f}s")
            if len(mismatches) > 5:
                print(f"  ... and {len(mismatches) - 5} more")
        
        return mismatches
    
    def generate_quality_report(self, output_file):
        """
        Run all checks and generate comprehensive quality report
        
        Args:
            output_file (str): Path to save report JSON
        """
        print("\n" + "=" * 60)
        print("GENERATING COMPREHENSIVE QUALITY REPORT")
        print("=" * 60)
        
        # Run all checks
        duration_anomalies = self.check_duration_anomalies()
        timing_issues = self.check_timing_gaps()
        statistical_outliers = self.check_phoneme_distribution()
        consistency_issues = self.check_word_phoneme_consistency()
        
        # Compile report
        report = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'total_phonemes': len(self.phoneme_df),
            'total_words': len(self.word_df),
            'duration_anomalies': {
                'too_short_vowels': len(duration_anomalies['too_short_vowels']),
                'too_long_vowels': len(duration_anomalies['too_long_vowels']),
                'too_short_consonants': len(duration_anomalies['too_short_consonants']),
                'too_long_consonants': len(duration_anomalies['too_long_consonants'])
            },
            'timing_issues': {
                'gaps': len(timing_issues['gaps']),
                'overlaps': len(timing_issues['overlaps'])
            },
            'statistical_outliers': len(statistical_outliers),
            'word_phoneme_mismatches': len(consistency_issues),
            'details': {
                'duration_anomalies': duration_anomalies,
                'timing_issues': timing_issues,
                'statistical_outliers': statistical_outliers,
                'consistency_issues': consistency_issues
            }
        }
        
        # Save report
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n✓ Quality report saved to: {output_file}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("QUALITY SUMMARY")
        print("=" * 60)
        total_issues = (
            sum(report['duration_anomalies'].values()) +
            sum(report['timing_issues'].values()) +
            report['statistical_outliers'] +
            report['word_phoneme_mismatches']
        )
        
        print(f"\nTotal potential issues found: {total_issues}")
        print(f"  - Duration anomalies: {sum(report['duration_anomalies'].values())}")
        print(f"  - Timing gaps/overlaps: {sum(report['timing_issues'].values())}")
        print(f"  - Statistical outliers: {report['statistical_outliers']}")
        print(f"  - Word-phoneme mismatches: {report['word_phoneme_mismatches']}")
        
        # Quality score
        error_rate = (total_issues / len(self.phoneme_df)) * 100
        print(f"\nOverall error rate: {error_rate:.2f}%")
        
        if error_rate < 5:
            print("✓ EXCELLENT alignment quality")
        elif error_rate < 10:
            print("✓ GOOD alignment quality")
        elif error_rate < 20:
            print("⚠ FAIR alignment quality - some issues to review")
        else:
            print("⚠ POOR alignment quality - significant issues found")
        
        print("=" * 60)
        
        return report


def main():
    """
    Main function to run quality checks
    """
    # Paths - MODIFY THESE
    phoneme_csv = r"C:\Users\athar\OneDrive\Documents\mfa_output_automated\acoustic_analysis\phoneme_measurements.csv"
    word_csv = r"C:\Users\athar\OneDrive\Documents\mfa_output_automated\acoustic_analysis\word_measurements.csv"
    output_json = r"C:\Users\athar\OneDrive\Documents\mfa_output_automated\acoustic_analysis\analysis_summary.json"
    # Initialize checker
    checker = AlignmentQualityChecker(phoneme_csv, word_csv)
    
    # Generate report
    checker.generate_quality_report(output_json)
    
    print("\n✓ Quality check complete!")
    print("\nReview the detailed report and check suspicious segments in Praat.")


if __name__ == "__main__":
    main()
