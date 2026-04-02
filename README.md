
# 🚀 MovingBase RTK Viewer

GNSS / RTK（Moving Base）データを可視化・解析するためのWebツール
NMEAログから軌跡・速度・姿勢（heading / roll）を直感的に確認できます

---

## ✨ Features

* 📍 **Trajectory Visualization**
  緯度・経度を地図上にプロット（OpenStreetMap）

* 🎨 **Speed Heatmap**
  速度に応じた色分布で動きの変化を可視化

* 📊 **Time-Series Analysis**

  * Speed（速度変化）
  * Heading（方位）
  * Roll（ロール）

* 📂 **NMEA Log Support**
  `$GPRMC`, `$GNRMC`, `$PSSN,HRP` に対応

---

## 🏗️ Architecture

```
FastAPI (Backend)
├── parser.py     # NMEA解析
├── main.py       # API + UI
└── Plotly        # 可視化
```

* 軽量構成（React不要）
* APIベースで拡張可能（将来WebSocket対応）

---

## 📦 Requirements

* Python 3.10+
* pip

---

## ⚙️ Installation

```bash
git clone https://github.com/yourname/movingbase-rtk-viewer.git
cd movingbase-rtk-viewer

# 仮想環境
python -m venv venv
venv\Scripts\activate  # Windows

# 依存関係
pip install -r requirements.txt
```

---

## ▶️ Usage

```bash
uvicorn main:app --reload
```

ブラウザでアクセス👇
http://127.0.0.1:8000

1. NMEAファイルをアップロード
2. 地図・グラフが表示される

---

## 📊 Supported Data Format

### RMC（位置・速度）

```
$GPRMC,hhmmss,A,lat,N,lon,E,speed,...
```

### HRP（姿勢）

```
$PSSN,HRP,time,...,heading,...,roll,...
```

---

## 🧠 Roadmap

* [ ] 時刻同期（RMC × HRP）
* [ ] ストローク検出（rowing分析）
* [ ] リアルタイム可視化（WebSocket）
* [ ] CSV / JSON エクスポート
* [ ] Reactフロントエンド化

---

## 🎯 Use Cases

* 🚣 Rowing performance analysis
* 🚁 Drone / robotics trajectory analysis
* 🛰️ GNSS / RTK validation
* 📡 Moving Base heading evaluation

---

## ⚠️ Notes

* 現在は簡易的なデータ同期（非時刻ベース）
* 大量データは間引き推奨

---

## 👤 Author

Satoshi
IT Engineer / GNSS / RTK / Robotics

---

## 📄 License

MIT License

---

## 🌟 Motivation

This project aims to bridge **research and real-world applications**
by transforming raw GNSS data into actionable insights.

---
