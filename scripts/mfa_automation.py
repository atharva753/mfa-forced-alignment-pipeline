"""
MFA (Montreal Forced Aligner) Pipeline Automation Script
=========================================================

This script automates the complete forced alignment workflow:
1. Validates corpus (checks for OOV words)
2. Runs forced alignment
3. Exports TextGrids
4. Generates analysis reports

Author: Research Assistant
Date: November 2025
"""

import subprocess
import os
import sys
from pathlib import Path
import json
from datetime import datetime


class MFAPipeline:
    """
    Automated pipeline for Montreal Forced Aligner
    
    This class handles the entire MFA workflow from validation to alignment.
    """
    
    def __init__(self, corpus_path, output_path, dictionary="english_us_arpa", 
                 acoustic_model="english_us_arpa"):
        """
        Initialize the MFA pipeline
        
        Args:
            corpus_path (str): Path to folder containing WAV and TXT files
            output_path (str): Path where TextGrids will be saved
            dictionary (str): Name of MFA dictionary to use
            acoustic_model (str): Name of MFA acoustic model to use
        """
        self.corpus_path = Path(corpus_path)
        self.output_path = Path(output_path)
        self.dictionary = dictionary
        self.acoustic_model = acoustic_model
        self.log_file = self.output_path / "pipeline_log.txt"
        
        # Create output directory if it doesn't exist
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        print("=" * 60)
        print("MFA PIPELINE INITIALIZED")
        print("=" * 60)
        print(f"Corpus Path: {self.corpus_path}")
        print(f"Output Path: {self.output_path}")
        print(f"Dictionary: {self.dictionary}")
        print(f"Acoustic Model: {self.acoustic_model}")
        print("=" * 60)
    
    def log(self, message):
        """
        Log messages to both console and log file
        
        Args:
            message (str): Message to log
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        # Append to log file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + "\n")
    
    def run_command(self, command, description):
        """
        Run a shell command and handle errors
        
        Args:
            command (list): Command and arguments as list
            description (str): Human-readable description of what command does
            
        Returns:
            bool: True if successful, False if failed
        """
        self.log(f"STEP: {description}")
        self.log(f"Running command: {' '.join(command)}")
        
        try:
            # Run the command and capture output
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            
            self.log(f"✓ SUCCESS: {description}")
            
            # Log output if there's any
            if result.stdout:
                self.log(f"Output: {result.stdout[:500]}")  # First 500 chars
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"✗ FAILED: {description}")
            self.log(f"Error: {e.stderr}")
            return False
        except FileNotFoundError:
            self.log(f"✗ ERROR: MFA command not found. Is MFA installed?")
            self.log(f"Make sure you're running this in the 'mfa' conda environment")
            return False
    
    def validate_corpus(self):
        """
        Step 1: Validate the corpus
        
        Checks:
        - File format correctness
        - Out-of-vocabulary words
        - Acoustic quality
        
        Returns:
            bool: True if validation successful
        """
        self.log("\n" + "=" * 60)
        self.log("STEP 1: VALIDATING CORPUS")
        self.log("=" * 60)
        
        command = [
            "mfa",
            "validate",
            str(self.corpus_path),
            self.dictionary
        ]
        
        success = self.run_command(
            command,
            "Validating corpus against dictionary"
        )
        
        if success:
            # Check if OOV file was created
            mfa_corpus_path = Path.home() / "Documents" / "MFA" / self.corpus_path.name
            oov_file = mfa_corpus_path / "oovs_found.txt"
            
            if oov_file.exists():
                with open(oov_file, 'r', encoding='utf-8') as f:
                    oovs = f.read().strip().split('\n')
                    self.log(f"Found {len(oovs)} out-of-vocabulary words")
                    self.log(f"OOV words: {', '.join(oovs[:10])}")  # Show first 10
                    if len(oovs) > 10:
                        self.log(f"... and {len(oovs) - 10} more")
        
        return success
    
    def run_alignment(self):
        """
        Step 2: Run forced alignment
        
        Aligns audio to text and generates word/phoneme boundaries
        
        Returns:
            bool: True if alignment successful
        """
        self.log("\n" + "=" * 60)
        self.log("STEP 2: RUNNING FORCED ALIGNMENT")
        self.log("=" * 60)
        
        command = [
            "mfa",
            "align",
            str(self.corpus_path),
            self.dictionary,
            self.acoustic_model,
            str(self.output_path)
        ]
        
        success = self.run_command(
            command,
            "Performing forced alignment"
        )
        
        if success:
            # Count generated TextGrids
            textgrids = list(self.output_path.glob("*.TextGrid"))
            self.log(f"Generated {len(textgrids)} TextGrid files")
            for tg in textgrids:
                self.log(f"  - {tg.name}")
        
        return success
    
    def generate_report(self):
        """
        Step 3: Generate analysis report
        
        Creates a summary of the alignment results
        
        Returns:
            dict: Report data
        """
        self.log("\n" + "=" * 60)
        self.log("STEP 3: GENERATING REPORT")
        self.log("=" * 60)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "corpus_path": str(self.corpus_path),
            "output_path": str(self.output_path),
            "dictionary": self.dictionary,
            "acoustic_model": self.acoustic_model,
            "textgrids": []
        }
        
        # Count files in corpus
        wav_files = list(self.corpus_path.glob("*.wav"))
        txt_files = list(self.corpus_path.glob("*.txt"))
        textgrid_files = list(self.output_path.glob("*.TextGrid"))
        
        report["corpus_stats"] = {
            "wav_files": len(wav_files),
            "txt_files": len(txt_files),
            "textgrids_generated": len(textgrid_files)
        }
        
        # List TextGrid files with sizes
        for tg in textgrid_files:
            report["textgrids"].append({
                "name": tg.name,
                "size_kb": round(tg.stat().st_size / 1024, 2)
            })
        
        # Save report as JSON
        report_file = self.output_path / "alignment_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, indent=2, fp=f)
        
        self.log(f"Report saved to: {report_file}")
        self.log(f"WAV files: {report['corpus_stats']['wav_files']}")
        self.log(f"TXT files: {report['corpus_stats']['txt_files']}")
        self.log(f"TextGrids generated: {report['corpus_stats']['textgrids_generated']}")
        
        return report
    
    def run_full_pipeline(self):
        """
        Execute the complete pipeline
        
        Runs all steps in sequence:
        1. Validate corpus
        2. Run alignment
        3. Generate report
        
        Returns:
            bool: True if entire pipeline successful
        """
        self.log("\n" + "=" * 60)
        self.log("STARTING FULL MFA PIPELINE")
        self.log("=" * 60)
        
        start_time = datetime.now()
        
        # Step 1: Validate
        if not self.validate_corpus():
            self.log("\n✗ Pipeline FAILED at validation step")
            return False
        
        # Step 2: Align
        if not self.run_alignment():
            self.log("\n✗ Pipeline FAILED at alignment step")
            return False
        
        # Step 3: Report
        self.generate_report()
        
        # Calculate total time
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.log("\n" + "=" * 60)
        self.log("✓ PIPELINE COMPLETED SUCCESSFULLY!")
        self.log(f"Total time: {duration:.2f} seconds")
        self.log("=" * 60)
        
        return True


def main():
    """
    Main function to run the pipeline
    
    Usage examples:
    
    Basic usage:
        python mfa_automation.py
        
    Custom paths:
        python mfa_automation.py --corpus /path/to/corpus --output /path/to/output
    """
    
    # Default paths - MODIFY THESE FOR YOUR SETUP
    default_corpus = r"C:\Users\athar\OneDrive\Documents\mfa_corpus"
    default_output = r"C:\Users\athar\OneDrive\Documents\mfa_output"
    
    # You can add command-line argument parsing here if needed
    # For now, using defaults
    
    print("\n" + "=" * 60)
    print("MFA AUTOMATED PIPELINE")
    print("=" * 60)
    print("\nThis script will:")
    print("1. Validate your corpus")
    print("2. Run forced alignment")
    print("3. Generate TextGrids")
    print("4. Create analysis report")
    print("\n" + "=" * 60)
    
    # Check if corpus path exists
    if not Path(default_corpus).exists():
        print(f"\n✗ ERROR: Corpus path does not exist: {default_corpus}")
        print("\nPlease update the 'default_corpus' path in the script")
        sys.exit(1)
    
    # Initialize pipeline
    pipeline = MFAPipeline(
        corpus_path=default_corpus,
        output_path=default_output,
        dictionary="english_us_arpa",
        acoustic_model="english_us_arpa"
    )
    
    # Run the full pipeline
    success = pipeline.run_full_pipeline()
    
    if success:
        print("\n✓ Check your output folder for TextGrids!")
        print(f"Output location: {default_output}")
        sys.exit(0)
    else:
        print("\n✗ Pipeline failed. Check the log file for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
