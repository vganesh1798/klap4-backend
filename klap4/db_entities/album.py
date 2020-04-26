#!/usr/bin/env python3

from datetime import datetime, timedelta

from sqlalchemy import Column, ForeignKey, Boolean, DateTime, String, Integer
from sqlalchemy.orm import backref, relationship

import klap4.db
from klap4.db_entities import decompose_tag, full_module_name, SQLBase


class Album(SQLBase):
    __tablename__ = "album"

    class FORMAT:
        VINYL = 0b00001
        CD = 0b00010
        DIGITAL =0b00100
        SINGLE = 0b01000
        SEVENINCH = 0b10000

    genre_abbr = Column(String(2), primary_key=True)
    artist_num = Column(Integer, primary_key=True)
    letter = Column(String(1), primary_key=True)
    name = Column(String, nullable=False)
    date_added = Column(DateTime, nullable=False)
    missing = Column(Boolean, nullable=False)
    format_bitfield = Column(Integer, nullable=False)
    label_id = Column(Integer, nullable=True)
    promoter_id = Column(Integer, nullable=True)

    genre = relationship("klap4.db_entities.genre.Genre",
                         backref=backref("albums", uselist=True, cascade="all"),
                         uselist=False,
                         primaryjoin="foreign(Genre.abbreviation) == Album.genre_abbr")

    artist = relationship("klap4.db_entities.artist.Artist",
                          backref=backref("albums", uselist=True, cascade="all"),
                          uselist=False,
                          primaryjoin="and_("
                                      "     foreign(Artist.genre_abbr) == Album.genre_abbr,"
                                      "     foreign(Artist.number) == Album.artist_num"
                                      ")")
    
    label = relationship("klap4.db_entities.label_and_promoter.Label",
                         backref=backref("albums", uselist=True, cascade="all"),
                         uselist=False,
                         primaryjoin="foreign(Label.id) == Album.label_id")
    
    promoter = relationship("klap4.db_entities.label_and_promoter.Promoter",
                            backref=backref("albums", uselist=True, cascade="all"),
                            uselist=False,
                            primaryjoin="foreign(Promoter.id) == Album.promoter_id")

    def __init__(self, **kwargs):
        if "id" in kwargs:
            decomposed_tag = decompose_tag(kwargs["id"])
            kwargs["genre_abbr"] = decomposed_tag.genre_abbr
            kwargs["artist_num"] = decomposed_tag.artist_num

            if decomposed_tag.album_letter is not None:
                kwargs["letter"] = decomposed_tag.album_letter

            kwargs.pop("id")

        if "letter" not in kwargs:
            from klap4.db_entities import get_entity_from_tag
            artist = get_entity_from_tag(f"{kwargs['genre_abbr']}{kwargs['artist_num']}")
            kwargs["letter"] = artist.next_album_letter

        defaults = {
            "date_added": datetime.now(),
            "missing": False,
        }
        kwargs = {**defaults, **kwargs}

        super().__init__(**kwargs)

    @property
    def is_new(self):
        return datetime.now() - self.date_added < timedelta(days=30 * 6)

    @property
    def id(self):
        return self.artist.id + self.letter

    def __repr__(self):
        return f"<Album(id={self.id}, " \
                      f"name={self.name}, " \
                      f"date_added={self.date_added}, " \
                      f"missing={self.missing}, " \
                      f"is_new={self.is_new}, " \
                      f"format={self.format_bitfield}, " \
                      f"label_id={self.label_id}, " \
                      f"promoter_id={self.promoter_id})>"


class AlbumReview(SQLBase):
    __tablename__ = "album_review"

    genre_abbr = Column(String(2), primary_key=True)
    artist_num = Column(Integer, primary_key=True)
    album_letter = Column(String(1), primary_key=True)
    dj_id = Column(String, primary_key=True)
    date_entered = Column(DateTime, nullable=False)
    content = Column(String, nullable=False)

    genre = relationship("klap4.db_entities.genre.Genre",
                         backref=backref("album_reviews", uselist=True, cascade="all"),
                         uselist=False,
                         primaryjoin="foreign(Genre.abbreviation) == AlbumReview.genre_abbr")
    
    artist = relationship("klap4.db_entities.artist.Artist",
                          backref=backref("album_reviews", uselist=True, cascade="all"),
                          uselist=False,
                          primaryjoin="and_("
                                      "     foreign(Artist.genre_abbr) == AlbumReview.genre_abbr,"
                                      "     foreign(Artist.number) == AlbumReview.artist_num"
                                      ")")
    
    album = relationship("klap4.db_entities.album.Album",
                         backref=backref("album_reviews", uselist=True, cascade="all"),
                         uselist=False,
                         primaryjoin="and_("
                                     "     foreign(Album.genre_abbr) == AlbumReview.genre_abbr,"
                                     "     foreign(Album.artist_num) == AlbumReview.artist_num,"
                                     "     foreign(Album.letter) == AlbumReview.album_letter"
                                     ")")
    
    dj = relationship("klap4.db_entities.dj.DJ",
                      backref=backref("album_reviews", uselist=True, cascade="all"),
                      uselist=False,
                      primaryjoin="foreign(DJ.id) == AlbumReview.dj_id")

    def __init__(self, **kwargs):
        if "date_entered" in kwargs:
            kwargs["date_entered"] = datetime.now()
        super().__init__(**kwargs)

    @property
    def is_recent(self):
        return datetime.now() - self.date_entered < timedelta(weeks=4)

    @property
    def id(self):
        return self.album.id + str(self.dj_id)

    def __repr__(self):
        return f"<AlbumReview(id={self.id}, " \
                            f"date_entered={self.date_entered}, " \
                            f"is_recent={self.is_recent}, " \
                            f"content={self.content[:20] + '...' if len(self.content) > 20 else self.content})>"


class AlbumProblem(SQLBase):
    __tablename__ = "album_problem"

    genre_abbr = Column(String(2), primary_key=True)
    artist_num = Column(Integer, primary_key=True)
    album_letter = Column(String(1), primary_key=True)
    dj_id = Column(String, primary_key=True)
    content = Column(String, nullable=False)

    genre = relationship("klap4.db_entities.genre.Genre",
                         backref=backref("album_problems", uselist=True, cascade="all"),
                         uselist=False,
                         primaryjoin="foreign(Genre.abbreviation) == AlbumProblem.genre_abbr")
    
    artist = relationship("klap4.db_entities.artist.Artist",
                          backref=backref("album_problems", uselist=True, cascade="all"),
                          uselist=False,
                          primaryjoin="and_("
                                      "     foreign(Artist.genre_abbr) == AlbumProblem.genre_abbr,"
                                      "     foreign(Artist.number) == AlbumProblem.artist_num"
                                      ")")
    
    album = relationship("klap4.db_entities.album.Album",
                         backref=backref("album_problems", uselist=True, cascade="all"),
                         uselist=False,
                         primaryjoin="and_("
                                     "     foreign(Album.genre_abbr) == AlbumProblem.genre_abbr,"
                                     "     foreign(Album.artist_num) == AlbumProblem.artist_num,"
                                     "     foreign(Album.letter) == AlbumProblem.album_letter"
                                     ")")
    
    dj = relationship("klap4.db_entities.dj.DJ",
                      backref=backref("album_problems", uselist=True, cascade="all"),
                      uselist=False,
                      primaryjoin="foreign(DJ.id) == AlbumProblem.dj_id")

    @property
    def id(self):
        return f"{self.album.id}!{self.dj_id}"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def __repr__(self):
        return f"<AlbumProblem(id={self.id}, " \
                             f"content={self.content[:20] + '...' if len(self.content) > 20 else self.content})>"
