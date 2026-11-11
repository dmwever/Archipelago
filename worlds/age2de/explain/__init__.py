"""Universal Tracker's /explain for age2de: how a location can be had, where, and what is short.

UT asks the world first (`explain_rule`, `explain_more`) and falls back to the rule's own
explanation when the world answers nothing. The answer here stays the same size however many
scenarios a seed has: one block per route, one line per campaign.
"""
from .Explainer import Explainer

__all__ = ["Explainer"]
