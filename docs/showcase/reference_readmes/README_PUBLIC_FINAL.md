# Batch Media Insight Extractor

A local-first AI workflow software prototype that converts batches of images and videos into structured text, summaries, keywords, key points, and Word/PDF reports.

## Product Positioning

Batch Media Insight Extractor is not just a small script. It is a local AI workflow software prototype designed to process unstructured media files and turn them into reusable knowledge assets.

It is built for scenarios where users need to handle many screenshots, images, short videos, lectures, screen recordings, or social media clips and convert them into structured reports.

## Key Features

- Batch image and video file detection
- Image OCR with Chinese and English support
- OCR text cleanup and formatting
- Local image summary and keyword extraction
- Video metadata extraction
- Video preview frame generation
- Video audio extraction
- Local Whisper speech-to-text transcription
- Video transcript cleanup and local summarization
- Word and PDF report generation
- Batch report archiving
- Apple-style Streamlit dashboard UI
- Chinese and English UI switching
- Theme color switching
- One-click local full workflow
- Environment check and repair launchers

## Screenshots

Screenshots should be added later using safe demo files only.

Suggested screenshot placeholders:

- Dashboard overview
- One-click local workflow success
- Video info and preview frames
- Reports center
- Environment READY check
- Demo Word/PDF report preview

## Workflow

1. Add images and videos into the local input folder.
2. Start the local web software.
3. Run the one-click local full workflow.
4. The system extracts image text, video transcripts, metadata, summaries, and keywords.
5. Word/PDF reports are generated and archived by batch.

## Tech Stack

- Python
- Streamlit
- Tesseract OCR
- faster-whisper
- OpenCV
- imageio-ffmpeg
- pandas
- python-docx
- pywin32
- Windows CMD launchers

## Local-First and Privacy-Aware Design

The current version is designed around local processing. Private media files, generated reports, logs, and local outputs are intentionally excluded from the public showcase version.

OpenAI or ChatGPT API enhanced summarization is reserved for a later content creation, portfolio demonstration, or commercialization stage.

## Public Showcase Safety

This public version should not include:

- input_media/
- output/
- logs/
- API keys
- private images
- private videos
- generated private reports
- model cache files

## Portfolio Value

This project demonstrates practical AI workflow design, local automation, OCR integration, speech-to-text integration, report generation, UI design, and privacy-aware GitHub packaging.

## Roadmap

- Add safe demo screenshots
- Improve onboarding and settings page
- Strengthen local summarization quality
- Add optional OpenAI enhanced summary later
- Explore Windows packaging and installer options
- Prepare a polished public portfolio page

## Status

Checkpoint: VIDEO-EXTRACT-026

Current stage: working local software prototype plus public showcase preparation.