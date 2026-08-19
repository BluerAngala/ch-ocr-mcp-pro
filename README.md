<div align="center">

**🌐 Language / 语言选择**

[English](./README.md) | [中文](./README_CN.md)

</div>

---

# CH OCR MCP Pro — Multi-Engine OCR MCP Server

A [Model Context Protocol](https://modelcontextprotocol.io) server that gives AI
assistants (Claude Code, Copilot, Cursor, Codex, …) **OCR with first-class accuracy handling
and evaluation**. It wraps three engines behind one interface and can score and
compare them.

> 🇨🇳 Optimized for Chinese users with auto-install and China mirror support

| Engine | Backend | Local? | Confidence | Notes |
|--------|---------|--------|-----------|-------|
| **RapidOCR** (default) | PaddleOCR models on [onnxruntime](https://onnxruntime.ai) | ✅ fully local/headless | per-line | No GPU/torch needed; great default |
| **Tesseract** | Google [Tesseract](https://github.com/tesseract-ocr/tesseract) via `pytesseract` | ✅ local | per-word | Needs `tesseract.exe` on PATH |
| **ABBYY FineReader 16** | local FineReader Regular CLI (`/send Clipboard`) | ✅ local | — | Best accuracy; GUI flashes, 1 doc at a time. Headless file output needs ABBYY's paid Extended CLI |

> **Why multi-engine?** No single OCR engine wins on every document. This server
> lets the model run several, **compare their agreement**, and **score them against
> ground truth (CER/WER)** — so you can pick the right engine per job instead of
> guessing.

## 📚 Documentation

- **RapidOCR Docs**: https://rapidai.github.io/RapidOCRDocs/latest/
- **RapidOCR Install Guide**: https://rapidai.github.io/RapidOCRDocs/latest/install_usage/rapidocr/install/
- **RapidOCR Quick Start**: https://rapidai.github.io/RapidOCRDocs/latest/quickstart/

## 🤖 Let AI Install & Configure (Easiest)

**Just tell your AI assistant:**

```
Install and configure ch-ocr-mcp-pro from https://github.com/BluerAngala/ch-ocr-mcp-pro.git
```

**The AI will automatically:**
1. Clone the project
2. Install dependencies
3. Detect your AI tool (VS Code/Claude/Cursor/etc.)
4. Complete the configuration

**Or let AI run:**

```bash
git clone https://github.com/BluerAngala/ch-ocr-mcp-pro.git ~/ch-ocr-mcp-pro
cd ~/ch-ocr-mcp-pro
python3 auto-config.py --mirror tsinghua --output-json
```

The AI reads the JSON output and configures your environment automatically.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔧 Auto Install | `setup.py` installs all dependencies |
| 🚀 China Mirrors | Tsinghua/Aliyun/Huawei mirror support |
| 📦 Dependency Check | Auto-check on startup |
| 🛠️ MCP Tools | `check_environment` and `install_dependencies` tools |

## 🚀 Manual Install

```bash
# Clone
git clone https://github.com/BluerAngala/ch-ocr-mcp-pro.git
cd ch-ocr-mcp-pro

# Auto install with China mirror
python setup.py --mirror tsinghua

# Check config
cat mcp_config.example.json
```

## 🛠️ MCP Tools

| Tool | Description |
|------|-------------|
| `check_environment` | Check environment and dependencies |
| `install_dependencies` | Auto-install dependencies (supports mirrors) |
| `list_engines()` | Which engines are usable on this machine |
| `ocr_image(path, engine, lang)` | OCR one image |
| `ocr_pdf(path, engine, lang, pages, dpi)` | OCR a PDF (single file) |
| `batch_ocr(paths_or_glob, engine, lang)` | OCR many images |
| `batch_ocr_pdfs(paths_or_glob, engine, lang, pages, dpi)` | OCR many PDF files |
| `compare_engines(path, lang)` | Run all engines, compare agreement |
| `evaluate_accuracy(ground_truth, ocr_text/ocr_path)` | CER/WER vs ground truth |

`engine` ∈ `auto` (=RapidOCR) · `rapidocr` · `tesseract` · `finereader`.
`lang` is an ISO-639-1 code (`en`, `de`, `fr`, `zh`, …), mapped per engine.

## 📋 Configure MCP

Run `setup.py` and it will generate `mcp_config.example.json` automatically.

### Claude Desktop

```json
{
  "mcpServers": {
    "ch-ocr": {
      "command": "/path/to/.venv/bin/python",
      "args": ["-m", "ocr_mcp"],
      "env": {
        "PYTHONUTF8": "1",
        "PYTHONUNBUFFERED": "1",
        "PYTHONPATH": "/path/to/ch-ocr-mcp-pro/src"
      }
    }
  }
}
```

### VS Code Copilot

```json
{
  "github.copilot.chat.mcp.servers": {
    "ch-ocr": {
      "command": "/path/to/.venv/bin/python",
      "args": ["-m", "ocr_mcp"],
      "env": {
        "PYTHONPATH": "/path/to/ch-ocr-mcp-pro/src"
      }
    }
  }
}
```

### Codex (`~/.codex/config.toml`)

```toml
[mcp_servers.ch-ocr]
command = "/path/to/.venv/bin/python"
args = ["-m", "ocr_mcp"]
startup_timeout_sec = 60
tool_timeout_sec = 300

[mcp_servers.ch-ocr.env]
PYTHONUTF8 = "1"
PYTHONUNBUFFERED = "1"
PYTHONPATH = "/path/to/ch-ocr-mcp-pro/src"
```

## Usage Examples

```
> OCR this scan and tell me how confident you are.
  → ocr_image("C:/scans/invoice.png")  → text + mean_confidence + low-confidence lines

> Which engine reads this receipt best?
  → compare_engines("C:/scans/receipt.jpg")  → per-engine text + agreement + consensus

> How accurate is RapidOCR on this page vs my transcript?
  → evaluate_accuracy("truth.txt", ocr_path="page.png", engine="rapidocr") → CER/WER
```

## Evaluation Methodology

`evaluate_accuracy` uses [`jiwer`](https://github.com/jitsi/jiwer) for **CER**
(character error rate) and **WER** (word error rate). Lower is better;
`char_accuracy_pct = (1 − CER)·100`. Keep ground-truth `.txt` files next to your
test images to track engine accuracy over time. `compare_engines` is the
no-ground-truth fallback: it reports how much the engines agree and which one is
the consensus.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
pytest
```

## Security

This server reads any file path the MCP client gives it — i.e. **any file readable by
the server process**. There is no sandbox by default. Run it only with a **trusted MCP
client**, and be aware that an LLM driving the tools could be prompted to read arbitrary
local files.

For defense-in-depth, set **`OCR_MCP_ALLOWED_DIRS`** (an `os.pathsep`-separated list of
directories) to restrict all tools to files under those roots:

```toml
[mcp_servers.ocr.env]
OCR_MCP_ALLOWED_DIRS = "D:\\scans;D:\\documents"
```

Also note: `batch_ocr` with a recursive glob (`**/*.png`) can match very large file
sets — scope your globs. The FineReader engine shells out to the local
`FineReaderOCR.exe` (list-form args, no shell) and reads the OS clipboard.

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgements

[RapidOCR](https://github.com/RapidAI/RapidOCR) · [Tesseract](https://github.com/tesseract-ocr/tesseract) ·
[ABBYY FineReader](https://pdf.abbyy.com) · [jiwer](https://github.com/jitsi/jiwer) ·
[PyMuPDF](https://github.com/pymupdf/PyMuPDF) · [MCP](https://modelcontextprotocol.io)
