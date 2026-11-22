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

/// Legal claim audit verdict reconciled from camera documents and voice statements.
abstract class ClaimVerdict
    implements _is.TableRow<int?>, _is.ProtocolSerialization {
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
      timestamp: _is.DateTimeJsonExtension.fromJson(
        jsonSerialization['timestamp'],
      ),
    );
  }

  static final t = ClaimVerdictTable();

  static const db = ClaimVerdictRepository._();

  @override
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

  @override
  _is.Table<int?> get table => t;

  /// Returns a shallow copy of this [ClaimVerdict]
  /// with some or all fields replaced by the given arguments.
  @_is.useResult
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

  static ClaimVerdictInclude include() {
    return ClaimVerdictInclude._();
  }

  static ClaimVerdictIncludeList includeList({
    _is.WhereExpressionBuilder<ClaimVerdictTable>? where,
    int? limit,
    int? offset,
    _is.OrderByBuilder<ClaimVerdictTable>? orderBy,
    _is.OrderByListBuilder<ClaimVerdictTable>? orderByList,
    ClaimVerdictInclude? include,
  }) {
    return ClaimVerdictIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(ClaimVerdict.t),
      orderByList: orderByList?.call(ClaimVerdict.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _is.SerializationManager.encode(this);
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
  @_is.useResult
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

class ClaimVerdictUpdateTable extends _is.UpdateTable<ClaimVerdictTable> {
  ClaimVerdictUpdateTable(super.table);

  _is.ColumnValue<String, String> claimNumber(String value) => _is.ColumnValue(
    table.claimNumber,
    value,
  );

  _is.ColumnValue<String, String> policyholderName(String value) =>
      _is.ColumnValue(
        table.policyholderName,
        value,
      );

  _is.ColumnValue<String, String> insurerName(String value) => _is.ColumnValue(
    table.insurerName,
    value,
  );

  _is.ColumnValue<double, double> claimedAmount(double value) =>
      _is.ColumnValue(
        table.claimedAmount,
        value,
      );

  _is.ColumnValue<String, String> verdictStatus(String value) =>
      _is.ColumnValue(
        table.verdictStatus,
        value,
      );

  _is.ColumnValue<String, String> disputedClause(String value) =>
      _is.ColumnValue(
        table.disputedClause,
        value,
      );

  _is.ColumnValue<String, String> legalBasis(String value) => _is.ColumnValue(
    table.legalBasis,
    value,
  );

  _is.ColumnValue<String, String> spokenDefenseHindi(String value) =>
      _is.ColumnValue(
        table.spokenDefenseHindi,
        value,
      );

  _is.ColumnValue<String, String> spokenDefenseEnglish(String value) =>
      _is.ColumnValue(
        table.spokenDefenseEnglish,
        value,
      );

  _is.ColumnValue<String, String> grievanceLetterMarkdown(String value) =>
      _is.ColumnValue(
        table.grievanceLetterMarkdown,
        value,
      );

  _is.ColumnValue<int, int> evidenceCount(int value) => _is.ColumnValue(
    table.evidenceCount,
    value,
  );

  _is.ColumnValue<int, int> voiceStatementsCount(int value) => _is.ColumnValue(
    table.voiceStatementsCount,
    value,
  );

  _is.ColumnValue<DateTime, DateTime> timestamp(DateTime value) =>
      _is.ColumnValue(
        table.timestamp,
        value,
      );
}

class ClaimVerdictTable extends _is.Table<int?> {
  ClaimVerdictTable({super.tableRelation}) : super(tableName: 'claim_verdict') {
    updateTable = ClaimVerdictUpdateTable(this);
    claimNumber = _is.ColumnString(
      'claimNumber',
      this,
    );
    policyholderName = _is.ColumnString(
      'policyholderName',
      this,
    );
    insurerName = _is.ColumnString(
      'insurerName',
      this,
    );
    claimedAmount = _is.ColumnDouble(
      'claimedAmount',
      this,
    );
    verdictStatus = _is.ColumnString(
      'verdictStatus',
      this,
    );
    disputedClause = _is.ColumnString(
      'disputedClause',
      this,
    );
    legalBasis = _is.ColumnString(
      'legalBasis',
      this,
    );
    spokenDefenseHindi = _is.ColumnString(
      'spokenDefenseHindi',
      this,
    );
    spokenDefenseEnglish = _is.ColumnString(
      'spokenDefenseEnglish',
      this,
    );
    grievanceLetterMarkdown = _is.ColumnString(
      'grievanceLetterMarkdown',
      this,
    );
    evidenceCount = _is.ColumnInt(
      'evidenceCount',
      this,
    );
    voiceStatementsCount = _is.ColumnInt(
      'voiceStatementsCount',
      this,
    );
    timestamp = _is.ColumnDateTime(
      'timestamp',
      this,
    );
  }

  late final ClaimVerdictUpdateTable updateTable;

  /// Claim tracking number
  late final _is.ColumnString claimNumber;

  /// Policyholder full name
  late final _is.ColumnString policyholderName;

  /// Insurance provider company
  late final _is.ColumnString insurerName;

  /// Total claimed medical or vehicle repair amount in INR
  late final _is.ColumnDouble claimedAmount;

  /// Audit verdict: OVERTURN_REJECTION, FULLY_PAYABLE, DISPUTE_RECOMMENDED
  late final _is.ColumnString verdictStatus;

  /// Insurance policy clause wrongfully invoked by insurer
  late final _is.ColumnString disputedClause;

  /// Legal statute or IRDAI regulation protecting the policyholder
  late final _is.ColumnString legalBasis;

  /// Audible verbal defense script in Hindi for playback via Speaker
  late final _is.ColumnString spokenDefenseHindi;

  /// Audible verbal defense script in English for playback via Speaker
  late final _is.ColumnString spokenDefenseEnglish;

  /// Formatted legal grievance notice to Insurance Ombudsman and Insurer
  late final _is.ColumnString grievanceLetterMarkdown;

  /// Total count of supporting camera evidence items linked
  late final _is.ColumnInt evidenceCount;

  /// Total count of supporting voice statements linked
  late final _is.ColumnInt voiceStatementsCount;

  /// Timestamp of audit evaluation
  late final _is.ColumnDateTime timestamp;

  @override
  List<_is.Column> get columns => [
    id,
    claimNumber,
    policyholderName,
    insurerName,
    claimedAmount,
    verdictStatus,
    disputedClause,
    legalBasis,
    spokenDefenseHindi,
    spokenDefenseEnglish,
    grievanceLetterMarkdown,
    evidenceCount,
    voiceStatementsCount,
    timestamp,
  ];
}

class ClaimVerdictInclude extends _is.IncludeObject {
  ClaimVerdictInclude._();

  @override
  Map<String, _is.Include?> get includes => {};

  @override
  _is.Table<int?> get table => ClaimVerdict.t;
}

class ClaimVerdictIncludeList extends _is.IncludeList {
  ClaimVerdictIncludeList._({
    _is.WhereExpressionBuilder<ClaimVerdictTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(ClaimVerdict.t);
  }

  @override
  Map<String, _is.Include?> get includes => include?.includes ?? {};

  @override
  _is.Table<int?> get table => ClaimVerdict.t;
}

class ClaimVerdictRepository {
  const ClaimVerdictRepository._();

  /// Returns a list of [ClaimVerdict]s matching the given query parameters.
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
  Future<List<ClaimVerdict>> find(
    _is.DatabaseSession session, {
    _is.WhereExpressionBuilder<ClaimVerdictTable>? where,
    int? limit,
    int? offset,
    _is.OrderByBuilder<ClaimVerdictTable>? orderBy,
    _is.OrderByListBuilder<ClaimVerdictTable>? orderByList,
    _is.Transaction? transaction,
    _is.LockMode? lockMode,
    _is.LockBehavior? lockBehavior,
  }) async {
    return session.db.find<ClaimVerdict>(
      where: where?.call(ClaimVerdict.t),
      orderBy: orderBy?.call(ClaimVerdict.t),
      orderByList: orderByList?.call(ClaimVerdict.t),
      limit: limit,
      offset: offset,
      transaction: transaction,
      lockMode: lockMode,
      lockBehavior: lockBehavior,
    );
  }

  /// Emits [ClaimVerdict]s matching the given query parameters every time the
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
  /// to that set. Pass [Table] instances such as `ClaimVerdict.t`.
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
  _ida.Stream<List<ClaimVerdict>> watch(
    _is.DatabaseSession session, {
    _is.WhereExpressionBuilder<ClaimVerdictTable>? where,
    int? limit,
    int? offset,
    _is.OrderByBuilder<ClaimVerdictTable>? orderBy,
    _is.OrderByListBuilder<ClaimVerdictTable>? orderByList,
    Duration? throttle = const Duration(milliseconds: 30),
    Iterable<_is.Table>? alsoTriggerOnTables,
  }) {
    return session.db.watch<ClaimVerdict>(
      where: where?.call(ClaimVerdict.t),
      orderBy: orderBy?.call(ClaimVerdict.t),
      orderByList: orderByList?.call(ClaimVerdict.t),
      limit: limit,
      offset: offset,
      throttle: throttle,
      alsoTriggerOnTables: alsoTriggerOnTables,
    );
  }

  /// Returns the first matching [ClaimVerdict] matching the given query parameters.
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
  Future<ClaimVerdict?> findFirstRow(
    _is.DatabaseSession session, {
    _is.WhereExpressionBuilder<ClaimVerdictTable>? where,
    int? offset,
    _is.OrderByBuilder<ClaimVerdictTable>? orderBy,
    _is.OrderByListBuilder<ClaimVerdictTable>? orderByList,
    _is.Transaction? transaction,
    _is.LockMode? lockMode,
    _is.LockBehavior? lockBehavior,
  }) async {
    return session.db.findFirstRow<ClaimVerdict>(
      where: where?.call(ClaimVerdict.t),
      orderBy: orderBy?.call(ClaimVerdict.t),
      orderByList: orderByList?.call(ClaimVerdict.t),
      offset: offset,
      transaction: transaction,
      lockMode: lockMode,
      lockBehavior: lockBehavior,
    );
  }

  /// Finds a single [ClaimVerdict] by its [id] or null if no such row exists.
  Future<ClaimVerdict?> findById(
    _is.DatabaseSession session,
    int id, {
    _is.Transaction? transaction,
    _is.LockMode? lockMode,
    _is.LockBehavior? lockBehavior,
  }) async {
    return session.db.findById<ClaimVerdict>(
      id,
      transaction: transaction,
      lockMode: lockMode,
      lockBehavior: lockBehavior,
    );
  }

  /// Inserts all [ClaimVerdict]s in the list and returns the inserted rows.
  ///
  /// The returned [ClaimVerdict]s will have their `id` fields set.
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
  Future<List<ClaimVerdict>> insert(
    _is.DatabaseSession session,
    List<ClaimVerdict> rows, {
    _is.Transaction? transaction,
    bool ignoreConflicts = false,
    bool noReturn = false,
  }) async {
    return session.db.insert<ClaimVerdict>(
      rows,
      transaction: transaction,
      ignoreConflicts: ignoreConflicts,
      noReturn: noReturn,
    );
  }

  /// Inserts a single [ClaimVerdict] and returns the inserted row.
  ///
  /// The returned [ClaimVerdict] will have its `id` field set.
  Future<ClaimVerdict> insertRow(
    _is.DatabaseSession session,
    ClaimVerdict row, {
    _is.Transaction? transaction,
  }) async {
    return session.db.insertRow<ClaimVerdict>(
      row,
      transaction: transaction,
    );
  }

  /// Upserts all [ClaimVerdict]s in the list and returns the resulting rows.
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
  /// The returned [ClaimVerdict]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails,
  /// none of the rows will be affected.
  ///
  /// If [noReturn] is set to `true`, the resulting rows are not read back from
  /// the database and an empty list is returned. This avoids the overhead of
  /// transferring and deserializing the rows when the result is not needed.
  Future<List<ClaimVerdict>> upsert(
    _is.DatabaseSession session,
    List<ClaimVerdict> rows, {
    required _is.ColumnSelections<ClaimVerdictTable> conflictColumns,
    _is.ColumnSelections<ClaimVerdictTable>? updateColumns,
    _is.WhereExpressionBuilder<ClaimVerdictTable>? updateWhere,
    _is.Transaction? transaction,
    bool noReturn = false,
  }) async {
    return session.db.upsert<ClaimVerdict>(
      rows,
      conflictColumns: conflictColumns(ClaimVerdict.t),
      updateColumns: updateColumns?.call(ClaimVerdict.t),
      updateWhere: updateWhere?.call(ClaimVerdict.t),
      transaction: transaction,
      noReturn: noReturn,
    );
  }

  /// Upserts a single [ClaimVerdict] and returns the resulting row.
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
  /// The returned [ClaimVerdict] will have its `id` field set.
  Future<ClaimVerdict?> upsertRow(
    _is.DatabaseSession session,
    ClaimVerdict row, {
    required _is.ColumnSelections<ClaimVerdictTable> conflictColumns,
    _is.ColumnSelections<ClaimVerdictTable>? updateColumns,
    _is.WhereExpressionBuilder<ClaimVerdictTable>? updateWhere,
    _is.Transaction? transaction,
  }) async {
    return session.db.upsertRow<ClaimVerdict>(
      row,
      conflictColumns: conflictColumns(ClaimVerdict.t),
      updateColumns: updateColumns?.call(ClaimVerdict.t),
      updateWhere: updateWhere?.call(ClaimVerdict.t),
      transaction: transaction,
    );
  }

  /// Updates all [ClaimVerdict]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  ///
  /// If [noReturn] is set to `true`, the updated rows are not read back from
  /// the database and an empty list is returned. This avoids the overhead of
  /// transferring and deserializing the rows when the result is not needed.
  Future<List<ClaimVerdict>> update(
    _is.DatabaseSession session,
    List<ClaimVerdict> rows, {
    _is.ColumnSelections<ClaimVerdictTable>? columns,
    _is.Transaction? transaction,
    bool noReturn = false,
  }) async {
    return session.db.update<ClaimVerdict>(
      rows,
      columns: columns?.call(ClaimVerdict.t),
      transaction: transaction,
      noReturn: noReturn,
    );
  }

  /// Updates a single [ClaimVerdict]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<ClaimVerdict> updateRow(
    _is.DatabaseSession session,
    ClaimVerdict row, {
    _is.ColumnSelections<ClaimVerdictTable>? columns,
    _is.Transaction? transaction,
  }) async {
    return session.db.updateRow<ClaimVerdict>(
      row,
      columns: columns?.call(ClaimVerdict.t),
      transaction: transaction,
    );
  }

  /// Updates a single [ClaimVerdict] by its [id] with the specified [columnValues].
  /// Returns the updated row or null if no row with the given id exists.
  Future<ClaimVerdict?> updateById(
    _is.DatabaseSession session,
    int id, {
    required _is.ColumnValueListBuilder<ClaimVerdictUpdateTable> columnValues,
    _is.Transaction? transaction,
  }) async {
    return session.db.updateById<ClaimVerdict>(
      id,
      columnValues: columnValues(ClaimVerdict.t.updateTable),
      transaction: transaction,
    );
  }

  /// Updates all [ClaimVerdict]s matching the [where] expression with the specified [columnValues].
  /// Returns the list of updated rows.
  ///
  /// If [noReturn] is set to `true`, the updated rows are not read back from
  /// the database and an empty list is returned. This avoids the overhead of
  /// transferring and deserializing the rows when the result is not needed.
  Future<List<ClaimVerdict>> updateWhere(
    _is.DatabaseSession session, {
    required _is.ColumnValueListBuilder<ClaimVerdictUpdateTable> columnValues,
    required _is.WhereExpressionBuilder<ClaimVerdictTable> where,
    int? limit,
    int? offset,
    _is.OrderByBuilder<ClaimVerdictTable>? orderBy,
    _is.OrderByListBuilder<ClaimVerdictTable>? orderByList,
    _is.Transaction? transaction,
    bool noReturn = false,
  }) async {
    return session.db.updateWhere<ClaimVerdict>(
      columnValues: columnValues(ClaimVerdict.t.updateTable),
      where: where(ClaimVerdict.t),
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(ClaimVerdict.t),
      orderByList: orderByList?.call(ClaimVerdict.t),
      transaction: transaction,
      noReturn: noReturn,
    );
  }

  /// Deletes all [ClaimVerdict]s in the list and returns the deleted rows.
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
  Future<List<ClaimVerdict>> delete(
    _is.DatabaseSession session,
    List<ClaimVerdict> rows, {
    _is.OrderByBuilder<ClaimVerdictTable>? orderBy,
    _is.OrderByListBuilder<ClaimVerdictTable>? orderByList,
    _is.Transaction? transaction,
    bool noReturn = false,
  }) async {
    return session.db.delete<ClaimVerdict>(
      rows,
      orderBy: orderBy?.call(ClaimVerdict.t),
      orderByList: orderByList?.call(ClaimVerdict.t),
      transaction: transaction,
      noReturn: noReturn,
    );
  }

  /// Deletes a single [ClaimVerdict].
  Future<ClaimVerdict> deleteRow(
    _is.DatabaseSession session,
    ClaimVerdict row, {
    _is.Transaction? transaction,
  }) async {
    return session.db.deleteRow<ClaimVerdict>(
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
  Future<List<ClaimVerdict>> deleteWhere(
    _is.DatabaseSession session, {
    required _is.WhereExpressionBuilder<ClaimVerdictTable> where,
    _is.OrderByBuilder<ClaimVerdictTable>? orderBy,
    _is.OrderByListBuilder<ClaimVerdictTable>? orderByList,
    _is.Transaction? transaction,
    bool noReturn = false,
  }) async {
    return session.db.deleteWhere<ClaimVerdict>(
      where: where(ClaimVerdict.t),
      orderBy: orderBy?.call(ClaimVerdict.t),
      orderByList: orderByList?.call(ClaimVerdict.t),
      transaction: transaction,
      noReturn: noReturn,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _is.DatabaseSession session, {
    _is.WhereExpressionBuilder<ClaimVerdictTable>? where,
    int? limit,
    _is.Transaction? transaction,
  }) async {
    return session.db.count<ClaimVerdict>(
      where: where?.call(ClaimVerdict.t),
      limit: limit,
      transaction: transaction,
    );
  }

  /// Acquires row-level locks on [ClaimVerdict] rows matching the [where] expression.
  Future<void> lockRows(
    _is.DatabaseSession session, {
    required _is.WhereExpressionBuilder<ClaimVerdictTable> where,
    required _is.LockMode lockMode,
    required _is.Transaction transaction,
    _is.LockBehavior lockBehavior = _is.LockBehavior.wait,
  }) async {
    return session.db.lockRows<ClaimVerdict>(
      where: where(ClaimVerdict.t),
      lockMode: lockMode,
      lockBehavior: lockBehavior,
      transaction: transaction,
    );
  }
}
