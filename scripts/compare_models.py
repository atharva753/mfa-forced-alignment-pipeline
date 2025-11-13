import pandas as pd

# Load both quality reports (they're CSV files, not Excel)
model1 = pd.read_csv(r"C:\Users\athar\OneDrive\Documents\mfa_output\alignment_analysis.csv")
model2 = pd.read_csv(r"C:\Users\athar\OneDrive\Documents\mfa_output_english_mfa\alignment_analysis.csv")

print("="*60)
print("ACOUSTIC MODEL COMPARISON")
print("="*60)

print("\nModel 1: english_us_arpa")
print(f"Mean overall likelihood: {model1['overall_log_likelihood'].mean():.2f}")
print(f"Mean phone duration deviation: {model1['phone_duration_deviation'].mean():.2f}")

print("\nModel 2: english_mfa")
print(f"Mean overall likelihood: {model2['overall_log_likelihood'].mean():.2f}")
print(f"Mean phone duration deviation: {model2['phone_duration_deviation'].mean():.2f}")

print("\n" + "="*60)
print("COMPARISON SUMMARY")
print("="*60)

likelihood_diff = model2['overall_log_likelihood'].mean() - model1['overall_log_likelihood'].mean()
deviation_diff = model2['phone_duration_deviation'].mean() - model1['phone_duration_deviation'].mean()

print(f"\nLikelihood difference: {likelihood_diff:+.2f} (positive = Model 2 better)")
print(f"Duration deviation difference: {deviation_diff:+.2f} (negative = Model 2 better)")

if likelihood_diff > 0 and deviation_diff < 0:
    print("\n✓ Model 2 (english_mfa) performs BETTER overall")
elif likelihood_diff < 0 and deviation_diff > 0:
    print("\n✓ Model 1 (english_us_arpa) performs BETTER overall")
else:
    print("\n≈ Models perform SIMILARLY (mixed results)")

print("\nPer-file breakdown:")
print("\nModel 1 (english_us_arpa):")
print(model1[['file', 'overall_log_likelihood', 'phone_duration_deviation']])
print("\nModel 2 (english_mfa):")
print(model2[['file', 'overall_log_likelihood', 'phone_duration_deviation']])

print("="*60)