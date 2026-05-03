# Tarobot One

Tarobot One is a ROS 2-based mobile robot platform designed for simulation and navigation development. This repository provides robot description, configuration, and launch files for different ROS 2 distributions.

---

## 📦 Features

* Differential drive mobile robot
* URDF/Xacro robot description
* Navigation2 (Nav2) configuration
* Simulation support (RViz / Gazebo)
* Multi-distro support (Humble & Jazzy)

---

## 🌿 Branch Structure

This repository uses separate branches for each ROS 2 distribution:

* `main` → Base / shared configuration
* `humble` → ROS 2 Humble version
* `jazzy` → ROS 2 Jazzy version

> ⚠️ Each branch may contain different parameters and configurations depending on the ROS 2 distribution.

---

## 🚀 Getting Started

### Clone for ROS 2 Humble

```bash
git clone -b humble git@github.com:mifadikr24/tarobot_one.git
```

### Clone for ROS 2 Jazzy

```bash
git clone -b jazzy git@github.com:mifadikr24/tarobot_one.git
```

---

## 🛠️ Build Instructions

```bash
cd ~/your_workspace
colcon build
source install/setup.bash
```

---

## 📁 Repository Structure

* `description/` → URDF and robot model
* `config/` → Navigation and controller parameters
* `launch/` → Launch files
* `rviz/` → RViz configurations
* `worlds/` → Simulation environments

---

## 📌 Notes

* Use the correct branch for your ROS 2 distribution.
* Avoid mixing configurations between branches.
* Each workspace should be built separately per distribution.

---

## 📄 License

See `LICENSE.md` for details.

