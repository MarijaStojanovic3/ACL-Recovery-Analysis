import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

# 1. Loading the Excel file you just created
try:
   
    df = pd.read_excel('ACL_Research_Results.xlsx')
    print("✅ File loaded successfully!")
except FileNotFoundError:
    print("❌ Error: Could not find 'ACL_Research_Results.xlsx'. Make sure the file is in the same folder.")
    exit()

# 2. Data Cleaning: Remove extreme outliers (above 200% LSI)
# This removes measurements where an electrode might have slipped or noise was too high
df_clean = df[df['LSI'] < 200].copy()

print("\n--- STATISTICAL ANALYSIS (Cleaned Data) ---")
for speed in df_clean['Speed'].unique():
    patients = df_clean[(df_clean['Cohort'] == 'Patient') & (df_clean['Speed'] == speed)]['LSI']
    healthy = df_clean[(df_clean['Cohort'] == 'Healthy') & (df_clean['Speed'] == speed)]['LSI']
    
    t_stat, p_val = ttest_ind(patients, healthy)
    print(f"Speed {speed}:")
    print(f"  - Average Patient LSI: {patients.mean():.2f}%")
    print(f"  - Average Healthy LSI: {healthy.mean():.2f}%")
    print(f"  - P-value: {p_val:.4f} ({'Significant' if p_val < 0.05 else 'Not significant'})\n")

# 3. Final Research Visualization
plt.figure(figsize=(10, 6))
sns.set_context("talk")
# Swarmplot showing individual subjects + Boxplot for averages
sns.boxplot(x='Speed', y='LSI', hue='Cohort', data=df_clean, palette="Set2", showfliers=False)
sns.swarmplot(x='Speed', y='LSI', hue='Cohort', data=df_clean, dodge=True, color=".25", alpha=0.6)

plt.axhline(90, color='red', linestyle='--', label='90% Clinical Threshold')
plt.title('Final LSI Comparison: Patients vs Healthy Controls')
plt.ylabel('Limb Symmetry Index (%)')
plt.ylim(0, 180) 
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

# Save the plot automatically
plt.savefig('Final_LSI_Plot.png', dpi=300)
print("✅ Plot saved as 'Final_LSI_Plot.png'")

plt.show()
