# Smart Crop Advisor — Final Features (After All Steps)

This file is a **feature checklist** for what the Smart Crop Advisor project will contain after you complete all steps (data prep → EDA → training → Streamlit app).

---

## Current progress (what’s done vs pending)
- **Done**
  - Step 1: project scaffold (`app.py`, `train_model.py`, `requirements.txt`, `README.md`, `notebooks/`)
  - Step 2: dataset prepared → `[data/crop_data.csv](data/crop_data.csv)` (with `soil_type`, `organic_matter`)
  - Step 3: notebook file created → `[notebooks/smart_crop_advisor.ipynb](notebooks/smart_crop_advisor.ipynb)` (ready to run)
  - Model evaluation run (4 models) → **best model found: RandomForest**

- **Pending**
  - Step 4: implement final `[train_model.py](train_model.py)` (train RandomForest + save `crop_model.pkl`, `soil_encoder.pkl`)
  - Step 5: build final `[app.py](app.py)` (weather + prediction + market panel)
  - Step 7: improve `[README.md](README.md)` with final run instructions (after Step 4/5)

---

## Data layer features
- **Input datasets**
  - `[data/Crop_recommendation.csv](data/Crop_recommendation.csv)` (Kaggle)
  - `[data/market_demand.csv](data/market_demand.csv)` (seed market file)

- **Prepared training dataset**
  - Generates `[data/crop_data.csv](data/crop_data.csv)` with the original Kaggle columns plus:
    - **`soil_type`** (categorical)
      - Created using a Bihar-inspired weighted distribution:
        - alluvial 70%
        - loamy 15%
        - clay 10%
        - sandy 5%
    - **`organic_matter`** (numeric)
      - Generated using `np.random.uniform()` by soil range and rounded to **2 decimals**:
        - sandy: 0.5–1.5
        - alluvial: 1.0–3.0
        - loamy: 1.5–4.0
        - clay: 2.0–5.0
  - Uses a **fixed random seed** so results are reproducible.

---

## Notebook (learning) features
Notebook: `[notebooks/smart_crop_advisor.ipynb](notebooks/smart_crop_advisor.ipynb)`

- **Problem statement** focused on Bihar farmers and practical decision-making.
- **Data creation explanation**
  - Shows original dataset overview
  - Shows new columns added (`soil_type`, `organic_matter`) and explains logic
- **EDA (Exploratory Data Analysis)**
  - Crop (`label`) distribution plot
  - Soil distribution plot
  - Correlation heatmap (numeric features)
  - Each plot explained in markdown
- **Feature engineering**
  - Encodes `soil_type` using **`LabelEncoder`**
- **Train/test split evaluation**
  - Uses `train_test_split(test_size=0.2, random_state=42, stratify=y)`
  - Prints **train vs test accuracy** to understand **underfitting vs overfitting**
- **4-model comparison**
  - Logistic Regression
  - Decision Tree
  - Random Forest
  - Gradient Boosting
  - For each model:
    - Train
    - Predict
    - Accuracy + classification report (test set)
- **Model selection**
  - Selects the best model primarily using **test accuracy**
  - Uses train-vs-test gap as a simple overfit signal
- **Export artifacts**
  - Saves:
    - `[crop_model.pkl](crop_model.pkl)`
    - `[soil_encoder.pkl](soil_encoder.pkl)`

---

## Training script features
Script: `[train_model.py](train_model.py)`

- Loads `[data/crop_data.csv](data/crop_data.csv)`
- Encodes `soil_type` with `LabelEncoder`
- Splits into train/test (same parameters as notebook)
- Trains the final chosen model (expected best: **RandomForest** based on evaluation)
- Prints:
  - Train accuracy
  - Test accuracy
  - Classification report
- Saves:
  - `[crop_model.pkl](crop_model.pkl)`
  - `[soil_encoder.pkl](soil_encoder.pkl)`

---

## Streamlit application (UI) features
App: `[app.py](app.py)`

### UI + inputs
- Title: `st.title("🌾 Smart Crop Advisor")`
- Input widgets for:
  - **N, P, K**
  - **temperature** (auto-filled from weather; editable)
  - **humidity** (auto-filled from weather; editable)
  - **pH**
  - **rainfall** (manual input by default)
  - **soil_type** (dropdown)
  - **organic_matter**
  - **city** (used for weather lookup)

### Weather integration (city-based)
- `get_weather()` feature:
  - City → **geocoding** → latitude/longitude
  - Calls weather API to return:
    - **temperature**
    - **humidity**
  - Uses try/except fallback values if API fails:
    - **(28°C, 75%)**

### Prediction + confidence
- Loads:
  - `[crop_model.pkl](crop_model.pkl)`
  - `[soil_encoder.pkl](soil_encoder.pkl)`
  - `[data/market_demand.csv](data/market_demand.csv)`
- On button click:
  - Encodes soil type using the saved encoder
  - Predicts crop using the trained model
  - Computes confidence using `predict_proba()` (top-class probability)
- Shows:
  - Crop name (prominent)
  - Confidence percentage
  - Progress bar

### Market insights panel
- Looks up the predicted crop in `[data/market_demand.csv](data/market_demand.csv)`
- Displays:
  - demand_level (mapped to indicator)
    - High → 🟢
    - Medium → 🟡
    - Low → 🔴
  - price_per_kg
  - buyer_type
  - buyer_location

---

## Run experience (end-to-end)
- **Step order you can run**
  - Generate data: `python prepare_data.py`
  - Train model: `python train_model.py`
  - Run app: `streamlit run app.py`
- **Goal**
  - Notebook teaches the pipeline
  - Script reproduces training and exports artifacts
  - App gives real-time predictions with weather + market context

