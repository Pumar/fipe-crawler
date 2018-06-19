from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from enum import Enum


Base = declarative_base()


class Status(Enum):
    UNVISITED = 1
    VISITED = 2
    ERROR = 3


class Reference(Base):
    __tablename__ = 'reference'
    id = Column(Integer, primary_key=True, autoincrement=True)
    period = Column(String(50), nullable=False, unique=True)
    status = Column(Integer, default=1)

    def __str__(self):
        return 'Reference: (id: {}, period: {}, status: {})'.format(self.id, self.status, self.status)

    def __repr__(self):
        return 'Reference: (id: {}, period: {}, status: {})'.format(self.id, self.period, self.status)


class ReferenceHasMarca(Base):
    __tablename__ = 'reference_has_marca'
    id = Column(Integer, primary_key=True, autoincrement=True)
    reference_id = Column(Integer, ForeignKey('reference.id'))
    marca_id = Column(Integer, ForeignKey('marca.id'))
    status = Column(Integer, default=1)

    def __str__(self):
        return 'ReferenceHasMarca: (id: {}, reference_id: {}, marca_id:{})'.format(
            self.id, self.reference_id, self.marca_id
        )

    def __repr__(self):
        return 'ReferenceHasMarca: (id: {}, reference_id: {}, marca_id:{})'.format(
            self.id, self.reference_, self.marca_id
        )


class Marca(Base):
    __tablename__ = 'marca'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=False, unique=True)
    reference_id = Column(Integer, ForeignKey('reference.id'))
    status = Column(Integer, default=1)

    def __str__(self):
        return 'Marca: (id: {}, name: {}, status: {}, reference_id: {})'.format(
            self.id, self.name, self.status, self.reference_id
        )

    def __repr__(self):
        return 'Marca: (id: {}, name: {}, status: {}, reference_id: {})'.format(
            self.id, self.name, self.status, self.reference_id
        )


class Modelo(Base):
    __tablename__ = 'modelo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=False)
    marca_id = Column(Integer, ForeignKey('marca.id'))
    status = Column(Integer, default=1)

    def __str__(self):
        return 'Modelo: (id: {}, name: {}, status: {}, marca_id: {})'.format(
            self.id, self.name, self.status, self.marca_id
        )

    def __repr__(self):
        return 'Modelo: (id: {}, name: {}, status: {}, marca_id: {})'.format(
            self.id, self.name, self.status, self.marca_id
        )


class AnoModelo(Base):
    __tablename__ = 'ano_modelo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ano_modelo = Column(String(250), nullable=False)
    codigo_fipe = Column(String(20))
    preco = Column(String(20))
    modelo_id = Column(Integer, ForeignKey('modelo.id'))
    status = Column(Integer, default=1)

    def __str__(self):
        return 'AnoModelo: (id: {}, ano_modelo: {}, codigo_fipe: {}, preco: {}, modelo_id: {}, status: {})'.format(
            self.id, self.ano_modelo, self.codigo_fipe, self.preco, self.modelo_id, self.status
        )

    def __repr__(self):
        return 'AnoModelo: (id: {}, ano_modelo: {}, codigo_fipe: {}, preco: {}, modelo_id: {}, status: {})'.format(
            self.id, self.ano_modelo, self.codigo_fipe, self.preco, self.modelo_id, self.status
        )


engine = create_engine('sqlite:///fipe.db')
Base.metadata.create_all(engine)
