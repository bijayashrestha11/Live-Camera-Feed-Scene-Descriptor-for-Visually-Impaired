# Scene Descriptor - Project Instructions

Real-time video captioning system for visually impaired users using WebRTC and ML.

## Tech Stack

- **Backend**: Python 3.9+, aiohttp, aiortc, PyTorch, Transformers (GIT-base-vatex)
- **Frontend**: Flutter/Dart, flutter_webrtc, Provider, flutter_tts

## Quick Start

```bash
# Backend
cd Backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m scene_descriptor --host 0.0.0.0 --port 8080

# Frontend (new terminal)
cd Frontend
flutter pub get
flutter run
```

## Directory Structure

```
Backend/
├── src/scene_descriptor/    # Main Python package
│   ├── config/              # Settings and constants
│   ├── models/              # ML model management
│   ├── services/            # Business logic
│   ├── webrtc/              # WebRTC handling
│   ├── api/                 # HTTP routes and handlers
│   ├── utils/               # Logging, exceptions, state
│   └── enums/               # Status enumerations
├── scripts/                 # Standalone scripts
├── tests/                   # Test suite
├── data/                    # Video files
└── logs/                    # Application logs

Frontend/lib/
├── config/                  # App configuration
├── screens/                 # UI screens
├── widgets/                 # Reusable widgets
├── services/                # API services
├── provider/                # State management
└── constants/               # Colors, styles, paths
```

## Common Commands

| Command | Description |
|---------|-------------|
| `make run` | Run backend server |
| `make test` | Run tests with coverage |
| `make format` | Format code (black, isort) |
| `make lint` | Lint code (flake8, mypy) |
| `make logs` | View application logs |

## Environment Variables

See `Backend/.env.example` for all options:
- `HOST`, `PORT` - Server binding
- `LOG_LEVEL` - DEBUG, INFO, WARNING, ERROR
- `MODEL_DIR` - Path to ML models
- `DEFAULT_MODEL` - git or pulchowk
- `CUDA_DEVICE` - GPU device (cuda:0) or cpu

## Coding Standards

- **Python**: PEP 8, type hints, docstrings for public functions
- **Dart**: Flutter style guide, const constructors
- Always add logging for errors and important operations
- Use custom exceptions from `utils/exceptions.py`

## Logging Levels

| Level | Use For |
|-------|---------|
| ERROR | Application errors requiring attention |
| WARNING | Unexpected but handled situations |
| INFO | Important operational events |
| DEBUG | Detailed diagnostic information |

## Architecture Flow

```
Flutter App (Camera)
    → WebRTC Video Stream
    → Python Backend
    → Frame Collection (5 sec)
    → ML Model Inference
    → Caption Generation
    → Data Channel
    → Flutter App (Display + TTS)
```

## Custom Skills (/.claude/commands/)

- `/backend-setup` - Setup Python environment
- `/backend-run` - Run server
- `/backend-test` - Run tests
- `/backend-lint` - Lint code
- `/frontend-setup` - Setup Flutter
- `/frontend-run` - Run app
- `/logs-view` - View logs
- `/logs-clear` - Clear logs
- `/docker-build` - Build Docker image
- `/docker-run` - Run with Docker
- `/full-stack-run` - Run entire stack
