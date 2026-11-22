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

/// Legal claim audit verdict reconciled from camera documents and voice statements.
abstract class ClaimVerdict
    implements _isc.SerializableModel, _isc.ProtocolSerialization {
  ClaimVerdict._({
    this.id,
    required this.claimNumber,
    required this.policyholderName,
    required this.insurerName,
    required this.claimedAmount,
    required this.verdictStatus,
    required this.disputedClause,
    required this.legalBasis,
    required this.spokenDefenseHindi,
    required this.spokenDefenseEnglish,
    required this.grievanceLetterMarkdown,
    required this.evidenceCount,
    required this.voiceStatementsCount,
    required this.timestamp,
  });

  factory ClaimVerdict({
    int? id,
    required String claimNumber,
    required String policyholderName,
    required String insurerName,
    required double claimedAmount,
    required String verdictStatus,
    required String disputedClause,
    required String legalBasis,
    required String spokenDefenseHindi,
    required String spokenDefenseEnglish,
    required String grievanceLetterMarkdown,
    required int evidenceCount,
    required int voiceStatementsCount,
    required DateTime timestamp,
  }) = _ClaimVerdictImpl;

  factory ClaimVerdict.fromJson(Map<String, dynamic> jsonSerialization) {
    return ClaimVerdict(
      id: jsonSerialization['id'] as int?,
      claimNumber: jsonSerialization['claimNumber'] as String,
      policyholderName: jsonSerialization['policyholderName'] as String,
      insurerName: jsonSerialization['insurerName'] as String,
      claimedAmount: (jsonSerialization['claimedAmount'] as num).toDouble(),
      verdictStatus: jsonSerialization['verdictStatus'] as String,
      disputedClause: jsonSerialization['disputedClause'] as String,
      legalBasis: jsonSerialization['legalBasis'] as String,
      spokenDefenseHindi: jsonSerialization['spokenDefenseHindi'] as String,
      spokenDefenseEnglish: jsonSerialization['spokenDefenseEnglish'] as String,
      grievanceLetterMarkdown:
          jsonSerialization['grievanceLetterMarkdown'] as String,
      evidenceCount: jsonSerialization['evidenceCount'] as int,
      voiceStatementsCount: jsonSerialization['voiceStatementsCount'] as int,
      timestamp: _isc.DateTimeJsonExtension.fromJson(
        jsonSerialization['timestamp'],
      ),
    );
  }

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  /// Claim tracking number
  String claimNumber;

  /// Policyholder full name
  String policyholderName;

  /// Insurance provider company
  String insurerName;

  /// Total claimed medical or vehicle repair amount in INR
  double claimedAmount;

  /// Audit verdict: OVERTURN_REJECTION, FULLY_PAYABLE, DISPUTE_RECOMMENDED
  String verdictStatus;

  /// Insurance policy clause wrongfully invoked by insurer
  String disputedClause;

  /// Legal statute or IRDAI regulation protecting the policyholder
  String legalBasis;

  /// Audible verbal defense script in Hindi for playback via Speaker
  String spokenDefenseHindi;

  /// Audible verbal defense script in English for playback via Speaker
  String spokenDefenseEnglish;

  /// Formatted legal grievance notice to Insurance Ombudsman and Insurer
  String grievanceLetterMarkdown;

  /// Total count of supporting camera evidence items linked
  int evidenceCount;

  /// Total count of supporting voice statements linked
  int voiceStatementsCount;

  /// Timestamp of audit evaluation
  DateTime timestamp;

  /// Returns a shallow copy of this [ClaimVerdict]
  /// with some or all fields replaced by the given arguments.
  @_isc.useResult
  ClaimVerdict copyWith({
    int? id,
    String? claimNumber,
    String? policyholderName,
    String? insurerName,
    double? claimedAmount,
    String? verdictStatus,
    String? disputedClause,
    String? legalBasis,
    String? spokenDefenseHindi,
    String? spokenDefenseEnglish,
    String? grievanceLetterMarkdown,
    int? evidenceCount,
    int? voiceStatementsCount,
    DateTime? timestamp,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      '__className__': 'ClaimVerdict',
      if (id != null) 'id': id,
      'claimNumber': claimNumber,
      'policyholderName': policyholderName,
      'insurerName': insurerName,
      'claimedAmount': claimedAmount,
      'verdictStatus': verdictStatus,
      'disputedClause': disputedClause,
      'legalBasis': legalBasis,
      'spokenDefenseHindi': spokenDefenseHindi,
      'spokenDefenseEnglish': spokenDefenseEnglish,
      'grievanceLetterMarkdown': grievanceLetterMarkdown,
      'evidenceCount': evidenceCount,
      'voiceStatementsCount': voiceStatementsCount,
      'timestamp': timestamp.toJson(),
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      '__className__': 'ClaimVerdict',
      if (id != null) 'id': id,
      'claimNumber': claimNumber,
      'policyholderName': policyholderName,
      'insurerName': insurerName,
      'claimedAmount': claimedAmount,
      'verdictStatus': verdictStatus,
      'disputedClause': disputedClause,
      'legalBasis': legalBasis,
      'spokenDefenseHindi': spokenDefenseHindi,
      'spokenDefenseEnglish': spokenDefenseEnglish,
      'grievanceLetterMarkdown': grievanceLetterMarkdown,
      'evidenceCount': evidenceCount,
      'voiceStatementsCount': voiceStatementsCount,
      'timestamp': timestamp.toJson(),
    };
  }

  @override
  String toString() {
    return _isc.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _ClaimVerdictImpl extends ClaimVerdict {
  _ClaimVerdictImpl({
    int? id,
    required String claimNumber,
    required String policyholderName,
    required String insurerName,
    required double claimedAmount,
    required String verdictStatus,
    required String disputedClause,
    required String legalBasis,
    required String spokenDefenseHindi,
    required String spokenDefenseEnglish,
    required String grievanceLetterMarkdown,
    required int evidenceCount,
    required int voiceStatementsCount,
    required DateTime timestamp,
  }) : super._(
         id: id,
         claimNumber: claimNumber,
         policyholderName: policyholderName,
         insurerName: insurerName,
         claimedAmount: claimedAmount,
         verdictStatus: verdictStatus,
         disputedClause: disputedClause,
         legalBasis: legalBasis,
         spokenDefenseHindi: spokenDefenseHindi,
         spokenDefenseEnglish: spokenDefenseEnglish,
         grievanceLetterMarkdown: grievanceLetterMarkdown,
         evidenceCount: evidenceCount,
         voiceStatementsCount: voiceStatementsCount,
         timestamp: timestamp,
       );

  /// Returns a shallow copy of this [ClaimVerdict]
  /// with some or all fields replaced by the given arguments.
  @_isc.useResult
  @override
  ClaimVerdict copyWith({
    Object? id = _Undefined,
    String? claimNumber,
    String? policyholderName,
    String? insurerName,
    double? claimedAmount,
    String? verdictStatus,
    String? disputedClause,
    String? legalBasis,
    String? spokenDefenseHindi,
    String? spokenDefenseEnglish,
    String? grievanceLetterMarkdown,
    int? evidenceCount,
    int? voiceStatementsCount,
    DateTime? timestamp,
  }) {
    return ClaimVerdict(
      id: id is int? ? id : this.id,
      claimNumber: claimNumber ?? this.claimNumber,
      policyholderName: policyholderName ?? this.policyholderName,
      insurerName: insurerName ?? this.insurerName,
      claimedAmount: claimedAmount ?? this.claimedAmount,
      verdictStatus: verdictStatus ?? this.verdictStatus,
      disputedClause: disputedClause ?? this.disputedClause,
      legalBasis: legalBasis ?? this.legalBasis,
      spokenDefenseHindi: spokenDefenseHindi ?? this.spokenDefenseHindi,
      spokenDefenseEnglish: spokenDefenseEnglish ?? this.spokenDefenseEnglish,
      grievanceLetterMarkdown:
          grievanceLetterMarkdown ?? this.grievanceLetterMarkdown,
      evidenceCount: evidenceCount ?? this.evidenceCount,
      voiceStatementsCount: voiceStatementsCount ?? this.voiceStatementsCount,
      timestamp: timestamp ?? this.timestamp,
    );
  }
}
