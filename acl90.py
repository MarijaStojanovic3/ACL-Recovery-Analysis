import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simpson

# --- 1. CONFIGURATION ---
user_profile = os.environ['USERPROFILE']
# Make sure this folder name matches your desktop folder exactly!
folder_path = os.path.join(user_profile, 'OneDrive', 'Desktop', 'acl90')

def clean_process(data_series, time_series):
    """Clean data, rectify, and create linear envelope"""
    # Remove NaN values
    combined = pd.DataFrame({'sig': data_series, 't': time_series}).dropna()
    if combined.empty:
        return None
    
    t = combined['t'].values
    sig = combined['sig'].values
    
    # Rectification (Absolute value)
    rectified = np.abs(sig)
    
    # Linear Envelope (Smoothing)
    envelope = pd.Series(rectified).rolling(window=100, center=True).mean().fillna(0)
    
    # Metrics
    peak = np.max(envelope)
    # Total Work using Simpson's rule (more accurate than trapezoid)
    work = simpson(y=envelope.values, x=t)
    
    return {'peak': peak, 'work': work, 'env': envelope, 't': t}

def run_final_master_pipeline():
    print(">>> Initializing Biomechanical Analysis...")
    
    # Define required files
    f_names = {
        'inv': 'patient_iso90_inv.csv',
        'inv_t': 'patient_iso90_inv_time.csv',
        'uninv': 'patient_iso90_uninv.csv',
        'uninv_t': 'patient_iso90_uninv_time.csv'
    }

    # Load dataframes
    try:
        df_inv = pd.read_csv(os.path.join(folder_path, f_names['inv']))
        df_inv_t = pd.read_csv(os.path.join(folder_path, f_names['inv_t']))
        df_uninv = pd.read_csv(os.path.join(folder_path, f_names['uninv']))
        df_uninv_t = pd.read_csv(os.path.join(folder_path, f_names['uninv_t']))
    except Exception as e:
        print(f"CRITICAL ERROR: Could not load files. Check path or filenames.\n{e}")
        return

    final_results = []
    
    # Iterate through columns (assuming each column is a participant)
    for i in range(df_inv.shape[1]):
        p_name = df_inv.columns[i]
        
        # Process Involved (Surgical) Limb
        res_inv = clean_process(df_inv.iloc[:, i], df_inv_t.iloc[:, i] if i < df_inv_t.shape[1] else df_inv_t.iloc[:, 0])
        
        # Process Uninvolved (Healthy) Limb
        res_uninv = clean_process(df_uninv.iloc[:, i], df_uninv_t.iloc[:, i] if i < df_uninv_t.shape[1] else df_uninv_t.iloc[:, 0])
        
        if res_inv and res_uninv:
            # Calculate LSI (Limb Symmetry Index)
            lsi_peak = (res_inv['peak'] / res_uninv['peak']) * 100
            lsi_work = (res_inv['work'] / res_uninv['work']) * 100
            
            final_results.append({
                'Participant': p_name,
                'LSI_Peak_%': round(lsi_peak, 2),
                'LSI_Work_%': round(lsi_work, 2),
                'Deficit': 'YES' if lsi_peak < 90 else 'NO'
            })
            print(f"Analysis Complete: {p_name} | LSI: {lsi_peak:.1f}%")

    # Save to Excel-ready CSV
    if final_results:
        summary_df = pd.DataFrame(final_results)
        save_path = os.path.join(folder_path, 'RESEARCH_SUMMARY_LSI.csv')
        summary_df.to_csv(save_path, index=False)
        print(f"\n" + "="*50)
        print(f"SUCCESS: Summary saved to {save_path}")
        print(f"Group Average LSI: {summary_df['LSI_Peak_%'].mean():.2f}%")
        print("="*50)

        # Plot the last participant for visual verification
        plt.figure(figsize=(12, 5))
        plt.plot(res_inv['t'], res_inv['env'], label='Involved (Surgical)', color='red', linewidth=2)
        plt.plot(res_uninv['t'], res_uninv['env'], label='Uninvolved (Healthy)', color='blue', linewidth=2)
        plt.fill_between(res_inv['t'], res_inv['env'], color='red', alpha=0.1)
        plt.title(f'Final Biomechanical Comparison: {p_name}', fontsize=14)
        plt.xlabel('Time (s)')
        plt.ylabel('sEMG Amplitude (V)')
        plt.legend()
        plt.grid(True, alpha=0.2)
        plt.show()
    else:
        print("ERROR: No data processed. Check column consistency.")

if __name__ == "__main__":
    run_full_research_analysis = run_final_master_pipeline()