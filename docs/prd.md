# PRD: KnowledgeOps

**Status:** Draft v1  **Owner:** <your name>  **Date:** <today>

## 1. Problem
Teams keep knowledge in long documents. Finding an answer means searching by
hand, and general chatbots often invent answers that are not in the documents.
Companies need a service that answers **only from their own documents**, shows
**where** the answer came from, and says **"I don't know"** when the documents
do not contain the answer. Many companies share the service, so one company
must never see another company's data.

## 2. Users (personas)
| Persona | Who | What they need |
|---|---|---|
| **Tenant admin (Maya)** | Manages a company's account | Create users and API keys, upload and delete documents, see failures |
| **Member (Sam)** | Asks questions | Fast, correct, cited answers; clear "I don't know" |
| **Operator (you, on call)** | Runs the service | Dashboards, traces, runbook, safe deploys |

## 3. Goals
1. Strict tenant isolation, enforced by the database.
2. Reliable document ingestion that survives crashes without duplicates.
3. Answers that are grounded in documents, cited, and refused when unsupported.
4. Answers stream to the user as they are written.
5. Quality is **measured** on a golden dataset, and a pull request that lowers
   quality fails CI.
6. The service is observable (metrics, traces, cost per query) and protected
   (rate limits, caching).

## 4. Non-goals (we will NOT do these)
- A polished web frontend (a simple demo page or curl is enough).
- OCR for scanned PDFs (text-based PDFs only).
- Fine-grained permissions per document (permissions are per tenant and role).
- Billing, payments, or usage invoices.
- Training a model from scratch (we only fine-tune an embedding model).
- Supporting languages other than English.

## 5. User stories
| # | Story |
|---|---|
| U1 | As an admin, I want to sign up my company so that my team has a private space. |
| U2 | As an admin, I want to create and revoke API keys so that our programs can use the service safely. |
| U3 | As an admin, I want to upload PDF, Markdown and HTML files so that they become searchable. |
| U4 | As an admin, I want to see the status of each upload and why a failure happened so that I can fix it. |
| U5 | As a member, I want to ask a question and get an answer with citations so that I can verify it. |
| U6 | As a member, I want the answer to appear as it is written so that I do not wait for a long pause. |
| U7 | As a member, I want a clear "I don't have enough information" instead of a made-up answer. |
| U8 | As a member, I want to give a thumbs up or down so that bad answers can be improved. |
| U9 | As a tenant, I want to be sure no other company can read my documents. |
| U10 | As an operator, I want dashboards, traces and a runbook so that I can find and fix problems fast. |
| U11 | As an operator, I want CI to block changes that make answer quality worse. |

## 6. Requirements
| ID | Requirement | Priority |
|---|---|---|
| R1 | Sign up, log in (JWT), API keys, roles admin/member | Must |
| R2 | Row-level security on every tenant table | Must |
| R3 | Upload, status, list (cursor pagination), delete documents | Must |
| R4 | Background ingestion with retries, backoff, failed-state reporting | Must |
| R5 | Hybrid retrieval (keyword + vector) with reranking | Must |
| R6 | Cited answers; refusal when evidence is missing | Must |
| R7 | Streaming answers over SSE | Must |
| R8 | Response cache and per-tenant rate limits | Should |
| R9 | Tracing, metrics, cost per query | Should |
| R10 | Golden-dataset evaluation and CI eval gate | Must |
| R11 | Embedding fine-tuning experiment with honest results | Should |
| R12 | Public demo with HTTPS | Should |

## 7. Success metrics (first targets; measured on the golden dataset)
| Area | Metric | Target |
|---|---|---|
| Retrieval | recall@5 | at least 0.85 |
| Retrieval | MRR | at least 0.70 |
| Answers | faithfulness (claims supported by context) | at least 0.90 |
| Refusal | correct refusal on unanswerable questions | at least 0.85 |
| Refusal | false refusal on answerable questions | at most 0.10 |
| Speed | time to first token, p95 | under 2.5 seconds |
| Speed | whole answer, p95 | under 12 seconds |
| Reliability | error rate (5xx) | under 0.5% |
| Cost | cost per 1,000 queries | set a number after the first measurement |
| Safety | cross-tenant leaks found by tests | zero |

> These are **first guesses**. After your first measurements you may change a
> target, but write the change and the reason in `docs/retros/`. Never change a
> target silently to make a result look good.

## 8. Risks
| Risk | How we reduce it |
|---|---|
| Hallucinated answers | Grounding prompt, citation validation, refusal gate, evals |
| Cross-tenant data leak | Row-level security, isolation tests, mutation test |
| Runaway LLM cost | Cache, rate limits, token and cost metrics |
| Slow answers (reranker, LLM) | Measure each stage; limit candidates; timeouts |
| Poor golden dataset | Hand-write 60+ questions, review generated ones, freeze versions |
| Prompt injection inside documents | Treat retrieved text as data; add injection tests |

## 9. Open questions
- Which LLM provider and model? (decide in Sprint 4)
- Which cloud to deploy on? (decide in Sprint 6)