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

/// Evidence media item captured via camera or uploaded as proof.
abstract class EvidenceMedia
    implements _is.TableRow<int?>, _is.ProtocolSerialization {
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
      timestamp: _is.DateTimeJsonExtension.fromJson(
        jsonSerialization['timestamp'],
      ),
    );
  }

  static final t = EvidenceMediaTable();

  static const db = EvidenceMediaRepository._();

  @override
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

  @override
  _is.Table<int?> get table => t;

  /// Returns a shallow copy of this [EvidenceMedia]
  /// with some or all fields replaced by the given arguments.
  @_is.useResult
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

  static EvidenceMediaInclude include() {
    return EvidenceMediaInclude._();
  }

  static EvidenceMediaIncludeList includeList({
    _is.WhereExpressionBuilder<EvidenceMediaTable>? where,
    int? limit,
    int? offset,
    _is.OrderByBuilder<EvidenceMediaTable>? orderBy,
    _is.OrderByListBuilder<EvidenceMediaTable>? orderByList,
    EvidenceMediaInclude? include,
  }) {
    return EvidenceMediaIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(EvidenceMedia.t),
      orderByList: orderByList?.call(EvidenceMedia.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _is.SerializationManager.encode(this);
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
  @_is.useResult
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

class EvidenceMediaUpdateTable extends _is.UpdateTable<EvidenceMediaTable> {
  EvidenceMediaUpdateTable(super.table);

  _is.ColumnValue<String, String> title(String value) => _is.ColumnValue(
    table.title,
    value,
  );

  _is.ColumnValue<String, String> category(String value) => _is.ColumnValue(
    table.category,
    value,
  );

  _is.ColumnValue<String, String> mediaType(String value) => _is.ColumnValue(
    table.mediaType,
    value,
  );

  _is.ColumnValue<String, String> dataBase64(String value) => _is.ColumnValue(
    table.dataBase64,
    value,
  );

  _is.ColumnValue<String, String> notes(String? value) => _is.ColumnValue(
    table.notes,
    value,
  );

  _is.ColumnValue<DateTime, DateTime> timestamp(DateTime value) =>
      _is.ColumnValue(
        table.timestamp,
        value,
      );
}

class EvidenceMediaTable extends _is.Table<int?> {
  EvidenceMediaTable({super.tableRelation})
    : super(tableName: 'evidence_media') {
    updateTable = EvidenceMediaUpdateTable(this);
    title = _is.ColumnString(
      'title',
      this,
    );
    category = _is.ColumnString(
      'category',
      this,
    );
    mediaType = _is.ColumnString(
      'mediaType',
      this,
    );
    dataBase64 = _is.ColumnString(
      'dataBase64',
      this,
    );
    notes = _is.ColumnString(
      'notes',
      this,
    );
    timestamp = _is.ColumnDateTime(
      'timestamp',
      this,
    );
  }

  late final EvidenceMediaUpdateTable updateTable;

  /// User-assigned or auto-generated title for this evidence item.
  late final _is.ColumnString title;

  /// Category: vehicle_damage, hospital_bill, rejection_letter, prescription, other.
  late final _is.ColumnString category;

  /// Media format: image, audio, or document.
  late final _is.ColumnString mediaType;

  /// Base64 data payload or image data URI.
  late final _is.ColumnString dataBase64;

  /// Optional user notes or voice transcript.
  late final _is.ColumnString notes;

  /// Timestamp when the evidence was recorded.
  late final _is.ColumnDateTime timestamp;

  @override
  List<_is.Column> get columns => [
    id,
    title,
    category,
    mediaType,
    dataBase64,
    notes,
    timestamp,
  ];
}

class EvidenceMediaInclude extends _is.IncludeObject {
  EvidenceMediaInclude._();

  @override
  Map<String, _is.Include?> get includes => {};

  @override
  _is.Table<int?> get table => EvidenceMedia.t;
}

class EvidenceMediaIncludeList extends _is.IncludeList {
  EvidenceMediaIncludeList._({
    _is.WhereExpressionBuilder<EvidenceMediaTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(EvidenceMedia.t);
  }

  @override
  Map<String, _is.Include?> get includes => include?.includes ?? {};

  @override
  _is.Table<int?> get table => EvidenceMedia.t;
}

class EvidenceMediaRepository {
  const EvidenceMediaRepository._();

  /// Returns a list of [EvidenceMedia]s matching the given query parameters.
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
  Future<List<EvidenceMedia>> find(
    _is.DatabaseSession session, {
    _is.WhereExpressionBuilder<EvidenceMediaTable>? where,
    int? limit,
    int? offset,
    _is.OrderByBuilder<EvidenceMediaTable>? orderBy,
    _is.OrderByListBuilder<EvidenceMediaTable>? orderByList,
    _is.Transaction? transaction,
    _is.LockMode? lockMode,
    _is.LockBehavior? lockBehavior,
  }) async {
    return session.db.find<EvidenceMedia>(
      where: where?.call(EvidenceMedia.t),
      orderBy: orderBy?.call(EvidenceMedia.t),
      orderByList: orderByList?.call(EvidenceMedia.t),
      limit: limit,
      offset: offset,
      transaction: transaction,
      lockMode: lockMode,
      lockBehavior: lockBehavior,
    );
  }

  /// Emits [EvidenceMedia]s matching the given query parameters every time the
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
  /// to that set. Pass [Table] instances such as `EvidenceMedia.t`.
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
  _ida.Stream<List<EvidenceMedia>> watch(
    _is.DatabaseSession session, {
    _is.WhereExpressionBuilder<EvidenceMediaTable>? where,
    int? limit,
    int? offset,
    _is.OrderByBuilder<EvidenceMediaTable>? orderBy,
    _is.OrderByListBuilder<EvidenceMediaTable>? orderByList,
    Duration? throttle = const Duration(milliseconds: 30),
    Iterable<_is.Table>? alsoTriggerOnTables,
  }) {
    return session.db.watch<EvidenceMedia>(
      where: where?.call(EvidenceMedia.t),
      orderBy: orderBy?.call(EvidenceMedia.t),
      orderByList: orderByList?.call(EvidenceMedia.t),
      limit: limit,
      offset: offset,
      throttle: throttle,
      alsoTriggerOnTables: alsoTriggerOnTables,
    );
  }

  /// Returns the first matching [EvidenceMedia] matching the given query parameters.
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
  Future<EvidenceMedia?> findFirstRow(
    _is.DatabaseSession session, {
    _is.WhereExpressionBuilder<EvidenceMediaTable>? where,
    int? offset,
    _is.OrderByBuilder<EvidenceMediaTable>? orderBy,
    _is.OrderByListBuilder<EvidenceMediaTable>? orderByList,
    _is.Transaction? transaction,
    _is.LockMode? lockMode,
    _is.LockBehavior? lockBehavior,
  }) async {
    return session.db.findFirstRow<EvidenceMedia>(
      where: where?.call(EvidenceMedia.t),
      orderBy: orderBy?.call(EvidenceMedia.t),
      orderByList: orderByList?.call(EvidenceMedia.t),
      offset: offset,
      transaction: transaction,
      lockMode: lockMode,
      lockBehavior: lockBehavior,
    );
  }

  /// Finds a single [EvidenceMedia] by its [id] or null if no such row exists.
  Future<EvidenceMedia?> findById(
    _is.DatabaseSession session,
    int id, {
    _is.Transaction? transaction,
    _is.LockMode? lockMode,
    _is.LockBehavior? lockBehavior,
  }) async {
    return session.db.findById<EvidenceMedia>(
      id,
      transaction: transaction,
      lockMode: lockMode,
      lockBehavior: lockBehavior,
    );
  }

  /// Inserts all [EvidenceMedia]s in the list and returns the inserted rows.
  ///
  /// The returned [EvidenceMedia]s will have their `id` fields set.
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
  Future<List<EvidenceMedia>> insert(
    _is.DatabaseSession session,
    List<EvidenceMedia> rows, {
    _is.Transaction? transaction,
    bool ignoreConflicts = false,
    bool noReturn = false,
  }) async {
    return session.db.insert<EvidenceMedia>(
      rows,
      transaction: transaction,
      ignoreConflicts: ignoreConflicts,
      noReturn: noReturn,
    );
  }

  /// Inserts a single [EvidenceMedia] and returns the inserted row.
  ///
  /// The returned [EvidenceMedia] will have its `id` field set.
  Future<EvidenceMedia> insertRow(
    _is.DatabaseSession session,
    EvidenceMedia row, {
    _is.Transaction? transaction,
  }) async {
    return session.db.insertRow<EvidenceMedia>(
      row,
      transaction: transaction,
    );
  }

  /// Upserts all [EvidenceMedia]s in the list and returns the resulting rows.
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
  /// The returned [EvidenceMedia]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails,
  /// none of the rows will be affected.
  ///
  /// If [noReturn] is set to `true`, the resulting rows are not read back from
  /// the database and an empty list is returned. This avoids the overhead of
  /// transferring and deserializing the rows when the result is not needed.
  Future<List<EvidenceMedia>> upsert(
    _is.DatabaseSession session,
    List<EvidenceMedia> rows, {
    required _is.ColumnSelections<EvidenceMediaTable> conflictColumns,
    _is.ColumnSelections<EvidenceMediaTable>? updateColumns,
    _is.WhereExpressionBuilder<EvidenceMediaTable>? updateWhere,
    _is.Transaction? transaction,
    bool noReturn = false,
  }) async {
    return session.db.upsert<EvidenceMedia>(
      rows,
      conflictColumns: conflictColumns(EvidenceMedia.t),
      updateColumns: updateColumns?.call(EvidenceMedia.t),
      updateWhere: updateWhere?.call(EvidenceMedia.t),
      transaction: transaction,
      noReturn: noReturn,
    );
  }

  /// Upserts a single [EvidenceMedia] and returns the resulting row.
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
  /// The returned [EvidenceMedia] will have its `id` field set.
  Future<EvidenceMedia?> upsertRow(
    _is.DatabaseSession session,
    EvidenceMedia row, {
    required _is.ColumnSelections<EvidenceMediaTable> conflictColumns,
    _is.ColumnSelections<EvidenceMediaTable>? updateColumns,
    _is.WhereExpressionBuilder<EvidenceMediaTable>? updateWhere,
    _is.Transaction? transaction,
  }) async {
    return session.db.upsertRow<EvidenceMedia>(
      row,
      conflictColumns: conflictColumns(EvidenceMedia.t),
      updateColumns: updateColumns?.call(EvidenceMedia.t),
      updateWhere: updateWhere?.call(EvidenceMedia.t),
      transaction: transaction,
    );
  }

  /// Updates all [EvidenceMedia]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  ///
  /// If [noReturn] is set to `true`, the updated rows are not read back from
  /// the database and an empty list is returned. This avoids the overhead of
  /// transferring and deserializing the rows when the result is not needed.
  Future<List<EvidenceMedia>> update(
    _is.DatabaseSession session,
    List<EvidenceMedia> rows, {
    _is.ColumnSelections<EvidenceMediaTable>? columns,
    _is.Transaction? transaction,
    bool noReturn = false,
  }) async {
    return session.db.update<EvidenceMedia>(
      rows,
      columns: columns?.call(EvidenceMedia.t),
      transaction: transaction,
      noReturn: noReturn,
    );
  }

  /// Updates a single [EvidenceMedia]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<EvidenceMedia> updateRow(
    _is.DatabaseSession session,
    EvidenceMedia row, {
    _is.ColumnSelections<EvidenceMediaTable>? columns,
    _is.Transaction? transaction,
  }) async {
    return session.db.updateRow<EvidenceMedia>(
      row,
      columns: columns?.call(EvidenceMedia.t),
      transaction: transaction,
    );
  }

  /// Updates a single [EvidenceMedia] by its [id] with the specified [columnValues].
  /// Returns the updated row or null if no row with the given id exists.
  Future<EvidenceMedia?> updateById(
    _is.DatabaseSession session,
    int id, {
    required _is.ColumnValueListBuilder<EvidenceMediaUpdateTable> columnValues,
    _is.Transaction? transaction,
  }) async {
    return session.db.updateById<EvidenceMedia>(
      id,
      columnValues: columnValues(EvidenceMedia.t.updateTable),
      transaction: transaction,
    );
  }

  /// Updates all [EvidenceMedia]s matching the [where] expression with the specified [columnValues].
  /// Returns the list of updated rows.
  ///
  /// If [noReturn] is set to `true`, the updated rows are not read back from
  /// the database and an empty list is returned. This avoids the overhead of
  /// transferring and deserializing the rows when the result is not needed.
  Future<List<EvidenceMedia>> updateWhere(
    _is.DatabaseSession session, {
    required _is.ColumnValueListBuilder<EvidenceMediaUpdateTable> columnValues,
    required _is.WhereExpressionBuilder<EvidenceMediaTable> where,
    int? limit,
    int? offset,
    _is.OrderByBuilder<EvidenceMediaTable>? orderBy,
    _is.OrderByListBuilder<EvidenceMediaTable>? orderByList,
    _is.Transaction? transaction,
    bool noReturn = false,
  }) async {
    return session.db.updateWhere<EvidenceMedia>(
      columnValues: columnValues(EvidenceMedia.t.updateTable),
      where: where(EvidenceMedia.t),
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(EvidenceMedia.t),
      orderByList: orderByList?.call(EvidenceMedia.t),
      transaction: transaction,
      noReturn: noReturn,
    );
  }

  /// Deletes all [EvidenceMedia]s in the list and returns the deleted rows.
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
  Future<List<EvidenceMedia>> delete(
    _is.DatabaseSession session,
    List<EvidenceMedia> rows, {
    _is.OrderByBuilder<EvidenceMediaTable>? orderBy,
    _is.OrderByListBuilder<EvidenceMediaTable>? orderByList,
    _is.Transaction? transaction,
    bool noReturn = false,
  }) async {
    return session.db.delete<EvidenceMedia>(
      rows,
      orderBy: orderBy?.call(EvidenceMedia.t),
      orderByList: orderByList?.call(EvidenceMedia.t),
      transaction: transaction,
      noReturn: noReturn,
    );
  }

  /// Deletes a single [EvidenceMedia].
  Future<EvidenceMedia> deleteRow(
    _is.DatabaseSession session,
    EvidenceMedia row, {
    _is.Transaction? transaction,
  }) async {
    return session.db.deleteRow<EvidenceMedia>(
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
  Future<List<EvidenceMedia>> deleteWhere(
    _is.DatabaseSession session, {
    required _is.WhereExpressionBuilder<EvidenceMediaTable> where,
    _is.OrderByBuilder<EvidenceMediaTable>? orderBy,
    _is.OrderByListBuilder<EvidenceMediaTable>? orderByList,
    _is.Transaction? transaction,
    bool noReturn = false,
  }) async {
    return session.db.deleteWhere<EvidenceMedia>(
      where: where(EvidenceMedia.t),
      orderBy: orderBy?.call(EvidenceMedia.t),
      orderByList: orderByList?.call(EvidenceMedia.t),
      transaction: transaction,
      noReturn: noReturn,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _is.DatabaseSession session, {
    _is.WhereExpressionBuilder<EvidenceMediaTable>? where,
    int? limit,
    _is.Transaction? transaction,
  }) async {
    return session.db.count<EvidenceMedia>(
      where: where?.call(EvidenceMedia.t),
      limit: limit,
      transaction: transaction,
    );
  }

  /// Acquires row-level locks on [EvidenceMedia] rows matching the [where] expression.
  Future<void> lockRows(
    _is.DatabaseSession session, {
    required _is.WhereExpressionBuilder<EvidenceMediaTable> where,
    required _is.LockMode lockMode,
    required _is.Transaction transaction,
    _is.LockBehavior lockBehavior = _is.LockBehavior.wait,
  }) async {
    return session.db.lockRows<EvidenceMedia>(
      where: where(EvidenceMedia.t),
      lockMode: lockMode,
      lockBehavior: lockBehavior,
      transaction: transaction,
    );
  }
}
