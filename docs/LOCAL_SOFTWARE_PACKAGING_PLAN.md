# Local Software Packaging Plan

Target packaging direction: Windows local software folder version first, EXE later.

## Recommended Structure

- Start_VideoExtractSkill.cmd
- Run_Local_Full_Workflow.cmd
- Check_Environment.cmd
- Repair_Environment.cmd
- app.py
- modules
- config
- assets
- docs
- demo_assets
- input_media
- output

## Why Not Single EXE Yet

The project depends on Tesseract OCR, Whisper, ffmpeg, Word PDF conversion, Streamlit, OpenCV, and local model files. A single EXE is possible later, but the stable software folder version is a better next milestone.

## Packaging Milestones

1. Stable software folder version
2. Better launcher and repair flow
3. Demo mode
4. Clean README and screenshots
5. Portable package test
6. PyInstaller exploration
7. Installer exploration