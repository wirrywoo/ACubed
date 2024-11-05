"""Module to define customized datatypes in ACubed."""

from typing import List, NamedTuple, cast, Type, Any
from operator import attrgetter, add
from itertools import groupby, chain
from functools import reduce
import hashlib
import re

class BaseType(NamedTuple):
    """
    Base datatype to define the occurrence of a note event at a specific
    timestamp.
    
    Attributes:
        time (float): The time at which the event occurs.
        step (str): A string representing the required keytaps.
    """
    time: float
    step: str

class Note(BaseType):
    """
    A class representing the occurrence of a note event at a specific timestamp
    for any $n-$key vertical scroll rhythm game.
    
    This class extends the BaseType to include additional functionality
    for manipulating and validating note events. It ensures that the timestamp
    to successfully hit a note is non-negative and the required keytaps belong
    to a set of valid binary step combinations determined by the number of
    receptors, $n$.
    
    Parameters:
        time (float): The time at which the note occurs. Must be non-negative.
        step (str): A binary string representing the required keytaps.
    """
    def __new__(cls: Type['Note'], time: float,
                step: str, num_receptors: int = 4) -> 'Note':
        """
        Instantiates the Note class.
        """
        cls.num_receptors = num_receptors

        if time < 0:
            raise ValueError("Time attribute must be non-negative.")

        valid_steps = [f"{i:0{cls.num_receptors}b}"
                       for i in range(1, pow(2, cls.num_receptors))]
        if step not in valid_steps:
            raise ValueError(f"Step attribute must be one of {valid_steps}.")

        return cast(Note, super().__new__(cls, time, step))

    def __getitem__(self, item: Any) -> Any:
        """
        Enables indexing to access the time or step directly.
        """
        return (self.time, self.step)[item]

    def __add__(self, other: Any = None) -> Any:
        """
        Redefine sum to represent the union of the steps for two notes at
        the same timestamp.
        """
        if not isinstance(other, Note):
            return NotImplemented

        if self.time != other.time:
            raise ValueError("Cannot add two Notes with different times attributes.")

        if other:
            if ('1', '1') in zip(self.step, other.step):
                raise ValueError("Cannot add Notes with overlapping step orientations.")
            updated_step = f"{int(self.step, 2) + int(other.step, 2):0{self.num_receptors}b}"
        else:
            updated_step = self.step
        return Note(time=self.time, step=updated_step)

    def __radd__(self, other):
        """
        Redefine right summation to enable use of sum().
        """
        return self if other == 0 else self.__add__(other)

class Stepfile:
    """
    A class representing the collection of note events for any $n-$key
    vertical scroll rhythm game.

    This class performs additional preprocessing to address zero-framer data
    quality issues and aggregate steps during object instantiation. 
    
    Parameters:
        notes (List[Note]): The list of Note objects within the stepfile.
    """
    def __init__(self, notes: List[Note], num_receptors: int = 4) -> None:
        """
        Instantiates the Stepfile class.
        """
        self.delta = 1e-6
        self.num_receptors = num_receptors
        self.notes = self._preprocess(notes)
        self._steps = reduce(add, map(attrgetter("step"), self.notes))

    def _preprocess(self, notes: List[Note]) -> List[Note]:
        """
        Increments timestamps by a negligible amount for zero framers and
        aggregates steps to create jumps, hands and quads.
        """
        _notes = sorted(notes, key=attrgetter("time", "step"))
        _stepfile = list(
            chain.from_iterable(
                [
                    [Note(time=t + i * self.delta, step=s) for i, _ in enumerate(_)]
                    for (t, s), _ in groupby(_notes, key=attrgetter("time", "step"))
                ]
            )
        )
        return list(
            reduce(add, sublist)
            for _, sublist in groupby(
                sorted(_stepfile, key=attrgetter("time")), key=attrgetter("time")
            )
        )

    def __getitem__(self, item: Any) -> Any:
        """
        Enables note-level indexing to access the note at a specific timestamp.
        """
        return self.notes[
            [
                int(m.start() / self.num_receptors)
                for m in re.finditer("1", self._steps)
            ][item]
        ]

    def __len__(self) -> int:
        """
        Returns the number of notes in the stepfile.
        """
        return self._steps.count("1")

    def __repr__(self) -> str:
        """
        Returns a string representation of the stepfile.
        """
        stepfile_id = hashlib.md5(self._steps.encode('utf-8')).hexdigest()
        return f"Stepfile(id={stepfile_id}, num_notes={len(self)})"
