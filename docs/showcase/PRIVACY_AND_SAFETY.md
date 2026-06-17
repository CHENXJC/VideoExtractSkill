# Privacy and Safety

## Local-First Design

The current version is designed to run locally.

Private image files, video files, transcripts, and generated reports stay on the user's computer.

## Excluded from Public GitHub Version

The project intentionally excludes:

- input_media/
- output/
- logs/
- API keys
- private media files
- generated reports
- local cache files
- personal screenshots

## API Strategy

OpenAI / ChatGPT API enhanced summarization is not required in the current local version.

API-based features are reserved for a future stage when the project is used for content creation, public showcase, or commercialization.

## GitHub Safety Rule

Before publishing, always run:

python run_github_safety_check.py
