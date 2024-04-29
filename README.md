# Solipnet

_This project started its life as a fork of [Sebby37's Dead Internet](https://github.com/Sebby37/Dead-Internet) repo, but has since diverged._


## Overview

This project presents an alternate reality web browser, powered by an LLM. You start at the Solipnet search engine, where you can enter any query imaginable. This will present a list of search results which link out to AI generated websites. Those websites may further link to other AI generated websites.

## Requirements

- Access to an OpenAI compatible API, ideally with a locally hosted model (llama.cpp server, ollama, LM Studio, oobabooga, etc.)
- Python 3.10.12
- A SearXNG instance with the JSON API support enabled, if you want images in your pages.

The model I used for testing is the [Llama 3 8B Instruct Q4_K_M GGUF from QuantFactory](https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF).

## Setup

Install the requirements:

```bash
pip install -r requirements.txt
```

Modify the `.env` file with your API URL and API key.
Optionally, you can also modify the `ENABLE_IMAGES` environment variable to `true` and provide a URL in the `SEARXNG_URL` environment variable to your SearXNG instance.

## Usage

Run the server:

```bash
python main.py
```

Open your browser to `http://localhost:5000`.

## Screenshots

![image](https://github.com/Zetaphor/solipnet/assets/3112763/70925576-478d-4c7b-875f-c6c796623f1d)
![image](https://github.com/Zetaphor/solipnet/assets/3112763/4c489f83-3f2a-4deb-97fe-60e391a6a59e)

