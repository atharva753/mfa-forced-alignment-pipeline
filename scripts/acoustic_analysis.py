"""
Acoustic Measurements Extraction from MFA TextGrids
====================================================

This script extracts detailed acoustic measurements from TextGrid files:
- Phoneme and word durations
- Vowel formants (F1, F2, F3)
- Pitch (F0) statistics
- Intensity measurements
- Voice quality metrics

Requires: Parselmouth library (Praat functionality in Python)

Installation:
    pip install praat-parselmouth

Author: Research Assistant
Date: November 2025
"""

import parselmouth
from parselmouth.praat import call
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime


class AcousticAnalyzer:
    """
    Extracts acoustic measurements from audio files with TextGrid annotations
    """
    
    def __init__(self, audio_folder, textgrid_folder, output_folder):
        """
        Initialize the acoustic analyzer
        
        Args:
            audio_folder (str): Path to folder with WAV files
            textgrid_folder (str): Path to folder with TextGrid files
            output_folder (str): Where to save results
        """
        self.audio_folder = Path(audio_folder)
        self.textgrid_folder = Path(textgrid_folder)
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        # Define vowel phonemes (ARPA notation)
        self.vowels = [
            'AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 
            'IH', 'IY', 'OW', 'OY', 'UH', 'UW',
            # With stress markers
            'AA0', 'AA1', 'AA2', 'AE0', 'AE1', 'AE2', 
            'AH0', 'AH1', 'AH2', 'AO0', 'AO1', 'AO2',
            'AW0', 'AW1', 'AW2', 'AY0', 'AY1', 'AY2',
            'EH0', 'EH1', 'EH2', 'ER0', 'ER1', 'ER2',
            'EY0', 'EY1', 'EY2', 'IH0', 'IH1', 'IH2',
            'IY0', 'IY1', 'IY2', 'OW0', 'OW1', 'OW2',
            'OY0', 'OY1', 'OY2', 'UH0', 'UH1', 'UH2',
            'UW0', 'UW1', 'UW2'
        ]
        
        print("=" * 60)
        print("ACOUSTIC ANALYZER INITIALIZED")
        print("=" * 60)
        print(f"Audio folder: {self.audio_folder}")
        print(f"TextGrid folder: {self.textgrid_folder}")
        print(f"Output folder: {self.output_folder}")
        print("=" * 60)
    
    def load_audio_and_textgrid(self, basename):
        """
        Load audio file and corresponding TextGrid
        
        Args:
            basename (str): File name without extension
            
        Returns:
            tuple: (Sound object, TextGrid object) or (None, None) if error
        """
        audio_path = self.audio_folder / f"{basename}.wav"
        textgrid_path = self.textgrid_folder / f"{basename}.TextGrid"
        
        try:
            sound = parselmouth.Sound(str(audio_path))
            textgrid = parselmouth.read(str(textgrid_path))
            return sound, textgrid
        except Exception as e:
            print(f"Error loading {basename}: {e}")
            return None, None
    
    def extract_formants(self, sound, start_time, end_time, num_points=3):
        """
        Extract formant values at multiple time points
        
        Args:
            sound: Parselmouth Sound object
            start_time (float): Start time in seconds
            end_time (float): End time in seconds
            num_points (int): Number of measurement points (default: 3 for start/mid/end)
            
        Returns:
            dict: F1, F2, F3 measurements
        """
        # Create formant object
        formant = sound.to_formant_burg(
            time_step=0.01,
            max_number_of_formants=5,
            maximum_formant=5500,
            window_length=0.025,
            pre_emphasis_from=50
        )
        
        # Calculate measurement points
        duration = end_time - start_time
        if duration < 0.03:  # Too short for reliable formants
            return None
        
        times = np.linspace(start_time, end_time, num_points)
        
        f1_values = []
        f2_values = []
        f3_values = []
        
        for t in times:
            try:
                f1 = call(formant, "Get value at time", 1, t, "Hertz", "Linear")
                f2 = call(formant, "Get value at time", 2, t, "Hertz", "Linear")
                f3 = call(formant, "Get value at time", 3, t, "Hertz", "Linear")
                
                if f1 and not np.isnan(f1):
                    f1_values.append(f1)
                if f2 and not np.isnan(f2):
                    f2_values.append(f2)
                if f3 and not np.isnan(f3):
                    f3_values.append(f3)
            except:
                continue
        
        if not f1_values:
            return None
        
        return {
            'f1_mean': np.mean(f1_values),
            'f1_std': np.std(f1_values) if len(f1_values) > 1 else 0,
            'f2_mean': np.mean(f2_values) if f2_values else None,
            'f2_std': np.std(f2_values) if len(f2_values) > 1 else 0,
            'f3_mean': np.mean(f3_values) if f3_values else None,
            'f3_std': np.std(f3_values) if len(f3_values) > 1 else 0
        }
    
    def extract_pitch(self, sound, start_time, end_time):
        """
        Extract pitch (F0) statistics
        
        Args:
            sound: Parselmouth Sound object
            start_time (float): Start time in seconds
            end_time (float): End time in seconds
            
        Returns:
            dict: Pitch measurements
        """
        try:
            pitch = sound.to_pitch(
                time_step=0.01,
                pitch_floor=75,
                pitch_ceiling=500
            )
            
            # Extract pitch in the time range
            pitch_values = []
            times = np.arange(start_time, end_time, 0.01)
            
            for t in times:
                f0 = call(pitch, "Get value at time", t, "Hertz", "Linear")
                if f0 and not np.isnan(f0):
                    pitch_values.append(f0)
            
            if not pitch_values:
                return None
            
            return {
                'f0_mean': np.mean(pitch_values),
                'f0_std': np.std(pitch_values),
                'f0_min': np.min(pitch_values),
                'f0_max': np.max(pitch_values),
                'f0_range': np.max(pitch_values) - np.min(pitch_values)
            }
        except:
            return None
    
    def extract_intensity(self, sound, start_time, end_time):
        """
        Extract intensity measurements
        
        Args:
            sound: Parselmouth Sound object
            start_time (float): Start time in seconds
            end_time (float): End time in seconds
            
        Returns:
            dict: Intensity measurements
        """
        try:
            intensity = sound.to_intensity(
                time_step=0.01,
                minimum_pitch=75
            )
            
            intensity_values = []
            times = np.arange(start_time, end_time, 0.01)
            
            for t in times:
                intens = call(intensity, "Get value at time", t, "Cubic")
                if intens and not np.isnan(intens):
                    intensity_values.append(intens)
            
            if not intensity_values:
                return None
            
            return {
                'intensity_mean': np.mean(intensity_values),
                'intensity_std': np.std(intensity_values),
                'intensity_min': np.min(intensity_values),
                'intensity_max': np.max(intensity_values)
            }
        except:
            return None
    
    def analyze_phoneme(self, sound, phoneme_label, start_time, end_time):
        """
        Complete acoustic analysis of a single phoneme
        
        Args:
            sound: Parselmouth Sound object
            phoneme_label (str): Phoneme label (e.g., 'AE1')
            start_time (float): Start time
            end_time (float): End time
            
        Returns:
            dict: All measurements
        """
        duration = end_time - start_time
        
        measurements = {
            'phoneme': phoneme_label,
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration
        }
        
        # Check if it's a vowel
        is_vowel = phoneme_label in self.vowels
        measurements['is_vowel'] = is_vowel
        
        # Extract formants for vowels
        if is_vowel and duration > 0.03:
            formants = self.extract_formants(sound, start_time, end_time)
            if formants:
                measurements.update(formants)
        
        # Extract pitch
        pitch = self.extract_pitch(sound, start_time, end_time)
        if pitch:
            measurements.update(pitch)
        
        # Extract intensity
        intensity = self.extract_intensity(sound, start_time, end_time)
        if intensity:
            measurements.update(intensity)
        
        return measurements
    
    def analyze_file(self, basename):
        """
        Analyze all phonemes and words in a single file
        
        Args:
            basename (str): File name without extension
            
        Returns:
            tuple: (phoneme_data, word_data) as DataFrames
        """
        print(f"\nAnalyzing: {basename}")
        
        sound, textgrid = self.load_audio_and_textgrid(basename)
        if sound is None:
            return None, None
        
        phoneme_data = []
        word_data = []
        
        # Find word and phone tiers using Praat call functions
        word_tier_idx = None
        phone_tier_idx = None
        
        # Get number of tiers
        try:
            n_tiers = call(textgrid, "Get number of tiers")
        except:
            print(f"  Error: Could not get tiers from {basename}")
            return None, None
        
        # Find tier indices
        for i in range(1, n_tiers + 1):
            tier_name = call(textgrid, "Get tier name", i)
            if 'word' in tier_name.lower():
                word_tier_idx = i
            elif 'phone' in tier_name.lower():
                phone_tier_idx = i
        
        # Extract word durations
        if word_tier_idx:
            n_intervals = call(textgrid, "Get number of intervals", word_tier_idx)
            for j in range(1, n_intervals + 1):
                label = call(textgrid, "Get label of interval", word_tier_idx, j)
                if label and label.strip():
                    start = call(textgrid, "Get start time of interval", word_tier_idx, j)
                    end = call(textgrid, "Get end time of interval", word_tier_idx, j)
                    word_data.append({
                        'file': basename,
                        'word': label,
                        'start_time': start,
                        'end_time': end,
                        'duration': end - start
                    })
        
        # Extract phoneme measurements
        if phone_tier_idx:
            n_intervals = call(textgrid, "Get number of intervals", phone_tier_idx)
            for j in range(1, n_intervals + 1):
                label = call(textgrid, "Get label of interval", phone_tier_idx, j)
                if label and label.strip():
                    start = call(textgrid, "Get start time of interval", phone_tier_idx, j)
                    end = call(textgrid, "Get end time of interval", phone_tier_idx, j)
                    measurements = self.analyze_phoneme(
                        sound,
                        label,
                        start,
                        end
                    )
                    measurements['file'] = basename
                    phoneme_data.append(measurements)
        
        print(f"  - Extracted {len(word_data)} words")
        print(f"  - Extracted {len(phoneme_data)} phonemes")
        
        return pd.DataFrame(phoneme_data), pd.DataFrame(word_data)
    
    def analyze_all_files(self):
        """
        Analyze all TextGrid files in the folder
        
        Returns:
            tuple: (combined_phoneme_df, combined_word_df)
        """
        print("\n" + "=" * 60)
        print("STARTING ACOUSTIC ANALYSIS")
        print("=" * 60)
        
        all_phoneme_data = []
        all_word_data = []
        
        # Find all TextGrid files
        textgrid_files = list(self.textgrid_folder.glob("*.TextGrid"))
        
        print(f"\nFound {len(textgrid_files)} TextGrid files")
        
        for tg_path in textgrid_files:
            basename = tg_path.stem
            phoneme_df, word_df = self.analyze_file(basename)
            
            if phoneme_df is not None:
                all_phoneme_data.append(phoneme_df)
            if word_df is not None:
                all_word_data.append(word_df)
        
        # Combine all data
        combined_phonemes = pd.concat(all_phoneme_data, ignore_index=True) if all_phoneme_data else pd.DataFrame()
        combined_words = pd.concat(all_word_data, ignore_index=True) if all_word_data else pd.DataFrame()
        
        return combined_phonemes, combined_words
    
    def save_results(self, phoneme_df, word_df):
        """
        Save analysis results to CSV and generate summary
        
        Args:
            phoneme_df: DataFrame with phoneme measurements
            word_df: DataFrame with word measurements
        """
        # Save to CSV
        phoneme_csv = self.output_folder / "phoneme_measurements.csv"
        word_csv = self.output_folder / "word_measurements.csv"
        
        phoneme_df.to_csv(phoneme_csv, index=False)
        word_df.to_csv(word_csv, index=False)
        
        print("\n" + "=" * 60)
        print("RESULTS SAVED")
        print("=" * 60)
        print(f"Phoneme data: {phoneme_csv}")
        print(f"Word data: {word_csv}")
        
        # Generate summary statistics
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_files': len(phoneme_df['file'].unique()),
            'total_phonemes': len(phoneme_df),
            'total_words': len(word_df),
            'vowels_analyzed': len(phoneme_df[phoneme_df['is_vowel'] == True]),
            'phoneme_stats': {
                'mean_duration': float(phoneme_df['duration'].mean()),
                'std_duration': float(phoneme_df['duration'].std()),
                'min_duration': float(phoneme_df['duration'].min()),
                'max_duration': float(phoneme_df['duration'].max())
            },
            'word_stats': {
                'mean_duration': float(word_df['duration'].mean()),
                'std_duration': float(word_df['duration'].std())
            }
        }
        
        # Add vowel formant statistics if available
        vowels = phoneme_df[phoneme_df['is_vowel'] == True]
        if 'f1_mean' in vowels.columns and len(vowels) > 0:
            summary['vowel_formants'] = {
                'f1_mean': float(vowels['f1_mean'].mean()),
                'f2_mean': float(vowels['f2_mean'].mean()),
                'f1_range': [float(vowels['f1_mean'].min()), float(vowels['f1_mean'].max())],
                'f2_range': [float(vowels['f2_mean'].min()), float(vowels['f2_mean'].max())]
            }
        
        # Save summary
        summary_file = self.output_folder / "analysis_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, indent=2, fp=f)
        
        print(f"Summary: {summary_file}")
        print("\n" + "=" * 60)
        print("SUMMARY STATISTICS")
        print("=" * 60)
        print(f"Total phonemes: {summary['total_phonemes']}")
        print(f"Total words: {summary['total_words']}")
        print(f"Vowels analyzed: {summary['vowels_analyzed']}")
        print(f"Mean phoneme duration: {summary['phoneme_stats']['mean_duration']:.4f} s")
        print(f"Mean word duration: {summary['word_stats']['mean_duration']:.4f} s")
        
        if 'vowel_formants' in summary:
            print(f"\nVowel Formants:")
            print(f"  F1 mean: {summary['vowel_formants']['f1_mean']:.1f} Hz")
            print(f"  F2 mean: {summary['vowel_formants']['f2_mean']:.1f} Hz")
        
        print("=" * 60)


def main():
    """
    Main function to run acoustic analysis
    """
    # Default paths - MODIFY THESE
    audio_folder = r"C:\Users\athar\OneDrive\Documents\mfa_corpus"
    textgrid_folder = r"C:\Users\athar\OneDrive\Documents\mfa_output"
    output_folder = r"C:\Users\athar\OneDrive\Documents\acoustic_analysis"
    
    print("\n" + "=" * 60)
    print("ACOUSTIC MEASUREMENTS EXTRACTION")
    print("=" * 60)
    print("\nThis script extracts:")
    print("  • Phoneme and word durations")
    print("  • Vowel formants (F1, F2, F3)")
    print("  • Pitch (F0) statistics")
    print("  • Intensity measurements")
    print("\n" + "=" * 60)
    
    # Initialize analyzer
    analyzer = AcousticAnalyzer(audio_folder, textgrid_folder, output_folder)
    
    # Run analysis
    phoneme_df, word_df = analyzer.analyze_all_files()
    
    # Save results
    if not phoneme_df.empty:
        analyzer.save_results(phoneme_df, word_df)
        print("\n✓ Analysis complete!")
        print(f"\nCheck output folder: {output_folder}")
    else:
        print("\n✗ No data extracted. Check your file paths.")


if __name__ == "__main__":
    main()