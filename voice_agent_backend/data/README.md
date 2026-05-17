# Local Data

This directory stores local runtime artifacts.

- `models/` holds Kokoro ONNX and voice files used by native TTS.
- `sqlite/` holds the local SQLite database used for auth/session metadata.

Large model and database files are preserved locally but ignored by Git. Use Git LFS or another artifact store if these files need to be shared through a repository.
