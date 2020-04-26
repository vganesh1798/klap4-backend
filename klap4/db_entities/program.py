#!/usr/bin/env python3

from datetime import *

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Time, Table
from sqlalchemy.orm import backref, relationship

import klap4.db
from klap4.db_entities import SQLBase


class ProgramFormat(SQLBase):
    __tablename__ = "program_format"

    type = Column(String, primary_key=True)
    description = Column(String, nullable=False)

    programs = relationship("Program", back_populates="program_format", cascade="all, delete-orphan")
    program_slots = relationship("ProgramSlot", back_populates="program_format", cascade="all, delete-orphan")
    program_log_entries = relationship("ProgramLogEntry", back_populates="program_format", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @property
    def id(self):
        return str(self.type)
    
    def __repr__(self):
        return f"<Program(type={self.type}, " \
                        f"description={self.description})>"
    
    def __str__(self):
        return str(self.type)


class Program(SQLBase):
    __tablename__ = "program"

    type = Column(String, ForeignKey("program_format.type"), primary_key=True)
    name = Column(String, primary_key=True)
    duration = Column(Integer)
    months = Column(String)

    program_format = relationship("ProgramFormat", back_populates="programs")
    program_log_entries = relationship("ProgramLogEntry", back_populates="program_desc", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @property
    def id(self):
        return str(self.type)+'+'+str(self.name)
    
    def __repr__(self):
        return f"<Program(type={self.type}, " \
                        f"name={self.name}, " \
                        f"months={self.months})>"
    
    def __str__(self):
        return str(self.name)


class ProgramSlot(SQLBase):
    __tablename__ = "program_slot"

    id = Column(Integer, primary_key=True)
    program_type = Column(String, ForeignKey("program_format.type"), nullable=False)
    day = Column(Integer)
    time = Column(Time)

    program_format = relationship("ProgramFormat", back_populates="program_slots")
    program_log_entries = relationship("ProgramLogEntry", back_populates="program_slot")
    

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<ProgramSlot(program_type={self.program_type}, " \
                            f"day={self.day}, " \
                            f"time={self.time})>"


class ProgramLogEntry(SQLBase):
    __tablename__ = "program_log_entry"

    program_type = Column(String, ForeignKey("program_format.type"), primary_key=True)
    program_name = Column(String, ForeignKey("program.name"))
    slot_id = Column(String, ForeignKey("program_slot.id"), primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    dj = Column(String, ForeignKey("dj.id"), nullable=False)

    program_format = relationship("ProgramFormat", back_populates="program_log_entries")
    program_desc = relationship("Program", back_populates="program_log_entries")
    program_slot = relationship("ProgramSlot", back_populates="program_log_entries")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    

    @property
    def id(self):
        return str(self.program_type) + str(self.slot_id) + str(self.timestamp)

    def __repr__(self):
        return f"<ProgramLogEntry(program_type={self.program_type}, " \
                                f"program_name={self.program_name}, " \
                                f"timestamp={self.timestamp}, " \
                                f"dj={self.dj})>"


class Quarter(SQLBase):
    __tablename__ = "quarter"

    id = Column(Integer, primary_key=True)
    begin = Column(DateTime, primary_key=True)
    end = Column(DateTime, primary_key=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def __repr__(self):
        return f"<Quarter(id={self.id}, " \
                    f"begin={self.begin}, " \
                    f"end={self.end})>"
