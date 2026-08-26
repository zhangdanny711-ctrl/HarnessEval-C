"""Stable public-only identities used to freeze and validate the showcase."""

from harnesseval_c.io import value_digest

MODEL_ID = "deterministic-public-showcase-v1"
GENERATOR_CONFIG_DIGEST = value_digest({
    "mode": "deterministic_public_fixture",
    "version": 1,
    "remote_judge": False,
})
