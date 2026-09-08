"""Pipeline agents: CV parsing, research, filtering, matching, ranking.

Each agent has one responsibility and does not reach into the others, which
keeps the pipeline easy to debug and lets a new job source or scoring rule be
added without rewriting the rest.
"""
