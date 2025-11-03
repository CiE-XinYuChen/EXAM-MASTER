import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:video_player/video_player.dart';
import 'package:chewie/chewie.dart';
import '../../../core/constants/api_constants.dart';

/// Rich Content Viewer
/// 富文本内容查看器 - 支持Markdown、图片、音频、视频
class RichContentViewer extends StatelessWidget {
  final String content;
  final TextStyle? textStyle;

  const RichContentViewer({
    super.key,
    required this.content,
    this.textStyle,
  });

  @override
  Widget build(BuildContext context) {
    // Parse content for media resources
    final parsedContent = _parseContent(content);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: parsedContent,
    );
  }

  List<Widget> _parseContent(String content) {
    final widgets = <Widget>[];

    // Split content by resource markers
    final resourcePattern = RegExp(
      r'\[(?<type>音频|视频)\]\((?<url>[^\)]+)\)|'
      r'!\[(?<altText>[^\]]*)\]\((?<imageUrl>[^\)]+)\)'
    );

    int lastIndex = 0;
    final matches = resourcePattern.allMatches(content);

    for (final match in matches) {
      // Add text before the match
      if (match.start > lastIndex) {
        final textBefore = content.substring(lastIndex, match.start);
        if (textBefore.trim().isNotEmpty) {
          widgets.add(_buildMarkdownText(textBefore));
        }
      }

      // Add resource widget based on type
      final type = match.namedGroup('type');
      final url = match.namedGroup('url');
      final imageUrl = match.namedGroup('imageUrl');
      final altText = match.namedGroup('altText');

      if (type == '音频' && url != null) {
        widgets.add(_buildAudioPlayer(url));
        widgets.add(const SizedBox(height: 12));
      } else if (type == '视频' && url != null) {
        widgets.add(_buildVideoPlayer(url));
        widgets.add(const SizedBox(height: 12));
      } else if (imageUrl != null) {
        widgets.add(_buildImage(imageUrl, altText));
        widgets.add(const SizedBox(height: 12));
      }

      lastIndex = match.end;
    }

    // Add remaining text
    if (lastIndex < content.length) {
      final remaining = content.substring(lastIndex);
      if (remaining.trim().isNotEmpty) {
        widgets.add(_buildMarkdownText(remaining));
      }
    }

    // If no resources found, just return markdown text
    if (widgets.isEmpty) {
      widgets.add(_buildMarkdownText(content));
    }

    return widgets;
  }

  Widget _buildMarkdownText(String text) {
    return MarkdownBody(
      data: text,
      selectable: true,
      styleSheet: MarkdownStyleSheet(
        p: textStyle ?? const TextStyle(fontSize: 16, height: 1.5),
        code: const TextStyle(
          fontFamily: 'monospace',
          backgroundColor: Color(0xFFF5F5F5),
        ),
        codeblockDecoration: BoxDecoration(
          color: const Color(0xFFF5F5F5),
          borderRadius: BorderRadius.circular(4),
        ),
      ),
    );
  }

  Widget _buildImage(String url, String? altText) {
    final fullUrl = _getFullResourceUrl(url);

    return Container(
      constraints: const BoxConstraints(maxWidth: 600),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: CachedNetworkImage(
              imageUrl: fullUrl,
              fit: BoxFit.contain,
              placeholder: (context, url) => Container(
                height: 200,
                color: Colors.grey.shade200,
                child: const Center(
                  child: CircularProgressIndicator(),
                ),
              ),
              errorWidget: (context, url, error) => Container(
                height: 200,
                color: Colors.grey.shade200,
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.broken_image, size: 48, color: Colors.grey.shade400),
                    const SizedBox(height: 8),
                    Text(
                      '图片加载失败',
                      style: TextStyle(color: Colors.grey.shade600),
                    ),
                  ],
                ),
              ),
            ),
          ),
          if (altText != null && altText.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(
              altText,
              style: TextStyle(
                fontSize: 13,
                color: Colors.grey.shade600,
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildAudioPlayer(String url) {
    return AudioPlayerWidget(url: _getFullResourceUrl(url));
  }

  Widget _buildVideoPlayer(String url) {
    return VideoPlayerWidget(url: _getFullResourceUrl(url));
  }

  String _getFullResourceUrl(String url) {
    // If URL is already absolute, return as is
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url;
    }

    // Otherwise, construct full URL from base
    return '${ApiConstants.baseUrl}$url';
  }
}

/// Audio Player Widget
class AudioPlayerWidget extends StatefulWidget {
  final String url;

  const AudioPlayerWidget({super.key, required this.url});

  @override
  State<AudioPlayerWidget> createState() => _AudioPlayerWidgetState();
}

class _AudioPlayerWidgetState extends State<AudioPlayerWidget> {
  late AudioPlayer _audioPlayer;
  bool _isPlaying = false;
  Duration _duration = Duration.zero;
  Duration _position = Duration.zero;

  @override
  void initState() {
    super.initState();
    _audioPlayer = AudioPlayer();
    _audioPlayer.setSourceUrl(widget.url);

    _audioPlayer.onDurationChanged.listen((duration) {
      setState(() {
        _duration = duration;
      });
    });

    _audioPlayer.onPositionChanged.listen((position) {
      setState(() {
        _position = position;
      });
    });

    _audioPlayer.onPlayerStateChanged.listen((state) {
      setState(() {
        _isPlaying = state == PlayerState.playing;
      });
    });
  }

  @override
  void dispose() {
    _audioPlayer.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey.shade100,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade300),
      ),
      child: Row(
        children: [
          IconButton(
            icon: Icon(_isPlaying ? Icons.pause : Icons.play_arrow),
            onPressed: () {
              if (_isPlaying) {
                _audioPlayer.pause();
              } else {
                _audioPlayer.play(UrlSource(widget.url));
              }
            },
            color: Theme.of(context).colorScheme.primary,
          ),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SliderTheme(
                  data: SliderTheme.of(context).copyWith(
                    thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 6),
                    trackHeight: 3,
                  ),
                  child: Slider(
                    value: _position.inMilliseconds.toDouble(),
                    max: _duration.inMilliseconds.toDouble().clamp(1, double.infinity),
                    onChanged: (value) {
                      _audioPlayer.seek(Duration(milliseconds: value.toInt()));
                    },
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 8),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        _formatDuration(_position),
                        style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                      ),
                      Text(
                        _formatDuration(_duration),
                        style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _formatDuration(Duration duration) {
    String twoDigits(int n) => n.toString().padLeft(2, '0');
    final minutes = twoDigits(duration.inMinutes.remainder(60));
    final seconds = twoDigits(duration.inSeconds.remainder(60));
    return '$minutes:$seconds';
  }
}

/// Video Player Widget
class VideoPlayerWidget extends StatefulWidget {
  final String url;

  const VideoPlayerWidget({super.key, required this.url});

  @override
  State<VideoPlayerWidget> createState() => _VideoPlayerWidgetState();
}

class _VideoPlayerWidgetState extends State<VideoPlayerWidget> {
  late VideoPlayerController _videoController;
  ChewieController? _chewieController;
  bool _isInitialized = false;

  @override
  void initState() {
    super.initState();
    _initializePlayer();
  }

  Future<void> _initializePlayer() async {
    _videoController = VideoPlayerController.networkUrl(Uri.parse(widget.url));

    try {
      await _videoController.initialize();
      _chewieController = ChewieController(
        videoPlayerController: _videoController,
        autoPlay: false,
        looping: false,
        aspectRatio: _videoController.value.aspectRatio,
      );

      if (mounted) {
        setState(() {
          _isInitialized = true;
        });
      }
    } catch (e) {
      // Handle error
      if (mounted) {
        setState(() {
          _isInitialized = false;
        });
      }
    }
  }

  @override
  void dispose() {
    _videoController.dispose();
    _chewieController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!_isInitialized || _chewieController == null) {
      return Container(
        height: 200,
        decoration: BoxDecoration(
          color: Colors.grey.shade200,
          borderRadius: BorderRadius.circular(12),
        ),
        child: const Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
      ),
      clipBehavior: Clip.antiAlias,
      child: AspectRatio(
        aspectRatio: _videoController.value.aspectRatio,
        child: Chewie(controller: _chewieController!),
      ),
    );
  }
}
