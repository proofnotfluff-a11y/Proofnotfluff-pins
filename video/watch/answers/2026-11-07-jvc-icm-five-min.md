# Video answer

- Source: https://www.youtube.com/watch?v=dZ8P7zevuGw (link sent to Google)
- Model: gemini-3.8-flash (generateContent)
- Gemini tokens: 34066

## Answer (Gemini's observations, not frames Claude viewed)

### Ordered Steps, Folder Structure, and Layer Contents

#### 1. Architectural Layers
The presentation displays a four-layer architecture on slides:
* **Layer 1: The Front Desk** (seen at 02:06 to 02:10): The user interface layer where people interact via chat, voice, Slack, Teams, or email. In practice, this is shown as a chat interface such as ChatGPT (seen at 03:00 to 03:04) or Claude Desktop (seen at 03:41 to 03:52).
* **Layer 2: The Catalog** (seen at 02:06 to 02:12): A signal layer containing routing logic, organizational details, brand rules, and process definitions using short statements that point to external files rather than holding raw data.
* **Layer 3: The Request Slip** (seen at 02:06 to 02:07): Described on the slide as one-line calls within a workflow.
* **Layer 4: The Stacks** (seen at 02:06 to 02:07): The underlying data repository stored at scale.

#### 2. Root and System Configuration Files
In the file explorer and text editor views, the workspace directory structure is organized as follows:
* **Root Folder:** `High Tea Sessions` (seen at 01:24).
* **Root Routing Files:** 
  * `_AGENTS` or `_AGENTS.md` (seen at 01:24 and 02:30 to 02:35): Outlines the sequential tasks, commands, shell execution syntax, and pipeline milestones.
  * `_CONFIG` and `_CONTEXT` (seen at 01:24).
* **Shared Assets:** `Eduba Design System (1)` containing subfolders for `brand`, `fonts`, `icons`, and `ui-kit` (seen at 02:20 to 02:22).
* **Work Directory:** `sessions` (seen at 01:35 to 01:41), containing individual session directories such as `ht11-solution-not-software` (seen at 01:42) and `ht13-discovery-drill` (seen at 01:37).

#### 3. Ordered Workflow Stages
The video shows two slightly different naming conventions for the pipeline stages: one in the actual Windows filesystem and another on the conceptual summary slide.

**As shown in the Windows filesystem (seen at 01:37 to 02:04 and 02:47 to 02:52):**
1. `10_in-place`: Holds initial planning documents or session briefs (seen at 01:37 and 02:49).
2. `20_recording`: Contains raw audio or video files such as `CONTENT` (seen at 01:44).
3. `30_transcript`: Contains transcript files, specifically `raw.txt` (seen at 01:46 to 01:49).
4. `40_package` and `45_package`: Contains assembled outputs, including `Member-Responses` (seen at 01:51 to 01:56) or subfolders like `consulting-pilot-kit` containing briefs, contracts, and pricing sheets (seen at 02:01 to 02:04).
5. `50_publish`: Final staging folder for public distribution (seen at 01:37 and 02:49).

**As shown on the summary slide (seen at 04:35 to 04:43):**
1. `00_RECORDING`: User drops in `session.mp4` (seen at 04:36).
2. `10_TRANSCRIPT`: Generates `raw.txt`, `session.vtt`, and `cleaned.md` (seen at 04:37 to 04:38).
3. `20_PACKAGE`: Generates deliverables such as `session-notes`, `tape-sheet`, `discord-drop`, and `vault-page` (seen at 04:39 to 04:40).
4. `30_PUBLISH`: Generates `youtube-assets` and a `checklist` (seen at 04:40 to 04:43).

#### 4. How an AI Run Reads the Files
* **Prompting the Model (03:00 to 03:15):** The user enters a standard chat request, such as asking the model to build the package for session 15 (seen at 03:01; heard at 03:13 to 03:15).
* **Command-Line Discovery (03:20 to 03:24):** The model runs PowerShell commands (e.g., `rg -files -m "AGENTS.md"`, `Get-ChildItem`) to locate the root instruction files.
* **Parsing Context (seen at 03:21 to 03:24; heard at 03:20 to 03:28):** The speaker explains that the model reads `agent.md` or `claude.md` alongside the directory's `_CONTEXT` file. This lets it inspect folder status, inputs, and stage boundaries without needing pre-coded agent software.
* **Generating Artifacts (03:25 to 03:39):** The model executes scripts, validates rules, and writes markdown artifacts (such as `session-notes.md` and `README.md`) directly into the target folders.

---

### Rules Taught in the Video

#### Rules for Keeping Context Small
* **Pointers over Content:** Slide 2 notes that the catalog holds short, stable sentences rather than full texts (seen at 02:11).
* **Hierarchical Nesting:** The speaker states that context should live inside each subfolder, so the model only loads instructions relevant to the specific directory it navigates into (heard at 02:44 to 02:53).
* **Missing Details:** The video does not provide exact token budgets, context window thresholds, or programmatic context pruning algorithms.

#### Rules for Checks Between Stages
* **Human-in-the-Loop Signoffs:** The `_CONTEXT` file explicitly defines a human check checkpoint for each stage before proceeding (seen at 02:49).
* **Status Audits:** Automated checks must verify privacy rules, link integrity, and voice compliance, logging whether status is started, in progress, or pending human review (seen at 03:01 to 03:04, 03:25 to 03:28, and 04:35 to 04:44).

#### Rules for When to Use or Not Use Agents
* **Avoid Hard-Coded Agent Chains:** The speaker argues that coding specialized Planner, Analyst, and Writer classes inside application code is unnecessary (heard at 00:10 to 00:38; seen at 00:23 to 00:25). Because modern models can reason, read files, and call tools natively, wrapping them in multi-agent code is redundant.
* **When to Use Multi-Agent Frameworks:** The video does not specify any valid use cases for traditional multi-agent orchestration code, rejecting it entirely in favor of one model navigating an organized workspace.

---

### Evidence Shown vs. Claims Merely Asserted

#### Supported by Visual Evidence
* **Single Model Directory Navigation:** The video demonstrates both ChatGPT (03:01 to 03:39) and Claude Desktop (03:41 to 04:00) reading file paths via shell commands, inspecting markdown guides, and generating structured notes.
* **Readable Workspace Structure:** The video shows working markdown instruction files (`_AGENTS` and `_CONTEXT`) that define stage inputs, shell script calls, and verification gates (02:30 to 02:35 and 02:49 to 02:51).

#### Merely Asserted Without Empirical Proof
* **Orchestration Code is Wasted Work:** The speaker asserts that multi-agent coding is generally wasted effort (00:23 to 00:34), but does not present benchmark tests, latency figures, or cost comparisons comparing ICM to coded multi-agent frameworks.
* **Accessibility for Non-Technical Users:** The speaker asserts that folder-based ICMs are easier for non-technical people to edit and audit (04:44 to 04:48), but only demonstrates technical markdown editing in code environments and shell terminals.
* **Scalability and Enterprise Fit:** The slides describe four enterprise layers suitable for organization-wide scale (02:06 to 02:15), but only demonstrate a personal desktop file workflow for video lecture processing.
