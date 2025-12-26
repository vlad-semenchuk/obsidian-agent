# Obsidian Tools

A filesystem-based tool discovery system where Python scripts are discoverable via a JSON registry.

## Installation

```bash
# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install -r tools/requirements.txt
```

**Requirements:** Python 3.9+

## Usage

### Run a tool directly

```bash
# Fetch YouTube transcript
python tools/fetch_youtube.py --url "https://youtube.com/watch?v=dQw4w9WgXcQ"

# Using short URL
python tools/fetch_youtube.py --url "https://youtu.be/dQw4w9WgXcQ"

# Using video ID only
python tools/fetch_youtube.py --url "dQw4w9WgXcQ"
```

### Programmatic usage

```bash
# Get transcript and extract full text
result=$(python tools/fetch_youtube.py --url "dQw4w9WgXcQ")
echo "$result" | jq -r '.full_text'

# Check if successful
if python tools/fetch_youtube.py --url "dQw4w9WgXcQ" > /dev/null 2>&1; then
    echo "Success"
fi
```

## Tool Registry

All tools are defined in `tools/tools.json`. This registry describes:

- Available tools and their descriptions
- Input parameters (name, type, required/optional)
- Output schema
- CLI usage examples

### Reading the registry

```bash
cat tools/tools.json | jq '.tools | keys'
# Output: ["fetch_youtube"]
```

### Registry Schema

```json
{
  "version": "1.0.0",
  "tools": {
    "<tool_name>": {
      "name": "string",
      "description": "string",
      "script": "string (filename)",
      "inputs": {
        "<param_name>": {
          "type": "string",
          "required": true|false,
          "description": "string",
          "cli_arg": "--param-name",
          "examples": ["..."]
        }
      },
      "outputs": {
        "<field_name>": {
          "type": "string|number|boolean|array|object",
          "description": "string"
        }
      },
      "exit_codes": {
        "0": "Success",
        "1": "Error"
      },
      "usage": "string"
    }
  }
}
```

## Available Tools

### fetch_youtube

Fetches transcript from a YouTube video.

**Input:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--url` | string | Yes | YouTube URL or video ID |
| `--output` | string | No | Output format (default: json) |

**Output (success):**
```json
{
  "success": true,
  "video_id": "dQw4w9WgXcQ",
  "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
  "transcript": [
    {"text": "Hello", "start": 0.0, "duration": 2.5}
  ],
  "full_text": "Hello ...",
  "language": "en"
}
```

**Output (error):**
```json
{
  "success": false,
  "error": "Transcripts are disabled for this video",
  "error_code": "TRANSCRIPT_DISABLED"
}
```

**Error codes:**
- `INVALID_URL` - Cannot parse video ID from input
- `TRANSCRIPT_DISABLED` - Transcripts disabled by uploader
- `NO_TRANSCRIPT` - No transcript available
- `VIDEO_NOT_FOUND` - Video does not exist
- `NETWORK_ERROR` - Network request failed

## Adding New Tools

1. Create a new Python script in `tools/`:
   ```python
   #!/usr/bin/env python3
   import argparse
   import json
   import sys

   def main():
       parser = argparse.ArgumentParser()
       parser.add_argument('--input', required=True)
       args = parser.parse_args()

       result = {"success": True, "data": "..."}
       print(json.dumps(result, indent=2))
       sys.exit(0)

   if __name__ == '__main__':
       main()
   ```

2. Add dependencies to `tools/requirements.txt`

3. Register the tool in `tools/tools.json`:
   ```json
   {
     "tools": {
       "my_new_tool": {
         "name": "my_new_tool",
         "description": "...",
         "script": "my_new_tool.py",
         "inputs": {...},
         "outputs": {...}
       }
     }
   }
   ```

## Design Principles

- **Simple**: Standalone Python scripts with CLI interface
- **Discoverable**: JSON registry describes all tools
- **Self-contained**: Each tool is independent
- **Testable**: Tools work via direct CLI execution
- **Structured**: Consistent JSON output format
- **Extensible**: Easy to add more tools following the same pattern
