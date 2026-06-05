"""Source metadata for the NYU off-campus housing corpus."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    source_id: str
    title: str
    url: str
    doc_type: str  # "reddit" or "official"
    reddit_id: str | None = None


SOURCES: list[Source] = [
    Source(
        "reddit_01",
        "r/nyu megathread: searches for on-campus or off-campus housing",
        "https://www.reddit.com/r/nyu/comments/18elmin/megathread_searches_for_oncampus_or_offcampus/",
        "reddit",
        "18elmin",
    ),
    Source(
        "reddit_02",
        "How hard is it to live off campus?",
        "https://www.reddit.com/r/nyu/comments/1ibva9c/how_hard_is_it_to_live_off_campus/",
        "reddit",
        "1ibva9c",
    ),
    Source(
        "reddit_03",
        "Where do students find off-campus apartments these days?",
        "https://www.reddit.com/r/nyu/comments/1jai7o9/where_do_students_find_offcampus_apartments_these/",
        "reddit",
        "1jai7o9",
    ),
    Source(
        "reddit_04",
        "For those living off campus, how much is rent?",
        "https://www.reddit.com/r/nyu/comments/muupej/for_those_who_are_living_off_campus_how_much_is/",
        "reddit",
        "muupej",
    ),
    Source(
        "reddit_05",
        "How long before the start of the semester did you start looking?",
        "https://www.reddit.com/r/nyu/comments/o1r94w/people_living_offcampus_how_long_before_the_start/",
        "reddit",
        "o1r94w",
    ),
    Source(
        "reddit_06",
        "Questions regarding off-campus housing",
        "https://www.reddit.com/r/nyu/comments/avc7qv/questions_regarding_offcampus_housing/",
        "reddit",
        "avc7qv",
    ),
    Source(
        "reddit_07",
        "Is it cheaper to live on or off campus?",
        "https://www.reddit.com/r/nyu/comments/twlt4z/is_it_cheaper_to_live_on_or_off_campus/",
        "reddit",
        "twlt4z",
    ),
    Source(
        "official_08",
        "NYU Off-Campus Housing portal",
        "https://offcampushousing.nyu.edu/",
        "official",
    ),
    Source(
        "official_09",
        "Home away from campus: NYU's commuter community",
        "https://meet.nyu.edu/life/campus-resources/home-away-from-campus-nyus-commuter-community/",
        "official",
    ),
    Source(
        "official_10",
        "Should I live off or on campus as an NYU student?",
        "https://meet.nyu.edu/life/residential-life/should-i-live-off-or-on-campus-as-an-nyu-student/",
        "official",
    ),
]
