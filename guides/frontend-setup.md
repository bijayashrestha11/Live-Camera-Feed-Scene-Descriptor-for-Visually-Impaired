# Frontend Setup Guide

Guide to run the Flutter frontend for the Live Camera Feed Scene Descriptor project.

## Prerequisites

- macOS (Apple Silicon or Intel)
- Flutter SDK 3.x+
- A Chromium-based browser (Chrome, Edge, Brave, Arc) for web development
- Xcode (for iOS/macOS builds)

## Install Flutter

### Option 1: Homebrew (Recommended)

```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add Homebrew to PATH (Apple Silicon)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# Install Flutter
brew install --cask flutter
```

### Option 2: Manual Installation

Download from https://docs.flutter.dev/get-started/install/macos

### Add Flutter to PATH

Add to `~/.zshrc`:

```bash
export PATH="/opt/homebrew/Caskroom/flutter/3.38.9/flutter/bin:$PATH"
```

Then reload:

```bash
source ~/.zshrc
```

### Verify Installation

```bash
flutter doctor
```

## Project Setup

### 1. Navigate to Frontend Directory

```bash
cd /path/to/Live-Camera-Feed-Scene-Descriptor-for-Visually-Impaired/Frontend
```

### 2. Install Dependencies

```bash
flutter pub get
```

### 3. Check for Outdated Packages (Optional)

```bash
flutter pub outdated
```

## Running the App

### Web (Development)

```bash
flutter run -d web-server --web-port=3000
```

Then open http://localhost:3000 in a Chromium-based browser.

**Browser Compatibility:**

| Browser | Support |
|---------|---------|
| Chrome, Edge, Brave, Arc | Full |
| Safari | Partial |
| Firefox, Zen | Limited |

### macOS Desktop

Requires Xcode installed.

```bash
flutter run -d macos
```

### iOS Device

Requires:
- Xcode (from App Store)
- CocoaPods (`sudo gem install cocoapods`)
- Developer Mode enabled on iPhone

```bash
# Setup Xcode
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -runFirstLaunch

# Run on connected iPhone
flutter run -d ios
```

### List Available Devices

```bash
flutter devices
```

## Backend Requirement

The app requires the backend server running at `http://localhost:8080`.

Start the backend first:

```bash
cd ../Backend
source venv/bin/activate
PYTHONPATH=src python -m scene_descriptor --host 0.0.0.0 --port 8080
```

## Stopping the Server

```bash
# Stop Flutter web server
pkill -f "flutter.*web-server"

# Or by port
lsof -ti:3000 | xargs kill -9
```

## Troubleshooting

### Flutter not found

Ensure Flutter is in your PATH:

```bash
echo 'export PATH="/opt/homebrew/Caskroom/flutter/3.38.9/flutter/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Port already in use

```bash
lsof -ti:3000 | xargs kill -9
```

### Dependency errors

```bash
flutter clean
flutter pub get
```

### Web page blank/not loading

- Use a Chromium-based browser (Chrome, Edge, Brave)
- Check browser console for errors (F12 > Console)
- Ensure backend is running

### iOS device not detected

1. Trust the computer on your iPhone
2. Enable Developer Mode: Settings > Privacy & Security > Developer Mode
3. Restart Flutter: `flutter devices`
