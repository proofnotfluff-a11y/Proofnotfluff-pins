# Decisions, Nov 2, 2026

## The story desk (live chat, 12:28 pm)
- [stated] 12:28 pm: "We need to create an agent that is an investigative journalist master, somebody who can go out on the web and find really, really interesting new stories about trades in AI software implementation, and write these scripts as if they were a Pulitzer Prize winning investigative journalist, but made for short form videos. So still keep the same techniques that we have with regard to hooks and grabbing people's attention, but the content has to be really interesting. I think we need a designated agent for this, so look into building something like that."
- Built: .claude/skills/story-desk/SKILL.md (3 beat reporters: records, money, the field; a 10-point story test; verify every receipt; dossier; script); video/studio/_shared/investigative.md (story test, beats, verification, fairness, script craft, dossier template); research/STORIES.md and research/stories/; format dispatch (45 to 70 s, 115 to 180 words) and hook pattern receipt in anim.py and _shared/formats.md; prompts/facts.md item 7; lanes.md: a Ready story is the AI lane's first pick.
- No new runs (weekly usage 78% on Nov 1): the record and make task runs one report a day inside a run where 2 lessons already wait, and makes a Ready story before any other AI idea (task prompt updated).
- First run, live: 9 leads, 2 verified Ready (Google moves Local Services Ads into its AI ad system and the max cost per lead goes away; homeowners would ask ChatGPT for a contractor almost as often as Yelp), 2 leads to verify (FCC opt-out rule Nov 25; ServiceTitan's 11% AI trust survey), 6 killed with reasons.

## The Radar (live chat, about 1:30 pm)
- Todd shared the joebrunner.ai New Home Radar reel and a screen recording: "Please learn from this and engineer this for PNF". Teardown: video/studio/research/runs/2026-11-02-new-home-radar-reel.md.
- [stated] Asked which Radar to build first, Todd picked "Both, restaurants first". Spec: launches/chicago-restaurant-radar.md (restaurants on data we pull; homeowner version waits on his CONSTITUTION 4 change and the Legal desk).
- [stated] Asked whether to drop our rule against a "comment a word" ask and DMs, Todd picked "Allow it". Not active: the CONSTITUTION 2 line is written only once he picks a comment-to-DM tool and plan in a live chat (price notes in the spec).
