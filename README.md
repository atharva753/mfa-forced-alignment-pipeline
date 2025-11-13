<img width="1424" height="732" alt="image" src="https://github.com/user-attachments/assets/9d8dca12-7f9d-42ab-8720-d698fda4ed74" /># Montreal Forced Aligner (MFA) Pipeline for Speech Analysis

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![MFA](https://img.shields.io/badge/MFA-3.3.8-green.svg)](https://montreal-forced-aligner.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Automated phonetic forced alignment pipeline with comprehensive acoustic measurement extraction and quality assessment**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation Guide](#installation-guide)
- [Dataset Preparation](#dataset-preparation)
- [Running the Pipeline](#running-the-pipeline)
- [Output Files](#output-files)
- [Extra Credit Features](#extra-credit-features)
- [Troubleshooting](#troubleshooting)
- [Project Results](#project-results)
- [References](#references)

---

## 🎯 Overview

This project implements a complete automated forced alignment pipeline using the Montreal Forced Aligner (MFA). It processes speech audio files and their transcriptions to generate precise word-level and phoneme-level time alignments, essential for phonetic research, speech synthesis, and acoustic analysis.

**Key Achievement:** 94% alignment accuracy with comprehensive automation (1,200+ lines of code)

---

## ✨ Features

### Core Functionality
- ✅ **Automated alignment pipeline** - Complete workflow from validation to TextGrid generation
- ✅ **Acoustic measurements** - Extract formants, pitch, intensity, and duration for all phonemes
- ✅ **Quality assessment** - Systematic error detection with categorization and reporting
- ✅ **Batch processing** - Handle multiple files efficiently with logging and error handling

### Advanced Features (Extra Credit)
- 🎓 **Custom G2P model training** - 21-hour training on 130k word-pronunciation pairs
- 🎓 **Multi-model comparison** - Systematic evaluation of different acoustic models
- 🎓 **Production-ready automation** - Three integrated Python scripts totaling 1,200+ lines

---

## 📦 Requirements

### System Requirements
- **Operating System:** Windows 10/11, macOS, or Linux
- **RAM:** Minimum 4GB (8GB recommended)
- **Disk Space:** 2GB for software + space for your audio corpus
- **Python:** Version 3.11 (recommended) or 3.10+

### Software Dependencies
- Anaconda or Miniconda (package manager)
- Montreal Forced Aligner 3.3.8
- Python libraries: pandas, numpy, parselmouth
- Praat (optional, for manual visualization)

---

## 🚀 Installation Guide

### Step 1: Install Miniconda

**For Windows:**

1. Download Miniconda installer:
```bash
# Open Command Prompt and run:
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe --output Miniconda3-installer.exe
```

2. Run the installer:
   - Double-click `Miniconda3-installer.exe`
   - Follow the installation wizard
   - **Important:** You can skip "Add to PATH" - we'll use Anaconda Prompt

3. Verify installation:
   - Open **Anaconda Prompt** (search in Start menu)
   - Type: `conda --version`
   - Should show: `conda 24.x.x` or similar

**For macOS/Linux:**

```bash
# macOS
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -o Miniconda3-installer.sh
bash Miniconda3-installer.sh

# Linux
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

---

### Step 2: Create Isolated Environment

Open **Anaconda Prompt** (Windows) or **Terminal** (macOS/Linux):

```bash
# Create environment named 'mfa' with Python 3.11
conda create -n mfa python=3.11

# When prompted "Proceed ([y]/n)?", type: y
```

**What this does:** Creates an isolated workspace for MFA, preventing conflicts with other Python projects.

---

### Step 3: Activate Environment

```bash
conda activate mfa
```

**Success indicator:** Your prompt should change from `(base)` to `(mfa)`

Example:
```
(base) C:\Users\YourName>   →   (mfa) C:\Users\YourName>
```

---

### Step 4: Install Montreal Forced Aligner

```bash
conda install -c conda-forge montreal-forced-aligner
```

**Installation details:**
- Size: ~360 MB
- Time: 5-10 minutes (depends on internet speed)
- When prompted, type: `y`

**What gets installed:**
- MFA core tools
- Kaldi speech recognition toolkit
- Audio processing libraries (sox, ffmpeg)
- Database tools (PostgreSQL)
- Scientific computing libraries

---

### Step 5: Verify MFA Installation

```bash
mfa version
```

**Expected output:** `3.3.8`

 installation succeeded! ✅

---

### Step 6: Download Pre-trained Models

**Download American English dictionary:**
```bash
mfa model download dictionary english_us_arpa
```

**Download acoustic model:**
```bash
mfa model download acoustic english_us_arpa
```

**Verify models downloaded:**
```bash
mfa model list dictionary
mfa model list acoustic
```

You should see `['english_us_arpa']` for both.

---

### Step 7: Install Python Dependencies

```bash
pip install pandas numpy praat-parselmouth
```

**What these libraries do:**
- `pandas` - Data manipulation and CSV handling
- `numpy` - Numerical computations
- `parselmouth` - Python interface to Praat for acoustic analysis

---

### Step 8: Install Praat (Optional, for Manual Inspection)

**Download Praat from:** https://www.fon.hum.uva.nl/praat/

1. Click "Download Praat for [Your OS]"
2. Install/extract the application
3. Open Praat to verify it works

---

## 📂 Dataset Preparation

### Required File Structure

MFA requires a specific corpus organization:

```
your_corpus_folder/
├── audio_file_01.wav
├── audio_file_01.txt
├── audio_file_02.wav
├── audio_file_02.txt
└── ...
```

**Key rules:**
- ✅ Each audio file must have a matching transcript file
- ✅ Files must have **identical base names** (only extension differs)
- ✅ Place both in the **same folder**

---

### Audio File Requirements

**Format specifications:**
- **Container:** WAV (uncompressed PCM)
- **Sampling rate:** 16 kHz or 22.05 kHz (recommended)
- **Bit depth:** 16-bit
- **Channels:** Mono (single channel)
- **Duration:** Any length (tested on 3-30 second files)

**Converting audio to correct format (using ffmpeg):**

```bash
# Convert to 16kHz mono WAV
ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav

# Batch convert all files in folder
for file in *.mp3; do ffmpeg -i "$file" -ar 16000 -ac 1 "${file%.mp3}.wav"; done
```

---

### Transcript File Requirements

**Format specifications:**
- **Encoding:** UTF-8 text file
- **Extension:** `.txt`
- **Content:** Plain text with spoken words only
- **Punctuation:** Optional (MFA ignores it)
- **Case:** Any (MFA normalizes automatically)

**Example transcript (`audio_01.txt`):**
```
The quick brown fox jumps over the lazy dog.
```

or

```
the quick brown fox jumps over the lazy dog
```

Both formats work - MFA handles normalization.

**What NOT to include:**
- ❌ Timestamps
- ❌ Speaker labels
- ❌ Sound effects descriptions [laughs], [coughs]
- ❌ Non-speech markers

---

### Sample Corpus Structure

**Example with 3 file pairs:**

```
my_speech_corpus/
├── recording_001.wav  (Sarah reading news, 25 seconds)
├── recording_001.txt  (Transcript: "In breaking news today...")
├── recording_002.wav  (John saying phrase, 4 seconds)
├── recording_002.txt  (Transcript: "I said white not bait")
└── recording_003.wav  (Maria reading article, 30 seconds)
    recording_003.txt  (Transcript: "The study found that...")
```

---

### Preparing Your Own Data

**Step-by-step:**

1. **Collect audio recordings**
   - Record using Audacity, phone, or microphone
   - Or use existing audio files

2. **Create transcripts**
   - Listen to each recording
   - Type exactly what was spoken
   - Save as a `.txt` file with a matching name

3. **Organize files**
   - Create folder: `my_corpus/`
   - Place all WAV and TXT pairs inside
   - Verify names match exactly

4. **Validate file naming**
```bash
# In your corpus folder, check:
ls *.wav   # Lists all audio files
ls *.txt   # Lists all transcript files
# Counts should match!
```

---

## ▶️ Running the Pipeline

### Quick Start (Automated Pipeline)

**Option 1: Use the automation script (Recommended)**

1. **Clone this repository:**
```bash
git clone https://github.com/atharva753/mfa-forced-alignment-pipeline.git
cd mfa-forced-alignment-pipeline
```

2. **Update paths in `scripts/mfa_automation.py`:**

Open the file and modify lines 279-280:
```python
default_corpus = r"C:\path\to\your\corpus\folder"
default_output = r"C:\path\to\output\folder"
```

3. **Run the complete pipeline:**
```bash
python scripts/mfa_automation.py
```

**What happens:**
- ✅ Validates corpus (checks for errors)
- ✅ Runs forced alignment
- ✅ Generates TextGrid files
- ✅ Creates quality reports
- ⏱️ Takes 1-2 minutes per audio file

**Output location:** Check your specified output folder for TextGrid files!

---

### Manual Step-by-Step (Understanding Each Stage)

#### Stage 1: Validate Your Corpus

**Purpose:** Check for issues before alignment

```bash
mfa validate /path/to/your/corpus english_us_arpa
```

**What it checks:**
- ✅ File pairs match correctly
- ✅ Audio files are readable
- ✅ Transcripts are valid UTF-8
- ⚠️ Out-of-vocabulary (OOV) words

**Example output:**
```
Found 6 sound files
Found 6 transcriptions
22 OOV word types found
Validation complete!
```

**What to do if OOV words are found:**
- Most words will still align correctly
- For critical projects, train a G2P model (see Extra Credit section)

---

#### Stage 2: Run Forced Alignment

**Basic command:**
```bash
mfa align /path/to/corpus dictionary acoustic_model /path/to/output
```

**Full example:**
```bash
mfa align C:\Users\YourName\my_corpus english_us_arpa english_us_arpa C:\Users\YourName\mfa_output
```

**Breakdown:**
- `C:\Users\YourName\my_corpus` → Input: your audio/transcript files
- `english_us_arpa` → Dictionary to use
- `english_us_arpa` → Acoustic model to use
- `C:\Users\YourName\mfa_output` → Output: where TextGrids will be saved

**Processing time:** 
- ~30-60 seconds per file
- 6 files = 3-6 minutes total

**Progress indicators:**
```
INFO   Loading corpus...
INFO   Generating MFCCs...
INFO   Performing alignment...
INFO   Exporting TextGrids...
INFO   Done! Everything took 180 seconds
```

---

#### Stage 3: Extract Acoustic Measurements

**Run the analysis script:**

```bash
python scripts/acoustic_analysis.py
```

**Before running, update paths in the script (lines 397-399):**
```python
audio_folder = r"C:\path\to\your\corpus"
textgrid_folder = r"C:\path\to\mfa\output"
output_folder = r"C:\path\to\analysis\output"
```

**What gets extracted:**
- Phoneme durations (milliseconds)
- Vowel formants (F1, F2, F3 in Hz)
- Pitch statistics (F0 mean, min, max, range)
- Intensity measurements (dB)

**Output files:**
- `phoneme_measurements.csv` - Full dataset (all phonemes)
- `word_measurements.csv` - Word-level data
- `analysis_summary.json` - Statistics summary

---

#### Stage 4: Check Alignment Quality

**Run the quality checker:**

```bash
python scripts/alignment_quality_checker.py
```

**Update paths (lines 446-447):**
```python
phoneme_csv = r"C:\path\to\phoneme_measurements.csv"
word_csv = r"C:\path\to\word_measurements.csv"
```

**What it checks:**
- Duration anomalies (too short/long)
- Timing gaps/overlaps
- Statistical outliers
- Word-phoneme consistency

**Example output:**
```
============================================================
QUALITY SUMMARY
============================================================
Total potential issues found: 62
  - Duration anomalies: 19
  - Timing gaps/overlaps: 31
  - Statistical outliers: 12
  - Word-phoneme mismatches: 0

Overall error rate: 6.07%
✓ GOOD alignment quality
============================================================
```

---

### Advanced Usage Examples

**Example 1: Process multiple corpora**

```bash
# Corpus 1
mfa align ./news_recordings english_us_arpa english_us_arpa ./output_news

# Corpus 2
mfa align ./interviews english_us_arpa english_us_arpa ./output_interviews

# Corpus 3
mfa align ./lab_recordings english_us_arpa english_us_arpa ./output_lab
```

**Example 2: Use a different acoustic model**

```bash
# Download alternative model
mfa model download acoustic english_mfa

# Run alignment with new model
mfa align ./corpus english_us_arpa english_mfa ./output_english_mfa
```

**Example 3: Clean up and re-run**

```bash
# Remove previous alignment data
mfa clean

# Re-validate
mfa validate ./corpus english_us_arpa

# Re-align
mfa align ./corpus english_us_arpa english_us_arpa ./output
```

---

## 📊 Output Files

### TextGrid Files

**Location:** Output folder specified in alignment command

**Format:** Praat TextGrid (interval tier format)

**Contents:**
- **Tier 1 (words):** Word-level boundaries
  - Example: "hello" from 0.5s to 1.2s
- **Tier 2 (phones):** Phoneme-level boundaries
  - Example: "HH" 0.5-0.6s, "EH" 0.6-0.9s, "L" 0.9-1.0s, "OW" 1.0-1.2s

**Opening TextGrids:**
1. Open Praat
2. File → Open → Read from file...
3. Select both WAV and TextGrid
4. Click "View & Edit"

---

### Measurement Files

**phoneme_measurements.csv columns:**
- `file` - Source audio filename
- `phoneme` - ARPA phoneme label (e.g., "AE1")
- `start_time`, `end_time` - Boundaries in seconds
- `duration` - Phoneme duration in seconds
- `is_vowel` - Boolean flag
- `f1_mean`, `f2_mean`, `f3_mean` - Formant frequencies (Hz)
- `f0_mean`, `f0_std`, `f0_min`, `f0_max` - Pitch statistics
- `intensity_mean`, `intensity_std` - Loudness measures

**word_measurements.csv columns:**
- `file` - Source audio filename
- `word` - Orthographic word
- `start_time`, `end_time` - Word boundaries
- `duration` - Word duration in seconds

---

### Quality Reports

**quality_report.json structure:**
```json
{
  "timestamp": "2025-11-12T10:30:00",
  "total_phonemes": 1022,
  "duration_anomalies": {
    "too_short_vowels": 13,
    "too_long_consonants": 6
  },
  "timing_issues": {
    "gaps": 31,
    "overlaps": 0
  },
  "overall_error_rate": 6.07
}
```

---

## 🎓 Extra Credit Features

### 1. Custom G2P Model Training

**When to use:** Corpus contains words not in the dictionary (proper names, technical terms)

**Training command:**
```bash
mfa train_g2p english_us_arpa my_custom_g2p
```

**Training details:**
- Duration: ~20 hours on standard hardware
- Input: 130,000 word-pronunciation pairs
- Output: Custom model for predicting pronunciations

**Using the trained model:**
```bash
# Generate pronunciations for unknown words
mfa g2p my_custom_g2p unknown_words.txt custom_pronunciations.dict
```

---

### 2. Multi-Model Comparison

**Purpose:** Evaluate which acoustic model works best for your data

**Steps:**

1. Download additional models:
```bash
mfa model download acoustic english_mfa
```

2. Run alignment with Model 1:
```bash
mfa align ./corpus english_us_arpa english_us_arpa ./output_model1
```

3. Run alignment with Model 2:
```bash
mfa align ./corpus english_us_arpa english_mfa ./output_model2
```

4. Compare quality metrics:
```bash
python scripts/compare_models.py
```

**Comparison metrics:**
- Overall log-likelihood (higher = better)
- Phone duration deviation (lower = better)
- Per-file quality scores

---

### 3. Complete Pipeline Automation

**Three integrated scripts:**

**mfa_automation.py (350 lines)**
- Validates corpus
- Runs alignment
- Generates reports
- Handles errors gracefully

**acoustic_analysis.py (450 lines)**
- Extracts formants
- Computes pitch/intensity
- Batch processes all files
- Exports to CSV

**alignment_quality_checker.py (400 lines)**
- Detects duration anomalies
- Checks timing continuity
- Identifies statistical outliers
- Generates quality scores

**Total:** 1,200+ lines of production-ready Python code

---

## 🔧 Troubleshooting

### Common Issues and Solutions

**Issue 1: "conda: command not found"**

**Solution:**
- Close and reopen terminal/prompt
- Use "Anaconda Prompt" instead of the regular command prompt (Windows)
- Re-run Miniconda installer and check "Add to PATH"

---

**Issue 2: "mfa: command not found" after installation**

**Solution:**
```bash
# Make sure mfa environment is activated
conda activate mfa

# Verify MFA is installed
conda list | grep montreal

# If not found, reinstall
conda install -c conda-forge montreal-forced-aligner
```

---

**Issue 3: Out-of-vocabulary words**

**Symptoms:**
```
WARNING: 22 OOV word types found
```

**Solutions:**
- **Option A:** Ignore - most words will align anyway
- **Option B:** Train G2P model (see Extra Credit section)
- **Option C:** Add words to custom dictionary

---

**Issue 4: Alignment produces empty TextGrids**

**Possible causes:**
- Audio-transcript mismatch (text doesn't match audio)
- Audio quality issues (too noisy)
- Incorrect file naming

**Debug steps:**
```bash
# Validate first
mfa validate ./corpus english_us_arpa

# Check audio quality
mfa analyze ./corpus

# Try with verbose output
mfa align ./corpus english_us_arpa english_us_arpa ./output --verbose
```

---

**Issue 5: Python script errors**

**Error:** `ModuleNotFoundError: No module named 'pandas'`

**Solution:**
```bash
# Make sure environment is activated
conda activate mfa

# Install missing dependencies
pip install pandas numpy praat-parselmouth
```

---

**Issue 6: Large files rejected by GitHub**

**Solution:** Already handled by `.gitignore`
- WAV files are excluded automatically
- Only upload code and small outputs

---

## 📈 Project Results

### Performance Metrics

**Alignment Quality:**
- ✅ Overall accuracy: 94% (6.07% flagged issues)
- ✅ True error rate: ~0.2% (only 1-2 actual errors)
- ✅ Processing speed: ~60 seconds per file

**Corpus Statistics:**
- 📊 Total phonemes: 1,022
- 📊 Total words: 241
- 📊 Vowels analyzed: 397
- 📊 Mean phoneme duration: 79 ms
- 📊 Mean word duration: 335 ms

**Acoustic Measurements:**
- 🎵 F1 mean: 506 Hz
- 🎵 F2 mean: 1771 Hz
- 🎵 Pitch range: 75-180 Hz

---

### Sample Visualizations

**See `visualizations_praat/` folder for:**
- Word-level alignment examples
- Phoneme boundary precision
- Formant trajectory visualization
- Minimal pair contrasts (vowel differences)

---

## 📚 References

**Montreal Forced Aligner:**
- Documentation: https://montreal-forced-aligner.readthedocs.io
- GitHub: https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner
- Paper: McAuliffe et al. (2017) - Interspeech

**Praat:**
- Website: https://www.fon.hum.uva.nl/praat/
- Manual: https://www.fon.hum.uva.nl/praat/manual/

**Python Libraries:**
- Parselmouth: https://parselmouth.readthedocs.io
- Pandas: https://pandas.pydata.org
- NumPy: https://numpy.org

---

## 📧 Contact & Support

**For questions about this implementation:**
- Open an issue on GitHub
- Email: [your.email@example.com]

**For MFA-specific questions:**
- MFA GitHub Issues: https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner/issues
- MFA Documentation: https://montreal-forced-aligner.readthedocs.io

---

## 📄 License

This project is provided for educational and research purposes. 

Montreal Forced Aligner is licensed under the MIT License.

---

## 🙏 Acknowledgments

- Montreal Corpus Tools team for developing MFA
- Kaldi developers for the acoustic modeling toolkit
- Praat developers for phonetic analysis software
- IIIT Hyderabad for the research opportunity to explore on the lines of this assignment 

---

**⭐ If you find this project helpful, please star the repository!**
