# Model Weights Directory

This directory should contain the trained model weights for edge deployment.

## Required Models

Copy the following model files from your training environment to this directory:

### 1. Main Detection Model
```bash
# From Windows PC to Raspberry Pi:
scp backend/yolov8n.pt pi@raspberrypi.local:~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/models/best.pt

# Or if you have ONNX model:
scp backend/best.onnx pi@raspberrypi.local:~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/models/best.onnx
```

### 2. Helmet Detection Model (Optional)
```bash
scp backend/yolov8n-pose.pt pi@raspberrypi.local:~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/models/yolo11nHelmet_Detection_using_Yolo11.pt
```

### 3. Number Plate Detection Model (Optional)
```bash
scp model/checkpoints/yolo11n_numberplate.pt pi@raspberrypi.local:~/Embedded\ AI-Based\ Traffic\ Violation\ Detection\ System/models/yolo11n_numberplate.pt
```

## Model Optimization for Raspberry Pi 5

For best performance on Raspberry Pi 5, convert your PyTorch models to ONNX format with INT8 quantization:

### Convert to ONNX
```python
from ultralytics import YOLO

# Load PyTorch model
model = YOLO('best.pt')

# Export to ONNX
model.export(format='onnx', imgsz=320, simplify=True)
```

### INT8 Quantization (Advanced)
For even better performance, quantize to INT8:

```bash
# Use the quantization script
python ../scripts/quantize_int8.py --model best.onnx --output best_int8.onnx
```

## Expected Performance

| Model Type | Size | Inference (RPi5) | FPS |
|------------|------|------------------|-----|
| PyTorch FP32 (640px) | 9.3 MB | ~300ms | 3-5 |
| PyTorch FP32 (320px) | 9.3 MB | ~120ms | 8-12 |
| ONNX FP32 (320px) | 9.3 MB | ~80ms | 12-15 |
| ONNX INT8 (320px) | ~2.5 MB | ~60ms | 15-25 |

**Recommended:** ONNX INT8 @ 320×320 for real-time operation on Raspberry Pi 5.

## File Structure

After copying models, your directory should look like:

```
models/
├── README.md (this file)
├── best.pt                                    # Main detection model (PyTorch)
├── best.onnx                                  # Main detection model (ONNX)
├── best_int8.onnx                            # INT8 quantized (optional)
├── yolo11nHelmet_Detection_using_Yolo11.pt   # Helmet detection (optional)
└── yolo11n_numberplate.pt                    # Plate detection (optional)
```

## Troubleshooting

### Model Not Found Error
If you see "Model not found" error:
1. Check file exists: `ls -lh models/`
2. Check file permissions: `chmod 644 models/*.pt models/*.onnx`
3. Verify path in `.env` file matches actual filename

### Out of Memory Error
If Raspberry Pi runs out of memory:
1. Use smaller model (320×320 instead of 640×640)
2. Use INT8 quantized model
3. Close other applications
4. Increase swap space: `sudo dphys-swapfile swapoff && sudo nano /etc/dphys-swapfile` (set CONF_SWAPSIZE=2048)

### Slow Inference
If inference is too slow:
1. Use ONNX model instead of PyTorch
2. Reduce inference size in `.env`: `INFERENCE_SIZE=256`
3. Process every Nth frame: `PROCESS_EVERY_N_FRAMES=2`
4. Ensure active cooling is working (check CPU temp: `vcgencmd measure_temp`)

## Model Training

If you need to train custom models, refer to the main project documentation:
- Training guide: `../../docs/guides/DETECTOR_GUIDE.md`
- Dataset preparation: `../../docs/guides/IMPLEMENTATION_CHECKLIST.md`
