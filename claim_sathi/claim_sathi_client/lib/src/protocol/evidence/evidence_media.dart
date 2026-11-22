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

/// Evidence media item captured via camera or uploaded as proof.
abstract class EvidenceMedia
    implements _isc.SerializableModel, _isc.ProtocolSerialization {
  EvidenceMedia._({
    this.id,
    required this.title,
    required this.category,
    required this.mediaType,
    required this.dataBase64,
    this.notes,
    required this.timestamp,
  });

  factory EvidenceMedia({
    int? id,
    required String title,
    required String category,
    required String mediaType,
    required String dataBase64,
    String? notes,
    required DateTime timestamp,
  }) = _EvidenceMediaImpl;

  factory EvidenceMedia.fromJson(Map<String, dynamic> jsonSerialization) {
    return EvidenceMedia(
      id: jsonSerialization['id'] as int?,
      title: jsonSerialization['title'] as String,
      category: jsonSerialization['category'] as String,
      mediaType: jsonSerialization['mediaType'] as String,
      dataBase64: jsonSerialization['dataBase64'] as String,
      notes: jsonSerialization['notes'] as String?,
      timestamp: _isc.DateTimeJsonExtension.fromJson(
        jsonSerialization['timestamp'],
      ),
    );
  }

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  /// User-assigned or auto-generated title for this evidence item.
  String title;

  /// Category: vehicle_damage, hospital_bill, rejection_letter, prescription, other.
  String category;

  /// Media format: image, audio, or document.
  String mediaType;

  /// Base64 data payload or image data URI.
  String dataBase64;

  /// Optional user notes or voice transcript.
  String? notes;

  /// Timestamp when the evidence was recorded.
  DateTime timestamp;

  /// Returns a shallow copy of this [EvidenceMedia]
  /// with some or all fields replaced by the given arguments.
  @_isc.useResult
  EvidenceMedia copyWith({
    int? id,
    String? title,
    String? category,
    String? mediaType,
    String? dataBase64,
    String? notes,
    DateTime? timestamp,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      '__className__': 'EvidenceMedia',
      if (id != null) 'id': id,
      'title': title,
      'category': category,
      'mediaType': mediaType,
      'dataBase64': dataBase64,
      if (notes != null) 'notes': notes,
      'timestamp': timestamp.toJson(),
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      '__className__': 'EvidenceMedia',
      if (id != null) 'id': id,
      'title': title,
      'category': category,
      'mediaType': mediaType,
      'dataBase64': dataBase64,
      if (notes != null) 'notes': notes,
      'timestamp': timestamp.toJson(),
    };
  }

  @override
  String toString() {
    return _isc.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _EvidenceMediaImpl extends EvidenceMedia {
  _EvidenceMediaImpl({
    int? id,
    required String title,
    required String category,
    required String mediaType,
    required String dataBase64,
    String? notes,
    required DateTime timestamp,
  }) : super._(
         id: id,
         title: title,
         category: category,
         mediaType: mediaType,
         dataBase64: dataBase64,
         notes: notes,
         timestamp: timestamp,
       );

  /// Returns a shallow copy of this [EvidenceMedia]
  /// with some or all fields replaced by the given arguments.
  @_isc.useResult
  @override
  EvidenceMedia copyWith({
    Object? id = _Undefined,
    String? title,
    String? category,
    String? mediaType,
    String? dataBase64,
    Object? notes = _Undefined,
    DateTime? timestamp,
  }) {
    return EvidenceMedia(
      id: id is int? ? id : this.id,
      title: title ?? this.title,
      category: category ?? this.category,
      mediaType: mediaType ?? this.mediaType,
      dataBase64: dataBase64 ?? this.dataBase64,
      notes: notes is String? ? notes : this.notes,
      timestamp: timestamp ?? this.timestamp,
    );
  }
}
