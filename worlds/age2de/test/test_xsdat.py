"""write_vector packed the tuple without unpacking it, so it raised on any call.

Nothing calls it today, which is why the suite never noticed. read_vector is its counterpart and
pins the byte layout the game reads.
"""
import io
import unittest

from ..campaign import XsdatFile


class TestVector(unittest.TestCase):
    def test_a_vector_round_trips(self) -> None:
        buffer = io.BytesIO()
        XsdatFile.write_vector(buffer, (1.5, -2.0, 3.25))
        self.assertEqual(12, buffer.tell(), "a vector is three 4-byte floats")

        buffer.seek(0)
        self.assertEqual([1.5, -2.0, 3.25], XsdatFile.read_vector(buffer))


if __name__ == "__main__":
    unittest.main()
