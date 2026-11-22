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
import 'dart:async' as _ida;
import 'package:serverpod/serverpod.dart' as _is;

/// Voice statement recorded via microphone (Gnani AI transcription).
abstract class VoiceStatement
    implements _is.TableRow<int?>, _is.ProtocolSerialization {
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
      timestamp: _is.DateTimeJsonExtension.fromJson(
        jsonSerialization['timestamp'],
      ),
      claimId: jsonSerialization['claimId'] as String?,
    );
  }

  static final t = VoiceStatementTable();

  static const db = VoiceStatementRepository._();

  @override
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

  @override
  _is.Table<int?> get table => t;

  /// Returns a shallow copy of this [VoiceStatement]
  /// with some or all fields replaced by the given arguments.
  @_is.useResult
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

  static VoiceStatementInclude include() {
    return VoiceStatementInclude._();
  }

  static VoiceStatementIncludeList includeList({
    _is.WhereExpressionBuilder<VoiceStatementTable>? where,
    int? limit,
    int? offset,
    _is.OrderByBuilder<VoiceStatementTable>? orderBy,
    _is.OrderByListBuilder<VoiceStatementTable>? orderByList,
    VoiceStatementInclude? include,
  }) {
    return VoiceStatementIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(VoiceStatement.t),
      orderByList: orderByList?.call(VoiceStatement.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _is.SerializationManager.encode(this);
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
  @_is.useResult
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

class VoiceStatementUpdateTable extends _is.UpdateTable<VoiceStatementTable> {
  VoiceStatementUpdateTable(super.table);

  _is.ColumnValue<String, String> speakerRole(String value) => _is.ColumnValue(
    table.speakerRole,
    value,
  );

  _is.ColumnValue<String, String> language(String value) => _is.ColumnValue(
    table.language,
    value,
  );

  _is.ColumnValue<int, int> durationSeconds(int value) => _is.ColumnValue(
    table.durationSeconds,
    value,
  );

  _is.ColumnValue<String, String> transcript(String value) => _is.ColumnValue(
    table.transcript,
    value,
  );

  _is.ColumnValue<String, String> extractedKeyFacts(String? value) =>
      _is.ColumnValue(
        table.extractedKeyFacts,
        value,
      );

  _is.ColumnValue<double, double> confidenceScore(double value) =>
      _is.ColumnValue(
        table.confidenceScore,
        value,
      );

  _is.ColumnValue<String, String> audioDataBase64(String? value) =>
      _is.ColumnValue(
        table.audioDataBase64,
        value,
      );

  _is.ColumnValue<DateTime, DateTime> timestamp(DateTime value) =>
      _is.ColumnValue(
        table.timestamp,
        value,
      );

  _is.ColumnValue<String, String> claimId(String? value) => _is.ColumnValue(
    table.claimId,
    value,
  );
}

class VoiceStatementTable extends _is.Table<int?> {
  VoiceStatementTable({super.tableRelation})
    : super(tableName: 'voice_statement') {
    updateTable = VoiceStatementUpdateTable(this);
    speakerRole = _is.ColumnString(
      'speakerRole',
      this,
    );
    language = _is.ColumnString(
      'language',
      this,
    );
    durationSeconds = _is.ColumnInt(
      'durationSeconds',
      this,
    );
    transcript = _is.ColumnString(
      'transcript',
      this,
    );
    extractedKeyFacts = _is.ColumnString(
      'extractedKeyFacts',
      this,
    );
    confidenceScore = _is.ColumnDouble(
      'confidenceScore',
      this,
    );
    audioDataBase64 = _is.ColumnString(
      'audioDataBase64',
      this,
    );
    timestamp = _is.ColumnDateTime(
      'timestamp',
      this,
    );
    claimId = _is.ColumnString(
      'claimId',
      this,
    );
  }

  late final VoiceStatementUpdateTable updateTable;

  /// Speaker role: policyholder, attending_doctor, surveyor, eyewitness
  late final _is.ColumnString speakerRole;

  /// Language: hi-IN, en-IN, hinglish
  late final _is.ColumnString language;

  /// Duration of the recorded statement in seconds
  late final _is.ColumnInt durationSeconds;

  /// Transcribed text of the voice note
  late final _is.ColumnString transcript;

  /// Key factual entities extracted from statement (e.g. onset, emergency, symptoms)
  late final _is.ColumnString extractedKeyFacts;

  /// Confidence score of the speech-to-text recognition (0.0 - 1.0)
  late final _is.ColumnDouble confidenceScore;

  /// Base64 encoded audio or data URI
  late final _is.ColumnString audioDataBase64;

  /// Timestamp when the voice statement was recorded
  late final _is.ColumnDateTime timestamp;

  /// Associated claim ID reference if available
  late final _is.ColumnString claimId;

  @override
  List<_is.Column> get columns => [
    id,
    speakerRole,
    language,
    durationSeconds,
    transcript,
    extractedKeyFacts,
    confidenceScore,
    audioDataBase64,
    timestamp,
    claimId,
  ];
}

class VoiceStatementInclude extends _is.IncludeObject {
  VoiceStatementInclude._();

  @override
  Map<String, _is.Include?> get includes => {};

  @override
  _is.Table<int?> get table => VoiceStatement.t;
}

class VoiceStatementIncludeList extends _is.IncludeList {
  VoiceStatementIncludeList._({
    _is.WhereExpressionBuilder<VoiceStatementTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(VoiceStatement.t);
  }

  @override
  Map<String, _is.Include?> get includes => include?.includes ?? {};

  @override
  _is.Table<int?> get table => VoiceStatement.t;
}

class VoiceStatementRepository {
  const VoiceStatementRepository._();

  /// Returns a list of [VoiceStatement]s matching the given query parameters.
  ///
  /// Use [where] to specify which items to include in the return value.
  /// If none is specified, all items will be returned.
  ///
  /// To specify the order of the items use [orderBy] or [orderByList]
  /// when sorting by multiple columns.
  ///
  /// The maximum number of items can be set by [limit]. If no limit is set,
  /// all items matching the query will be returned.
  ///
  /// [offset] defines how many items to skip, after which [limit] (or all)
  /// items are read from the database.
  ///
  /// ```dart
  /// var persons = await Persons.db.find(
  ///   session,
  ///   where: (t) => t.lastName.equals('Jones'),
  ///   orderBy: (t) => t.firstName,
  ///   limit: 100,
  /// );
  /// ```
  Future<List<VoiceStatement>> find(
    _is.DatabaseSession session, {
    _is.WhereExpressionBuilder<VoiceStatementTable>? where,
    int? limit,
    int? offset,
    _is.OrderByBuilder<VoiceStatementTable>? orderBy,
    _is.OrderByListBuilder<VoiceStatementTable>? orderByList,
    _is.Transaction? transaction,
    _is.LockMode? lockMode,
    _is.LockBehavior? lockBehavior,
  }) async {
    return session.db.find<VoiceStatement>(
      where: where?.call(VoiceStatement.t),
      orderBy: orderBy?.call(VoiceStatement.t),
      orderByList: orderByList?.call(VoiceStatement.t),
      limit: limit,
      offset: offset,
      transaction: transaction,
      lockMode: lockMode,
      lockBehavior: lockBehavior,
    );
  }

  /// Emits [VoiceStatement]s matching the given query parameters every time the
  /// source tables are modified.
  ///
  /// Use [where] to specify which items to include in the return value.
  /// If none is specified, all items will be returned.
  ///
  /// To specify the order of the items use [orderBy] or [orderByList]
  /// when sorting by multiple columns.
  ///
  /// The maximum number of items can be set by [limit]. If no limit is set,
  /// all items matching the query will be returned.
  ///
  /// [offset] defines how many items to skip, after which [limit] (or all)
  /// items are read from the database.
  ///
  /// Use [throttle] to specify the minimum interval between queries. It can
  /// also be set to `null`, in which case the stream will only be throttled
  /// when its subscription is paused.
  ///
  /// Source tables are collected from the queried table, [where], [orderBy],
  /// [orderByList], and the [include] graph. [alsoTriggerOnTables] is added
  /// to that set. Pass [Table] instances such as `VoiceStatement.t`.
  ///
  /// Raw [Expression] SQL is not inspected. Tables referenced only in raw
  /// SQL must be passed via [alsoTriggerOnTables].
  ///
  /// The stream always reads committed state and never joins an ambient
  /// [Transaction]. Emissions for a write fire after that write commits.
  ///
  /// Currently only supported on SQLite. Calling this method on PostgreSQL
  /// throws an [UnsupportedError].
  ///
  /// ```dart
  /// var subscription = Persons.db.watch(
  ///   session,
  ///   where: (t) => t.lastName.equals('Jones'),
  ///   orderBy: (t) => t.firstName,
  ///   limit: 100,
  /// ).listen((persons) {
  ///   // Handle the latest matching rows.
  /// });
  /// ```
  _ida.Stream<List<VoiceStatement>> watch(
    _is.DatabaseSession session, {
    _is.WhereExpressionBuilder<VoiceStatementTable>? where,
    int? limit,
    int? offset,
    _is.OrderByBuilder<VoiceStatementTable>? orderBy,
    _is.OrderByListBuilder<VoiceStatementTable>? orderByList,
    Duration? throttle = const Duration(milliseconds: 30),
    Iterable<_is.Table>? alsoTriggerOnTables,
  }) {
    return session.db.watch<VoiceStatement>(
      where: where?.call(VoiceStatement.t),
      orderBy: orderBy?.call(VoiceStatement.t),
      orderByList: orderByList?.call(VoiceStatement.t),
      limit: limit,
      offset: offset,
      throttle: throttle,
      alsoTriggerOnTables: alsoTriggerOnTables,
    );
  }

  /// Returns the first matching [VoiceStatement] matching the given query parameters.
  ///
  /// Use [where] to specify which items to include in the return value.
  /// If none is specified, all items will be returned.
  ///
  /// To specify the order use [orderBy] or [orderByList]
  /// when sorting by multiple columns.
  ///
  /// [offset] defines how many items to skip, after which the next one will be picked.
  ///
  /// ```dart
  /// var youngestPerson = await Persons.db.findFirstRow(
  ///   session,
  ///   where: (t) => t.lastName.equals('Jones'),
  ///   orderBy: (t) => t.age,
  /// );
  /// ```
  Future<VoiceStatement?> findFirstRow(
    _is.DatabaseSession session, {
    _is.WhereExpressionBuilder<VoiceStatementTable>? where,
    int? offset,
    _is.OrderByBuilder<VoiceStatementTable>? orderBy,
    _is.OrderByListBuilder<VoiceStatementTable>? orderByList,
    _is.Transaction? transaction,
    _is.LockMode? lockMode,
    _is.LockBehavior? lockBehavior,
  }) async {
    return session.db.findFirstRow<VoiceStatement>(
      where: where?.call(VoiceStatement.t),
      orderBy: orderBy?.call(VoiceStatement.t),
      orderByList: orderByList?.call(VoiceStatement.t),
      offset: offset,
      transaction: transaction,
      lockMode: lockMode,
      lockBehavior: lockBehavior,
    );
  }

  /// Finds a single [VoiceStatement] by its [id] or null if no such row exists.
  Future<VoiceStatement?> findById(
    _is.DatabaseSession session,
    int id, {
    _is.Transaction? transaction,
    _is.LockMode? lockMode,
    _is.LockBehavior? lockBehavior,
  }) async {
    return session.db.findById<VoiceStatement>(
      id,
      transaction: transaction,
      lockMode: lockMode,
      lockBehavior: lockBehavior,
    );
  }

  /// Inserts all [VoiceStatement]s in the list and returns the inserted rows.
  ///
  /// The returned [VoiceStatement]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  ///
  /// If [ignoreConflicts] is set to `true`, rows that conflict with existing
  /// rows are silently skipped, and only the successfully inserted rows are
  /// returned.
  ///
  /// If [noReturn] is set to `true`, the inserted rows are not read back from
  /// the database and an empty list is returned. This avoids the overhead of
  /// transferring and deserializing the rows when the result is not needed.
  Future<List<VoiceStatement>> insert(
    _is.DatabaseSession session,
    List<VoiceStatement> rows, {
    _is.Transaction? transaction,
    bool ignoreConflicts = false,
    bool noReturn = false,
  }) async {
    return session.db.insert<VoiceStatement>(
      rows,
      transaction: transaction,
      ignoreConflicts: ignoreConflicts,
      noReturn: noReturn,
    );
  }

  /// Inserts a single [VoiceStatement] and returns the inserted row.
  ///
  /// The returned [VoiceStatement] will have its `id` field set.
  Future<VoiceStatement> insertRow(
    _is.DatabaseSession session,
    VoiceStatement row, {
    _is.Transaction? transaction,
  }) async {
    return session.db.insertRow<VoiceStatement>(
      row,
      transaction: transaction,
    );
  }

  /// Upserts all [VoiceStatement]s in the list and returns the resulting rows.
  ///
  /// If a row conflicts on the given [conflictColumns], the existing row is
  /// updated with the new values. Otherwise, a new row is inserted.
  ///
  /// If [updateColumns] is provided, only those columns will be updated on
  /// conflict. If null, all non-conflict, non-id columns are updated.
  ///
  /// If [updateWhere] is provided, the update only applies to rows matching the
  /// given expression. Conflicting rows that don't match are skipped and not
  /// returned, so the resulting list may be shorter than [rows].
  ///
  /// The returned [VoiceStatement]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails,
  /// none of the rows will be affected.
  ///
  /// If [noReturn] is set to `true`, the resulting rows are not read back from
  /// the database and an empty list is returned. This avoids the overhead of
  /// transferring and deserializing the rows when the result is not needed.
  Future<List<VoiceStatement>> upsert(
    _is.DatabaseSession session,
    List<VoiceStatement> rows, {
    required _is.ColumnSelections<VoiceStatementTable> conflictColumns,
    _is.ColumnSelections<VoiceStatementTable>? updateColumns,
    _is.WhereExpressionBuilder<VoiceStatementTable>? updateWhere,
    _is.Transaction? transaction,
    bool noReturn = false,
  }) async {
    return session.db.upsert<VoiceStatement>(
      rows,
      conflictColumns: conflictColumns(VoiceStatement.t),
      updateColumns: updateColumns?.call(VoiceStatement.t),
      updateWhere: updateWhere?.call(VoiceStatement.t),
      transaction: transaction,
      noReturn: noReturn,
    );
  }

  /// Upserts a single [VoiceStatement] and returns the resulting row.
  ///
  /// If the row conflicts on the given [conflictColumns], the existing row is
  /// updated. Otherwise, a new row is inserted.
  ///
  /// If [updateColumns] is provided, only those columns will be updated on
  /// conflict. If null, all non-conflict, non-id columns are updated.
  ///
  /// If [updateWhere] is provided, the update only applies when the existing
  /// row matches the expression. Returns `null` if no row was affected — for
  /// example when [updateWhere] does not match the conflicting row.
  ///
  /// The returned [VoiceStatement] will have its `id` field set.
  Future<VoiceStatement?> upsertRow(
    _is.DatabaseSession session,
    VoiceStatement row, {
    required _is.ColumnSelections<VoiceStatementTable> conflictColumns,
    _is.ColumnSelections<VoiceStatementTable>? updateColumns,
    _is.WhereExpressionBuilder<VoiceStatementTable>? updateWhere,
    _is.Transaction? transaction,
  }) async {
    return session.db.upsertRow<VoiceStatement>(
      row,
      conflictColumns: conflictColumns(VoiceStatement.t),
      updateColumns: updateColumns?.call(VoiceStatement.t),
      updateWhere: updateWhere?.call(VoiceStatement.t),
      transaction: transaction,
    );
  }

  /// Updates all [VoiceStatement]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  ///
  /// If [noReturn] is set to `true`, the updated rows are not read back from
  /// the database and an empty list is returned. This avoids the overhead of
  /// transferring and deserializing the rows when the result is not needed.
  Future<List<VoiceStatement>> update(
    _is.DatabaseSession session,
    List<VoiceStatement> rows, {
    _is.ColumnSelections<VoiceStatementTable>? columns,
    _is.Transaction? transaction,
    bool noReturn = false,
  }) async {
    return session.db.update<VoiceStatement>(
      rows,
      columns: columns?.call(VoiceStatement.t),
      transaction: transaction,
      noReturn: noReturn,
    );
  }

  /// Updates a single [VoiceStatement]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<VoiceStatement> updateRow(
    _is.DatabaseSession session,
    VoiceStatement row, {
    _is.ColumnSelections<VoiceStatementTable>? columns,
    _is.Transaction? transaction,
  }) async {
    return session.db.updateRow<VoiceStatement>(
      row,
      columns: columns?.call(VoiceStatement.t),
      transaction: transaction,
    );
  }

  /// Updates a single [VoiceStatement] by its [id] with the specified [columnValues].
  /// Returns the updated row or null if no row with the given id exists.
  Future<VoiceStatement?> updateById(
    _is.DatabaseSession session,
    int id, {
    required _is.ColumnValueListBuilder<VoiceStatementUpdateTable> columnValues,
    _is.Transaction? transaction,
  }) async {
    return session.db.updateById<VoiceStatement>(
      id,
      columnValues: columnValues(VoiceStatement.t.updateTable),
      transaction: transaction,
    );
  }

  /// Updates all [VoiceStatement]s matching the [where] expression with the specified [columnValues].
  /// Returns the list of updated rows.
  ///
  /// If [noReturn] is set to `true`, the updated rows are not read back from
  /// the database and an empty list is returned. This avoids the overhead of
  /// transferring and deserializing the rows when the result is not needed.
  Future<List<VoiceStatement>> updateWhere(
    _is.DatabaseSession session, {
    required _is.ColumnValueListBuilder<VoiceStatementUpdateTable> columnValues,
    required _is.WhereExpressionBuilder<VoiceStatementTable> where,
    int? limit,
    int? offset,
    _is.OrderByBuilder<VoiceStatementTable>? orderBy,
    _is.OrderByListBuilder<VoiceStatementTable>? orderByList,
    _is.Transaction? transaction,
    bool noReturn = false,
  }) async {
    return session.db.updateWhere<VoiceStatement>(
      columnValues: columnValues(VoiceStatement.t.updateTable),
      where: where(VoiceStatement.t),
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(VoiceStatement.t),
      orderByList: orderByList?.call(VoiceStatement.t),
      transaction: transaction,
      noReturn: noReturn,
    );
  }

  /// Deletes all [VoiceStatement]s in the list and returns the deleted rows.
  ///
  /// To specify the order of the returned rows use [orderBy] or [orderByList]
  /// when sorting by multiple columns.
  ///
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  ///
  /// If [noReturn] is set to `true`, the deleted rows are not read back from
  /// the database and an empty list is returned. This avoids the overhead of
  /// transferring and deserializing the rows when the result is not needed.
  Future<List<VoiceStatement>> delete(
    _is.DatabaseSession session,
    List<VoiceStatement> rows, {
    _is.OrderByBuilder<VoiceStatementTable>? orderBy,
    _is.OrderByListBuilder<VoiceStatementTable>? orderByList,
    _is.Transaction? transaction,
    bool noReturn = false,
  }) async {
    return session.db.delete<VoiceStatement>(
      rows,
      orderBy: orderBy?.call(VoiceStatement.t),
      orderByList: orderByList?.call(VoiceStatement.t),
      transaction: transaction,
      noReturn: noReturn,
    );
  }

  /// Deletes a single [VoiceStatement].
  Future<VoiceStatement> deleteRow(
    _is.DatabaseSession session,
    VoiceStatement row, {
    _is.Transaction? transaction,
  }) async {
    return session.db.deleteRow<VoiceStatement>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  ///
  /// To specify the order of the returned rows use [orderBy] or [orderByList]
  /// when sorting by multiple columns.
  ///
  /// If [noReturn] is set to `true`, the deleted rows are not read back from
  /// the database and an empty list is returned. This avoids the overhead of
  /// transferring and deserializing the rows when the result is not needed.
  Future<List<VoiceStatement>> deleteWhere(
    _is.DatabaseSession session, {
    required _is.WhereExpressionBuilder<VoiceStatementTable> where,
    _is.OrderByBuilder<VoiceStatementTable>? orderBy,
    _is.OrderByListBuilder<VoiceStatementTable>? orderByList,
    _is.Transaction? transaction,
    bool noReturn = false,
  }) async {
    return session.db.deleteWhere<VoiceStatement>(
      where: where(VoiceStatement.t),
      orderBy: orderBy?.call(VoiceStatement.t),
      orderByList: orderByList?.call(VoiceStatement.t),
      transaction: transaction,
      noReturn: noReturn,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _is.DatabaseSession session, {
    _is.WhereExpressionBuilder<VoiceStatementTable>? where,
    int? limit,
    _is.Transaction? transaction,
  }) async {
    return session.db.count<VoiceStatement>(
      where: where?.call(VoiceStatement.t),
      limit: limit,
      transaction: transaction,
    );
  }

  /// Acquires row-level locks on [VoiceStatement] rows matching the [where] expression.
  Future<void> lockRows(
    _is.DatabaseSession session, {
    required _is.WhereExpressionBuilder<VoiceStatementTable> where,
    required _is.LockMode lockMode,
    required _is.Transaction transaction,
    _is.LockBehavior lockBehavior = _is.LockBehavior.wait,
  }) async {
    return session.db.lockRows<VoiceStatement>(
      where: where(VoiceStatement.t),
      lockMode: lockMode,
      lockBehavior: lockBehavior,
      transaction: transaction,
    );
  }
}
