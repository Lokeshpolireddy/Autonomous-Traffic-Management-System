# Advanced Traffic Management System (ATMS) 🚦

A smart traffic control system designed to optimize vehicle flow, reduce congestion, and prioritize emergency vehicles using SUMO simulations and embedded control logic.

## 💡 Project Overview

This project simulates an intelligent traffic management system using:
- **SUMO (Simulation of Urban Mobility)** for realistic traffic modeling
- **Python** and **OpenCV** for logic control and visualization
- **Sensor-based logic** to detect and respond to traffic density
- **Emergency vehicle prioritization** to clear routes during critical conditions

## 🎯 Key Features

- 🔁 **Adaptive Signal Control** — Real-time traffic flow-based signal management
- 🚑 **Emergency Vehicle Detection** — Immediate clearance path for ambulances/fire trucks
- 🎥 **Camera Input Integration** — Optional visual input processing using OpenCV
- 📈 **Simulation Data Analytics** — Monitor performance metrics like wait time and throughput

## 🛠️ Tech Stack

- **SUMO** – Traffic simulation environment
- **Python** – Backend logic and simulation control
- **OpenCV** – Visual traffic analysis (optional)
- **TraCI** – Interface for controlling SUMO via Python

## 📁 Project Structure

```plaintext
ATMS/
├── simulation/
│   ├── network.net.xml        # Road network
│   ├── route.rou.xml          # Vehicle routes
│   ├── traffic_control.py     # Signal control logic
│   └── emergency_handler.py   # Emergency vehicle logic
├── images/                    # Output and documentation images
├── results/                   # Summary logs and reports
└── README.md                  # Project documentation
```
