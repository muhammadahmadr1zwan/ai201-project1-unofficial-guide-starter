# The Unofficial Guide — Project 1

**NYU off-campus housing guide** — a retrieval-augmented system over Reddit threads and NYU housing resources.

**Run the app:** `python app.py` → open http://localhost:7860  
**Demo video:** *[Add your 3–5 minute recording link here before submission]*

---

## Domain

**NYU off-campus housing experiences and survival advice for students**

This unofficial guide focuses on NYU students' off-campus housing experiences: where students look for housing, what rent ranges they report, which neighborhoods come up often, how early they search, and what tradeoffs they face compared with dorming. This knowledge is hard to find because the most useful advice is scattered across Reddit threads, NYU resource pages, commuter-life posts, and housing portals rather than being organized in one student-friendly guide. The system should answer practical student questions using both official NYU resources and unofficial lived-experience discussions.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | r/nyu megathread: searches for on-campus or off-campus housing | Reddit thread | https://www.reddit.com/r/nyu/comments/18elmin/megathread_searches_for_oncampus_or_offcampus/ |
| 2 | How hard is it to live off campus? | Reddit thread | https://www.reddit.com/r/nyu/comments/1ibva9c/how_hard_is_it_to_live_off_campus/ |
| 3 | Where do students find off-campus apartments these days? | Reddit thread | https://www.reddit.com/r/nyu/comments/1jai7o9/where_do_students_find_offcampus_apartments_these/ |
| 4 | For those living off campus, how much is rent? | Reddit thread | https://www.reddit.com/r/nyu/comments/muupej/for_those_who_are_living_off_campus_how_much_is/ |
| 5 | How long before the start of the semester did you start looking? | Reddit thread | https://www.reddit.com/r/nyu/comments/o1r94w/people_living_offcampus_how_long_before_the_start/ |
| 6 | Questions regarding off-campus housing | Reddit thread | https://www.reddit.com/r/nyu/comments/avc7qv/questions_regarding_offcampus_housing/ |
| 7 | Is it cheaper to live on or off campus? | Reddit thread | https://www.reddit.com/r/nyu/comments/twlt4z/is_it_cheaper_to_live_on_or_off_campus/ |
| 8 | NYU Off-Campus Housing portal | Official NYU page | https://offcampushousing.nyu.edu/ |
| 9 | Home away from campus: NYU's commuter community | Meet NYU article | https://meet.nyu.edu/life/campus-resources/home-away-from-campus-nyus-commuter-community/ |
| 10 | Should I live off or on campus as an NYU student? | Meet NYU article | https://meet.nyu.edu/life/residential-life/should-i-live-off-or-on-campus-as-an-nyu-student/ |

Raw and cleaned files live under `documents/raw/` and `documents/cleaned/`. Reddit threads were archived via the PullPush API when live Reddit returned 403; three official pages used `documents/manual/` fallbacks when NYU servers blocked automated fetch.

---

## Chunking Strategy

**Chunk size:**

- **Reddit:** One chunk per comment (or post) when ≤500 characters; longer comments split at sentence boundaries (max 500 chars).
- **Official pages:** Split on H2/H3 headings, then paragraphs (max 600 chars per chunk), with the section heading prepended.

**Overlap:**

- **Reddit:** 80 characters only when splitting a single long comment.
- **Official:** 100 characters between consecutive chunks when a section exceeds 600 characters.

**Why these choices fit your documents:**

Reddit housing advice is concentrated in individual comments (rent, timing, platforms). Merging whole threads would mix unrelated answers and hurt retrieval precision. Official NYU/Meet NYU pages are organized by topic, so heading + paragraph chunks preserve policy-style structure. Metadata (URL, `doc_type`, thread title) is prepended to every chunk for attribution at generation time.

**Final chunk count:**

**158 chunks** across 10 sources (regenerate with `python run_pipeline.py`).

---

## Embedding Model

**Model used:**

`all-MiniLM-L6-v2` via `sentence-transformers` (384-dimensional embeddings, runs locally). Vectors are stored in a persistent **ChromaDB** collection (`chroma_db/`, cosine distance). Retrieval uses **top-k = 5** (`retrieve.get_relevant_chunks`).

**Production tradeoff reflection:**

For a production NYU student guide, I would weigh: (1) **domain/colloquial matching** — larger models (e.g., `bge-large-en-v1.5`) may better match informal Reddit phrasing and neighborhood nicknames; (2) **multilingual queries** — international students might ask in other languages, favoring `multilingual-e5-large`; (3) **latency and cost** — MiniLM runs on-device with no embedding API fees, which fits a class project but may underperform on nuanced semantic matches (see Failure Case Analysis); (4) **context length** — longer Meet NYU articles could be embedded at section level with a longer-context model to reduce over-splitting.

---

## Grounded Generation

**System prompt grounding instruction:**

`generate.py` uses **Groq** `llama-3.3-70b-versatile` with a system prompt that:

- Requires answers **only** from labeled `[Source N]` blocks in the user message
- Mandates the exact phrase *"I don't have enough information on that"* when context is insufficient
- Forbids general NYU/NYC knowledge not present in chunks
- Requires inline `[Source N]` citations for factual claims
- Separates **official** vs **reddit** (student anecdote) voice

**Structural enforcement (not prompt-only):**

- If **no chunks** are retrieved, or the **best cosine distance > 0.52**, the LLM is **not called** and the system returns a refusal.
- **Temperature = 0.1** to reduce hallucination.
- **Sources are appended programmatically** after the LLM response (`_append_sources`), so attribution does not depend on the model remembering to cite.

**How source attribution is surfaced in the response:**

1. Inline `[Source N]` citations in the answer body (model-generated, tied to chunk labels in the prompt)  
2. A **Retrieved from** footer listing `source_file`, `doc_type`, title, and URL  
3. Gradio **Retrieved from** textbox (`app.py` → `query.ask()`)

---

## Evaluation Report

Evaluated with `python run_evaluation.py` after `python build_index.py`. Judgments compare responses to `planning.md` expected answers.

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | How much do NYU students usually pay for off-campus rent? | Wide student-reported range (~$1,000–$2,000+/person/mo); not one official price; note utilities/broker fees. | Cited portal listing ranges ($1,595–$7k), Reddit studio estimates ($1,300–$2k near campus), and a $1,755 Chelsea example; noted variability and extra costs. Sources: `reddit_04`, `official_08`, `reddit_07`. | Relevant | **Accurate** |
| 2 | Which neighborhoods do NYU students mention as realistic on a budget? | Outer-borough/commuter areas (Brooklyn neighborhoods, Astoria, Jersey City/Hoboken, Washington Heights); not East Village as a budget default. | Mostly said neighborhoods were **not specified**; mentioned StreetEasy/Zillow and one East Village roommate comment as "good value." Did **not** list Bushwick, Astoria, Jersey City, etc. Sources: `reddit_06`, `reddit_04` only. | Partially relevant | **Partially accurate** |
| 3 | How early should I start looking for an apartment before fall semester? | ~2–3 months before move-in (often May–June for Aug/Sep); summer peak season. | Recommended **mid/late July** (~4–5 weeks before lease start) from `reddit_05` comments; mentioned fast market and signing quickly. Missed May–June lead time in corpus. | Relevant | **Partially accurate** |
| 4 | Is living off campus cheaper or better than dorming? | Neither universally; tradeoffs (roommates, commute, utilities, brokers vs dorm convenience). | Presented mixed Reddit anecdotes ($1600 off-campus vs dorm, scholarship case for on-campus, extra off-campus costs); no single yes/no. Sources: `reddit_07`. | Relevant | **Accurate** |
| 5 | Where do NYU students look for roommates, sublets, or apartments? | NYU Off-Campus Housing portal + StreetEasy, Facebook groups, Leasebreak, Roomi, Craigslist, r/nyu. | Named **Facebook, Craigslist, NYU portal**; mentioned Furnished Finder; **did not** name StreetEasy, Leasebreak, or Roomi despite some appearing in corpus. Sources: `reddit_06`, `reddit_03`, `official_08`. | Partially relevant | **Partially accurate** |

**Out-of-domain check:** *"What is the best NYU dining hall for pizza?"* → **Declined** (weak retrieval + refusal message). Grounding checkpoint passed.

**Retrieval quality scale:** Relevant / Partially relevant / Off-target  
**Response accuracy scale:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:**

Which neighborhoods do NYU students mention as realistic on a budget?

**What the system returned:**

The model said specific budget neighborhoods were **not in the sources**, while citing StreetEasy/Zillow for price research and one **East Village** roommate comment as economical — contradicting the expected answer (outer-borough/commuter neighborhoods like Brooklyn, Astoria, Jersey City). Top retrieval distances were ~0.27–0.31 (acceptable), so the LLM ran rather than refusing.

**Root cause (tied to a specific pipeline stage):**

**Retrieval + corpus coverage mismatch.** The embedding search ranked chunks from `reddit_06` (international student with a **$600** budget) and generic StreetEasy advice from `reddit_04` highly because they mention "budget" and "neighborhood" co-occurring, but **did not retrieve** stronger chunks in the same index that explicitly name **Brooklyn, Astoria, Jersey City, and Queens** (e.g., comments in `reddit_04`, `reddit_06`, `reddit_02` — verified in `data/chunks.json`). Those neighborhood names live in **rent/timing threads**, not in the highest-ranked "budget" comments, so semantic search under-weighted them for this query phrasing.

A secondary factor is **ingestion**: official Meet NYU pages were thin manual summaries (only **7** official chunks total), so the system lacked structured university neighborhood guidance even though Reddit contained the answers.

**What you would change to fix it:**

1. Add **query expansion** or a second retrieval pass (e.g., also retrieve with "Brooklyn Astoria Jersey City NYU off campus") and merge results.  
2. Tag chunks with **metadata keywords** (borough, price_range) at ingest time and filter/boost on those fields.  
3. Expand official document ingestion so Meet NYU commuter/housing pages contribute more than a short manual summary.  
4. For generation, if retrieved chunks lack named neighborhoods, force a partial answer: *"Sources mention Brooklyn and Queens generally but do not list a complete budget neighborhood list."*

---

## Spec Reflection

**One way the spec helped you during implementation:**

`planning.md` forced decisions **before** coding — especially the hybrid chunking rules (atomic Reddit comments vs heading-based official sections) and top-k = 5. That spec was pasted into AI prompts for Milestones 3–5, which produced `chunk.py` and `generate.py` that matched the planned architecture diagram instead of a generic character-splitter or unconstrained chatbot. The Evaluation Plan also gave concrete test questions I could run after each milestone (retrieval distances in M4, full answers in M6).

**One way your implementation diverged from the spec, and why:**

The spec assumed **live URL ingestion** for all 10 sources. In practice, **Reddit returned HTTP 403** from the development environment, so ingestion used the **PullPush archive API** for Reddit JSON instead of `reddit.com/*.json`. NYU pages were sometimes blocked as well, so three official sources used **`documents/manual/*.md` summaries** rather than full HTML parsing. Chunk sizes and top-k stayed as specified, but the **document corpus is archive-based and partially manual**, which affects freshness and official-page depth — directly visible in the neighborhood failure above.

---

## AI Usage

**Instance 1 — Milestone 1 (domain & sources)**

- *What I gave the AI:* Milestone 1 instructions, domain description (NYU off-campus housing), and the starter repo template.
- *What it produced:* Draft text for `README.md` Domain/Document Sources and `planning.md` skim notes, checkpoint questions, and a 10-source table.
- *What I changed or overrode:* I reviewed URLs and kept Meet NYU / NYU portal sources instead of harder-to-scrape alternatives; I wrote the domain summary in my own course voice before commit.

**Instance 2 — Milestone 3 (ingest & chunk)**

- *What I gave the AI:* `planning.md` Documents + Chunking Strategy sections and the architecture diagram; requirement for `ingest.py`, `chunk.py`, and chunk inspection.
- *What it produced:* `sources.py`, `clean.py`, `chunk.py`, `ingest.py`, `run_pipeline.py` with hybrid 500/600-character rules and metadata prepended to chunks.
- *What I changed or overrode:* When Reddit blocked requests, I redirected ingestion to **PullPush** and added **manual official `.md` fallbacks** instead of shipping a broken scraper; I verified 5 random chunks and chunk count (158) before Milestone 4.

**Instance 3 — Milestones 4–5 (embed, retrieve, generate, UI)**

- *What I gave the AI:* Retrieval Approach from `planning.md`, `data/chunks.json` shape, grounding requirements (context-only answers, programmatic sources), and the Gradio Blocks skeleton from the assignment.
- *What it produced:* `retrieve.py`, `build_index.py`, `test_retrieval.py`, `generate.py`, `query.py`, `app.py`, `run_evaluation.py`.
- *What I changed or overrode:* I added a **distance > 0.52 guard** to refuse weak matches, lowered temperature to **0.1**, and ensured the **Retrieved from** footer is always appended in code — not left to the LLM. I tested an out-of-domain dining-hall question to confirm refusal behavior.

---

## Demo Video Checklist

Record **3–5 minutes** and link it at the top of this README. Include:

- [ ] At least **3 different queries** with **source citations** visible (answer + Retrieved from box)
- [ ] One query where **retrieval and generation both work well** (e.g., rent or on/off-campus tradeoffs)
- [ ] One query where the system **struggles or fails** (e.g., budget neighborhoods — narrate retrieval gap)
- [ ] Brief walkthrough of this **Evaluation Report** and **Failure Case Analysis**

Suggested commands: `python build_index.py` → `python app.py`
