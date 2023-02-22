from nltk import data

def edit_distance(
    s1: str, s2: str, substitution_cost: int = ..., transpositions: bool = ...
) -> int: ...

__all__ = ["edit_distance", "data"]
