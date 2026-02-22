import 'package:cammelive/config/app_config.dart';
import 'package:cammelive/constants/colors.dart';
import 'package:cammelive/constants/text_styles.dart';
import 'package:cammelive/utils/navigator.dart';
import 'package:cammelive/widgets/custom_button.dart';
import 'package:flutter/material.dart';

import 'package:flutter_tts/flutter_tts.dart';
// import 'package:flutter_tts/flutter_tts.dart';

import 'dart:async';
import 'dart:convert';

import 'package:flutter_webrtc/flutter_webrtc.dart';
import 'package:http/http.dart' as http;

class P2PVideo extends StatefulWidget {
  const P2PVideo({Key? key}) : super(key: key);

  /// Server URL from configuration - update in lib/config/app_config.dart
  static String get SERVER_URL => AppConfig.serverUrl;

  @override
  LiveCaptionState createState() => LiveCaptionState();
}

// class _LiveCaptionState {
// }

enum TtsState { playing, stopped, paused, continued }

class LiveCaptionState extends State<P2PVideo> {
  RTCPeerConnection? _peerConnection;
  final _localRenderer = RTCVideoRenderer();
  final _remoteRenderer = RTCVideoRenderer();

  MediaStream? _localStream;

  RTCDataChannelInit? _dataChannelDict;
  RTCDataChannel? _dataChannel;
  String transformType = "none";

  // MediaStream? _localStream;
  bool _inCalling = false;

  bool _loading = false;

  String _caption = "";

  TtsState _ttsstate = TtsState.stopped;

  FlutterTts flutterTts = FlutterTts();

  void setFlutterTtsConfig() async {
    await flutterTts.setLanguage('en-US');
    await flutterTts.setPitch(1);
    await flutterTts.setVolume(1.0);
    await flutterTts.setSpeechRate(0.2);
  }

  Future<void> textToSpeech(String text) async {
    print(_ttsstate);
    if (_ttsstate == TtsState.stopped) {
      setState(() {
        _ttsstate = TtsState.playing;
      });

      await flutterTts.speak(text);
      setState(() {
        _ttsstate = TtsState.stopped;
      });
    }
    print(_ttsstate);
  }

  void _onTrack(RTCTrackEvent event) {
    print("TRACK EVENT: ${event.streams.map((e) => e.id)}, ${event.track.id}");
    if (event.track.kind == "video") {
      print("HERE");
      _remoteRenderer.srcObject = event.streams[0];
      _remoteRenderer.srcObject?.getAudioTracks()[0].enabled = true;
      _remoteRenderer.srcObject?.getAudioTracks()[0].enableSpeakerphone(true);
      //setAudioDeviceInternal(device=SPEAKER_PHONE)
    }
  }

  void _onAddTrack(MediaStream stream) {
    print("ADD STREAM: ${stream.id}");
    stream
        .getTracks()
        .forEach((track) => {_peerConnection?.addTrack(track, stream)});
  }

  void _onDataChannelState(RTCDataChannelState? state) {
    switch (state) {
      case RTCDataChannelState.RTCDataChannelClosed:
        print("Camera Closed!!!!!!!");
        break;
      case RTCDataChannelState.RTCDataChannelOpen:
        print("Camera Opened!!!!!!!");
        break;
      default:
        print("Data Channel State: $state");
    }
  }

  Future<bool> _waitForGatheringComplete(_) async {
    print("WAITING FOR GATHERING COMPLETE");
    if (_peerConnection!.iceGatheringState ==
        RTCIceGatheringState.RTCIceGatheringStateComplete) {
      print("WAITING FOR GATHERING COMPLETED");
      return true;
    } else {
      // Reduced from 1 second to 100ms for faster response
      await Future.delayed(const Duration(milliseconds: 100));
      return await _waitForGatheringComplete(_);
    }
  }

  void _toggleCamera() async {
    if (_localStream == null) throw Exception('Stream is not initialized');

    final videoTrack = _localStream!
        .getVideoTracks()
        .firstWhere((track) => track.kind == 'video');
    await Helper.switchCamera(videoTrack);
  }

  Future<void> _negotiateRemoteConnection() async {
    return _peerConnection!
        .createOffer()
        .then((offer) {
          return _peerConnection!.setLocalDescription(offer);
        })
        .then(_waitForGatheringComplete)
        .then((_) async {
          var des = await _peerConnection!.getLocalDescription();
          var headers = {
            'Content-Type': 'application/json',
          };
          var request = http.Request(
            'POST',
            Uri.parse(
                '${P2PVideo.SERVER_URL}/offer'), // CHANGE URL HERE TO LOCAL SERVER
          );
          request.body = json.encode(
            {
              "sdp": des!.sdp,
              "type": des.type,
              // "video_transform": transformType,
            },
          );
          request.headers.addAll(headers);

          http.StreamedResponse response = await request.send();
          print("OFFER SENT");

          String data = "";
          print(response);
          if (response.statusCode == 200) {
            data = await response.stream.bytesToString();
            var dataMap = json.decode(data);
            print(dataMap);
            print(dataMap["type"]);
            await _peerConnection!.setRemoteDescription(
              RTCSessionDescription(
                dataMap["sdp"],
                dataMap["type"],
              ),
            );
          } else {
            print(response.reasonPhrase);
          }
        });
  }

  Future<void> _makeCall() async {
    setState(() {
      _loading = true;
    });
    var configuration = <String, dynamic>{
      'sdpSemantics': 'unified-plan',
      'iceServers': [
        {'urls': 'stun:stun.l.google.com:19302'},
        {'urls': 'stun:stun1.l.google.com:19302'},
      ],
    };

    //* Create Peer Connection
    if (_peerConnection != null) return;
    _peerConnection = await createPeerConnection(
      configuration,
    );

    _peerConnection!.onTrack = _onTrack;
    // _peerConnection!.onAddTrack = _onAddTrack;

    //* Create Data Channel
    _dataChannelDict = RTCDataChannelInit();
    _dataChannelDict!.ordered = true;
    _dataChannel = await _peerConnection!.createDataChannel(
      "chat",
      _dataChannelDict!,
    );
    _dataChannel!.onDataChannelState = _onDataChannelState;
    // _dataChannel!.onMessage = _onDataChannelMessage;
    // RTCDataChannel _dataChannel;

    _peerConnection!.onDataChannel = (channel) {
      print("DATA CHANNEL CREATED");
      _addDataChannel(channel);
    };

    final mediaConstraints = <String, dynamic>{
      'audio': false,
      'video': {
        'mandatory': {
          'minWidth':
              '224', // Provide your own width, height and frame rate here
          'minHeight': '224',
          'maxWidth':
              '224', // Provide your own width, height and frame rate here
          'maxHeight': '224',
          'minFrameRate': '30',
          'maxFrameRate': '30',
        },
        // 'facingMode': 'user',
        'facingMode': 'environment',
        'optional': [],
      }
    };

    try {
      var stream = await navigator.mediaDevices.getUserMedia(mediaConstraints);
      // _mediaDevicesList = await navigator.mediaDevices.enumerateDevices();
      _localStream = stream;
      // display the local camera feed on the preview
      _localRenderer.srcObject = _localStream;

      // Show STOP button immediately when camera starts
      if (mounted) {
        setState(() {
          _inCalling = true;
          _loading = false;
        });
      }

      stream.getTracks().forEach((element) {
        _peerConnection!.addTrack(element, stream);
      });

      print("NEGOTIATE");
      await _negotiateRemoteConnection();
    } catch (e) {
      print(e.toString());
      // Reset state if there's an error
      if (mounted) {
        setState(() {
          _inCalling = false;
          _loading = false;
        });
      }
    }
  }

  void _addDataChannel(RTCDataChannel channel) {
    _dataChannel = channel;
    _dataChannel!.onMessage = (data) {
      // yo message chai text box ko ma store garne
      print("MSG: , ${data.text}");
      flutterTts.speak(data.text);
      setState(() {
        _caption = data.text;
      });
    };
    _dataChannel!.onDataChannelState = (state) {
      print("Data channel state: $state");
    };
  }

  Future<void> _stopCall() async {
    try {
      // Stop all tracks in the local stream
      if (_localStream != null) {
        for (var track in _localStream!.getTracks()) {
          await track.stop();
        }
        await _localStream!.dispose();
        _localStream = null;
      }

      // Close data channel
      await _dataChannel?.close();
      _dataChannel = null;

      // Close peer connection
      print("close peer connection");
      await _peerConnection?.close();
      _peerConnection = null;

      // Clear the renderer
      _localRenderer.srcObject = null;

      // Reset caption
      _caption = "";
    } catch (e) {
      print(e.toString());
    }

    if (!mounted) return;
    setState(() {
      _inCalling = false;
      _loading = false;
    });
  }

  Future<void> initLocalRenderers() async {
    await _localRenderer.initialize();
  }

  @override
  void initState() {
    super.initState();

    initLocalRenderers();
    setFlutterTtsConfig();
  }

  @override
  void dispose() {
    _stopCall();
    _localRenderer.dispose();
    _remoteRenderer.dispose();
    flutterTts.stop();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    bool isStop = true;
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          onPressed: () async {
            await _stopCall();
            if (context.mounted) {
              navigateBack(context: context);
            }
          },
          icon: const Icon(
            Icons.arrow_back_ios_new_rounded,
            color: Colors.black,
          ),
        ),
      ),
      body: Padding(
        padding:
            const EdgeInsets.only(left: 25, right: 25, top: 10, bottom: 40),
        child: Column(children: [
          AspectRatio(
            aspectRatio: 1,
            child: Stack(
              children: [
                Positioned.fill(
                  child: Container(
                    color: Colors.black,
                    child: _loading
                        ? const Center(
                            child: CircularProgressIndicator(
                              strokeWidth: 4,
                            ),
                          )
                        : Container(),
                  ),
                ),
                Positioned.fill(
                  child: RTCVideoView(
                    _localRenderer,
                    // mirror: true,
                  ),
                ),
                _inCalling
                    ? Align(
                        alignment: Alignment.bottomRight,
                        child: InkWell(
                          onTap: _toggleCamera,
                          child: Container(
                            height: 50,
                            width: 50,
                            color: Colors.black26,
                            child: Center(
                              child: Icon(
                                Icons.cameraswitch,
                                color: Colors.grey,
                              ),
                            ),
                          ),
                        ),
                      )
                    : Container(),
              ],
            ),
          ),
          const SizedBox(
            height: 20,
          ),
          Container(
            width: MediaQuery.of(context).size.width,
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(20),
              color: AppColor.boxColor,
            ),
            child: Text(
              _caption,
              style: normalStyle(
                  weight: FontWeight.w500, color: AppColor.secondaryColor),
            ),
          ),
          Expanded(child: Container()),
          _inCalling
              ? SizedBox(
                  width: MediaQuery.of(context).size.width,
                  height: 50,
                  child: ElevatedButton(
                    onPressed: _stopCall,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                      shadowColor: Colors.transparent,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(40.0),
                      ),
                    ),
                    child: Text(
                      'STOP',
                      style: normalStyle(
                        weight: FontWeight.w600,
                        color: Colors.white,
                      ).copyWith(letterSpacing: 1),
                    ),
                  ),
                )
              : customButton(
                  'START',
                  width: MediaQuery.of(context).size.width,
                  onPress: _loading ? () {} : _makeCall,
                )
        ]),
      ),
    );
  }
}
