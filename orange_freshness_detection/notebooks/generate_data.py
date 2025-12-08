import pandas as pd
import numpy as np
from scipy.ndimage import shift
import os

# ==========================================
# 1. CONFIGURATION (The "Knobs")
# ==========================================
# Paths (Relative to where you run this script)
INPUT_FILE = '../datasets/master_all_batches.csv'
OUTPUT_FILE = '../datasets/synthetic_augmented_data.csv'

# Generation Settings
SAMPLES_TO_GENERATE = 2000  # Increased to have more diversity
SAMPLES_PER_BATCH = 150     # Generate batch-specific data

# Auto-calibrate noise from real data (will be calculated below)
NOISE_LEVEL = None          # Will be calibrated from real data variance
DRIFT_RANGE = None          # Will be calibrated from batch-to-batch variation
TIME_SHIFT_MAX = 3          # Reduced for more realistic timing

# Physics Settings (Decay logic) - Will use multiple decay patterns
# k = Decay constant. Higher k = Rots faster.
AVG_DECAY_RATE = 0.15       
DECAY_VARIANCE = 0.02       # Variation in rotting speed between oranges

# ==========================================
# 2. LOAD & EXTRACT TEMPLATE
# ==========================================
print(f"Loading Master Data from: {INPUT_FILE}...")

if not os.path.exists(INPUT_FILE):
    # Fallback for different folder structures
    INPUT_FILE = 'master_all_batches.csv' # Try current folder
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError("❌ Could not find 'master_all_batches.csv'. Please check the path.")

df = pd.read_csv(INPUT_FILE)

# Identify signal columns (f1 to f3700+)
signal_cols = [c for c in df.columns if c.startswith('f') and c != 'filename']
print(f"✅ Features Detected: {len(signal_cols)} signal points per sample.")
print(f"✅ Original Dataset Size: {len(df)} samples.")

# Create the "Master Template" (Average of all Day 0 samples)
# This gives us the "Ideal Fresh Orange" signature
fresh_data = df[df['day'] == 0][signal_cols]

if len(fresh_data) == 0:
    # Fallback: If no Day 0 exists, take the earliest available day
    min_day = df['day'].min()
    print(f"⚠️ Warning: No 'Day 0' data found. Using 'Day {min_day}' as baseline.")
    fresh_data = df[df['day'] == min_day][signal_cols]

# Calculate the mean signal shape
template_signal = fresh_data.mean(axis=0).values

# ==========================================
# 2B. CALIBRATE FROM REAL DATA
# ==========================================
print("\n📊 Calibrating parameters from real data...")

# Calculate realistic noise from actual measurement variance
all_signals = df[signal_cols].values
within_sample_std = np.std(all_signals, axis=0).mean()  # Average std across features
NOISE_LEVEL = within_sample_std * 0.5  # Use half of observed variance

# Calculate drift from batch-to-batch variation
batch_means = df.groupby('batch')[signal_cols].mean()
between_batch_std = batch_means.std().mean()
DRIFT_RANGE = between_batch_std * 0.8

print(f"✓ Calibrated Noise Level: {NOISE_LEVEL:.4f} (from real data variance)")
print(f"✓ Calibrated Drift Range: ±{DRIFT_RANGE:.4f} (from batch variation)")

# Create batch-specific templates (learn from each real batch)
batch_templates = {}
for batch_id in df['batch'].unique():
    batch_samples = df[df['batch'] == batch_id][signal_cols]
    if len(batch_samples) > 0:
        batch_templates[batch_id] = batch_samples.mean(axis=0).values

print(f"✓ Created {len(batch_templates)} batch-specific templates")

# Learn day-specific patterns from real data
day_patterns = {}
for day_val in sorted(df['day'].unique()):
    day_samples = df[df['day'] == day_val][signal_cols]
    if len(day_samples) > 0:
        day_patterns[day_val] = day_samples.mean(axis=0).values

print(f"✓ Learned {len(day_patterns)} day-specific decay patterns")

# ==========================================
# 3. THE GENERATOR ENGINE (IMPROVED)
# ==========================================
synthetic_data = []

print(f"\n🚀 Generating {SAMPLES_TO_GENERATE} synthetic samples with calibrated parameters...")

for i in range(SAMPLES_TO_GENERATE):
    # --- A. SIMULATE PARAMETERS ---
    # Random Day: Pick any float between 0.0 and 14.0
    day = np.random.uniform(0, 14)
    
    # Assign to a synthetic batch (create 10 virtual batches for variety)
    virtual_batch = (i % 10) + 1
    
    # --- B. USE HYBRID APPROACH: Real Pattern + Decay Model ---
    # Strategy: Start from real data pattern, then apply decay
    
    # Find closest real day measurement to interpolate from
    closest_day = min(day_patterns.keys(), key=lambda x: abs(x - day))
    base_pattern = day_patterns[closest_day].copy()
    
    # Add batch-specific characteristics (use one of the real batch templates)
    if len(batch_templates) > 0:
        reference_batch = list(batch_templates.keys())[i % len(batch_templates)]
        batch_signature = batch_templates[reference_batch]
        # Blend: 60% day pattern + 40% batch signature
        base_pattern = 0.6 * base_pattern + 0.4 * batch_signature
    
    # Random Decay Rate: Some oranges rot slightly faster/slower
    k = np.random.normal(AVG_DECAY_RATE, DECAY_VARIANCE)
    k = max(0.01, k)
    
    # Apply exponential decay from closest day pattern
    day_difference = day - closest_day
    decay_factor = np.exp(-k * abs(day_difference))
    
    # Random Initial Quality variation
    initial_conc_variation = np.random.normal(1.0, 0.03)  # Reduced from 0.05
    
    # Create the base signal from real pattern + decay
    simulated_signal = base_pattern * decay_factor * initial_conc_variation
    
    # --- C. APPLY CALIBRATED SENSOR IMPERFECTIONS ---
    # 1. Baseline Drift (Shift signal up/down) - calibrated from real data
    drift = np.random.uniform(-DRIFT_RANGE, DRIFT_RANGE)
    simulated_signal += drift
    
    # 2. Realistic Noise - calibrated from real measurements
    noise = np.random.normal(0, NOISE_LEVEL, len(template_signal))
    simulated_signal += noise
    
    # 3. Time Shift (Shift signal left/right) - reduced for realism
    shift_amount = np.random.randint(-TIME_SHIFT_MAX, TIME_SHIFT_MAX)
    simulated_signal = shift(simulated_signal, shift_amount, mode='nearest')
    
    # 4. Add slight non-linear effects (real sensors are not perfectly linear)
    if np.random.random() < 0.3:  # 30% of samples get slight non-linearity
        nonlinear_factor = 1.0 + np.random.normal(0, 0.02)
        simulated_signal = simulated_signal * nonlinear_factor
    
    # --- D. FORMATTING ---
    row = {
        'batch': virtual_batch,  # Use batch numbers instead of 'Synthetic'
        'day': round(day, 2),
        'filename': f'syn_batch{virtual_batch}_day{day:.1f}_{i:04d}',
    }
    
    # Add all signal columns (f1...fN)
    for idx, col_name in enumerate(signal_cols):
        row[col_name] = simulated_signal[idx]
        
    synthetic_data.append(row)

# ==========================================
# 4. EXPORT
# ==========================================
# Convert list to DataFrame
df_syn = pd.DataFrame(synthetic_data)

# Combine Real + Synthetic Data
df_final = pd.concat([df, df_syn], ignore_index=True)

# Save to CSV
# Ensure output directory exists
output_dir = os.path.dirname(OUTPUT_FILE)
if output_dir and not os.path.exists(output_dir):
    os.makedirs(output_dir)

df_final.to_csv(OUTPUT_FILE, index=False)

print("\n" + "="*40)
print("✅ GENERATION COMPLETE")
print("="*40)
print(f"Original Real Samples:   {len(df)}")
print(f"Synthetic Samples:       {len(df_syn)}")
print(f"TOTAL DATASET SIZE:      {len(df_final)}")
print(f"Saved to:                {OUTPUT_FILE}")
print("="*40)

