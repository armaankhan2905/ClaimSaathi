/* AUTOMATICALLY GENERATED CODE DO NOT MODIFY */
/*   To generate run: "serverpod generate"    */

// ignore_for_file: implementation_imports
// ignore_for_file: library_private_types_in_public_api
// ignore_for_file: non_constant_identifier_names
// ignore_for_file: public_member_api_docs
// ignore_for_file: type_literal_in_constant_pattern
// ignore_for_file: use_super_parameters
// ignore_for_file: invalid_use_of_internal_member

// ignore_for_file: no_leading_underscores_for_library_prefixes
import 'package:serverpod_client/serverpod_client.dart' as _isc;

/// Voice statement recorded via microphone (Gnani AI transcription).
abstract class VoiceStatement
    implements _isc.SerializableModel, _isc.ProtocolSerialization {
  VoiceStatement._({
    this.id,
    required this.speakerRole,
    required this.language,
    required this.durationSeconds,
    required this.transcript,
    this.extractedKeyFacts,
    required this.confidenceScore,
    this.audioDataBase64,
    required this.timestamp,
    this.claimId,
  });

  factory VoiceStatement({
    int? id,
    required String speakerRole,
    required String language,
    required int durationSeconds,
    required String transcript,
    String? extractedKeyFacts,
    required double confidenceScore,
    String? audioDataBase64,
    required DateTime timestamp,
    String? claimId,
  }) = _VoiceStatementImpl;

  factory VoiceStatement.fromJson(Map<String, dynamic> jsonSerialization) {
    return VoiceStatement(
      id: jsonSerialization['id'] as int?,
      speakerRole: jsonSerialization['speakerRole'] as String,
      language: jsonSerialization['language'] as String,
      durationSeconds: jsonSerialization['durationSeconds'] as int,
      transcript: jsonSerialization['transcript'] as String,
      extractedKeyFacts: jsonSerialization['extractedKeyFacts'] as String?,
      confidenceScore: (jsonSerialization['confidenceScore'] as num).toDouble(),
      audioDataBase64: jsonSerialization['audioDataBase64'] as String?,
      timestamp: _isc.DateTimeJsonExtension.fromJson(
        jsonSerialization['timestamp'],
      ),
      claimId: jsonSerialization['claimId'] as String?,
    );
  }

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  /// Speaker role: policyholder, attending_doctor, surveyor, eyewitness
  String speakerRole;

  /// Language: hi-IN, en-IN, hinglish
  String language;

  /// Duration of the recorded statement in seconds
  int durationSeconds;

  /// Transcribed text of the voice note
  String transcript;

  /// Key factual entities extracted from statement (e.g. onset, emergency, symptoms)
  String? extractedKeyFacts;

  /// Confidence score of the speech-to-text recognition (0.0 - 1.0)
  double confidenceScore;

  /// Base64 encoded audio or data URI
  String? audioDataBase64;

  /// Timestamp when the voice statement was recorded
  DateTime timestamp;

  /// Associated claim ID reference if available
  String? claimId;

  /// Returns a shallow copy of this [VoiceStatement]
  /// with some or all fields replaced by the given arguments.
  @_isc.useResult
  VoiceStatement copyWith({
    int? id,
    String? speakerRole,
    String? language,
    int? durationSeconds,
    String? transcript,
    String? extractedKeyFacts,
    double? confidenceScore,
    String? audioDataBase64,
    DateTime? timestamp,
    String? claimId,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      '__className__': 'VoiceStatement',
      if (id != null) 'id': id,
      'speakerRole': speakerRole,
      'language': language,
      'durationSeconds': durationSeconds,
      'transcript': transcript,
      if (extractedKeyFacts != null) 'extractedKeyFacts': extractedKeyFacts,
      'confidenceScore': confidenceScore,
      if (audioDataBase64 != null) 'audioDataBase64': audioDataBase64,
      'timestamp': timestamp.toJson(),
      if (claimId != null) 'claimId': claimId,
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      '__className__': 'VoiceStatement',
      if (id != null) 'id': id,
      'speakerRole': speakerRole,
      'language': language,
      'durationSeconds': durationSeconds,
      'transcript': transcript,
      if (extractedKeyFacts != null) 'extractedKeyFacts': extractedKeyFacts,
      'confidenceScore': confidenceScore,
      if (audioDataBase64 != null) 'audioDataBase64': audioDataBase64,
      'timestamp': timestamp.toJson(),
      if (claimId != null) 'claimId': claimId,
    };
  }

  @override
  String toString() {
    return _isc.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _VoiceStatementImpl extends VoiceStatement {
  _VoiceStatementImpl({
    int? id,
    required String speakerRole,
    required String language,
    required int durationSeconds,
    required String transcript,
    String? extractedKeyFacts,
    required double confidenceScore,
    String? audioDataBase64,
    required DateTime timestamp,
    String? claimId,
  }) : super._(
         id: id,
         speakerRole: speakerRole,
         language: language,
         durationSeconds: durationSeconds,
         transcript: transcript,
         extractedKeyFacts: extractedKeyFacts,
         confidenceScore: confidenceScore,
         audioDataBase64: audioDataBase64,
         timestamp: timestamp,
         claimId: claimId,
       );

  /// Returns a shallow copy of this [VoiceStatement]
  /// with some or all fields replaced by the given arguments.
  @_isc.useResult
  @override
  VoiceStatement copyWith({
    Object? id = _Undefined,
    String? speakerRole,
    String? language,
    int? durationSeconds,
    String? transcript,
    Object? extractedKeyFacts = _Undefined,
    double? confidenceScore,
    Object? audioDataBase64 = _Undefined,
    DateTime? timestamp,
    Object? claimId = _Undefined,
  }) {
    return VoiceStatement(
      id: id is int? ? id : this.id,
      speakerRole: speakerRole ?? this.speakerRole,
      language: language ?? this.language,
      durationSeconds: durationSeconds ?? this.durationSeconds,
      transcript: transcript ?? this.transcript,
      extractedKeyFacts: extractedKeyFacts is String?
          ? extractedKeyFacts
          : this.extractedKeyFacts,
      confidenceScore: confidenceScore ?? this.confidenceScore,
      audioDataBase64: audioDataBase64 is String?
          ? audioDataBase64
          : this.audioDataBase64,
      timestamp: timestamp ?? this.timestamp,
      claimId: claimId is String? ? claimId : this.claimId,
    );
  }
}
