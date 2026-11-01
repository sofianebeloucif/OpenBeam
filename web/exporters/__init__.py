"""Data exporters of the web viewers, keyed by beam id (the id used in ``src/beams.js``)."""

from . import chiral_vector, gaussian

EXPORTERS = {
    "chiral-vector": chiral_vector.export,
    "gaussian": gaussian.export,
}
