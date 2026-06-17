# Batch Media Insight Extractor

## Project Overview

Batch Media Insight Extractor is a local AI workflow software prototype for batch image and video information extraction.

It can process images and videos from a local folder, extract text and metadata, generate local summaries, and export structured Word/PDF reports.

This public showcase version is designed for portfolio demonstration. Private media files, generated reports, API keys, and personal data are excluded.

## Core Features

- Batch image and video file detection
- Image OCR with Chinese and English support
- OCR text cleanup
- Local rule-based image summarization
- Video metadata extraction
- Video preview frame generation
- Video audio extraction
- Local Whisper speech-to-text transcription
- Local video transcript summarization
- Word/PDF report generation
- Batch report archiving
- Apple-style Streamlit web interface
- Chinese / English UI switching
- Local full workflow launcher
- Environment check and repair launcher

## Current Strategy

This version prioritizes local functionality and does not require OpenAI API credits.

OpenAI / ChatGPT enhanced summarization is reserved for a later content-creation or commercialization stage.

## Tech Stack

- Python
- Streamlit
- Tesseract OCR
- faster-whisper
- OpenCV
- imageio-ffmpeg
- python-docx
- pywin32
- pandas
- Windows CMD launchers

## Privacy and Safety

The following are intentionally excluded from GitHub:

- input_media/
- output/
- logs/
- API keys
- private images
- private videos
- generated reports
- model cache files
- personal data

## Status

Current checkpoint: VIDEO-EXTRACT-018

The local software prototype is functional and ready for portfolio showcase preparation.
