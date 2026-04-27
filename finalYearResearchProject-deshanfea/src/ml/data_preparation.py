# src/ml/data_preparation.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from imblearn.over_sampling import SMOTE
import joblib
import os
import pickle

# Features that come directly from WESAD sensor data
WESAD_REAL_FEATURES = [
    'hrv',           # std of respiration signal (proxy)
    'heart_rate',    # mean ECG * 100
    'hrv_rmssd',     # RMSSD from R-R intervals
    'step_proxy',    # std of accelerometer magnitude
    'mean_acc',      # mean accelerometer magnitude
    'temperature',   # chest temperature
    'stress_level',  # ratio of stress labels in session
]

# Features that are synthetically generated (WESAD has no sleep/step data)
SYNTHETIC_FEATURES = [
    'sleep_hours',
    'sleep_quality',
    'step_count',
]


class DataPreparator:
    """Prepare data for ML models"""

    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_columns = None

    def generate_synthetic_data(self, n_samples=1000):
        """Generate fully synthetic training data (for testing only)"""
        np.random.seed(42)

        data = []
        for _ in range(n_samples):
            hrv = np.random.normal(65, 15)
            sleep_hours = np.random.normal(7, 1.5)
            sleep_quality = np.random.beta(5, 2)
            heart_rate = np.random.normal(72, 8)
            step_count = np.random.normal(7000, 2000)
            stress_level = np.random.beta(2, 5)

            if hrv < 45 and sleep_hours < 5:
                burnout = 2
            elif hrv < 55 and sleep_hours < 6:
                burnout = 1
            else:
                burnout = 0

            if np.random.random() < 0.1:
                burnout = np.random.randint(0, 3)

            data.append({
                'hrv': hrv, 'sleep_hours': sleep_hours,
                'sleep_quality': sleep_quality, 'heart_rate': heart_rate,
                'step_count': step_count, 'stress_level': stress_level,
                'burnout_level': burnout, 'data_source': 'synthetic',
            })

        return pd.DataFrame(data)

    # ------------------------------------------------------------------
    # WESAD loader — real features only, synthetic clearly tagged
    # ------------------------------------------------------------------

    def prepare_wesad_data(self):
        """Load WESAD dataset. Real sensor features are extracted directly;
        synthetic proxies (sleep, step_count) are clearly marked."""
        print("Loading real WESAD dataset...")

        wesad_folder = 'data/WESAD/'
        data_list = []

        for sid in range(2, 18):
            if sid == 12:
                continue
            pkl_file = os.path.join(wesad_folder, f'S{sid}', f'S{sid}.pkl')

            if not os.path.exists(pkl_file):
                print(f"  File not found: {pkl_file}")
                continue

            print(f"  Loading subject S{sid}...")
            with open(pkl_file, 'rb') as f:
                subject = pickle.load(f, encoding='latin1')

            labels = subject['label']
            chest = subject['signal']['chest']

            ecg_data = chest['ECG'][:, 0] if 'ECG' in chest else np.array([])
            resp_data = chest['Resp'][:, 0] if 'Resp' in chest else np.array([])
            acc_data = chest['ACC'] if 'ACC' in chest else np.array([])
            temp_data = chest['Temp'] if 'Temp' in chest else np.array([])

            # ---- REAL features from WESAD sensors ----
            mean_hr = np.mean(ecg_data) * 100 if len(ecg_data) > 0 else np.nan
            hrv_proxy = np.std(resp_data) if len(resp_data) > 0 else np.nan

            if len(acc_data) > 0:
                acc_magnitude = np.sqrt(np.sum(acc_data ** 2, axis=1))
                step_proxy = np.std(acc_magnitude) * 100
                mean_acc = np.mean(acc_magnitude)
            else:
                step_proxy = np.nan
                mean_acc = np.nan

            mean_temp = np.mean(temp_data) if len(temp_data) > 0 else np.nan

            if len(ecg_data) > 100:
                rr_intervals = np.diff(np.where(ecg_data > np.mean(ecg_data))[0])
                if len(rr_intervals) > 10:
                    hrv_rmssd = np.sqrt(np.mean(np.diff(rr_intervals) ** 2)) / 1000
                else:
                    hrv_rmssd = np.nan
            else:
                hrv_rmssd = np.nan

            valid_labels = labels[labels > 0]
            if len(valid_labels) > 0:
                stress_ratio = np.sum(valid_labels == 2) / len(valid_labels)
                stress_level = stress_ratio * 100
            else:
                stress_level = np.nan

            # ---- SYNTHETIC proxies (WESAD has no sleep/step data) ----
            if not np.isnan(step_proxy):
                if step_proxy < 50:
                    sleep_hours = np.random.normal(5, 1)
                elif step_proxy > 200:
                    sleep_hours = np.random.normal(8, 1)
                else:
                    sleep_hours = np.random.normal(7, 1)
            else:
                sleep_hours = np.random.normal(7, 1)

            if not np.isnan(hrv_proxy) and not np.isnan(stress_level):
                if hrv_proxy > 60 and stress_level < 20:
                    sleep_quality = np.random.beta(8, 2)
                elif hrv_proxy < 40 and stress_level > 30:
                    sleep_quality = np.random.beta(2, 8)
                else:
                    sleep_quality = np.random.beta(5, 5)
            else:
                sleep_quality = np.random.beta(5, 5)

            step_count = step_proxy * 100 if not np.isnan(step_proxy) else np.random.normal(6000, 2000)

            # ---- Burnout label (derived from WESAD stress protocol) ----
            if len(valid_labels) == 0:
                burnout_level = 0
            else:
                stress_count = np.sum(valid_labels == 2)
                stress_ratio = stress_count / len(valid_labels)
                has_positive = np.any(valid_labels == 3) or np.any(valid_labels == 4)

                if stress_ratio < 0.19:
                    base_level = 0
                elif stress_ratio < 0.21:
                    base_level = 1
                else:
                    base_level = 2

                burnout_level = max(0, base_level - 1) if has_positive else base_level
                print(f"  S{sid}: stress_ratio={stress_ratio:.3f}, burnout={burnout_level}")

            data_list.append({
                # Real WESAD features
                'hrv': hrv_proxy,
                'heart_rate': mean_hr,
                'hrv_rmssd': hrv_rmssd,
                'step_proxy': step_proxy,
                'mean_acc': mean_acc,
                'temperature': mean_temp,
                'stress_level': stress_level,
                # Synthetic proxies
                'sleep_hours': sleep_hours,
                'sleep_quality': sleep_quality,
                'step_count': step_count,
                # Metadata
                'data_source': 'wesad_real',
                # Target
                'burnout_level': burnout_level,
            })

        df = pd.DataFrame(data_list)

        real_count = len([c for c in df.columns if c in WESAD_REAL_FEATURES])
        synth_count = len([c for c in df.columns if c in SYNTHETIC_FEATURES])
        print(f"\n✅ Loaded {len(df)} subjects")
        print(f"📊 Real WESAD features: {real_count}  |  Synthetic proxies: {synth_count}")
        print(f"📊 Class Distribution:\n{df['burnout_level'].value_counts().sort_index()}")

        return df

    # ------------------------------------------------------------------
    # Feature engineering
    # ------------------------------------------------------------------

    def prepare_features(self, df):
        """Engineer features from available columns."""
        df = df.copy()

        # Drop metadata column before modelling
        if 'data_source' in df.columns:
            df = df.drop(columns=['data_source'])

        available = set(df.columns)
        print(f"Available columns: {sorted(available)}")

        # Ratio features
        if {'hrv', 'sleep_hours'} <= available:
            df['hrv_sleep_ratio'] = df['hrv'] / (df['sleep_hours'] + 1)
        if {'heart_rate', 'hrv'} <= available:
            df['heart_rate_variation'] = df['heart_rate'] / (df['hrv'] + 1)
        if {'hrv_rmssd', 'hrv'} <= available:
            df['hrv_ratio'] = df['hrv'] / (df['hrv_rmssd'] + 1)
        if {'step_count', 'sleep_hours'} <= available:
            df['activity_per_hour'] = df['step_count'] / (df['sleep_hours'] + 1)
        if {'step_count', 'stress_level'} <= available:
            df['activity_stress_ratio'] = df['step_count'] / (df['stress_level'] * 100 + 1)
        if {'step_proxy', 'mean_acc'} <= available:
            df['movement_quality'] = df['step_proxy'] / (df['mean_acc'] + 1)
        if {'temperature', 'stress_level'} <= available:
            df['temp_stress_correlation'] = df['temperature'] * df['stress_level']
        if {'sleep_hours', 'sleep_quality'} <= available:
            df['sleep_quality_score'] = df['sleep_hours'] * df['sleep_quality']
            df['sleep_efficiency'] = df['sleep_quality'] / (df['sleep_hours'] + 1)

        # Categorical bins (as float)
        if 'hrv' in available:
            df['hrv_category'] = pd.cut(
                df['hrv'], bins=[-np.inf, 40, 60, np.inf],
                labels=[0, 1, 2], include_lowest=True,
            ).astype('float')
        if 'sleep_hours' in available:
            df['sleep_category'] = pd.cut(
                df['sleep_hours'], bins=[-np.inf, 5, 7, np.inf],
                labels=[0, 1, 2], include_lowest=True,
            ).astype('float')
        if 'heart_rate' in available:
            df['hr_category'] = pd.cut(
                df['heart_rate'], bins=[-np.inf, 60, 80, np.inf],
                labels=[0, 1, 2], include_lowest=True,
            ).astype('float')
        if 'stress_level' in available:
            df['stress_category'] = pd.cut(
                df['stress_level'], bins=[-np.inf, 15, 25, np.inf],
                labels=[0, 1, 2], include_lowest=True,
            ).astype('float')
        if 'step_count' in available:
            df['step_category'] = pd.cut(
                df['step_count'], bins=[-np.inf, 4000, 8000, np.inf],
                labels=[0, 1, 2], include_lowest=True,
            ).astype('float')

        # Interaction features
        if {'stress_level', 'hrv'} <= available:
            df['stress_hrv_interaction'] = df['stress_level'] * (100 - df['hrv']) / 100
        if {'step_count', 'sleep_hours'} <= available:
            df['activity_sleep_score'] = df['step_count'] * df['sleep_hours'] / 10000
        if {'temperature', 'hrv'} <= available:
            df['temp_hrv_interaction'] = df['temperature'] * df['hrv'] / 100

        # Aggregate scores
        physical = []
        if 'heart_rate' in available:
            physical.append((df['heart_rate'] - 60) / 40)
        if 'temperature' in available:
            physical.append((df['temperature'] - 35) / 5)
        if physical:
            df['physical_stress_score'] = np.mean(physical, axis=0)

        recovery = []
        if 'hrv' in available:
            recovery.append(df['hrv'] / 100)
        if 'sleep_quality' in available:
            recovery.append(df['sleep_quality'])
        if 'sleep_hours' in available:
            recovery.append(df['sleep_hours'] / 10)
        if recovery:
            df['recovery_score'] = np.mean(recovery, axis=0)

        # Handle NaN
        df = df.dropna(axis=1, thresh=len(df) * 0.5)

        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isna().any():
                df[col] = df[col].fillna(df[col].mean())

        self.feature_columns = [c for c in df.columns if c != 'burnout_level']
        print(f"\n📊 Total features after engineering: {len(self.feature_columns)}")

        return df

    # ------------------------------------------------------------------
    # Split, scale, SMOTE
    # ------------------------------------------------------------------

    def split_and_scale(self, df, target_col='burnout_level'):
        X = df.drop(columns=[target_col])
        y = df[target_col]

        self.feature_columns = X.columns.tolist()

        print(f"Unique classes: {y.nunique()}")
        print(f"Class distribution:\n{y.value_counts()}")

        # Stratified manual split (small dataset)
        class_indices = {c: df[df[target_col] == c].index.tolist() for c in sorted(y.unique())}

        test_indices, train_indices = [], []
        for cls, indices in class_indices.items():
            if indices:
                test_indices.append(indices[0])
                train_indices.extend(indices[1:])

        X_train = df.loc[train_indices].drop(columns=[target_col])
        y_train = df.loc[train_indices][target_col]
        X_test = df.loc[test_indices].drop(columns=[target_col])
        y_test = df.loc[test_indices][target_col]

        print(f"\n✅ Train: {len(X_train)}, Test: {len(X_test)}")
        print(f"✅ Test classes: {np.unique(y_test)}")

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # SMOTE
        if y_train.nunique() > 1:
            min_class = y_train.value_counts().min()
            if min_class >= 2:
                k = min(5, min_class - 1)
                smote = SMOTE(random_state=42, k_neighbors=k)
                X_train_scaled, y_train = smote.fit_resample(X_train_scaled, y_train)
                print(f"SMOTE applied. New distribution: {np.bincount(y_train)}")
            else:
                print(f"⚠️ Too few samples ({min_class}) for SMOTE. Skipping.")

        return {
            'X_train': X_train_scaled,
            'X_test': X_test_scaled,
            'y_train': y_train,
            'y_test': y_test,
            'feature_names': self.feature_columns,
            'scaler': self.scaler,
        }

    def save_prepared_data(self, data_dict, path='data/processed/'):
        os.makedirs(path, exist_ok=True)
        np.save(f'{path}X_train.npy', data_dict['X_train'])
        np.save(f'{path}X_test.npy', data_dict['X_test'])
        np.save(f'{path}y_train.npy', data_dict['y_train'])
        np.save(f'{path}y_test.npy', data_dict['y_test'])
        with open(f'{path}feature_names.txt', 'w') as f:
            f.write('\n'.join(data_dict['feature_names']))
        joblib.dump(data_dict['scaler'], f'{path}scaler.pkl')
        print(f"✅ Data saved to {path}")
