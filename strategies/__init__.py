"""Strategy configurations."""

from . import carry, macro_composite

REGISTRY = {
    "macro_composite": macro_composite.weights_fn,
    "carry": carry.weights_fn,
}

__all__ = ["REGISTRY", "macro_composite", "carry"]
