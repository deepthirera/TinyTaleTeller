# Tiny Tale Teller

An MCP (Model Context Protocol) client-server application that delivers bilingual children's stories from a dataset of over 200,000 tiny stories.

## Overview

This project implements an MCP server that provides access to a large collection of children's stories from the Kaggle dataset [thedevastator/tinystories-narrative-classification](https://www.kaggle.com/datasets/thedevastator/tinystories-narrative-classification). The stories can be delivered in English or as bilingual content (English + Tamil or English + Hindi).

## Features
- **200K+ Story Library**: Access to a massive collection of tiny stories from Kaggle
- **Multilingual Support**: Stories available in:
  - English only
  - Bilingual English + Tamil
  - Bilingual English + Hindi
- **MCP Sampling**: Server uses the client's model to convert stories into child-friendly conversational format
- **Real-time Translation**: Uses Google Translate API for bilingual story generation

## Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- API keys for your chosen LLM provider (e.g., Google AI)
- Internet connection (for translation services)

## Installation

1. Clone the repository:
```bash
cd tiny_tale_teller
```

2. Install dependencies:
```bash
uv sync
```

3. Set up environment variables:
Create a `.env` file with your API keys:
```bash
GEMINI_API_KEY=your_api_key_here
```
NOTE: Sampling works with model = "google-gla:gemini-2.5-pro"

## Running the Application

The application requires running both the server and client in separate terminals.

### Terminal 1 - Start the MCP Server:
```bash
uv run server.py
```

The server will start on `http://localhost:8000/mcp`

### Terminal 2 - Run the Client:
```bash
uv run client.py
```


### Example Usage

```
You can ask for story in english/tamil/hindi. What would you like?
> Tell me a story in Tamil

User: Tell me a story in Tamil
Assistant: [Displays story in both English and Tamil]
```

## Running Evaluations

To run the automated test suite:

```bash
uv run evaluations.py
```

The evaluations validate:
- English story generation
- Tamil bilingual story generation
- Hindi bilingual story generation
- Proper handling of unsupported languages


## Dataset

Stories are sourced from the [TinyStories Narrative Classification dataset](https://www.kaggle.com/datasets/thedevastator/tinystories-narrative-classification) on Kaggle, containing over 200,000 short children's stories ideal for language learning and entertainment.

