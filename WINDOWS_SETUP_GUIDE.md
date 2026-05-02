# Windows Setup Guide - Traffic Violation Detection System

## Quick Setup Instructions

### 1. Install Python Dependencies

The installation is currently running in the background. It may take 10-15 minutes to complete.

**If the installation completes successfully**, you'll see a message indicating all packages were installed.

**If you need to restart the installation:**
```bash
.\venv\Scripts\activate
pip install -r requirements_windows.txt
```

### 2. Test Your Setup

Once installation completes, test the system:

#### Test Camera
```bash
.\venv\Scripts\activate
python scripts\test_camera.py
```

#### Run with Webcam
```bash
.\venv\Scripts\activate
python run_edge.py --source 0
```

#### Run with Video File
```bash
.\venv\Scripts\activate
python run_edge.py --video path\to\your\video.mp4
```

### 3. Configuration

The `.env` file has been created with Windows-optimized settings:
- **DEVICE=cpu** - Uses CPU (change to 'cuda' if you have NVIDIA GPU)
- **SHOW_DISPLAY=True** - Shows detection window
- **CAMERA_SOURCE=0** - Uses default webcam

### 4. Common Issues & Solutions

#### Issue: "Camera not found"
**Solution:** 
- Check if your webcam is connected
- Try different camera sources: `--source 1` or `--source 2`
- Test with a video file instead

#### Issue: "Model file not found"
**Solution:**
- Ensure model files are in the `models/` directory
- Download models if missing (check models/README.md)

#### Issue: "Slow performance"
**Solution:**
- Reduce inference size in `.env`: `INFERENCE_SIZE=320`
- Process fewer frames: `PROCESS_EVERY_N_FRAMES=2`
- Use smaller model if available

#### Issue: "Import errors"
**Solution:**
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements_windows.txt`

### 5. Running Modes

**Full Detection System:**
```bash
python run_edge.py
```

**Camera Test Only:**
```bash
python run_edge.py --mode test
```

**Performance Benchmark:**
```bash
python run_edge.py --mode benchmark
```

**Headless Mode (no display):**
```bash
python run_edge.py --no-display
```

### 6. Project Structure

```
├── edge_core/          # Core detection modules
├── edge_pipeline/      # Main pipeline
├── edge_database/      # Database operations
├── models/             # YOLO model files
├── logs/               # System logs
├── data/               # SQLite database
├── evidence/           # Captured violation images
└── run_edge.py         # Main entry point
```

### 7. Next Steps

1. **Wait for installation to complete** (check terminal)
2. **Test camera**: `python scripts\test_camera.py`
3. **Run detection**: `python run_edge.py`
4. **Check logs**: `logs\edge_system.log`
5. **View database**: `data\violations.db` (use SQLite browser)

### 8. GPU Support (Optional)

If you have an NVIDIA GPU:

1. Install CUDA Toolkit (11.8 or 12.1)
2. Update `.env`: `DEVICE=cuda`
3. Reinstall PyTorch with CUDA:
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

### 9. Useful Commands

**Activate virtual environment:**
```bash
.\venv\Scripts\activate
```

**Check installed packages:**
```bash
pip list
```

**Update a package:**
```bash
pip install --upgrade package_name
```

**View system info:**
```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}')"
```

## Support

For issues or questions:
1. Check the logs in `logs/edge_system.log`
2. Review the documentation files in the project root
3. Ensure all model files are present in `models/` directory

## Performance Tips

- **Laptop/Low-end PC**: Use `INFERENCE_SIZE=320`, `PROCESS_EVERY_N_FRAMES=2`
- **Mid-range PC**: Use `INFERENCE_SIZE=640`, `PROCESS_EVERY_N_FRAMES=1`
- **High-end PC with GPU**: Use `DEVICE=cuda`, `INFERENCE_SIZE=640`
