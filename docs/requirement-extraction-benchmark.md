# Requirement extraction benchmark (2026-11-11)

**Decision: keep the current pipeline.** `src/draft_job.py` and the `job-requirements` agent stay the way requirements are extracted and classified, and `src/db_sync.py` keeps linking terms to skills by exact alias. No new module or dependency was added.

This note records what was tested, so the comparison does not have to be redone from scratch.

## What was tested

The test set was the 6 job folders that have requirements: 191 posting lines and 226 terms, in English and French. The job folders were only read, never changed.

| Setup | Terms found (recall) | Line section | Priority | Speed |
|---|---|---|---|---|
| GLiNER2.5-multi, no training | 83% | 55% | 59% | 8 s for all 6 ads |
| Qwen3.5 9B (Ollama, JSON schema) | 86% | 71% | 80% | ~95 s per ad |
| TF-IDF + logistic regression, leave-one-job-out | — | 62% | 83% | milliseconds |
| multilingual-e5 embeddings + logistic regression | — | 67% | 82% | milliseconds |

- **Line section** sorts each line into requirement, preferred, responsibility, location, or company text.
- **Leave-one-job-out** means each job was scored by a model trained only on the other five.

To test linking a term to a catalog skill, each term's existing alias was removed from the catalog. The question was whether a method still finds the right skill:

| Method | Correct skill ranked first |
|---|---|
| Exact alias (current `db_sync.py`) | 0% |
| BM25 on letter groups | 64% |
| multilingual-e5 | 80% |
| e5 top 5, then Qwen picks one or "none" | 84% (right skill in the top 5 for 96%; 1.6 s per term) |

## Why the current pipeline stays

- **Extraction is already good enough.** The two setups that extract terms find 83–86% of them, and `draft_job.py missed` catches the rest. GLiNER2 is fast, but it was the weakest at telling requirements apart from company text.
- **The labels limit the scores.** Only 38 of the 181 requirements are marked reviewed. Many counted "errors" were correct answers on lines the drafts had skipped, so the table underestimates every model.
- **Better linking would cost something.** Fuzzy linking would add `sentence-transformers` and a running Ollama model. It also made confident mistakes (`Coaching` → `Harness Eng`), so every link would still need a human check.

## Known gaps in the current pipeline

These are not fixed. They are the reason to reopen this decision.

- Only 86 of 210 requirement terms are linked to a skill, because linking needs an exact alias. For example, `ES6` misses the alias `ES6+`, and `component library` misses `component libraries`. Adding these as `skill_keywords` fixes each one.
- The skill types `soft` and `language` are never used. Some soft skills (`results-oriented`, `cross-functional collaboration`) are typed `technical`.
- The catalog has no AI skill finer than `artificial intelligence`. So "AI engineer" and "build AI systems" cannot be told apart. This is a catalog gap, not a model gap.

## When to revisit

- **Linking:** if unlinked terms keep piling up, build the e5 + LLM-verify linker. Every link it proposes is confirmed by a human and saved as a `skill_keywords` row.
- **Classification:** once 30–50 jobs have reviewed requirements, retrain the logistic regression. Use it as a second opinion that flags lines where it disagrees with the drafter.
- **Skipped for now:**
  - H2O AutoML: it needs a Java runtime and cannot beat logistic regression on ~200 examples.
  - ESCO: the catalog is the owner's own skills, not a market taxonomy.
  - BERTopic and HDBSCAN: ~100 unlinked terms are faster to read by hand.

The benchmark scripts were run from a temporary folder and are not kept in the repo.
