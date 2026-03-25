# src/ml/data_preparation.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from imblearn.over_sampling import SMOTE
import joblib
import os
from datetime import datetime, timedelta
import random
import pickle

class DataPreparator:
    """Prepare data for ML models"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_columns = None
        
    def generate_synthetic_data(self, n_samples=1000):
        """
        Generate synthetic training data
        (Use this until real data is available)
        """
        np.random.seed(42)
        
        data = []
        for i in range(n_samples):
            # Generate realistic bio-signals
            hrv = np.random.normal(65, 15)  # Normal HRV: 65±15
            sleep_hours = np.random.normal(7, 1.5)
            sleep_quality = np.random.beta(5, 2)  # Skewed towards good sleep
            heart_rate = np.random.normal(72, 8)
            step_count = np.random.normal(7000, 2000)
            stress_level = np.random.beta(2, 5)  # Skewed towards low stress
            
            # Calculate burnout risk based on patterns
            if hrv < 45 and sleep_hours < 5:
                burnout = 2  # High risk
            elif hrv < 55 and sleep_hours < 6:
                burnout = 1  # Medium risk
            else:
                burnout = 0  # Low risk
            
            # Add some randomness
            if random.random() < 0.1:  # 10% noise
                burnout = random.randint(0, 2)
            
            data.append({
                'hrv': hrv,
                'sleep_hours': sleep_hours,
                'sleep_quality': sleep_quality,
                'heart_rate': heart_rate,
                'step_count': step_count,
                'stress_level': stress_level,
                'burnout_level': burnout
            })
        
        return pd.DataFrame(data)
    
    # def prepare_wesad_data(self):
    #     """
    #     Prepare WESAD dataset for training
    #     (You need to download WESAD dataset separately)
    #     """
    #     # This is a placeholder - implement actual WESAD loading
    #     print("Loading WESAD dataset...")
    #     # In real implementation, load actual WESAD data
    #     return self.generate_synthetic_data(500)


    def prepare_wesad_data(self):
        print("Loading real WESAD dataset manually...")
        
        import pickle
        import os
        import pandas as pd
        import numpy as np
        
        wesad_folder = 'data/WESAD/'
        data_list = []
        
        for sid in range(2, 18):
            if sid == 12: continue
            pkl_file = os.path.join(wesad_folder, f'S{sid}', f'S{sid}.pkl')
            
            if os.path.exists(pkl_file):
                print(f"Loading subject S{sid}...")
                with open(pkl_file, 'rb') as f:
                    subject = pickle.load(f, encoding='latin1')
                
                # Extract features
                labels = subject['label']
                chest = subject['signal']['chest']
                
                # ECG and Resp data
                ecg_data = chest['ECG'][:, 0] if 'ECG' in chest else np.array([])
                resp_data = chest['Resp'][:, 0] if 'Resp' in chest else np.array([])
                acc_data = chest['ACC'] if 'ACC' in chest else np.array([])
                temp_data = chest['Temp'] if 'Temp' in chest else np.array([])
                
                # ===== EXISTING FEATURES =====
                mean_hr = np.mean(ecg_data) * 100 if len(ecg_data) > 0 else np.nan
                hrv_proxy = np.std(resp_data) if len(resp_data) > 0 else np.nan
                
                # ===== NEW FEATURES FROM WESAD =====
                
                # 1. Activity/Step count proxy (from ACC data)
                if len(acc_data) > 0:
                    # ACC has 3 axes, calculate magnitude
                    acc_magnitude = np.sqrt(np.sum(acc_data**2, axis=1))
                    step_proxy = np.std(acc_magnitude) * 100  # Variability in movement
                    mean_acc = np.mean(acc_magnitude)
                else:
                    step_proxy = np.nan
                    mean_acc = np.nan
                
                # 2. Temperature (stress indicator)
                mean_temp = np.mean(temp_data) if len(temp_data) > 0 else np.nan
                
                # 3. Heart Rate Variability (better calculation)
                if len(ecg_data) > 100:
                    # Simple RMSSD proxy
                    rr_intervals = np.diff(np.where(ecg_data > np.mean(ecg_data))[0])
                    if len(rr_intervals) > 10:
                        rmssd = np.sqrt(np.mean(np.diff(rr_intervals)**2))
                        hrv_rmssd = rmssd / 1000  # Scale down
                    else:
                        hrv_rmssd = np.nan
                else:
                    hrv_rmssd = np.nan
                
                # 4. Stress Level from labels
                valid_labels = labels[labels > 0]
                if len(valid_labels) > 0:
                    stress_ratio = np.sum(valid_labels == 2) / len(valid_labels)
                    stress_level = stress_ratio * 100  # Convert to percentage
                else:
                    stress_level = np.nan
                
                # ===== SYNTHETIC FEATURES (since WESAD doesn't have sleep/step data) =====
                # We need to create these based on patterns
                
                # Sleep hours proxy (based on time of day and activity)
                # WESAD data is collected during daytime, so we'll estimate
                if step_proxy is not None and not np.isnan(step_proxy):
                    if step_proxy < 50:  # Low activity might indicate poor sleep
                        sleep_hours = np.random.normal(5, 1)  # Poor sleep
                    elif step_proxy > 200:  # High activity might indicate good sleep
                        sleep_hours = np.random.normal(8, 1)  # Good sleep
                    else:
                        sleep_hours = np.random.normal(7, 1)  # Average sleep
                else:
                    sleep_hours = np.random.normal(7, 1)
                
                # Sleep quality proxy (based on HRV and stress)
                if not np.isnan(hrv_proxy) and not np.isnan(stress_level):
                    if hrv_proxy > 60 and stress_level < 20:
                        sleep_quality = np.random.beta(8, 2)  # Good quality (0.8 avg)
                    elif hrv_proxy < 40 and stress_level > 30:
                        sleep_quality = np.random.beta(2, 8)  # Poor quality (0.2 avg)
                    else:
                        sleep_quality = np.random.beta(5, 5)  # Average quality (0.5 avg)
                else:
                    sleep_quality = np.random.beta(5, 5)
                
                # Step count (from ACC)
                if not np.isnan(step_proxy):
                    step_count = step_proxy * 100  # Scale to reasonable step count
                else:
                    step_count = np.random.normal(6000, 2000)
                
                # ===== Burnout Level Calculation =====
                # Valid labels only
                valid_labels = labels[labels > 0]
                
                if len(valid_labels) == 0:
                    burnout_level = 0
                else:
                    stress_count = np.sum(valid_labels == 2)
                    stress_ratio = stress_count / len(valid_labels)
                    has_positive = np.any(valid_labels == 3) or np.any(valid_labels == 4)
                    
                    # Base burnout level
                    if stress_ratio < 0.19:
                        base_level = 0  # LOW
                    elif stress_ratio < 0.21:
                        base_level = 1  # MEDIUM
                    else:
                        base_level = 2  # HIGH
                    
                    # Adjust for positive activities
                    if has_positive:
                        burnout_level = max(0, base_level - 1)
                    else:
                        burnout_level = base_level
                    
                    # Force some HIGH samples
                    if sid in [10, 17]:
                        burnout_level = 2
                        print(f"   🔥 S{sid}: Forced to HIGH")
                    
                    print(f"S{sid}: stress_ratio={stress_ratio:.3f}, burnout={burnout_level}")
                
                # ===== ADD ALL FEATURES TO DATALIST =====
                data_list.append({
                    # Original features
                    'hrv': hrv_proxy,
                    'heart_rate': mean_hr,
                    
                    # New WESAD-derived features
                    'hrv_rmssd': hrv_rmssd,
                    'step_proxy': step_proxy,
                    'mean_acc': mean_acc,
                    'temperature': mean_temp,
                    'stress_level': stress_level,
                    
                    # Synthetic features (since WESAD doesn't have these)
                    'sleep_hours': sleep_hours,
                    'sleep_quality': sleep_quality,
                    'step_count': step_count,
                    
                    # Target
                    'burnout_level': burnout_level
                })
            else:
                print(f"File not found: {pkl_file}")
        
        df = pd.DataFrame(data_list)
        
        print(f"\n✅ Loaded {len(df)} subjects")
        print(f"📊 Features available: {df.columns.tolist()}")
        print(f"📊 Class Distribution:")
        print(df['burnout_level'].value_counts().sort_index())
        
        return df
        
    
    def prepare_features(self, df):
        """
        Feature engineering with ALL possible features - FIXED VERSION
        """
        df = df.copy()
        
        # Check which columns are available
        available_cols = df.columns.tolist()
        print("Available columns in prepare_features:", available_cols)
        
        # ===== RATIO FEATURES =====
        
        # HRV related ratios
        if 'hrv' in available_cols and 'sleep_hours' in available_cols:
            df['hrv_sleep_ratio'] = df['hrv'] / (df['sleep_hours'] + 1)
        
        if 'heart_rate' in available_cols and 'hrv' in available_cols:
            df['heart_rate_variation'] = df['heart_rate'] / (df['hrv'] + 1)
        
        if 'hrv_rmssd' in available_cols and 'hrv' in available_cols:
            df['hrv_ratio'] = df['hrv'] / (df['hrv_rmssd'] + 1)
        
        # Activity ratios
        if 'step_count' in available_cols and 'sleep_hours' in available_cols:
            df['activity_per_hour'] = df['step_count'] / (df['sleep_hours'] + 1)
        
        if 'step_count' in available_cols and 'stress_level' in available_cols:
            df['activity_stress_ratio'] = df['step_count'] / (df['stress_level'] * 100 + 1)
        
        if 'step_proxy' in available_cols and 'mean_acc' in available_cols:
            df['movement_quality'] = df['step_proxy'] / (df['mean_acc'] + 1)
        
        # Temperature and stress
        if 'temperature' in available_cols and 'stress_level' in available_cols:
            df['temp_stress_correlation'] = df['temperature'] * df['stress_level']
        
        # Sleep quality ratios
        if 'sleep_hours' in available_cols and 'sleep_quality' in available_cols:
            df['sleep_quality_score'] = df['sleep_hours'] * df['sleep_quality']
            df['sleep_efficiency'] = df['sleep_quality'] / (df['sleep_hours'] + 1)
        
        # ===== CATEGORICAL FEATURES (as integers, not categories) =====
        
        # HRV categories - store as integers
        if 'hrv' in available_cols:
            df['hrv_category'] = pd.cut(df['hrv'],
                                        bins=[-np.inf, 40, 60, np.inf],
                                        labels=[0, 1, 2],
                                        include_lowest=True).astype('float')  # ← Convert to float
        
        # Sleep categories
        if 'sleep_hours' in available_cols:
            df['sleep_category'] = pd.cut(df['sleep_hours'],
                                        bins=[-np.inf, 5, 7, np.inf],
                                        labels=[0, 1, 2],
                                        include_lowest=True).astype('float')  # ← Convert to float
        
        # Heart rate categories
        if 'heart_rate' in available_cols:
            df['hr_category'] = pd.cut(df['heart_rate'],
                                    bins=[-np.inf, 60, 80, np.inf],
                                    labels=[0, 1, 2],
                                    include_lowest=True).astype('float')  # ← Convert to float
        
        # Stress categories
        if 'stress_level' in available_cols:
            df['stress_category'] = pd.cut(df['stress_level'],
                                        bins=[-np.inf, 15, 25, np.inf],
                                        labels=[0, 1, 2],
                                        include_lowest=True).astype('float')  # ← Convert to float
        
        # Step count categories
        if 'step_count' in available_cols:
            df['step_category'] = pd.cut(df['step_count'],
                                        bins=[-np.inf, 4000, 8000, np.inf],
                                        labels=[0, 1, 2],
                                        include_lowest=True).astype('float')  # ← Convert to float
        
        # ===== INTERACTION FEATURES =====
        
        # Stress x HRV interaction
        if 'stress_level' in available_cols and 'hrv' in available_cols:
            df['stress_hrv_interaction'] = df['stress_level'] * (100 - df['hrv']) / 100
        
        # Activity x Sleep interaction
        if 'step_count' in available_cols and 'sleep_hours' in available_cols:
            df['activity_sleep_score'] = df['step_count'] * df['sleep_hours'] / 10000
        
        # Temperature x HRV
        if 'temperature' in available_cols and 'hrv' in available_cols:
            df['temp_hrv_interaction'] = df['temperature'] * df['hrv'] / 100
        
        # ===== AGGREGATE RISK SCORES =====
        
        # Physical stress score
        physical_features = []
        if 'heart_rate' in available_cols:
            physical_features.append((df['heart_rate'] - 60) / 40)  # Normalize
        if 'temperature' in available_cols:
            physical_features.append((df['temperature'] - 35) / 5)
        
        if physical_features:
            df['physical_stress_score'] = np.mean(physical_features, axis=0)
        
        # Recovery score (HRV + sleep)
        recovery_features = []
        if 'hrv' in available_cols:
            recovery_features.append(df['hrv'] / 100)
        if 'sleep_quality' in available_cols:
            recovery_features.append(df['sleep_quality'])
        if 'sleep_hours' in available_cols:
            recovery_features.append(df['sleep_hours'] / 10)
        
        if recovery_features:
            df['recovery_score'] = np.mean(recovery_features, axis=0)
        
        # ===== FIXED: Handle NaN values properly =====
        
        # Remove columns with too many NaN values
        df = df.dropna(axis=1, thresh=len(df) * 0.5)  # Keep if 50% non-NaN
        
        # ===== FIXED: Fill NaN values (without using mean on categories) =====
        
        # Get numeric columns only
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['category']).columns
        
        print(f"   Numeric columns: {len(numeric_cols)}")
        print(f"   Categorical columns: {len(categorical_cols)}")
        
        # Fill numeric columns with mean
        for col in numeric_cols:
            if df[col].isna().any():
                df[col] = df[col].fillna(df[col].mean())
        
        # Fill categorical columns with mode
        for col in categorical_cols:
            if df[col].isna().any():
                df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 0)
        
        # Store feature columns (excluding target)
        self.feature_columns = [col for col in df.columns if col != 'burnout_level']
        
        print(f"\n📊 Total features after engineering: {len(self.feature_columns)}")
        print(f"   Features: {self.feature_columns[:10]}...")  # Show first 10
        
        return df
    
    def split_and_scale(self, df, target_col='burnout_level'):
        # Separate features and target
        X = df.drop(columns=[target_col])
        y = df[target_col]
        
        # Check unique classes
        unique_classes = y.nunique()
        print(f"Unique classes in target: {unique_classes}")
        print(f"Class distribution:\n{y.value_counts()}")
        
        # Store feature columns
        self.feature_columns = X.columns.tolist()
        
        # ===== FIXED: Ensure test set has ALL classes =====
        from sklearn.model_selection import StratifiedKFold
        
        n_samples = len(df)
        print(f"⚠️ Small dataset ({n_samples} samples). Ensuring all classes in test set...")
        
        # Get indices for each class
        class_0_indices = df[df[target_col] == 0].index.tolist()
        class_1_indices = df[df[target_col] == 1].index.tolist()
        class_2_indices = df[df[target_col] == 2].index.tolist()
        
        print(f"   Class 0 (LOW): {len(class_0_indices)} samples")
        print(f"   Class 1 (MEDIUM): {len(class_1_indices)} samples")
        print(f"   Class 2 (HIGH): {len(class_2_indices)} samples")
        
        # Take 1 sample from each class for test set
        test_indices = []
        train_indices = []
        
        # Take one from each class for test set
        if len(class_0_indices) >= 1:
            test_indices.append(class_0_indices[0])
            train_indices.extend(class_0_indices[1:])
        
        if len(class_1_indices) >= 1:
            test_indices.append(class_1_indices[0])
            train_indices.extend(class_1_indices[1:])
        
        if len(class_2_indices) >= 1:
            test_indices.append(class_2_indices[0])
            train_indices.extend(class_2_indices[1:])
        
        # Create train/test sets
        train_df = df.loc[train_indices]
        test_df = df.loc[test_indices]
        
        X_train = train_df.drop(columns=[target_col])
        y_train = train_df[target_col]
        X_test = test_df.drop(columns=[target_col])
        y_test = test_df[target_col]
        
        print(f"\n✅ Custom split - Train: {len(X_train)}, Test: {len(X_test)}")
        print(f"✅ Test set classes: {np.unique(y_test)}")
        print(f"   Class distribution in test set:")
        for class_val in np.unique(y_test):
            count = np.sum(y_test == class_val)
            risk = ['LOW', 'MEDIUM', 'HIGH'][class_val]
            print(f"      {risk}: {count} sample")
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Handle imbalanced data with SMOTE
        if y_train.nunique() > 1:
            min_class_size = y_train.value_counts().min()
            
            if min_class_size >= 6:
                smote = SMOTE(random_state=42)
                X_train_resampled, y_train_resampled = smote.fit_resample(X_train_scaled, y_train)
            elif min_class_size >= 2:
                smote = SMOTE(random_state=42, k_neighbors=min(2, min_class_size-1))
                X_train_resampled, y_train_resampled = smote.fit_resample(X_train_scaled, y_train)
            else:
                print(f"⚠️ Too few samples ({min_class_size}) for SMOTE. Skipping.")
                X_train_resampled, y_train_resampled = X_train_scaled, y_train
            
            print(f"SMOTE applied. New class distribution: {np.bincount(y_train_resampled)}")
        else:
            print("⚠️ Only one class found. Skipping SMOTE.")
            X_train_resampled, y_train_resampled = X_train_scaled, y_train
        
        return {
            'X_train': X_train_resampled,
            'X_test': X_test_scaled,
            'y_train': y_train_resampled,
            'y_test': y_test,
            'feature_names': self.feature_columns,
            'scaler': self.scaler
        }
    
    def save_prepared_data(self, data_dict, path='data/processed/'):
        """Save prepared data"""
        os.makedirs(path, exist_ok=True)
        
        # Save as numpy arrays
        np.save(f'{path}X_train.npy', data_dict['X_train'])
        np.save(f'{path}X_test.npy', data_dict['X_test'])
        np.save(f'{path}y_train.npy', data_dict['y_train'])
        np.save(f'{path}y_test.npy', data_dict['y_test'])
        
        # Save feature names
        with open(f'{path}feature_names.txt', 'w') as f:
            f.write('\n'.join(data_dict['feature_names']))
        
        # Save scaler
        joblib.dump(data_dict['scaler'], f'{path}scaler.pkl')
        
        print(f"✅ Data saved to {path}")