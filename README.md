# MiniCoder

MiniCoder is a small React and Python coding chatbot. It is deterministic and
uses no AI service or API key.

```bash
npm run setup
npm run dev
```

Open `http://localhost:5173`.

```bash
npm test
npm run check
npm run build
```

## Task

Find and fix the intentional behavioral bugs. Then add a
`delete_file(path)` tool alongside the existing file tools.

```python
from pathlib import Path

Path(path).unlink()
```
