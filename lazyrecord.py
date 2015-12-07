from flask import g
import datetime

class RecordNotFound(Exception):
    pass

class Base(object):
    
    def __init__(self, **kwargs):
        for attr, val in kwargs.items():
            if attr in (self.__class__.__attributes__ + ["created_at"]):
                setattr(self, attr, val)
        self.id = None

    @classmethod
    def backend(cls, **kwargs):
        obj = cls()
        for attr, val in kwargs.items():
            setattr(obj, attr, val)
        return obj

    def save(self):
        if self.id:
            update_command_arg = ", ".join("{} = ?".format(attr) for attr in self.__class__.__attributes__)
            cmd = "update {table} set {update_command_arg} where {table}.id = ?".format(
                update_command_arg=update_command_arg,
                table=self.__class__.table)
            x = g.db.execute(cmd,
                [getattr(self, attr) for attr in self.__class__.__attributes__] + [self.id])
            g.db.commit()
        else:
            created_at = datetime.date.today()
            cmd = "insert into {table} ({}) values ({})".format(
                ", ".join(self.__class__.__attributes__ + ["created_at"]),
                ", ".join(["?"] * (len(self.__class__.__attributes__) + 1)),
                table=self.__class__.table)
            x = g.db.execute(cmd,
                [getattr(self, attr) for attr in self.__class__.__attributes__] + [created_at])
            self.id = int(x.lastrowid)
            self.created_at = created_at
            g.db.commit()

    @classmethod
    def find(cls, id):
        cmd = 'select {attrs}, created_at, id from {table} where {table}.id = ?'.format(
            table = cls.table,
            attrs = ", ".join(cls.__attributes__)
        )
        cur = g.db.execute(cmd, [id])
        result = cur.fetchone()
        if result:
            args = dict(zip(cls.__attributes__ + ["created_at", "id"], result))
            obj = cls.backend(**args)
            return obj
        else:
            raise RecordNotFound({'id': id})

    @classmethod
    def find_by(cls, **kwargs):
        args = list(kwargs)
        cmd = 'select {attrs}, created_at, id from {table} where {where_clause}'.format(
            table = cls.table,
            attrs = ", ".join(cls.__attributes__),
            where_clause = " and ".join([
                "{table}.{attr} = ?".format(table = cls.table, attr = attr)
                for attr in args]))
        cur = g.db.execute(cmd, [kwargs[attr] for attr in args])
        result = cur.fetchone()
        if result:
            args = dict(zip(cls.__attributes__ + ["created_at", "id"], result))
            obj = cls.backend(**args)
            return obj
        else:
            raise RecordNotFound(kwargs)

    @classmethod
    def all(cls):
        def create_objects(cur):
            for record in cur.fetchall():
                args = dict(zip(cls.__attributes__ + ["id", "created_at"], record))
                obj = cls.backend(**args)
                yield obj
        cmd = 'select {attrs}, id, created_at from {table}'.format(
            table = cls.table,
            attrs = ", ".join(cls.__attributes__)
        )
        return list(create_objects(g.db.execute(cmd)))

    class __metaclass__(type):
        @property
        def table(self):
            return self.__name__.lower() + "s"

    def __repr__(self):
        return "Plant({})".format(", ".join("{}={!r}".format(attr, getattr(self, attr)) for attr in self.__class__.__attributes__))
