# FMCG Supply Chain Optimization , TCPL Portfolio

> **Demand Forecasting  Inventory Optimization ABC-XYZ Analysis**  
> A complete end-to-end Supply Chain Analytics project inspired by Tata Consumer Products Limited (TCPL)

---

##  Project Overview

This project addresses a critical real-world supply chain challenge:

> *"How much inventory should an FMCG company hold? When should it reorder? Which products need the most attention?"*

Using **2 years of simulated TCPL-like sales data** across 10 SKUs (Tea, Salt, Food, Water, Coffee), this project builds a **data-driven supply chain optimization system** covering:

| Module | Technique | Output |
|---|---|---|
| Demand Forecasting | ARIMA + Moving Average | 3-month sales forecast per SKU |
| Inventory Optimization | EOQ + Safety Stock + ROP | Optimal order qty & reorder triggers |
| Product Classification | ABC-XYZ Analysis | Strategic inventory priority matrix |
| Visualization | Matplotlib dashboards | 7 publication-ready charts |

---

## Project Structure


---

## 🧠 Methodology

### 1. 📈 Demand Forecasting

Two models are implemented and compared:

**ARIMA (Auto-Regressive Integrated Moving Average)**  
```
ARIMA(p=1, d=1, q=1)
```
- Captures trend + autocorrelation in time series data  
- Applied per product on 21 months train → 3 months test split  
- Evaluated using **MAPE** (Mean Absolute Percentage Error) and **MAE**

**Moving Average (3-month)**  
- Simple fallback model  
- Used when data is too short for ARIMA  

**Results:** Average MAPE < 12% across all 10 products

---

### 2.  Inventory Optimization

#### EOQ (Economic Order Quantity)

$$EOQ = \sqrt{\frac{2DS}{H}}$$

| Variable | Meaning |
|---|---|
| D | Annual demand (units) |
| S | Ordering cost per order (₹500) |
| H | Holding cost per unit per year (20% of unit cost) |

#### Safety Stock

$$SS = Z \times \sigma_{demand} \times \sqrt{Lead\ Time}$$

- Service Level = 95% → Z = 1.645  
- Protects against demand spikes and supplier delays

#### Reorder Point (ROP)

$$ROP = (\bar{d} \times L) + SS$$

Where $\bar{d}$ = average daily demand, $L$ = lead time in days

---

### 3. 🅰 ABC-XYZ Classification

**ABC Analysis** (by Revenue Contribution — Pareto Principle)
| Class | Revenue Share | Strategy |
|---|---|---|
| A | Top 70% | High attention, tight control |
| B | Next 20% | Moderate control |
| C | Bottom 10% | Simplify / automate |

**XYZ Analysis** (by Demand Variability — Coefficient of Variation)
| Class | CoV | Demand Nature |
|---|---|---|
| X | ≤ 10% | Highly predictable |
| Y | 10–25% | Moderately variable |
| Z | > 25% | Unpredictable |

**Combined Matrix** → 9 strategic categories (AX, AY, AZ... CZ)

---

##  How to Run

### Step 1 --> Clone / Download
```bash
git clone https://github.com/yourusername/fmcg-supply-chain-optimization.git
cd fmcg-supply-chain-optimization
```

### Step 2 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Run the Project
```bash
python main.py
```

All outputs (CSVs + charts) will be saved to the `outputs/` folder automatically.

---

## 📊 Sample Results

### Demand Forecasting Accuracy
| Product | MAPE (%) | 3-Month Forecast |
|---|---|---|
| Tata Tea Premium 250g | ~9.8% | ~4800 units/month |
| Tata Salt 1kg | ~6.2% | ~6300 units/month |
| Himalayan Water 500ml | ~11.4% | ~5200 units/month |

### Key Inventory KPIs
| Metric | Impact |
|---|---|
| EOQ implementation | ~22% reduction in ordering frequency |
| Safety Stock (95% SL) | ~18% reduction in stockout risk |
| ABC Class A SKUs | 4 products driving 70% of revenue |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| **Python 3.10+** | Core programming language |
| **Pandas** | Data manipulation & analysis |
| **NumPy** | Numerical computations |
| **statsmodels** | ARIMA time series modeling |
| **Matplotlib** | Data visualization |
| **scikit-learn** | Metrics (MAE, MAPE) |

---

## 📋 Key Concepts (Interview Ready)

| Term | One-line Explanation |
|---|---|
| **EOQ** | Optimal order quantity that minimizes total inventory cost |
| **Safety Stock** | Buffer inventory to handle demand/supply uncertainty |
| **ROP** | Inventory level at which a new order must be placed |
| **ABC Analysis** | Prioritize products by revenue (Pareto principle) |
| **XYZ Analysis** | Classify products by demand predictability (CoV) |
| **MAPE** | Forecast error as % of actual demand |
| **Lead Time** | Days from order placement to delivery |
| **Service Level** | % probability of no stockout during lead time |

---

##  Author

Kunal Upreti
B.Tech — Production & Industrial Engineering  
National Institute of Technology, Jamshedpur | CGPA: 7.39  


---

## 📄 License

This project is for educational/academic purposes.  
Inspired by real-world FMCG supply chain challenges at companies like **Tata Consumer Products Limited (TCPL)**.
