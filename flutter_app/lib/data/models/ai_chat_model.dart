import 'package:json_annotation/json_annotation.dart';
import 'package:equatable/equatable.dart';

part 'ai_chat_model.g.dart';

/// Message Role Enum
enum MessageRole {
  @JsonValue('user')
  user,
  @JsonValue('assistant')
  assistant,
  @JsonValue('system')
  system,
}

/// AI Chat Message Model
/// AI对话消息模型
@JsonSerializable()
class ChatMessageModel extends Equatable {
  final String id;
  @JsonKey(name: 'session_id')
  final String sessionId;
  final MessageRole role;
  final String content;
  @JsonKey(name: 'tool_calls')
  final List<Map<String, dynamic>>? toolCalls;
  @JsonKey(name: 'created_at')
  final String createdAt;

  const ChatMessageModel({
    required this.id,
    required this.sessionId,
    required this.role,
    required this.content,
    this.toolCalls,
    required this.createdAt,
  });

  factory ChatMessageModel.fromJson(Map<String, dynamic> json) =>
      _$ChatMessageModelFromJson(json);

  Map<String, dynamic> toJson() => _$ChatMessageModelToJson(this);

  @override
  List<Object?> get props => [
        id,
        sessionId,
        role,
        content,
        toolCalls,
        createdAt,
      ];

  bool get isUser => role == MessageRole.user;
  bool get isAssistant => role == MessageRole.assistant;
  bool get hasToolCalls => toolCalls != null && toolCalls!.isNotEmpty;
}

/// AI Chat Session Model
/// AI对话会话模型
@JsonSerializable()
class ChatSessionModel extends Equatable {
  final String id;
  @JsonKey(name: 'user_id')
  final int userId;
  final String title;
  @JsonKey(name: 'ai_config_id')
  final String? aiConfigId;
  @JsonKey(name: 'message_count')
  final int messageCount;
  @JsonKey(name: 'created_at')
  final String createdAt;
  @JsonKey(name: 'updated_at')
  final String updatedAt;
  final List<ChatMessageModel>? messages;

  const ChatSessionModel({
    required this.id,
    required this.userId,
    required this.title,
    this.aiConfigId,
    required this.messageCount,
    required this.createdAt,
    required this.updatedAt,
    this.messages,
  });

  factory ChatSessionModel.fromJson(Map<String, dynamic> json) =>
      _$ChatSessionModelFromJson(json);

  Map<String, dynamic> toJson() => _$ChatSessionModelToJson(this);

  @override
  List<Object?> get props => [
        id,
        userId,
        title,
        aiConfigId,
        messageCount,
        createdAt,
        updatedAt,
        messages,
      ];
}

/// Send Message Request
@JsonSerializable()
class SendMessageRequest {
  final String message;
  @JsonKey(name: 'enable_tools')
  final bool? enableTools;

  const SendMessageRequest({
    required this.message,
    this.enableTools,
  });

  Map<String, dynamic> toJson() => _$SendMessageRequestToJson(this);
}

/// Send Message Response
@JsonSerializable()
class SendMessageResponse extends Equatable {
  final bool success;
  final String response;
  @JsonKey(name: 'tool_calls')
  final List<Map<String, dynamic>>? toolCalls;
  @JsonKey(name: 'total_iterations')
  final int? totalIterations;
  @JsonKey(name: 'message_id')
  final String? messageId;

  const SendMessageResponse({
    required this.success,
    required this.response,
    this.toolCalls,
    this.totalIterations,
    this.messageId,
  });

  factory SendMessageResponse.fromJson(Map<String, dynamic> json) =>
      _$SendMessageResponseFromJson(json);

  Map<String, dynamic> toJson() => _$SendMessageResponseToJson(this);

  @override
  List<Object?> get props => [
        success,
        response,
        toolCalls,
        totalIterations,
        messageId,
      ];
}

/// Create Chat Session Request
@JsonSerializable()
class CreateChatSessionRequest {
  final String title;
  @JsonKey(name: 'ai_config_id')
  final String? aiConfigId;

  const CreateChatSessionRequest({
    required this.title,
    this.aiConfigId,
  });

  Map<String, dynamic> toJson() => _$CreateChatSessionRequestToJson(this);
}

/// Create Chat Session Response
@JsonSerializable()
class CreateChatSessionResponse extends Equatable {
  final bool success;
  @JsonKey(name: 'session_id')
  final String sessionId;
  final String? message;

  const CreateChatSessionResponse({
    required this.success,
    required this.sessionId,
    this.message,
  });

  factory CreateChatSessionResponse.fromJson(Map<String, dynamic> json) =>
      _$CreateChatSessionResponseFromJson(json);

  Map<String, dynamic> toJson() => _$CreateChatSessionResponseToJson(this);

  @override
  List<Object?> get props => [success, sessionId, message];
}

/// Chat Session List Response
@JsonSerializable()
class ChatSessionListResponse extends Equatable {
  final List<ChatSessionModel> sessions;
  final int total;

  const ChatSessionListResponse({
    required this.sessions,
    required this.total,
  });

  factory ChatSessionListResponse.fromJson(Map<String, dynamic> json) =>
      _$ChatSessionListResponseFromJson(json);

  Map<String, dynamic> toJson() => _$ChatSessionListResponseToJson(this);

  @override
  List<Object?> get props => [sessions, total];
}

/// Chat Message List Response
@JsonSerializable()
class ChatMessageListResponse extends Equatable {
  final List<ChatMessageModel> messages;
  final int total;

  const ChatMessageListResponse({
    required this.messages,
    required this.total,
  });

  factory ChatMessageListResponse.fromJson(Map<String, dynamic> json) =>
      _$ChatMessageListResponseFromJson(json);

  Map<String, dynamic> toJson() => _$ChatMessageListResponseToJson(this);

  @override
  List<Object?> get props => [messages, total];
}
