# Pattern: Lazy-Load Module Architecture

**Domain:** Python / FastAPI / Server Architecture  
**Source:** Kiosk Runtime design, 27-May-2026  
**Applies to:** Any server that loads ML models or heavy dependencies

---

## The Problem

ML models (LLMs, Whisper, Piper, etc.) can take 2–30 seconds to load and consume gigabytes of RAM. Loading everything at startup means:
- Slow boot time
- High idle memory usage
- Broken server on machines that lack certain models

## The Pattern

```
┌─────────────────────────────┐
│  FastAPI App                │
│  ┌───────────────────────┐  │
│  │ Module Registry       │  │
│  │  - config stored      │  │
│  │  - model NOT loaded   │  │
│  └───────────────────────┘  │
│                             │
│  Request comes in ─────────→│
│  ┌───────────────────────┐  │
│  │ Lazy Loader           │  │
│  │  - Check if loaded    │  │
│  │  - If not → load now  │  │
│  │  - Cache for next use │  │
│  └───────────────────────┘  │
└─────────────────────────────┘
```

## Implementation

```python
class LazyLoader:
    """Load a resource on first access, cache forever after."""
    
    def __init__(self, name: str, loader: callable):
        self.name = name
        self._loader = loader
        self._resource = None
        self._loaded = False
    
    @property
    def resource(self):
        if not self._loaded:
            self._resource = self._loader()
            self._loaded = True
        return self._resource
    
    @property
    def is_loaded(self):
        return self._loaded
```

## Benefits
- **Cold boot in ~2 seconds** (register all modules, load nothing)
- **Memory proportional to active usage** (not total capability)
- **Graceful degradation** (missing model = feature disabled, not server crash)
- **Hot-reload friendly** (swap module implementation without restart)

## Best Practices
- Always store config/metadata at registration time (for `/api/status` endpoints)
- Log load time and memory impact on first load
- Provide an `is_loaded` check for health endpoints
- Consider pre-warm endpoint for admin use
