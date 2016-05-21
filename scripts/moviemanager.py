class Item(object):

    def __init__(self,id, name, location, created_date, file_type):
        self.id = id
        self.location=location
        self.created_date = created_date
        self.file_type =  file_type
        self.name = name

    def move(self):
        pass

    def copy(self):
        pass

    def rename(self):
        pass

    def delete(self):
        pass


class Movie(Item):

    def __init__(self):

        pass


def get_data():
    pass

def store_data():
    pass

def main():
    import sqlite3
    conn = sqlite3.connect('movie.db')

    import os
    for root, dirs, files in os.walk(".", topdown=True):
        for name in files:
            print(os.path.join(root, name))



if __name__ == '__main__':
    main()

























# class QuerySet(object):
#     """
#     Represents a lazy database lookup for a set of objects.
#     """
#     def __init__(self, model=None, query=None, using=None):
#         self.model = model
#         self._db = using
#         self.query = query or sql.Query(self.model)
#         self._result_cache = None
#         self._sticky_filter = False
#         self._for_write = False
#         self._prefetch_related_lookups = []
#         self._prefetch_done = False
#         self._known_related_objects = {}        # {rel_field, {pk: rel_obj}}
#
#     ########################
#     # PYTHON MAGIC METHODS #
#     ########################
#
#     def __deepcopy__(self, memo):
#         """
#         Deep copy of a QuerySet doesn't populate the cache
#         """
#         obj = self.__class__()
#         for k, v in self.__dict__.items():
#             if k == '_result_cache':
#                 obj.__dict__[k] = None
#             else:
#                 obj.__dict__[k] = copy.deepcopy(v, memo)
#         return obj
#
#     def __getstate__(self):
#         """
#         Allows the QuerySet to be pickled.
#         """
#         # Force the cache to be fully populated.
#         self._fetch_all()
#         obj_dict = self.__dict__.copy()
#         return obj_dict
#
#     def __repr__(self):
#         data = list(self[:REPR_OUTPUT_SIZE + 1])
#         if len(data) > REPR_OUTPUT_SIZE:
#             data[-1] = "...(remaining elements truncated)..."
#         return repr(data)
#
#     def __len__(self):
#         self._fetch_all()
#         return len(self._result_cache)
#
#     def __iter__(self):
#         """
#         The queryset iterator protocol uses three nested iterators in the
#         default case:
#             1. sql.compiler:execute_sql()
#                - Returns 100 rows at time (constants.GET_ITERATOR_CHUNK_SIZE)
#                  using cursor.fetchmany(). This part is responsible for
#                  doing some column masking, and returning the rows in chunks.
#             2. sql/compiler.results_iter()
#                - Returns one row at time. At this point the rows are still just
#                  tuples. In some cases the return values are converted to
#                  Python values at this location (see resolve_columns(),
#                  resolve_aggregate()).
#             3. self.iterator()
#                - Responsible for turning the rows into model objects.
#         """
#         self._fetch_all()
#         return iter(self._result_cache)
#
#     def __nonzero__(self):
#         self._fetch_all()
#         return bool(self._result_cache)
#
#     def __getitem__(self, k):
#         """
#         Retrieves an item or slice from the set of results.
#         """
#         if not isinstance(k, (slice,) + six.integer_types):
#             raise TypeError
#         assert ((not isinstance(k, slice) and (k >= 0))
#                 or (isinstance(k, slice) and (k.start is None or k.start >= 0)
#                     and (k.stop is None or k.stop >= 0))), \
#                 "Negative indexing is not supported."
#
#         if self._result_cache is not None:
#             return self._result_cache[k]
#
#         if isinstance(k, slice):
#             qs = self._clone()
#             if k.start is not None:
#                 start = int(k.start)
#             else:
#                 start = None
#             if k.stop is not None:
#                 stop = int(k.stop)
#             else:
#                 stop = None
#             qs.query.set_limits(start, stop)
#             return list(qs)[::k.step] if k.step else qs
#
#         qs = self._clone()
#         qs.query.set_limits(k, k + 1)
#         return list(qs)[0]
#
#     def __and__(self, other):
#         self._merge_sanity_check(other)
#         if isinstance(other, EmptyQuerySet):
#             return other
#         if isinstance(self, EmptyQuerySet):
#             return self
#         combined = self._clone()
#         combined._merge_known_related_objects(other)
#         combined.query.combine(other.query, sql.AND)
#         return combined
#
#     def __or__(self, other):
#         self._merge_sanity_check(other)
#         if isinstance(self, EmptyQuerySet):
#             return other
#         if isinstance(other, EmptyQuerySet):
#             return self
#         combined = self._clone()
#         combined._merge_known_related_objects(other)
#         combined.query.combine(other.query, sql.OR)
#         return combined
#
#     ####################################
#     # METHODS THAT DO DATABASE QUERIES #
#     ####################################
#
#     def iterator(self):
#         """
#         An iterator over the results from applying this QuerySet to the
#         database.
#         """
#         fill_cache = False
#         if connections[self.db].features.supports_select_related:
#             fill_cache = self.query.select_related
#         if isinstance(fill_cache, dict):
#             requested = fill_cache
#         else:
#             requested = None
#         max_depth = self.query.max_depth
#
#         extra_select = list(self.query.extra_select)
#         aggregate_select = list(self.query.aggregate_select)
#
#         only_load = self.query.get_loaded_field_names()
#         if not fill_cache:
#             fields = self.model._meta.concrete_fields
#
#         load_fields = []
#         # If only/defer clauses have been specified,
#         # build the list of fields that are to be loaded.
#         if only_load:
#             for field, model in self.model._meta.get_concrete_fields_with_model():
#                 if model is None:
#                     model = self.model
#                 try:
#                     if field.name in only_load[model]:
#                         # Add a field that has been explicitly included
#                         load_fields.append(field.name)
#                 except KeyError:
#                     # Model wasn't explicitly listed in the only_load table
#                     # Therefore, we need to load all fields from this model
#                     load_fields.append(field.name)
#
#         index_start = len(extra_select)
#         aggregate_start = index_start + len(load_fields or self.model._meta.concrete_fields)
#
#         skip = None
#         if load_fields and not fill_cache:
#             # Some fields have been deferred, so we have to initialise
#             # via keyword arguments.
#             skip = set()
#             init_list = []
#             for field in fields:
#                 if field.name not in load_fields:
#                     skip.add(field.attname)
#                 else:
#                     init_list.append(field.attname)
#             model_cls = deferred_class_factory(self.model, skip)
#
#         # Cache db and model outside the loop
#         db = self.db
#         model = self.model
#         compiler = self.query.get_compiler(using=db)
#         if fill_cache:
#             klass_info = get_klass_info(model, max_depth=max_depth,
#                                         requested=requested, only_load=only_load)
#         for row in compiler.results_iter():
#             if fill_cache:
#                 obj, _ = get_cached_row(row, index_start, db, klass_info,
#                                         offset=len(aggregate_select))
#             else:
#                 # Omit aggregates in object creation.
#                 row_data = row[index_start:aggregate_start]
#                 if skip:
#                     obj = model_cls(**dict(zip(init_list, row_data)))
#                 else:
#                     obj = model(*row_data)
#
#                 # Store the source database of the object
#                 obj._state.db = db
#                 # This object came from the database; it's not being added.
#                 obj._state.adding = False
#
#             if extra_select:
#                 for i, k in enumerate(extra_select):
#                     setattr(obj, k, row[i])
#
#             # Add the aggregates to the model
#             if aggregate_select:
#                 for i, aggregate in enumerate(aggregate_select):
#                     setattr(obj, aggregate, row[i + aggregate_start])
#
#             # Add the known related objects to the model, if there are any
#             if self._known_related_objects:
#                 for field, rel_objs in self._known_related_objects.items():
#                     pk = getattr(obj, field.get_attname())
#                     try:
#                         rel_obj = rel_objs[pk]
#                     except KeyError:
#                         pass               # may happen in qs1 | qs2 scenarios
#                     else:
#                         setattr(obj, field.name, rel_obj)
#
#             yield obj
#
#     def aggregate(self, *args, **kwargs):
#         """
#         Returns a dictionary containing the calculations (aggregation)
#         over the current queryset
#
#         If args is present the expression is passed as a kwarg using
#         the Aggregate object's default alias.
#         """
#         if self.query.distinct_fields:
#             raise NotImplementedError("aggregate() + distinct(fields) not implemented.")
#         for arg in args:
#             kwargs[arg.default_alias] = arg
#
#         query = self.query.clone()
#
#         for (alias, aggregate_expr) in kwargs.items():
#             query.add_aggregate(aggregate_expr, self.model, alias,
#                 is_summary=True)
#
#         return query.get_aggregation(using=self.db)
#
#     def count(self):
#         """
#         Performs a SELECT COUNT() and returns the number of records as an
#         integer.
#
#         If the QuerySet is already fully cached this simply returns the length
#         of the cached results set to avoid multiple SELECT COUNT(*) calls.
#         """
#         if self._result_cache is not None:
#             return len(self._result_cache)
#
#         return self.query.get_count(using=self.db)
#
#     def get(self, *args, **kwargs):
#         """
#         Performs the query and returns a single object matching the given
#         keyword arguments.
#         """
#         clone = self.filter(*args, **kwargs)
#         if self.query.can_filter():
#             clone = clone.order_by()
#         num = len(clone)
#         if num == 1:
#             return clone._result_cache[0]
#         if not num:
#             raise self.model.DoesNotExist(
#                 "%s matching query does not exist." %
#                 self.model._meta.object_name)
#         raise self.model.MultipleObjectsReturned(
#             "get() returned more than one %s -- it returned %s!" %
#             (self.model._meta.object_name, num))
#
#     def create(self, **kwargs):
#         """
#         Creates a new object with the given kwargs, saving it to the database
#         and returning the created object.
#         """
#         obj = self.model(**kwargs)
#         self._for_write = True
#         obj.save(force_insert=True, using=self.db)
#         return obj
#
#     def bulk_create(self, objs, batch_size=None):
#         """
#         Inserts each of the instances into the database. This does *not* call
#         save() on each of the instances, does not send any pre/post save
#         signals, and does not set the primary key attribute if it is an
#         autoincrement field.
#         """
#         # So this case is fun. When you bulk insert you don't get the primary
#         # keys back (if it's an autoincrement), so you can't insert into the
#         # child tables which references this. There are two workarounds, 1)
#         # this could be implemented if you didn't have an autoincrement pk,
#         # and 2) you could do it by doing O(n) normal inserts into the parent
#         # tables to get the primary keys back, and then doing a single bulk
#         # insert into the childmost table. Some databases might allow doing
#         # this by using RETURNING clause for the insert query. We're punting
#         # on these for now because they are relatively rare cases.
#         assert batch_size is None or batch_size > 0
#         if self.model._meta.parents:
#             raise ValueError("Can't bulk create an inherited model")
#         if not objs:
#             return objs
#         self._for_write = True
#         connection = connections[self.db]
#         fields = self.model._meta.local_concrete_fields
#         with transaction.commit_on_success_unless_managed(using=self.db):
#             if (connection.features.can_combine_inserts_with_and_without_auto_increment_pk
#                 and self.model._meta.has_auto_field):
#                 self._batched_insert(objs, fields, batch_size)
#             else:
#                 objs_with_pk, objs_without_pk = partition(lambda o: o.pk is None, objs)
#                 if objs_with_pk:
#                     self._batched_insert(objs_with_pk, fields, batch_size)
#                 if objs_without_pk:
#                     fields= [f for f in fields if not isinstance(f, AutoField)]
#                     self._batched_insert(objs_without_pk, fields, batch_size)
#
#         return objs
#
#     def get_or_create(self, **kwargs):
#         """
#         Looks up an object with the given kwargs, creating one if necessary.
#         Returns a tuple of (object, created), where created is a boolean
#         specifying whether an object was created.
#         """
#         defaults = kwargs.pop('defaults', {})
#         lookup = kwargs.copy()
#         for f in self.model._meta.fields:
#             if f.attname in lookup:
#                 lookup[f.name] = lookup.pop(f.attname)
#         try:
#             self._for_write = True
#             return self.get(**lookup), False
#         except self.model.DoesNotExist:
#             try:
#                 params = dict((k, v) for k, v in kwargs.items() if LOOKUP_SEP not in k)
#                 params.update(defaults)
#                 obj = self.model(**params)
#                 with transaction.atomic(using=self.db):
#                     obj.save(force_insert=True, using=self.db)
#                 return obj, True
#             except DatabaseError:
#                 exc_info = sys.exc_info()
#                 try:
#                     return self.get(**lookup), False
#                 except self.model.DoesNotExist:
#                     # Re-raise the DatabaseError with its original traceback.
#                     six.reraise(*exc_info)
#
#     def _earliest_or_latest(self, field_name=None, direction="-"):
#         """
#         Returns the latest object, according to the model's
#         'get_latest_by' option or optional given field_name.
#         """
#         order_by = field_name or getattr(self.model._meta, 'get_latest_by')
#         assert bool(order_by), "earliest() and latest() require either a "\
#             "field_name parameter or 'get_latest_by' in the model"
#         assert self.query.can_filter(), \
#             "Cannot change a query once a slice has been taken."
#         obj = self._clone()
#         obj.query.set_limits(high=1)
#         obj.query.clear_ordering(force_empty=True)
#         obj.query.add_ordering('%s%s' % (direction, order_by))
#         return obj.get()
#
#     def earliest(self, field_name=None):
#         return self._earliest_or_latest(field_name=field_name, direction="")
#
#     def latest(self, field_name=None):
#         return self._earliest_or_latest(field_name=field_name, direction="-")
#
#     def first(self):
#         """
#         Returns the first object of a query, returns None if no match is found.
#         """
#         qs = self if self.ordered else self.order_by('pk')
#         try:
#             return qs[0]
#         except IndexError:
#             return None
#
#     def last(self):
#         """
#         Returns the last object of a query, returns None if no match is found.
#         """
#         qs = self.reverse() if self.ordered else self.order_by('-pk')
#         try:
#             return qs[0]
#         except IndexError:
#             return None
#
#     def in_bulk(self, id_list):
#         """
#         Returns a dictionary mapping each of the given IDs to the object with
#         that ID.
#         """
#         assert self.query.can_filter(), \
#                 "Cannot use 'limit' or 'offset' with in_bulk"
#         if not id_list:
#             return {}
#         qs = self.filter(pk__in=id_list).order_by()
#         return dict([(obj._get_pk_val(), obj) for obj in qs])
#
#     def delete(self):
#         """
#         Deletes the records in the current QuerySet.
#         """
#         assert self.query.can_filter(), \
#                 "Cannot use 'limit' or 'offset' with delete."
#
#         del_query = self._clone()
#
#         # The delete is actually 2 queries - one to find related objects,
#         # and one to delete. Make sure that the discovery of related
#         # objects is performed on the same database as the deletion.
#         del_query._for_write = True
#
#         # Disable non-supported fields.
#         del_query.query.select_for_update = False
#         del_query.query.select_related = False
#         del_query.query.clear_ordering(force_empty=True)
#
#         collector = Collector(using=del_query.db)
#         collector.collect(del_query)
#         collector.delete()
#
#         # Clear the result cache, in case this QuerySet gets reused.
#         self._result_cache = None
#     delete.alters_data = True
#
#     def _raw_delete(self, using):
#         """
#         Deletes objects found from the given queryset in single direct SQL
#         query. No signals are sent, and there is no protection for cascades.
#         """
#         sql.DeleteQuery(self.model).delete_qs(self, using)
#     _raw_delete.alters_data = True
#
#     def update(self, **kwargs):
#         """
#         Updates all elements in the current QuerySet, setting all the given
#         fields to the appropriate values.
#         """
#         assert self.query.can_filter(), \
#                 "Cannot update a query once a slice has been taken."
#         self._for_write = True
#         query = self.query.clone(sql.UpdateQuery)
#         query.add_update_values(kwargs)
#         with transaction.commit_on_success_unless_managed(using=self.db):
#             rows = query.get_compiler(self.db).execute_sql(None)
#         self._result_cache = None
#         return rows
#     update.alters_data = True
#
#     def _update(self, values):
#         """
#         A version of update that accepts field objects instead of field names.
#         Used primarily for model saving and not intended for use by general
#         code (it requires too much poking around at model internals to be
#         useful at that level).
#         """
#         assert self.query.can_filter(), \
#                 "Cannot update a query once a slice has been taken."
#         query = self.query.clone(sql.UpdateQuery)
#         query.add_update_fields(values)
#         self._result_cache = None
#         return query.get_compiler(self.db).execute_sql(None)
#     _update.alters_data = True
#
#     def exists(self):
#         if self._result_cache is None:
#             return self.query.has_results(using=self.db)
#         return bool(self._result_cache)
#
#     def _prefetch_related_objects(self):
#         # This method can only be called once the result cache has been filled.
#         prefetch_related_objects(self._result_cache, self._prefetch_related_lookups)
#         self._prefetch_done = True
#
#     ##################################################
#     # PUBLIC METHODS THAT RETURN A QUERYSET SUBCLASS #
#     ##################################################
#
#     def values(self, *fields):
#         return self._clone(klass=ValuesQuerySet, setup=True, _fields=fields)
#
#     def values_list(self, *fields, **kwargs):
#         flat = kwargs.pop('flat', False)
#         if kwargs:
#             raise TypeError('Unexpected keyword arguments to values_list: %s'
#                     % (list(kwargs),))
#         if flat and len(fields) > 1:
#             raise TypeError("'flat' is not valid when values_list is called with more than one field.")
#         return self._clone(klass=ValuesListQuerySet, setup=True, flat=flat,
#                 _fields=fields)
#
#     def dates(self, field_name, kind, order='ASC'):
#         """
#         Returns a list of date objects representing all available dates for
#         the given field_name, scoped to 'kind'.
#         """
#         assert kind in ("year", "month", "day"), \
#                 "'kind' must be one of 'year', 'month' or 'day'."
#         assert order in ('ASC', 'DESC'), \
#                 "'order' must be either 'ASC' or 'DESC'."
#         return self._clone(klass=DateQuerySet, setup=True,
#                 _field_name=field_name, _kind=kind, _order=order)
#
#     def datetimes(self, field_name, kind, order='ASC', tzinfo=None):
#         """
#         Returns a list of datetime objects representing all available
#         datetimes for the given field_name, scoped to 'kind'.
#         """
#         assert kind in ("year", "month", "day", "hour", "minute", "second"), \
#                 "'kind' must be one of 'year', 'month', 'day', 'hour', 'minute' or 'second'."
#         assert order in ('ASC', 'DESC'), \
#                 "'order' must be either 'ASC' or 'DESC'."
#         if settings.USE_TZ:
#             if tzinfo is None:
#                 tzinfo = timezone.get_current_timezone()
#         else:
#             tzinfo = None
#         return self._clone(klass=DateTimeQuerySet, setup=True,
#                 _field_name=field_name, _kind=kind, _order=order, _tzinfo=tzinfo)
#
#     def none(self):
#         """
#         Returns an empty QuerySet.
#         """
#         clone = self._clone()
#         clone.query.set_empty()
#         return clone
#
#     ##################################################################
#     # PUBLIC METHODS THAT ALTER ATTRIBUTES AND RETURN A NEW QUERYSET #
#     ##################################################################
#
#     def all(self):
#         """
#         Returns a new QuerySet that is a copy of the current one. This allows a
#         QuerySet to proxy for a model manager in some cases.
#         """
#         return self._clone()
#
#     def filter(self, *args, **kwargs):
#         """
#         Returns a new QuerySet instance with the args ANDed to the existing
#         set.
#         """
#         return self._filter_or_exclude(False, *args, **kwargs)
#
#     def exclude(self, *args, **kwargs):
#         """
#         Returns a new QuerySet instance with NOT (args) ANDed to the existing
#         set.
#         """
#         return self._filter_or_exclude(True, *args, **kwargs)
#
#     def _filter_or_exclude(self, negate, *args, **kwargs):
#         if args or kwargs:
#             assert self.query.can_filter(), \
#                     "Cannot filter a query once a slice has been taken."
#
#         clone = self._clone()
#         if negate:
#             clone.query.add_q(~Q(*args, **kwargs))
#         else:
#             clone.query.add_q(Q(*args, **kwargs))
#         return clone
#
#     def complex_filter(self, filter_obj):
#         """
#         Returns a new QuerySet instance with filter_obj added to the filters.
#
#         filter_obj can be a Q object (or anything with an add_to_query()
#         method) or a dictionary of keyword lookup arguments.
#
#         This exists to support framework features such as 'limit_choices_to',
#         and usually it will be more natural to use other methods.
#         """
#         if isinstance(filter_obj, Q) or hasattr(filter_obj, 'add_to_query'):
#             clone = self._clone()
#             clone.query.add_q(filter_obj)
#             return clone
#         else:
#             return self._filter_or_exclude(None, **filter_obj)
#
#     def select_for_update(self, **kwargs):
#         """
#         Returns a new QuerySet instance that will select objects with a
#         FOR UPDATE lock.
#         """
#         # Default to false for nowait
#         nowait = kwargs.pop('nowait', False)
#         obj = self._clone()
#         obj._for_write = True
#         obj.query.select_for_update = True
#         obj.query.select_for_update_nowait = nowait
#         return obj
#
#     def select_related(self, *fields, **kwargs):
#         """
#         Returns a new QuerySet instance that will select related objects.
#
#         If fields are specified, they must be ForeignKey fields and only those
#         related objects are included in the selection.
#
#         If select_related(None) is called, the list is cleared.
#         """
#         if 'depth' in kwargs:
#             warnings.warn('The "depth" keyword argument has been deprecated.\n'
#                     'Use related field names instead.', DeprecationWarning, stacklevel=2)
#         depth = kwargs.pop('depth', 0)
#         if kwargs:
#             raise TypeError('Unexpected keyword arguments to select_related: %s'
#                     % (list(kwargs),))
#         obj = self._clone()
#         if fields == (None,):
#             obj.query.select_related = False
#         elif fields:
#             if depth:
#                 raise TypeError('Cannot pass both "depth" and fields to select_related()')
#             obj.query.add_select_related(fields)
#         else:
#             obj.query.select_related = True
#         if depth:
#             obj.query.max_depth = depth
#         return obj
#
#     def prefetch_related(self, *lookups):
#         """
#         Returns a new QuerySet instance that will prefetch the specified
#         Many-To-One and Many-To-Many related objects when the QuerySet is
#         evaluated.
#
#         When prefetch_related() is called more than once, the list of lookups to
#         prefetch is appended to. If prefetch_related(None) is called, the
#         the list is cleared.
#         """
#         clone = self._clone()
#         if lookups == (None,):
#             clone._prefetch_related_lookups = []
#         else:
#             clone._prefetch_related_lookups.extend(lookups)
#         return clone
#
#     def annotate(self, *args, **kwargs):
#         """
#         Return a query set in which the returned objects have been annotated
#         with data aggregated from related fields.
#         """
#         for arg in args:
#             if arg.default_alias in kwargs:
#                 raise ValueError("The named annotation '%s' conflicts with the "
#                                  "default name for another annotation."
#                                  % arg.default_alias)
#             kwargs[arg.default_alias] = arg
#
#         names = getattr(self, '_fields', None)
#         if names is None:
#             names = set(self.model._meta.get_all_field_names())
#         for aggregate in kwargs:
#             if aggregate in names:
#                 raise ValueError("The annotation '%s' conflicts with a field on "
#                     "the model." % aggregate)
#
#         obj = self._clone()
#
#         obj._setup_aggregate_query(list(kwargs))
#
#         # Add the aggregates to the query
#         for (alias, aggregate_expr) in kwargs.items():
#             obj.query.add_aggregate(aggregate_expr, self.model, alias,
#                 is_summary=False)
#
#         return obj
#
#     def order_by(self, *field_names):
#         """
#         Returns a new QuerySet instance with the ordering changed.
#         """
#         assert self.query.can_filter(), \
#                 "Cannot reorder a query once a slice has been taken."
#         obj = self._clone()
#         obj.query.clear_ordering(force_empty=False)
#         obj.query.add_ordering(*field_names)
#         return obj
#
#     def distinct(self, *field_names):
#         """
#         Returns a new QuerySet instance that will select only distinct results.
#         """
#         assert self.query.can_filter(), \
#                 "Cannot create distinct fields once a slice has been taken."
#         obj = self._clone()
#         obj.query.add_distinct_fields(*field_names)
#         return obj
#
#     def extra(self, select=None, where=None, params=None, tables=None,
#               order_by=None, select_params=None):
#         """
#         Adds extra SQL fragments to the query.
#         """
#         assert self.query.can_filter(), \
#                 "Cannot change a query once a slice has been taken"
#         clone = self._clone()
#         clone.query.add_extra(select, select_params, where, params, tables, order_by)
#         return clone
#
#     def reverse(self):
#         """
#         Reverses the ordering of the QuerySet.
#         """
#         clone = self._clone()
#         clone.query.standard_ordering = not clone.query.standard_ordering
#         return clone
#
#     def defer(self, *fields):
#         """
#         Defers the loading of data for certain fields until they are accessed.
#         The set of fields to defer is added to any existing set of deferred
#         fields. The only exception to this is if None is passed in as the only
#         parameter, in which case all deferrals are removed (None acts as a
#         reset option).
#         """
#         clone = self._clone()
#         if fields == (None,):
#             clone.query.clear_deferred_loading()
#         else:
#             clone.query.add_deferred_loading(fields)
#         return clone
#
#     def only(self, *fields):
#         """
#         Essentially, the opposite of defer. Only the fields passed into this
#         method and that are not already specified as deferred are loaded
#         immediately when the queryset is evaluated.
#         """
#         if fields == (None,):
#             # Can only pass None to defer(), not only(), as the rest option.
#             # That won't stop people trying to do this, so let's be explicit.
#             raise TypeError("Cannot pass None as an argument to only().")
#         clone = self._clone()
#         clone.query.add_immediate_loading(fields)
#         return clone
#
#     def using(self, alias):
#         """
#         Selects which database this QuerySet should excecute its query against.
#         """
#         clone = self._clone()
#         clone._db = alias
#         return clone
#
#     ###################################
#     # PUBLIC INTROSPECTION ATTRIBUTES #
#     ###################################
#
#     def ordered(self):
#         """
#         Returns True if the QuerySet is ordered -- i.e. has an order_by()
#         clause or a default ordering on the model.
#         """
#         if self.query.extra_order_by or self.query.order_by:
#             return True
#         elif self.query.default_ordering and self.query.get_meta().ordering:
#             return True
#         else:
#             return False
#     ordered = property(ordered)
#
#     @property
#     def db(self):
#         "Return the database that will be used if this query is executed now"
#         if self._for_write:
#             return self._db or router.db_for_write(self.model)
#         return self._db or router.db_for_read(self.model)
#
#     ###################
#     # PRIVATE METHODS #
#     ###################
#     def _batched_insert(self, objs, fields, batch_size):
#         """
#         A little helper method for bulk_insert to insert the bulk one batch
#         at a time. Inserts recursively a batch from the front of the bulk and
#         then _batched_insert() the remaining objects again.
#         """
#         if not objs:
#             return
#         ops = connections[self.db].ops
#         batch_size = (batch_size or max(ops.bulk_batch_size(fields, objs), 1))
#         for batch in [objs[i:i+batch_size]
#                       for i in range(0, len(objs), batch_size)]:
#             self.model._base_manager._insert(batch, fields=fields,
#                                              using=self.db)
#
#     def _clone(self, klass=None, setup=False, **kwargs):
#         if klass is None:
#             klass = self.__class__
#         query = self.query.clone()
#         if self._sticky_filter:
#             query.filter_is_sticky = True
#         c = klass(model=self.model, query=query, using=self._db)
#         c._for_write = self._for_write
#         c._prefetch_related_lookups = self._prefetch_related_lookups[:]
#         c._known_related_objects = self._known_related_objects
#         c.__dict__.update(kwargs)
#         if setup and hasattr(c, '_setup_query'):
#             c._setup_query()
#         return c
#
#     def _fetch_all(self):
#         if self._result_cache is None:
#             self._result_cache = list(self.iterator())
#         if self._prefetch_related_lookups and not self._prefetch_done:
#             self._prefetch_related_objects()
#
#     def _next_is_sticky(self):
#         """
#         Indicates that the next filter call and the one following that should
#         be treated as a single filter. This is only important when it comes to
#         determining when to reuse tables for many-to-many filters. Required so
#         that we can filter naturally on the results of related managers.
#
#         This doesn't return a clone of the current QuerySet (it returns
#         "self"). The method is only used internally and should be immediately
#         followed by a filter() that does create a clone.
#         """
#         self._sticky_filter = True
#         return self
#
#     def _merge_sanity_check(self, other):
#         """
#         Checks that we are merging two comparable QuerySet classes. By default
#         this does nothing, but see the ValuesQuerySet for an example of where
#         it's useful.
#         """
#         pass
#
#     def _merge_known_related_objects(self, other):
#         """
#         Keep track of all known related objects from either QuerySet instance.
#         """
#         for field, objects in other._known_related_objects.items():
#             self._known_related_objects.setdefault(field, {}).update(objects)
#
#     def _setup_aggregate_query(self, aggregates):
#         """
#         Prepare the query for computing a result that contains aggregate annotations.
#         """
#         opts = self.model._meta
#         if self.query.group_by is None:
#             field_names = [f.attname for f in opts.concrete_fields]
#             self.query.add_fields(field_names, False)
#             self.query.set_group_by()
#
#     def _prepare(self):
#         return self
#
#     def _as_sql(self, connection):
#         """
#         Returns the internal query's SQL and parameters (as a tuple).
#         """
#         obj = self.values("pk")
#         if obj._db is None or connection == connections[obj._db]:
#             return obj.query.get_compiler(connection=connection).as_nested_sql()
#         raise ValueError("Can't do subqueries with queries on different DBs.")
#
#     # When used as part of a nested query, a queryset will never be an "always
#     # empty" result.
#     value_annotation = True