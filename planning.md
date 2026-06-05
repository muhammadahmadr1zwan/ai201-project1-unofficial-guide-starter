# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

**NYU off-campus housing experiences and survival advice for students**

This unofficial guide focuses on NYU students' off-campus housing experiences: where students look for housing, what rent ranges they report, which neighborhoods come up often, how early they search, and what tradeoffs they face compared with dorming. This knowledge is hard to find because the most useful advice is scattered across Reddit threads, NYU resource pages, commuter-life posts, and housing portals rather than being organized in one student-friendly guide. The system should answer practical student questions using both official NYU resources and unofficial lived-experience discussions.

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | r/nyu megathread: searches for on-campus or off-campus housing | Broad student Q&A on housing search, budgets, neighborhoods, and timing | https://www.reddit.com/r/nyu/comments/18elmin/megathread_searches_for_oncampus_or_offcampus/ |
| 2 | How hard is it to live off campus? | Student perspectives on feasibility, logistics, and first-year off-campus living | https://www.reddit.com/r/nyu/comments/1ibva9c/how_hard_is_it_to_live_off_campus/ |
| 3 | Where do students find off-campus apartments these days? | Platforms, brokers, Facebook groups, and search strategies students report using | https://www.reddit.com/r/nyu/comments/1jai7o9/where_do_students_find_offcampus_apartments_these/ |
| 4 | For those living off campus, how much is rent? | Student-reported rent ranges, roommate splits, and budget expectations | https://www.reddit.com/r/nyu/comments/muupej/for_those_who_are_living_off_campus_how_much_is/ |
| 5 | How long before the start of the semester did you start looking? | Timing advice for when to begin apartment hunting before fall | https://www.reddit.com/r/nyu/comments/o1r94w/people_living_offcampus_how_long_before_the_start/ |
| 6 | Questions regarding off-campus housing | General off-campus FAQ: leases, guarantors, neighborhoods, and process | https://www.reddit.com/r/nyu/comments/avc7qv/questions_regarding_offcampus_housing/ |
| 7 | Is it cheaper to live on or off campus? | Cost comparisons and tradeoffs between dorming and renting | https://www.reddit.com/r/nyu/comments/twlt4z/is_it_cheaper_to_live_on_or_off_campus/ |
| 8 | NYU Off-Campus Housing portal | Official listings, roommate search, renter resources, and university housing support | https://offcampushousing.nyu.edu/ |
| 9 | Home away from campus: NYU's commuter community | Commuter student life, campus resources, and off-campus community support | https://meet.nyu.edu/life/campus-resources/home-away-from-campus-nyus-commuter-community/ |
| 10 | Should I live off or on campus as an NYU student? | NYU guidance on on-campus vs. off-campus pros, cons, and decision factors | https://meet.nyu.edu/life/residential-life/should-i-live-off-or-on-campus-as-an-nyu-student/ |

**Additional candidate sources (not in primary set):**

- https://www.reddit.com/r/nyu/comments/142hmm9/transfer_off_campus_housing/
- https://www.reddit.com/r/nyu/comments/18kwk55/off_campus_students_how_much_do_you_pay_for_rent/
- https://www.nyu.edu/students/student-information-and-resources/housing-and-dining.html
- https://meet.nyu.edu/life/settling-into-your-off%E2%80%91campus-apartment-a-commuter-students-guide-to-lic/

### Document Skim Notes

**Reddit sources:** Mostly short, conversational posts and comments. Useful for student-reported budgets, roommate experiences, neighborhood suggestions, timing advice, scams, and tradeoffs between dorming and renting. Key facts are often concentrated in individual comments, so later chunking should preserve comment-level context instead of merging entire threads into one large chunk.

**Official NYU and Meet NYU sources:** More structured and reliable for university-provided information: the NYU Off-Campus Housing portal, roommate search, renter resources, commuter support, student-life guidance, and on-campus versus off-campus tradeoffs. These pages are better chunked by section heading or short paragraph because their information is organized by topic.

### Checkpoint Questions

Questions the system should be able to answer after the pipeline is built:

1. How much do NYU students usually pay for off-campus rent?
2. Which neighborhoods do students mention as realistic on a budget?
3. How early should I start looking for an apartment before fall semester?
4. Is living off campus cheaper or better than dorming?
5. Where do NYU students look for roommates, sublets, or apartments?

---

## Chunking Strategy

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

1.

2.

---

## Architecture

---

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
