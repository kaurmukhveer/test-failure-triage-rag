# Evaluation results

Run on 2026-10-15 with embedding model `gemini-embedding-001` and generation model `gemini-3.1-flash-lite`, k=3, on 13 synthetic labelled logs.

- Retrieval hit@1: 12/12 (100%)
- Retrieval hit@3: 12/12 (100%)
- Triage accuracy (incl. no-match cases): 13/13 (100%)

| Log | Expected | Retrieved (top 3) | Predicted | Correct |
|---|---|---|---|---|
| LOG-001 | KI-001 | KI-001, KI-011, KI-004 | KI-001 | ✅ |
| LOG-002 | KI-002 | KI-002, KI-001, KI-004 | KI-002 | ✅ |
| LOG-003 | KI-003 | KI-003, KI-008, KI-002 | KI-003 | ✅ |
| LOG-004 | KI-004 | KI-004, KI-001, KI-002 | KI-004 | ✅ |
| LOG-005 | KI-005 | KI-005, KI-004, KI-001 | KI-005 | ✅ |
| LOG-006 | KI-006 | KI-006, KI-004, KI-003 | KI-006 | ✅ |
| LOG-007 | KI-007 | KI-007, KI-010, KI-001 | KI-007 | ✅ |
| LOG-008 | KI-008 | KI-008, KI-003, KI-004 | KI-008 | ✅ |
| LOG-009 | KI-009 | KI-009, KI-004, KI-002 | KI-009 | ✅ |
| LOG-010 | KI-010 | KI-010, KI-001, KI-007 | KI-010 | ✅ |
| LOG-011 | KI-011 | KI-011, KI-004, KI-001 | KI-011 | ✅ |
| LOG-012 | KI-012 | KI-012, KI-009, KI-001 | KI-012 | ✅ |
| LOG-013 | none | KI-002, KI-009, KI-004 | none | ✅ |
