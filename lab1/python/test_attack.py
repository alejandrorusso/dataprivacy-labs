from itertools import chain
from pytest import mark
from typing import List

from db import *
from attack import *

def hamming_distance(ca: Candidate, cb: Candidate) -> float:
  return float(len(list(filter(lambda p: p[0] != p[1], zip(ca, cb)))))

# Generates a list of test cases.
def parameters() -> List[Tuple[str, Noise]]:
  db_names = ["db1-small", "db1-large", "db2-small", "db2-large"]
  noises = [1, 2, 4]

  return list(chain(*[[(db_name, noise) for noise in noises] for db_name in db_names]))

@mark.parametrize("db_name, noise", parameters())
def test_attack(db_name: str, noise: Noise) -> None:
  db = load_db(f"datasets/{db_name}.csv")
  candidates = attack(db, noise)

  assert len(candidates) > 0, "Your attack must produce at least 1 candidate."

  num_rows = db_size(db)
  actual_rows = [row.hiv for row in db.secret_rows]

  for candidate in candidates:
    assert len(candidate) == num_rows, f"""
      The length of the following candidate does not match the dataset's row count.

      {candidate}
    """

    dist = hamming_distance(actual_rows, [row[1] for row in candidate])
    max_dist = 4 * noise

    assert dist <= max_dist, f"""
      The following candidate has a Hamming distance of {dist}.
      The maximum admissible distance for noise {noise} is {max_dist}.

      {candidate}
    """
