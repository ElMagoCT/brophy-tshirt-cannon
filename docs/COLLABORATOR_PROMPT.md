# Prompt for a collaborator's Claude

Fill-in page with a copy button (Micah shares it): https://claude.ai/artifact/FC2tGChd7dJ44uQ9aeihVf

Paste this into Claude Code (it needs a terminal and git, so not the plain chat), after Micah has added your
GitHub account to the repo. Replace the two lines in angle brackets.

```text
You're helping design Brophy College Prep's T-shirt cannon robot (Mark 5, the "Glacis" design), a high-school
robotics build led by Micah Tucker. The whole robot is a parametric CadQuery model in the private GitHub repo
ElMagoCT/brophy-tshirt-cannon. Other people and other Claude chats are editing the same design, so the repo is the
source of truth and docs/UPDATES.md is how everyone knows what changed and who is working on what.

My name: <your name>
The change I want: <describe the design change>

1. If the repo isn't here yet, clone it (https://github.com/ElMagoCT/brophy-tshirt-cannon.git) and do the one-time
   setup in docs/COLLABORATING.md (Python 3.12 venv in cad/.venv from cad/requirements.txt). If you can't access the
   repo, stop and tell me to ask Micah to add my GitHub account.
2. Before anything else: git pull, read CLAUDE.md, docs/COLLABORATING.md, the "In progress" table and newest entries
   in docs/UPDATES.md, and run gh pr list. Tell me if my change overlaps someone's open work or undoes a settled
   decision, and ask before going on.
3. Follow docs/COLLABORATING.md exactly:
   - claim your files in UPDATES.md and push the claim;
   - work on a branch named <my-name>/<topic>;
   - make the change in cad/glacis;
   - run the checks until they're clean (one build at a time; they're heavy);
   - update bom/glacis_bom.py if parts change, with live, dated prices.
4. Finish:
   - add an entry at the top of docs/UPDATES.md using its template, and remove the claim;
   - commit, push the branch, and open a pull request with the entry as its description;
   - don't merge it, because Micah reviews.
5. Don't touch Onshape, the Google Sheet, purchases or anyone's accounts. List what's left for Micah under
   "Not done" in your entry.
6. When you're done, give me the PR link and a two-line summary of what changed.
```
