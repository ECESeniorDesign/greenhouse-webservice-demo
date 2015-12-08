from flask import g
import datetime

def date(datetime):
    # may get more complexity later
    return datetime

class RecordNotFound(Exception):
    pass

class RecordNotValid(Exception):
    pass

class Base(object):
    
    def __init__(self, **kwargs):
        for attr, val in kwargs.items():
            if attr in (list(self.__class__.__attributes__) + ["created_at"]):
                setattr(self, "_" + attr, val)
        self._id = None
        self._created_at = None

    def __getattr__(self, attr):
        if attr == "id":
            if self._id:
                return self._id
            else:
                return None
        elif attr == "created_at":
            return self._created_at
        elif attr in self.__class__.__attributes__:
            return self.__class__.__attributes__[attr](self.__getattribute__("_" + attr))
        else:
            return self.__getattribute__(attr)

    def __setattr__(self, name, value):
        if name == "id":
            self._id = int(value)
        elif name == "created_at":
            self._created_at = value
        elif name in self.__class__.__attributes__:
            setattr(self, "_" + name, self.__class__.__attributes__[name](value))
        else:
            super(Base, self).__setattr__(name, value)

    @classmethod
    def backend(cls, **kwargs):
        obj = cls()
        for attr, val in kwargs.items():
            setattr(obj, "_" + attr, val)
        return obj

    def delete(self):
        if self.id:
            cmd = "delete from {table} where {table}.id = ?".format(
                table=self.__class__.table)
            x = g.db.execute(cmd, [self.id])
            g.db.commit()

    def save(self):
        self.validate()
        if self.id:
            attrs = list(self.__class__.__attributes__)
            update_command_arg = ", ".join("{} = ?".format(attr) for attr in self.__class__.__attributes__)
            cmd = "update {table} set {update_command_arg} where {table}.id = ?".format(
                update_command_arg=update_command_arg,
                table=self.__class__.table)
            x = g.db.execute(cmd,
                [getattr(self, attr) for attr in attrs] + [self.id])
            g.db.commit()
        else:
            attrs = list(self.__class__.__attributes__)
            created_at = datetime.date.today()
            cmd = "insert into {table} ({}) values ({})".format(
                ", ".join(attrs + ["created_at"]),
                ", ".join(["?"] * (len(attrs) + 1)),
                table=self.__class__.table)
            x = g.db.execute(cmd,
                [getattr(self, attr) for attr in attrs] + [created_at])
            self.id = x.lastrowid
            self.created_at = created_at
            g.db.commit()

    def validate(self):
        reason = {}
        valid = True
        for attr, validation in self.__class__.__validates__.items():
            if not validation(getattr(self, attr)):
                reason[attr] = getattr(self, attr)
                valid = False
        if not valid:
            raise RecordNotValid(reason)

    @classmethod
    def find(cls, id):
        attrs = list(cls.__attributes__) + ["created_at", "id"]
        cmd = 'select {attrs} from {table} where {table}.id = ?'.format(
            table = cls.table,
            attrs = ", ".join(attrs)
        )
        cur = g.db.execute(cmd, [id])
        result = cur.fetchone()
        if result:
            args = dict(zip(attrs, result))
            obj = cls.backend(**args)
            return obj
        else:
            raise RecordNotFound({'id': id})

    @classmethod
    def find_by(cls, **kwargs):
        args = list(kwargs)
        attrs = list(cls.__attributes__) + ["created_at", "id"]
        cmd = 'select {attrs} from {table} where {where_clause}'.format(
            table = cls.table,
            attrs = ", ".join(attrs),
            where_clause = " and ".join([
                "{table}.{attr} = ?".format(table = cls.table, attr = attr)
                for attr in args]))
        cur = g.db.execute(cmd, [kwargs[attr] for attr in args])
        result = cur.fetchone()
        if result:
            args = dict(zip(attrs, result))
            obj = cls.backend(**args)
            return obj
        else:
            raise RecordNotFound(kwargs)

    @classmethod
    def all(cls):
        attrs = list(cls.__attributes__) + ["created_at", "id"]
        def create_objects(cur):
            for record in cur.fetchall():
                args = dict(zip(attrs, record))
                obj = cls.backend(**args)
                yield obj
        cmd = 'select {attrs} from {table}'.format(
            table = cls.table,
            attrs = ", ".join(attrs)
        )
        return list(create_objects(g.db.execute(cmd)))

    class __metaclass__(type):
        @property
        def table(self):
            return self.__name__.lower() + "s"

    def __repr__(self):
        return "Plant({})".format(", ".join("{}={!r}".format(attr, getattr(self, attr)) for attr in self.__class__.__attributes__ if hasattr(self, attr)))
