# Architecture Documentation

## Live Camera Feed Scene Descriptor for Visually Impaired

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Component Diagram](#component-diagram)
4. [Backend Architecture](#backend-architecture)
5. [Frontend Architecture](#frontend-architecture)
6. [Data Flow](#data-flow)
7. [WebRTC Signaling](#webrtc-signaling)
8. [ML Pipeline](#ml-pipeline)
9. [Directory Structure](#directory-structure)
10. [Technology Stack](#technology-stack)
11. [Deployment Architecture](#deployment-architecture)
12. [Security Considerations](#security-considerations)

---

## Overview

This application provides **real-time video captioning** for visually impaired users. It captures live camera feeds, processes video frames using machine learning models, generates descriptive captions, and delivers them via text-to-speech (TTS).

### Key Features

- Real-time video streaming via WebRTC
- ML-powered scene description using Microsoft's GIT model
- Text-to-speech output for accessibility
- Low-latency peer-to-peer communication
- Cross-platform mobile support (Flutter)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT (Flutter App)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Camera    │  │   WebRTC    │  │     TTS     │  │    UI Components    │ │
│  │   Capture   │──│   Client    │──│   Engine    │──│   (Provider State)  │ │
│  └─────────────┘  └──────┬──────┘  └─────────────┘  └─────────────────────┘ │
│                          │                                                   │
│                          │ Video Track + Data Channel                        │
└──────────────────────────┼──────────────────────────────────────────────────┘
                           │
                           │ WebRTC (UDP/DTLS-SRTP)
                           │
┌──────────────────────────┼──────────────────────────────────────────────────┐
│                          │           SERVER (Python/aiohttp)                 │
├──────────────────────────┼──────────────────────────────────────────────────┤
│                          ▼                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         WebRTC Layer                                 │    │
│  │  ┌─────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │    │
│  │  │   Signaling │  │  Peer Connection │  │   VideoCaptionTrack    │  │    │
│  │  │   (HTTP)    │  │    Management    │  │   (Frame Processing)   │  │    │
│  │  └─────────────┘  └─────────────────┘  └───────────┬─────────────┘  │    │
│  └────────────────────────────────────────────────────┼────────────────┘    │
│                                                       │                      │
│                                                       ▼                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         ML Pipeline                                  │    │
│  │  ┌─────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │    │
│  │  │   Frame     │  │   GIT Model     │  │   Caption Generator     │  │    │
│  │  │   Buffer    │──│   (Transformer) │──│   (Text Output)         │  │    │
│  │  └─────────────┘  └─────────────────┘  └─────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      Supporting Services                             │    │
│  │  ┌─────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │    │
│  │  │   Logging   │  │   Config/Env    │  │   Model Manager         │  │    │
│  │  │   Service   │  │   Settings      │  │   (Singleton)           │  │    │
│  │  └─────────────┘  └─────────────────┘  └─────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Diagram

```
                    ┌────────────────────────────────────┐
                    │           Flutter App              │
                    │  ┌──────────────────────────────┐  │
                    │  │      P2PVideo Widget         │  │
                    │  │  ┌────────┐  ┌────────────┐  │  │
                    │  │  │ Camera │  │ RTCVideo   │  │  │
                    │  │  │ Preview│  │ Renderer   │  │  │
                    │  │  └────────┘  └────────────┘  │  │
                    │  │  ┌────────────────────────┐  │  │
                    │  │  │  Caption Display +     │  │  │
                    │  │  │  TTS Controller        │  │  │
                    │  │  └────────────────────────┘  │  │
                    │  └──────────────────────────────┘  │
                    └─────────────────┬──────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │   HTTP POST     │   WebRTC        │
                    │   /offer        │   Media/Data    │
                    └─────────────────┼─────────────────┘
                                      │
                    ┌─────────────────┴──────────────────┐
                    │           Python Server            │
                    │  ┌──────────────────────────────┐  │
                    │  │        API Layer             │  │
                    │  │  ┌────────┐  ┌────────────┐  │  │
                    │  │  │/offer  │  │/change_model│  │  │
                    │  │  └────────┘  └────────────┘  │  │
                    │  └──────────────────────────────┘  │
                    │  ┌──────────────────────────────┐  │
                    │  │      WebRTC Layer            │  │
                    │  │  ┌────────────────────────┐  │  │
                    │  │  │  RTCPeerConnection     │  │  │
                    │  │  │  VideoCaptionTrack     │  │  │
                    │  │  │  DataChannel           │  │  │
                    │  │  └────────────────────────┘  │  │
                    │  └──────────────────────────────┘  │
                    │  ┌──────────────────────────────┐  │
                    │  │        ML Layer              │  │
                    │  │  ┌────────────────────────┐  │  │
                    │  │  │  ModelManager          │  │  │
                    │  │  │  ├─ GIT Model          │  │  │
                    │  │  │  ├─ Processor          │  │  │
                    │  │  │  └─ Frame Buffer       │  │  │
                    │  │  └────────────────────────┘  │  │
                    │  └──────────────────────────────┘  │
                    └────────────────────────────────────┘
```

---

## Backend Architecture

### Module Structure

```
src/scene_descriptor/
├── __init__.py              # Package initialization
├── __main__.py              # CLI entry point
│
├── config/                  # Configuration
│   ├── settings.py          # Pydantic settings (env vars)
│   └── constants.py         # ML hyperparameters
│
├── models/                  # ML Components
│   ├── model_manager.py     # Singleton model loader
│   └── processor.py         # Frame processing utilities
│
├── services/                # Business Logic
│   ├── caption_service.py   # Caption generation service
│   └── video_service.py     # Video processing service
│
├── webrtc/                  # WebRTC Components
│   ├── tracks.py            # VideoCaptionTrack
│   ├── connection.py        # Peer connection management
│   └── channels.py          # Data channel handling
│
├── api/                     # HTTP Layer
│   ├── routes.py            # Route definitions
│   ├── handlers.py          # Request handlers
│   └── middleware.py        # CORS, logging middleware
│
├── utils/                   # Utilities
│   ├── logging.py           # Logging configuration
│   ├── exceptions.py        # Custom exceptions
│   └── state.py             # UseState reactive class
│
└── enums/                   # Enumerations
    └── status.py            # Connection/model status
```

### Key Classes

#### ModelManager (Singleton)

```python
class ModelManager:
    """Manages ML model lifecycle and inference."""

    _instance: Optional['ModelManager'] = None

    # Attributes
    model: Optional[AutoModelForCausalLM]
    processor: Optional[AutoProcessor]
    device: str  # 'cuda:0' or 'cpu'
    current_model: str  # 'git' or 'pulchowk'

    # Methods
    def initialize(model_dir: Path) -> None
    def generate_caption(frames: List[np.ndarray]) -> str
    def switch_model(model_name: str) -> bool
```

#### VideoCaptionTrack

```python
class VideoCaptionTrack(MediaStreamTrack):
    """Processes incoming video and generates captions."""

    kind = "video"

    # Attributes
    track: MediaStreamTrack      # Input video track
    frame_buffer: List[Frame]    # Buffered frames
    data_channel: RTCDataChannel # For sending captions

    # Methods
    async def recv() -> Frame    # Process and forward frames
    def _should_generate() -> bool
    async def _generate_and_send() -> None
```

#### Settings (Pydantic)

```python
class Settings(BaseSettings):
    """Application configuration via environment variables."""

    # Server
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False

    # ML
    model_dir: Path = Path("ml-models")
    default_model: str = "git"
    cuda_device: str = "cuda:0"

    # Processing
    frame_capture_seconds: int = 5
    max_caption_length: int = 20
    num_sample_frames: int = 6
```

---

## Frontend Architecture

### Widget Structure

```
lib/
├── main.dart                    # App entry point
├── config/
│   └── app_config.dart          # Environment configuration
├── constants/
│   ├── api_url.dart             # API endpoints
│   ├── colors.dart              # Theme colors
│   └── text_styles.dart         # Typography
├── screens/
│   ├── home_screen.dart         # Landing page
│   └── live_caption.dart        # Main captioning screen
├── widgets/
│   └── custom_button.dart       # Reusable UI components
└── utils/
    └── navigator.dart           # Navigation utilities
```

### State Management

The app uses Flutter's built-in state management with `StatefulWidget`:

```dart
class LiveCaptionState extends State<P2PVideo> {
  // WebRTC State
  RTCPeerConnection? _peerConnection;
  MediaStream? _localStream;
  RTCDataChannel? _dataChannel;

  // UI State
  bool _inCalling = false;
  String _caption = "";

  // TTS State
  FlutterTts flutterTts;
  TtsState ttsState = TtsState.stopped;
}
```

### AppConfig

```dart
class AppConfig {
  // Environment
  static const bool isProduction = false;

  // Server URLs
  static const String _devServerUrl = "http://192.168.1.65:8080";
  static const String _prodServerUrl = "https://api.example.com";

  static String get serverUrl =>
      isProduction ? _prodServerUrl : _devServerUrl;

  // Endpoints
  static String get offerUrl => "$serverUrl/offer";
  static String get changeModelUrl => "$serverUrl/change_model";
}
```

---

## Data Flow

### Caption Generation Flow

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ Camera  │───▶│ WebRTC  │───▶│ Frame   │───▶│   ML    │───▶│ Caption │
│ Capture │    │ Stream  │    │ Buffer  │    │ Model   │    │  Text   │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └────┬────┘
                                                                  │
┌─────────┐    ┌─────────┐    ┌─────────┐                        │
│   TTS   │◀───│   UI    │◀───│  Data   │◀───────────────────────┘
│ Engine  │    │ Display │    │ Channel │
└─────────┘    └─────────┘    └─────────┘
```

### Sequence Diagram

```
┌────────┐          ┌────────┐          ┌────────┐          ┌────────┐
│ Client │          │ Server │          │ WebRTC │          │   ML   │
└───┬────┘          └───┬────┘          └───┬────┘          └───┬────┘
    │                   │                   │                   │
    │  POST /offer      │                   │                   │
    │  {sdp, type}      │                   │                   │
    │──────────────────▶│                   │                   │
    │                   │                   │                   │
    │                   │ Create PeerConn   │                   │
    │                   │──────────────────▶│                   │
    │                   │                   │                   │
    │  {sdp, type}      │                   │                   │
    │◀──────────────────│                   │                   │
    │                   │                   │                   │
    │  ICE Candidates   │                   │                   │
    │◀─────────────────▶│                   │                   │
    │                   │                   │                   │
    │  Video Frames     │                   │                   │
    │══════════════════▶│══════════════════▶│                   │
    │                   │                   │                   │
    │                   │                   │  Buffer Frames    │
    │                   │                   │──────────────────▶│
    │                   │                   │                   │
    │                   │                   │  Caption Text     │
    │                   │                   │◀──────────────────│
    │                   │                   │                   │
    │  DataChannel msg  │                   │                   │
    │◀══════════════════│◀══════════════════│                   │
    │                   │                   │                   │
    │  TTS Speak        │                   │                   │
    │◀─────────┐        │                   │                   │
    │          │        │                   │                   │
    └──────────┘        │                   │                   │
```

---

## WebRTC Signaling

### Offer/Answer Exchange

1. **Client creates offer**
   ```dart
   RTCSessionDescription offer = await _peerConnection!.createOffer();
   await _peerConnection!.setLocalDescription(offer);
   ```

2. **Client sends offer to server**
   ```dart
   final response = await http.post(
     Uri.parse(SERVER_URL + '/offer'),
     body: jsonEncode({'sdp': offer.sdp, 'type': offer.type}),
   );
   ```

3. **Server processes offer**
   ```python
   async def offer_handler(request):
       params = await request.json()
       offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

       pc = RTCPeerConnection()
       await pc.setRemoteDescription(offer)

       answer = await pc.createAnswer()
       await pc.setLocalDescription(answer)

       return web.json_response({
           "sdp": pc.localDescription.sdp,
           "type": pc.localDescription.type
       })
   ```

4. **Client sets answer**
   ```dart
   await _peerConnection!.setRemoteDescription(
     RTCSessionDescription(answer['sdp'], answer['type'])
   );
   ```

### Data Channel

Captions are sent via WebRTC DataChannel for low-latency delivery:

```python
@pc.on("datachannel")
def on_datachannel(channel):
    @channel.on("message")
    def on_message(message):
        # Handle client messages
        pass

    # Send caption
    channel.send(json.dumps({"caption": caption_text}))
```

---

## ML Pipeline

### Model: Microsoft GIT (Generative Image-to-Text)

- **Architecture**: Vision Transformer + GPT-2 decoder
- **Training**: VATEX video captioning dataset
- **Input**: 6 sampled frames from video buffer
- **Output**: Natural language description

### Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                      Frame Processing                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Frame Capture (every N seconds)                              │
│     └─▶ Collect frames into buffer                               │
│                                                                  │
│  2. Frame Sampling                                               │
│     └─▶ Select 6 evenly-spaced frames                            │
│                                                                  │
│  3. Preprocessing                                                │
│     ├─▶ Resize to 224x224                                        │
│     ├─▶ Convert BGR to RGB                                       │
│     └─▶ Normalize pixel values                                   │
│                                                                  │
│  4. Model Inference                                              │
│     ├─▶ Vision encoder extracts features                         │
│     └─▶ Language decoder generates caption                       │
│                                                                  │
│  5. Post-processing                                              │
│     └─▶ Decode tokens to text                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Inference Code

```python
def generate_caption(self, frames: List[np.ndarray]) -> str:
    # Sample frames
    indices = np.linspace(0, len(frames) - 1, self.num_frames, dtype=int)
    sampled = [frames[i] for i in indices]

    # Preprocess
    inputs = self.processor(
        images=sampled,
        return_tensors="pt"
    ).to(self.device)

    # Generate
    with torch.no_grad():
        output_ids = self.model.generate(
            **inputs,
            max_length=self.max_length,
            num_beams=4
        )

    # Decode
    caption = self.processor.decode(output_ids[0], skip_special_tokens=True)
    return caption
```

---

## Directory Structure

```
Live-Camera-Feed-Scene-Descriptor-for-Visually-Impaired/
│
├── Backend/
│   ├── src/
│   │   └── scene_descriptor/      # Main Python package
│   │       ├── __init__.py
│   │       ├── __main__.py
│   │       ├── config/
│   │       ├── models/
│   │       ├── services/
│   │       ├── webrtc/
│   │       ├── api/
│   │       ├── utils/
│   │       └── enums/
│   ├── scripts/                   # Standalone scripts
│   ├── tests/                     # Test suite
│   ├── logs/                      # Application logs
│   ├── ml-models/                 # Downloaded ML models
│   ├── venv/                      # Virtual environment
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── pyproject.toml
│   ├── Makefile
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .env.example
│
├── Frontend/
│   ├── lib/
│   │   ├── main.dart
│   │   ├── config/
│   │   ├── constants/
│   │   ├── screens/
│   │   ├── widgets/
│   │   └── utils/
│   ├── android/
│   ├── ios/
│   ├── pubspec.yaml
│   └── README.md
│
├── .claude/
│   └── commands/                  # Claude Code skills
│       ├── backend-setup.md
│       ├── backend-run.md
│       ├── backend-test.md
│       └── ...
│
├── CLAUDE.md                      # Project instructions
├── ARCHITECTURE.md                # This document
└── README.md                      # Project overview
```

---

## Technology Stack

### Backend

| Component | Technology | Version |
|-----------|------------|---------|
| Runtime | Python | 3.10+ |
| Web Framework | aiohttp | 3.9+ |
| WebRTC | aiortc | 1.9+ |
| ML Framework | PyTorch | 2.2+ |
| Transformers | HuggingFace | 4.40+ |
| Configuration | Pydantic | 2.7+ |
| Image Processing | OpenCV, Pillow | Latest |

### Frontend

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | Flutter | 3.x |
| Language | Dart | 3.x |
| WebRTC | flutter_webrtc | Latest |
| TTS | flutter_tts | Latest |
| HTTP | http package | Latest |
| State | StatefulWidget | Built-in |

### Infrastructure

| Component | Technology |
|-----------|------------|
| Containerization | Docker |
| Process Management | systemd / supervisord |
| Reverse Proxy | nginx (optional) |
| SSL/TLS | Let's Encrypt (production) |

---

## Deployment Architecture

### Development

```
┌─────────────────┐     ┌─────────────────┐
│  Flutter App    │     │  Python Server  │
│  (Emulator/     │────▶│  (localhost)    │
│   Device)       │     │                 │
└─────────────────┘     └─────────────────┘
```

### Production

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Mobile App    │     │     nginx       │     │  Python Server  │
│   (iOS/Android) │────▶│  (SSL termination│────▶│  (Docker/PM2)   │
│                 │     │   + reverse proxy)│    │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │   GPU Server    │
                                                │  (CUDA-enabled) │
                                                └─────────────────┘
```

### Docker Deployment

```yaml
# docker-compose.yml
services:
  scene-descriptor:
    build: ./Backend
    ports:
      - "8080:8080"
    volumes:
      - ./ml-models:/app/ml-models
      - ./logs:/app/logs
    environment:
      - HOST=0.0.0.0
      - PORT=8080
      - LOG_LEVEL=INFO
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]  # For CUDA
```

---

## Security Considerations

### Network Security

1. **HTTPS/WSS**: Use SSL certificates in production
2. **CORS**: Configured to allow only trusted origins
3. **WebRTC**: DTLS-SRTP encryption for media streams

### Application Security

1. **Input Validation**: All API inputs validated via Pydantic
2. **Rate Limiting**: Prevent DoS attacks (implement in production)
3. **Authentication**: Add JWT/OAuth for multi-user scenarios

### Data Privacy

1. **No Storage**: Video frames are processed in-memory only
2. **No Logging of PII**: Captions are not logged by default
3. **Local Processing**: ML inference happens on-device/server

---

## Performance Considerations

### Latency Optimization

| Stage | Target Latency |
|-------|---------------|
| Video capture → Server | < 100ms |
| Frame buffering | 5 seconds (configurable) |
| ML inference (GPU) | 200-500ms |
| ML inference (CPU) | 1-3 seconds |
| Caption → TTS | < 50ms |

### Resource Usage

| Resource | Typical Usage |
|----------|---------------|
| CPU (inference) | 50-100% (single core) |
| GPU Memory | ~2GB (GIT model) |
| RAM | ~1GB (model loaded) |
| Network | ~1-2 Mbps (video stream) |

### Scaling Strategies

1. **Horizontal**: Multiple server instances behind load balancer
2. **GPU Pooling**: Shared GPU resources for inference
3. **Model Optimization**: Quantization, ONNX export

---

## Future Enhancements

1. **Multi-language Support**: Captions in different languages
2. **Custom Models**: Fine-tuned models for specific domains
3. **Offline Mode**: On-device inference with TensorFlow Lite
4. **Object Detection**: Highlight specific objects in scene
5. **Audio Description**: Include ambient sound descriptions

---

*Last Updated: January 2026*
