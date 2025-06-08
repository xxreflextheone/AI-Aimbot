# 🧠 YoloV12 AI Aimbot - Lunar LITE

**Lunar LITE** is built on top of the original [Lunar](https://github.com/zeyad-mansour/lunar) project.

It features an updated triggerbot, modernized packages, and YOLOv12 support.

<div align="center">

<img src="https://ucarecdn.com/a90b3848-a54f-42ff-beab-6c07b5693a73/downloads.svg" alt="downloads" /><br>
<a href="https://discord.gg/aiaimbot">
  <img src="https://ucarecdn.com/50ea9c7c-7384-45bf-b8ee-1f8826b71bdd/lunar1.svg" alt="Join Discord" />
</a>

</div>

---

## 🚀 Lunar V2 (Premium)

**Lunar V2** includes:

- ✅ 25+ customizable settings  
- ✅ Built-in UI  
- ✅ Improved detection accuracy  
- ✅ Supports **YOLOv8**, **YOLOv10**, **YOLOv12**, and **TensorRT**  
- ✅ Xbox controller support
- ✅ Logitech GHUB mouse input
- ✅ Works on AMD and NVIDIA graphics cards

[Download Lunar V2](https://gannonr.com/lunar)

![Lunar V2 UI](https://github.com/user-attachments/assets/173ace44-2a46-45a3-aeba-5c2ce9c9e7b4)

---

## ❓ What Is an AI Aimbot?

Lunar uses screen capture + YOLO object detection to locate enemies in real-time.

> It doesn’t touch memory or inject code — think of it as a robot that watches your screen and gives you precise X,Y coordinates of targets.

🎯 Preconfigured for **Fortnite** — some sensitivity tuning may be needed for other games.

---

## 🔧 YOLOv12 Support

Lunar LITE works with:
- [YOLOv8](https://github.com/ultralytics/ultralytics)
- [YOLOv10](https://github.com/ultralytics/ultralytics)
- [YOLOv12](https://github.com/ultralytics/ultralytics)

---

![Lunar Lite Banner](https://github.com/user-attachments/assets/05864acf-cdd1-484f-be79-fa4a9643e8c2)
![Thumbnail](https://github.com/user-attachments/assets/afa30dd2-8168-4c64-999e-bedb0bef4dec)

---

<details>
<summary>📦 <strong>Installation</strong></summary>

1. Install [Python 3.10.5](https://www.python.org/downloads/release/python-3105/)
2. Install **CUDA Toolkit** 11.8, 12.4, or 12.6 (**12.6 recommended**)
3. Navigate to the root folder and run:
    ```
    install_requirements.bat
    ```
4. Launch with:
    ```
    start.bat
    ```

</details>

---

<details>
<summary>⚙️ <strong>Usage / Troubleshooting</strong></summary>

### If you get `CUDA IS UNAVAILABLE` error:
1. Make sure your installed CUDA version matches.
2. Visit [pytorch.org](https://pytorch.org/get-started/locally/) and install the right build.

Command for CUDA 12.6:
```
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
```

---

### If the console closes instantly:
```
python lunar.py
```

---

### To configure sensitivity:
```
python lunar.py setup
```

---

### To collect training images:
```
python lunar.py collect_data
```

</details>

---

## 💬 Discord Support

Support is only **guaranteed** for **Lunar V2**.  
Please don’t expect full help for the free **LITE** version.

👉 [Join our Discord](https://discord.gg/aiaimbot)
