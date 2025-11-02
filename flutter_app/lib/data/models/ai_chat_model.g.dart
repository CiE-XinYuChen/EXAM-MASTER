// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ai_chat_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ChatMessageModel _$ChatMessageModelFromJson(Map<String, dynamic> json) =>
    ChatMessageModel(
      id: json['id'] as String,
      sessionId: json['session_id'] as String,
      role: $enumDecode(_$MessageRoleEnumMap, json['role']),
      content: json['content'] as String,
      toolCalls: (json['tool_calls'] as List<dynamic>?)
          ?.map((e) => e as Map<String, dynamic>)
          .toList(),
      createdAt: json['created_at'] as String,
    );

Map<String, dynamic> _$ChatMessageModelToJson(ChatMessageModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'session_id': instance.sessionId,
      'role': _$MessageRoleEnumMap[instance.role]!,
      'content': instance.content,
      'tool_calls': instance.toolCalls,
      'created_at': instance.createdAt,
    };

const _$MessageRoleEnumMap = {
  MessageRole.user: 'user',
  MessageRole.assistant: 'assistant',
  MessageRole.system: 'system',
};

ChatSessionModel _$ChatSessionModelFromJson(Map<String, dynamic> json) =>
    ChatSessionModel(
      id: json['id'] as String,
      userId: (json['user_id'] as num).toInt(),
      title: json['title'] as String,
      aiConfigId: json['ai_config_id'] as String?,
      messageCount: (json['message_count'] as num).toInt(),
      createdAt: json['created_at'] as String,
      updatedAt: json['updated_at'] as String,
      messages: (json['messages'] as List<dynamic>?)
          ?.map((e) => ChatMessageModel.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$ChatSessionModelToJson(ChatSessionModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'user_id': instance.userId,
      'title': instance.title,
      'ai_config_id': instance.aiConfigId,
      'message_count': instance.messageCount,
      'created_at': instance.createdAt,
      'updated_at': instance.updatedAt,
      'messages': instance.messages,
    };

SendMessageRequest _$SendMessageRequestFromJson(Map<String, dynamic> json) =>
    SendMessageRequest(
      message: json['message'] as String,
      enableTools: json['enable_tools'] as bool?,
    );

Map<String, dynamic> _$SendMessageRequestToJson(SendMessageRequest instance) =>
    <String, dynamic>{
      'message': instance.message,
      'enable_tools': instance.enableTools,
    };

SendMessageResponse _$SendMessageResponseFromJson(Map<String, dynamic> json) =>
    SendMessageResponse(
      success: json['success'] as bool,
      response: json['response'] as String,
      toolCalls: (json['tool_calls'] as List<dynamic>?)
          ?.map((e) => e as Map<String, dynamic>)
          .toList(),
      totalIterations: (json['total_iterations'] as num?)?.toInt(),
      messageId: json['message_id'] as String?,
    );

Map<String, dynamic> _$SendMessageResponseToJson(
  SendMessageResponse instance,
) => <String, dynamic>{
  'success': instance.success,
  'response': instance.response,
  'tool_calls': instance.toolCalls,
  'total_iterations': instance.totalIterations,
  'message_id': instance.messageId,
};

CreateChatSessionRequest _$CreateChatSessionRequestFromJson(
  Map<String, dynamic> json,
) => CreateChatSessionRequest(
  title: json['title'] as String,
  aiConfigId: json['ai_config_id'] as String?,
);

Map<String, dynamic> _$CreateChatSessionRequestToJson(
  CreateChatSessionRequest instance,
) => <String, dynamic>{
  'title': instance.title,
  'ai_config_id': instance.aiConfigId,
};

CreateChatSessionResponse _$CreateChatSessionResponseFromJson(
  Map<String, dynamic> json,
) => CreateChatSessionResponse(
  success: json['success'] as bool,
  sessionId: json['session_id'] as String,
  message: json['message'] as String?,
);

Map<String, dynamic> _$CreateChatSessionResponseToJson(
  CreateChatSessionResponse instance,
) => <String, dynamic>{
  'success': instance.success,
  'session_id': instance.sessionId,
  'message': instance.message,
};

ChatSessionListResponse _$ChatSessionListResponseFromJson(
  Map<String, dynamic> json,
) => ChatSessionListResponse(
  sessions: (json['sessions'] as List<dynamic>)
      .map((e) => ChatSessionModel.fromJson(e as Map<String, dynamic>))
      .toList(),
  total: (json['total'] as num).toInt(),
);

Map<String, dynamic> _$ChatSessionListResponseToJson(
  ChatSessionListResponse instance,
) => <String, dynamic>{'sessions': instance.sessions, 'total': instance.total};

ChatMessageListResponse _$ChatMessageListResponseFromJson(
  Map<String, dynamic> json,
) => ChatMessageListResponse(
  messages: (json['messages'] as List<dynamic>)
      .map((e) => ChatMessageModel.fromJson(e as Map<String, dynamic>))
      .toList(),
  total: (json['total'] as num).toInt(),
);

Map<String, dynamic> _$ChatMessageListResponseToJson(
  ChatMessageListResponse instance,
) => <String, dynamic>{'messages': instance.messages, 'total': instance.total};
