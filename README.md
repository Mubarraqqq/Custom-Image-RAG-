# LexisNexis Hybrid RAG Prototype

This repository now centers on a small retrieval-augmented QA workflow built on structured JSON data.
The earlier OCR logic has been split into its own helper script, while the main app focuses on retrieval and answer generation.

## Project Preview

![Project preview](./IMG.png)

## Current Architecture

- `RAG.py` loads `main_data.json`, creates LangChain `Document` objects, stores embeddings in Chroma, and answers prompts with `gpt-4o-mini`.
- `image_extract.py` is a standalone OCR helper for extracting text from image files with Tesseract.
- `main_data.json` is the knowledge base currently queried by the app.
- `chrome_db/` stores the persisted vector database locally.

## How `RAG.py` Works

1. Loads the OpenAI API key from `.env`.
2. Reads the structured question/answer pairs from `main_data.json`.
3. Converts each JSON entry into a `Document` with `page_number` metadata.
4. Builds or reuses a local Chroma vector store in `chrome_db/`.
5. Creates a hybrid retriever using semantic search plus BM25 lexical search.
6. Retrieves the top matches for a user query.
7. Sends retrieved context to `gpt-4o-mini`.
8. Returns the answer with simple source labels such as `Page 1`.

## Setup

Install dependencies:
`pip install -r requirements.txt`

Create `.env` with:
`open_api_key=your_key_here`

If you plan to use `image_extract.py`, make sure Tesseract is installed and available at:
`/opt/homebrew/bin/tesseract`

## Usage

Run the retrieval app from the repo root:
`python RAG.py`

You will be prompted for a question, and the script will answer from the JSON-backed dataset.

To experiment with OCR extraction separately, update the placeholder path in `image_extract.py` and run:
`python image_extract.py`

## Important Behavior

If `chrome_db/` already exists, `RAG.py` reuses the existing embeddings instead of rebuilding them.
If `main_data.json` changes, remove `chrome_db/` before rerunning so the vector store reflects the new data.
The current source labels are generated from JSON entry order, not verified original document pages.

## Limitations

- The OCR helper and retrieval app are not yet wired into one end-to-end pipeline.
- `image_extract.py` only processes the first five files in the target folder.
- `RAG.py` assumes `main_data.json` already exists and is correctly formatted.
- Configuration is still hard-coded in a few places.
- There are no automated tests in the repository yet.

## Next Improvements

Unify OCR output with JSON generation, parameterize paths, and refactor the retrieval flow into cleaner modules or classes.
