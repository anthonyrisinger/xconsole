# coding: utf-8


nil = type('nil', (int,), dict())(0)


class mapo(dict):

    __slots__ = (
        '__dict__',
        )

    __types__ = dict()
    __feature__ = None

    def __copy__(self):
        return self.__class__(self)
    copy = __copy__

    @classmethod
    def type(cls, key=nil, attr=nil):
        if key is nil:
            return cls.__types__

        if attr is not nil:
            cls.__types__[key] = attr

        return cls.__types__.get(key, nil)

    @classmethod
    def features(cls, sep=None):
        feats = list()
        for base in reversed(cls.__mro__):
            feature = getattr(base, '__feature__', None)
            if feature:
                feats.append(feature)
        feats = tuple(feats)
        if hasattr(sep, 'join'):
            feats = sep.join(feats)
        return feats

    @classmethod
    def feature(cls, fun=None, *args, **kwds):
        def g(fun):
            key = kwds.get('key')
            merge = (not hasattr(fun, '__mro__')) and {fun.__name__: fun}
            if not key and not merge:
                key = fun.__name__
            if not key:
                raise TypeError('error: cannot derive key: %s' % (fun,))

            if merge:
                fun = cls.type(key) or dict()
                fun.update(merge)
            cls.type(key, fun)
            return fun if merge is None else None

        return g if fun is None else g(fun=fun)

    @classmethod
    def matic(cls, *args, **kwds):
        #TODO: should features express ordering constraints?
        feats = kwds.get('features') or tuple()
        if feats[0:0] == '':
            feats = tuple(feats.split())

        bases = list()
        for key in reversed(feats):
            typ = cls.type(key)
            if not typ:
                raise TypeError('error: undefined feature: %s' % (key,))

            typ = typ if hasattr(typ, '__mro__') else type('x', (cls,), typ)
            typ.__feature__ = key
            typ.__name__ = typ.features(sep='_')
            cls.type(key, typ)
            bases.append(typ)

        #TODO: should this be cached?
        typ = type('x', tuple(bases + [cls]), dict())
        typ.__feature__ = None
        typ.__name__ = typ.features(sep='_')
        return typ

@mapo.feature(key='attr')
class feature(mapo):
    def __new__(cls, *args, **kwds):
        supr = super(cls.type('attr'), cls)
        self = self.__dict__ = supr.__new__(cls, *args, **kwds)
        return self

@mapo.feature(key='autoa')
class feature(mapo):
    def __getattr__(self, key):
        supr = super(self.type('autoa'), self)
        try:
            return supr.__getattr__(key)
        except (KeyError, AttributeError):
            attr = self[key] = self.__class__()
            return attr

@mapo.feature(key='autoi')
class feature(mapo):
    def __missing__(self, key):
        supr = super(self.type('autoi'), self)
        try:
            return supr.__missing__(key)
        except (KeyError, AttributeError):
            attr = self[key] = self.__class__()
            return attr

@mapo.feature(key='auto')
class feature(mapo.type('autoa'), mapo.type('autoi')):
    pass

@mapo.feature(key='set')
class feature(mapo):
    __or__   = lambda s, o: s.__oper__(o, 'or')
    __xor__  = lambda s, o: s.__oper__(o, 'xor')
    __and__  = lambda s, o: s.__oper__(o, 'and')
    __sub__  = lambda s, o: s.__oper__(o, 'sub')
    __ror__  = lambda s, o: s.__oper__(o, 'ror')
    __rxor__ = lambda s, o: s.__oper__(o, 'rxor')
    __rand__ = lambda s, o: s.__oper__(o, 'rand')
    __rsub__ = lambda s, o: s.__oper__(o, 'rsub')
    __ior__  = lambda s, o: s.__oper__(o, 'ior')
    __ixor__ = lambda s, o: s.__oper__(o, 'ixor')
    __iand__ = lambda s, o: s.__oper__(o, 'iand')
    __isub__ = lambda s, o: s.__oper__(o, 'isub')
    def __oper__(self, other, op):
        iop = (op[0]=='i')
        rop = (op[0]=='r')
        typ = self.__class__
        get = lambda x: None
        if hasattr(other, 'keys'):
            get = other.__getitem__
        if rop:
            self, other = typ((x, get(x)) for x in other), self
            get = other.__getitem__
        elif not iop:
            self = self.copy()

        try:
            ikeys = self.viewkeys()
        except AttributeError:
            ikeys = frozenset(self)
        try:
            okeys = other.viewkeys()
        except AttributeError:
            okeys = frozenset(other)

        op = '__%s__' % op.lstrip('ir')
        oper = getattr(ikeys, op)
        keys = oper(okeys)
        if keys is NotImplemented:
            keys = oper(frozenset(okeys))
        if keys is NotImplemented:
            return keys

        get = lambda x: None
        if hasattr(other, 'keys'):
            get = other.__getitem__
        for key in keys - ikeys:
            self[key] = get(key)
        for key in ikeys - keys:
            del self[key]

        return self


record = mapo.matic(features='attr set')
automap = record.matic(features='auto')
