# This test code was written by the `hypothesis.extra.ghostwriter` module
# and is provided under the Creative Commons Zero public domain dedication.

import uts_logging
import valdec.data_classes
from hypothesis import given, strategies as st
from valdec.data_classes import Settings


@given(name=st.text(), filename=st.text())
def test_fuzz_set_logging(name: str, filename: str) -> None:
    uts_logging.set_logging(name=name, filename=filename)


@given(exclude=st.booleans(), settings=st.from_type(Settings))
def test_fuzz_validate(exclude: bool, settings: valdec.data_classes.Settings) -> None:
    uts_logging.validate(exclude=exclude, settings=settings)

