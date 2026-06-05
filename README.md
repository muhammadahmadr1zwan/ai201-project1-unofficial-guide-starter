# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

**NYU off-campus housing experiences and survival advice for students**

This unofficial guide focuses on NYU students' off-campus housing experiences: where students look for housing, what rent ranges they report, which neighborhoods come up often, how early they search, and what tradeoffs they face compared with dorming. This knowledge is hard to find because the most useful advice is scattered across Reddit threads, NYU resource pages, commuter-life posts, and housing portals rather than being organized in one student-friendly guide. The system should answer practical student questions using both official NYU resources and unofficial lived-experience discussions.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

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

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**

Reddit: ≤500 characters per comment/post (atomic when short). Official pages: ≤600 characters per paragraph under a section heading.

**Overlap:**

Reddit: 80 characters when splitting long comments only. Official: 100 characters between chunks when a section exceeds 600 characters.

**Why these choices fit your documents:**

Reddit comments carry rent figures, neighborhoods, and timing tips in single posts; official NYU/Meet NYU pages are structured by heading. See `planning.md` for full reasoning.

**Final chunk count:**

158 chunks across 10 sources (run `python run_pipeline.py` to regenerate).

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* Milestone 1 instructions and starter repo URL.
- *What it produced:* A focused domain, source list, skim notes, checkpoint questions, and documentation update plan.
- *What I changed or overrode:* I reviewed the proposed sources and replaced harder-to-access pages with more reliable NYU/Meet NYU sources.

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
