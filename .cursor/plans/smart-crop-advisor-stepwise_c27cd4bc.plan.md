---
name: smart-crop-advisor-stepwise
overview: "Build Smart Crop Advisor end-to-end in learnable, strict steps: dataset augmentation (soil_type, organic_matter), EDA + modeling with train/test split comparing 4 models, saving the best model/encoder, then a Streamlit app with weather + market insights."
todos:
  - id: step1-setup-structure
    content: Create folders and starter files (app.py, train_model.py, requirements.txt, README.md, notebooks/) matching the agreed structure.
    status: pending
  - id: step2-generate-crop-data
    content: Augment Crop_recommendation with soil_type + organic_matter and save as data/crop_data.csv with reproducible seed and markdown explanation.
    status: pending
  - id: step3-notebook-eda-models
    content: Build notebook with problem statement, data creation explanation, EDA plots, label encoding, 4-model train/test evaluation, comparison, and saving model+encoder.
    status: pending
  - id: step4-train-script
    content: Implement train_model.py to reproduce final training (split, metrics) and save crop_model.pkl + soil_encoder.pkl.
    status: pending
  - id: step5-streamlit-app
    content: Implement app.py with weather fetch (Open-Meteo + fallback), inputs, predict + proba confidence, and market insights panel.
    status: pending
  - id: step6-requirements
    content: Finalize requirements.txt and verify imports/install path.
    status: pending
  - id: step7-readme
    content: Write README with project story, setup, run steps, and future scope.
    status: pending
isProject: false
---

## Goals and constraints
- **Only Python**; Streamlit for UI.
- **Strict sequence**: we complete each step fully, with a clear “done” checkpoint, before moving on.
- Use your existing inputs: `[data/Crop_recommendation.csv](data/Crop_recommendation.csv)` and `[data/market_demand.csv](data/market_demand.csv)`.
- Replace “3 models” with **4-model comparison**: Logistic Regression, Decision Tree, Random Forest, Gradient Boosting.
- Use **train/test split** (and optional cross-validation later) and beginner-friendly metrics.
- Weather integration will be **city-based** (user enters city) to auto-fill `temperature` and `humidity`. `rainfall` stays a manual input by default.

## Final deliverables (what you’ll be able to run)
- **EDA + learning notebook**: `[notebooks/smart_crop_advisor.ipynb](notebooks/smart_crop_advisor.ipynb)`
- **Training script**: `[train_model.py](train_model.py)` generates `[crop_model.pkl](crop_model.pkl)` and `[soil_encoder.pkl](soil_encoder.pkl)`
- **Streamlit app**: `[app.py](app.py)` loads the pickles + `[data/market_demand.csv](data/market_demand.csv)` and serves predictions with confidence + market panel

## Project structure we will create (Step 1)
- Root
  - `[app.py](app.py)`
  - `[train_model.py](train_model.py)`
  - `[crop_model.pkl](crop_model.pkl)` (generated later)
  - `[soil_encoder.pkl](soil_encoder.pkl)` (generated later)
  - `[requirements.txt](requirements.txt)`
  - `[README.md](README.md)`
- `[data/](data/)`
  - `[data/Crop_recommendation.csv](data/Crop_recommendation.csv)` (already present)
  - `[data/market_demand.csv](data/market_demand.csv)` (already present)
  - `[data/crop_data.csv](data/crop_data.csv)` (generated later)
- `[notebooks/](notebooks/)`
  - `[notebooks/smart_crop_advisor.ipynb](notebooks/smart_crop_advisor.ipynb)`

## Step-by-step build sequence (you will tell me “proceed” each time)

### Step 1 — Project setup (files + environment)
- Create folders: `data/`, `notebooks/`
- Add starter files (minimal but runnable placeholders): `app.py`, `train_model.py`, `requirements.txt`, `README.md`
- **Checkpoint**: `python -c "import pandas, numpy, sklearn"` works after installing requirements.

### Step 2 — Data preparation (create `data/crop_data.csv`)
Using `[data/Crop_recommendation.csv](data/Crop_recommendation.csv)` (columns: `N,P,K,temperature,humidity,ph,rainfall,label`).

#### 2.1 Add `soil_type` (weighted distribution)
- Add a new categorical column `soil_type` sampled with weights:
  - `alluvial`: 0.70
  - `loamy`: 0.15
  - `clay`: 0.10
  - `sandy`: 0.05
- In markdown (not code), explain: **assumed Bihar soil distribution** used to simulate soil types.

#### 2.2 Add `organic_matter` (soil-based ranges)
- Add numeric column `organic_matter` using `np.random.uniform(low, high)` per soil:
  - `sandy`: 0.5–1.5
  - `alluvial`: 1.0–3.0
  - `loamy`: 1.5–4.0
  - `clay`: 2.0–5.0
- Round to **2 decimals**.
- Set a fixed random seed for reproducibility.

#### 2.3 Save dataset
- Save final augmented dataset as `[data/crop_data.csv](data/crop_data.csv)`.
- **Checkpoint**: file exists; has 2 new columns; no missing values.

### Step 3 — EDA + modeling notebook (learning-first)
Create `[notebooks/smart_crop_advisor.ipynb](notebooks/smart_crop_advisor.ipynb)` with clear markdown explanations and code outputs.

#### Notebook sections
1. **Problem Statement**: Bihar farmer context + why soil + weather + market signals matter.
2. **Data Creation**:
   - Show original dataframe head (`Crop_recommendation.csv`).
   - Show new columns `soil_type`, `organic_matter`.
   - Explain the weighted soil logic + organic matter ranges.
3. **EDA** (each plot explained):
   - Crop (`label`) distribution bar chart.
   - Soil distribution bar chart.
   - Correlation heatmap for numeric features.
4. **Feature Engineering**:
   - Encode `soil_type` with `LabelEncoder`.
   - Define `X` and `y` (`y = label`).
5. **Train/Test split + Modeling (4 models)**:
   - Use `train_test_split(..., test_size=0.2, random_state=42, stratify=y)`.
   - Print **train accuracy and test accuracy** for each model so you can understand **underfitting vs overfitting**:
     - Underfit sign: train low and test low
     - Overfit sign: train very high but test noticeably lower
   - Train and evaluate:
     - Logistic Regression
     - Decision Tree
     - Random Forest
     - Gradient Boosting
   - For each: fit → predict → show **train accuracy**, **test accuracy**, and a **classification report** on the test set.
6. **Model Comparison**:
   - Compare metrics and pick a best model (default criterion: highest test accuracy; tie-breaker: stability/overfitting signs).
7. **Save Model**:
   - Save best model to `[crop_model.pkl](crop_model.pkl)`.
   - Save `soil_encoder.pkl`.
- **Checkpoint**: notebook runs end-to-end without errors; model/encoder files are created.

### Step 4 — Training script (`train_model.py`)
Convert the notebook’s training logic into a repeatable script:
- Load `[data/crop_data.csv](data/crop_data.csv)`.
- Encode `soil_type` using `LabelEncoder` (save it).
- Split train/test (same params as notebook).
- Train the chosen final model (we will likely pick **RandomForest** unless comparison suggests otherwise).
- Print metrics (train accuracy, test accuracy, and classification report on test) to detect overfit/underfit quickly.
- Save `[crop_model.pkl](crop_model.pkl)` and `[soil_encoder.pkl](soil_encoder.pkl)`.
- **Checkpoint**: running `python train_model.py` regenerates the pickles and prints metrics.

### Step 5 — Streamlit app (`app.py`)
Implement UI in the same sub-steps you listed.

#### 5.1 Title
- `st.title("🌾 Smart Crop Advisor")`

#### 5.2 Load files
- Load `crop_model.pkl`, `soil_encoder.pkl`, and `[data/market_demand.csv](data/market_demand.csv)`.
- Add friendly error messages if missing.

#### 5.3 Weather function `get_weather()`
- Use **Open-Meteo** (no API key) by default.
- Add a city input and resolve it using geocoding:
  - City → **Open-Meteo Geocoding API** → `(latitude, longitude)`
  - Then call Open-Meteo forecast endpoint for current `temperature` and `humidity`
- Return `temperature`, `humidity`.
- Fallback via `try/except` to `(28, 75)`.

#### 5.4 Inputs
- Inputs: `N,P,K, temperature (auto-filled), humidity (auto-filled), ph, rainfall (manual), soil_type dropdown, organic_matter`, plus `city` (for weather fetch).

#### 5.5 Prediction
- On click:
  - encode soil
  - predict crop
  - compute confidence via `predict_proba` (top class probability)

#### 5.6 Confidence score
- Show percentage + `st.progress()`.

#### 5.7 Market panel
- Lookup predicted crop in market CSV.
- Show demand indicator mapping:
  - High → 🟢
  - Medium → 🟡
  - Low → 🔴
- Display `price_per_kg`, `buyer_type`, `buyer_location`.

#### 5.8 Final output
- Big crop name, confidence, and market insights.
- **Checkpoint**: `streamlit run app.py` works and produces a prediction.

### Step 6 — `requirements.txt`
Include (minimum): `streamlit, pandas, numpy, scikit-learn, matplotlib, seaborn, requests`.
- **Checkpoint**: fresh venv can install successfully.

### Step 7 — `README.md`
Include:
- Project description + Bihar farmer problem
- Features (ML, weather, market)
- Setup + run instructions
- Future scope

## Notes / defaults we’ll use
- Reproducibility: fixed random seeds for soil/organic matter and train/test.
- Evaluation: accuracy + classification report; optional confusion matrix in notebook.
- Deployment simplicity: keep everything file-based (CSV + pickle), no databases.
