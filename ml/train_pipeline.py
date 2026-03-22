import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib
from ml.preprocessor import text_preprocessing
from ml.embedder import encode

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "complex_transaction_dataset.csv")
ARTEFACTS_DIR = os.path.join(BASE_DIR, "ml", "artefacts")

def train():
    print("Loading Data.......")
    data = pd.read_csv(DATA_PATH)
    
    print("Preprocessing textual data")
    data['cleaned'] = data['description'].apply(text_preprocessing)
    
    print("Generating the embeddings for sentences")
    embeddings = encode(data['cleaned'].tolist())
    
    print("Scalling amount.......")
    data['log_amount'] = np.log1p(data['amount'])
    scaling = StandardScaler()
    print(data['log_amount'].head(5))
    scaled_amount = scaling.fit_transform(data[['log_amount']])
    
    print("Building feature matrix")
    X =np.hstack([embeddings, scaled_amount])
    
    print("Encoding labels")
    encoder = LabelEncoder()
    y = encoder.fit_transform(data['category'])
    print("Splitting the data into train_test")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1,
                                                        stratify=y )
    
    print("Model Training......")
    model = RandomForestClassifier(max_depth=20, n_estimators=100)
    model.fit(X_train, y_train)
    
    print("Evaluating...")
    y_pred = model.predict(X_test)
    print(f"Accuracy Score: {accuracy_score(y_test, y_pred)}")
    print(classification_report(y_test, y_pred, target_names=encoder.classes_))

    print("Saving artefacts...")
    os.makedirs(ARTEFACTS_DIR, exist_ok=True)
    joblib.dump(model, f"{ARTEFACTS_DIR}/model.pkl")
    joblib.dump(scaling, f"{ARTEFACTS_DIR}/scaler.pkl")
    joblib.dump(encoder, f"{ARTEFACTS_DIR}/label_encoder.pkl")
    print("Done. Artefacts saved to ml/artefacts/")

if __name__ == "__main__":
    train()
    