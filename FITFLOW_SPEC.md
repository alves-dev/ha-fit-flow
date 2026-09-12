# FitFlow — MVP Specification

> Repository: `ha-fit-flow`  
> Home Assistant domain: `fit_flow`  
> Integration name: **FitFlow**

## 1. Overview

FitFlow is a custom Home Assistant integration for managing a continuous, flexible workout routine rather than a fixed weekly schedule.

The integration must allow the user to configure exercises, muscle groups, workouts, external physical activities, and directional recovery/conflict rules. Based on the execution history, FitFlow recommends the next eligible workout, helps the user perform it through a custom panel, and stores the resulting workout history.

The initial use case is a gym routine composed of workouts such as A, B, C, and D, mixed with external activities such as volleyball and running. External activities may temporarily make specific workouts unsuitable.

The MVP is intentionally focused on **which exercises were performed**. Weight, sets, repetitions, progression, and more advanced performance tracking are explicitly future concerns.

---

## 2. Core principles

1. There is no weekly schedule.
2. Workouts are recommended dynamically from history and conflict rules.
3. The recommendation favors the eligible workout that has gone the longest without being performed.
4. Workouts define required muscle groups and exercise quantities, not a fixed list of exercises.
5. Exercises belong to muscle groups and can be rotated between workout sessions.
6. Exercise recommendations should favor exercises used less recently, but never block manual selection.
7. External activities such as volleyball and running are part of history and can affect workout recommendations.
8. Conflict rules are directional and time-based.
9. The UI guides the user but should avoid unnecessary hard restrictions.
10. Completed workouts count normally even when fewer or more exercises than planned were performed.

---

## 3. MVP scope

### Included

- Custom Home Assistant integration.
- Config Flow for initial setup.
- Custom sidebar panel.
- Muscle group management.
- Exercise management.
- Workout management.
- Physical activity management.
- Directional conflict/recovery rules expressed in hours.
- Dynamic next-workout recommendation.
- Exercise recommendation/rotation based on history.
- Active workout session persisted across frontend refreshes/restarts.
- Workout history.
- External activity history.
- Action for externally registering configured physical activities.
- Sensors for last activity, next recommended workout, and lifetime counters.

### Not included in MVP

- Weight tracking.
- Sets and repetitions.
- Exercise progression.
- Exercise performance metrics.
- Editing/deleting historical records through the UI.
- Multiple users/profiles.
- Workout opt-out from recommendations.
- Activity intensity variants.
- Activity-based recommendation behavior other than configured conflicts.
- Automatic workout scheduling by weekday.
- Nutrition tracking.
- Resetting lifetime counters.

---

# 4. Domain model

## 4.1 MuscleGroup

Represents a logical exercise group.

Examples:

- Chest
- Shoulders
- Triceps
- Core
- Quadriceps
- Glutes
- Hamstrings
- Calves
- Back
- Biceps
- Forearms / Grip

Suggested structure:

```yaml
id: chest
name: Chest
```

Requirements:

- `id` must be unique and stable.
- `name` must be editable.
- A muscle group cannot be deleted while referenced by an exercise or workout requirement unless those references are removed first.

---

## 4.2 Exercise

Represents an exercise available for selection during a workout.

```yaml
id: incline_dumbbell_press
name: Incline Dumbbell Press
muscle_group_id: chest
```

MVP fields:

- `id`
- `name`
- `muscle_group_id`

An exercise belongs to exactly one primary muscle group in the MVP.

This is intentionally simple. Secondary muscle groups can be introduced later without changing the basic workout model.

### Validation

- Name is required.
- Muscle group must exist.
- ID must be unique.
- Exercise deletion must not corrupt historical sessions. Historical entries should retain enough snapshot information to remain readable even if the exercise is later removed or renamed.

---

## 4.3 Workout

A workout describes how many exercises must be selected from each muscle group.

Example:

```yaml
id: workout_a
name: Workout A
requirements:
  - muscle_group_id: chest
    exercise_count: 2
  - muscle_group_id: shoulders
    exercise_count: 2
  - muscle_group_id: triceps
    exercise_count: 1
  - muscle_group_id: core
    exercise_count: 1
```

A workout does **not** contain a fixed exercise list.

The available exercises are resolved dynamically from exercises associated with each required muscle group.

### Validation

- Workout name is required.
- At least one requirement is required.
- Each requirement must reference an existing muscle group.
- `exercise_count >= 1`.
- The same muscle group should appear only once per workout.
- The UI should warn when fewer exercises exist for a muscle group than the workout requests, but configuration does not necessarily need to be permanently blocked if the user is still building the catalog.

---

## 4.4 Activity

Represents a physical activity performed outside FitFlow workouts.

Examples:

```yaml
id: volleyball
name: Volleyball
```

```yaml
id: running
name: Running
```

MVP fields:

- `id`
- `name`

Activities do not participate directly in the next-workout candidate list. Their purpose in the recommendation engine is to affect workouts through explicitly configured conflict rules.

There are no intensity variants in the MVP.

---

## 4.5 ConflictRule

Defines how long a performed workout or activity makes a target workout temporarily ineligible.

Example:

```yaml
source_type: activity
source_id: volleyball
target_workout_id: workout_d
recovery_hours: 36
```

Another example:

```yaml
source_type: workout
source_id: workout_b
target_workout_id: workout_d
recovery_hours: 48
```

### Important semantics

Rules are **directional**.

A rule:

```text
Workout B -> Workout D = 48 hours
```

does not imply:

```text
Workout D -> Workout B = 48 hours
```

If both directions are desired, two rules must exist.

The source can be:

- workout
- external activity

The target is always a workout in the MVP.

### Validation

- Source must exist.
- Target workout must exist.
- Recovery hours must be greater than zero.
- Duplicate source/target rules should be prevented or edited as a single rule.

---

# 5. History model

FitFlow must maintain its own persistent history rather than relying exclusively on Home Assistant Recorder.

This history is required for:

- recommendations;
- conflicts;
- exercise rotation;
- lifetime counters;
- panel history display.

Two event categories exist.

## 5.1 Workout history entry

Suggested structure:

```yaml
id: uuid
kind: workout
workout_id: workout_a
workout_name: Workout A
started_at: "2026-09-12T08:00:00-03:00"
finished_at: "2026-09-12T08:52:00-03:00"
exercises:
  - exercise_id: bench_press
    exercise_name: Bench Press
    muscle_group_id: chest
  - exercise_id: lateral_raise
    exercise_name: Lateral Raise
    muscle_group_id: shoulders
```

Snapshot names should be stored alongside IDs where useful so historical records remain understandable after configuration changes.

A workout is considered performed when the user explicitly finishes it.

It counts even if the workout was incomplete or exceeded the planned number of exercises.

---

## 5.2 Activity history entry

```yaml
id: uuid
kind: activity
activity_id: volleyball
activity_name: Volleyball
performed_at: "2026-09-11T19:00:00-03:00"
duration_minutes: 90
```

`duration_minutes` is optional.

Past activities may be registered by providing an explicit datetime.

If datetime is omitted, current time is used.

---

# 6. Active workout session

Starting a workout creates a persisted active session.

This is not yet a completed history entry.

Suggested structure:

```yaml
workout_id: workout_a
started_at: "2026-09-12T08:00:00-03:00"
selected_exercise_ids:
  - bench_press
  - lateral_raise
```

Only one active workout session is required in the MVP.

The session must survive:

- browser refresh;
- leaving/reopening the custom panel;
- Home Assistant frontend reload;
- preferably Home Assistant restart.

While a session is active, the panel should make it clear that the workout is in progress and prevent accidentally starting/replacing another workout without first cancelling or finishing the current session.

## Start

When the user starts the recommended or manually selected workout:

1. create active session;
2. store `started_at`;
3. show workout execution UI;
4. keep selection changes persisted.

## Finish

Finishing:

1. validates the current selection;
2. warns about deviations from planned quantities;
3. never blocks completion because of those deviations;
4. creates workout history entry;
5. increments lifetime workout counter;
6. clears active session;
7. recalculates next workout recommendation;
8. updates relevant entities.

## Cancel

Cancelling:

- clears active session;
- creates no history entry;
- increments no counters.

A confirmation dialog is recommended.

---

# 7. Workout execution behavior

For every workout requirement, the panel displays exercises belonging to the configured muscle group.

Example:

```text
Workout A

Chest — planned 2
[x] Bench Press
[ ] Incline Dumbbell Press
[x] Crossover
[ ] Peck Deck

Shoulders — planned 2
[x] Lateral Raise
[ ] Cable Lateral Raise
...

Progress: 3 / 6 planned exercises
```

The user can select any exercises.

The configured quantity is a **target**, not a hard constraint.

Examples:

- planned 2, selected 1 -> warning only;
- planned 2, selected 2 -> valid;
- planned 2, selected 3 -> warning only.

Finishing must remain possible in every case.

The history stores what actually happened.

---

# 8. Exercise recommendation and rotation

The custom panel should not merely display exercises alphabetically.

For each required muscle group, FitFlow should prioritize exercises based on exercise history.

## Principle

Prefer exercises that have not been performed recently.

Do not block exercises used recently.

Example:

```text
Chest — choose 2

Recommended
★ Incline Dumbbell Press
★ Crossover

Other exercises
  Bench Press
  Peck Deck
```

The user can freely select any exercise regardless of recommendation.

## Suggested ranking

For each exercise in the target muscle group:

1. exercises never performed come first;
2. otherwise sort by oldest `last_performed_at` first;
3. deterministic tie-breaker such as name or ID.

The algorithm should use all recorded workout history, not only history from the same workout, because the same exercise may eventually be available to multiple workouts using the same muscle group.

The UI may preselect the recommended number of exercises or merely highlight them. For the MVP, **highlighting/recommending is preferred over silently forcing selection**. The user remains in control.

---

# 9. Next workout recommendation engine

This is the main FitFlow domain service.

## Inputs

- configured workouts;
- completed workout history;
- external activity history;
- conflict rules;
- current datetime.

## Candidate selection

All configured workouts are initially candidates.

A workout becomes temporarily ineligible when at least one conflict rule affecting it is still active.

For every conflict rule:

```text
source -> target workout for N hours
```

FitFlow finds the most recent matching source occurrence.

The target is blocked while:

```text
current_time < source_time + recovery_hours
```

Once the recovery window expires, the workout becomes eligible again.

## Ranking eligible workouts

Among eligible workouts:

1. workouts never performed have highest priority;
2. otherwise choose the workout whose most recent completed session is oldest;
3. use a stable deterministic tie-breaker if required.

This is deliberately **not** a fixed A -> B -> C -> D cycle.

Example history:

```text
A: 2 days ago
B: 5 days ago
C: 4 days ago
D: 6 days ago
```

Without conflicts:

```text
Recommended: D
```

If volleyball occurred 12 hours ago and rules block D for 36 hours and B for 24 hours:

```text
B: blocked
D: blocked
A: eligible
C: eligible

Recommended: C
```

## No eligible workout

The engine must support a state where every workout is temporarily blocked.

In that case:

```text
sensor.fit_flow_next_workout = unavailable
```

or another clearly defined no-recommendation state consistent with HA entity conventions.

Attributes/UI should expose when the next workout becomes available when that can be calculated.

The panel should display a useful message rather than treating this as an error.

---

# 10. Conflict explanation

Recommendation decisions should be explainable.

The engine should internally produce information similar to:

```yaml
recommended_workout: workout_c
eligible_workouts:
  - workout_a
  - workout_c
blocked_workouts:
  workout_b:
    source: volleyball
    until: "2026-09-13T07:00:00-03:00"
  workout_d:
    source: volleyball
    until: "2026-09-13T19:00:00-03:00"
```

This allows both the sensor and custom panel to explain why a workout was or was not recommended.

---

# 11. Home Assistant action

The MVP exposes one public integration action:

```yaml
fit_flow.log_activity
```

Purpose: register a configured external physical activity.

Example:

```yaml
action: fit_flow.log_activity
data:
  activity: volleyball
```

Optional fields:

```yaml
action: fit_flow.log_activity
data:
  activity: volleyball
  datetime: "2026-09-11T19:00:00-03:00"
  duration_minutes: 90
```

## Validation

`activity` must resolve to an Activity already configured in FitFlow.

Unknown values must fail with a clear Home Assistant action validation error.

Do not silently create activities from action input.

`duration_minutes`, when provided, must be positive.

`datetime`, when omitted, defaults to now.

After successful registration:

1. persist activity history entry;
2. increment lifetime activity counter;
3. recalculate recommendation;
4. update entities.

This action is the automation-friendly public API for external activities.

No public start/finish/cancel workout actions are required in the MVP.

---

# 12. Home Assistant entities

## 12.1 Last activity sensor

Suggested entity:

```text
sensor.fit_flow_last_activity
```

The sensor represents the most recent completed item across both workouts and external activities.

Example workout:

```yaml
state: workout_a
attributes:
  type: workout
  name: Workout A
  datetime: "2026-09-12T08:52:00-03:00"
  started_at: "2026-09-12T08:00:00-03:00"
  duration_minutes: 52
  exercise_count: 6
```

Example activity:

```yaml
state: volleyball
attributes:
  type: activity
  name: Volleyball
  datetime: "2026-09-11T19:00:00-03:00"
  duration_minutes: 90
```

Do not expose the entire historical database as entity attributes.

---

## 12.2 Next workout sensor

Suggested entity:

```text
sensor.fit_flow_next_workout
```

Example:

```yaml
state: workout_c
attributes:
  name: Workout C
  last_performed: "2026-09-07T18:00:00-03:00"
  blocked_workouts:
    - workout_b
    - workout_d
```

Additional small explanatory attributes are acceptable, but avoid turning entity state attributes into a large history/configuration dump.

The custom panel can obtain richer recommendation details from the integration's frontend API/websocket layer.

---

## 12.3 Lifetime workout counters

One sensor per configured workout.

Examples:

```text
sensor.fit_flow_workout_a_count
sensor.fit_flow_workout_b_count
sensor.fit_flow_workout_c_count
sensor.fit_flow_workout_d_count
```

State is an integer representing total completed sessions since FitFlow history began.

Incomplete-but-finished workouts count.

Cancelled workouts do not count.

---

## 12.4 Lifetime activity counters

One sensor per configured external activity.

Examples:

```text
sensor.fit_flow_volleyball_count
sensor.fit_flow_running_count
```

State is total registered occurrences.

Counters are lifetime values in the MVP.

No reset functionality is required.

Counters should preferably be derived from or kept consistent with persistent history so they cannot drift silently.

---

# 13. Custom panel

FitFlow should register a custom panel accessible from the Home Assistant sidebar.

The panel has two primary responsibilities:

1. configure FitFlow;
2. perform and monitor workouts.

A third history view is useful and should be included in the MVP even though editing history is not required.

Suggested navigation:

```text
FitFlow
├── Today
├── History
└── Configuration
    ├── Muscle Groups
    ├── Exercises
    ├── Workouts
    ├── Activities
    └── Conflict Rules
```

The exact visual navigation may use tabs, routes, or sections.

---

# 14. Today screen

When no workout is active, show the recommended workout prominently.

Example:

```text
FitFlow

Recommended workout

Workout C — Pull
Last performed: 5 days ago

3 Back
1 Rear Deltoid
1 Biceps
1 Forearm / Grip

[ START WORKOUT ]
```

Optionally show other eligible workouts beneath the recommendation so the user can manually choose a different workout.

A recommendation is guidance, not an obligation.

Blocked workouts should be visually distinguishable and explain the blocking source/recovery time.

Example:

```text
Workout B
Unavailable for 11h 23m
Reason: Volleyball
```

The user should not normally start a currently conflicting workout without at least a warning. Since the overall product philosophy avoids hard restrictions, the implementation may permit an explicit override after warning. The recommendation engine itself must still consider it blocked.

---

# 15. Active workout screen

Once started, the Today screen switches into session mode.

Requirements:

- workout name;
- start time;
- elapsed duration display;
- sections grouped by workout requirement/muscle group;
- target quantity for each group;
- recommended exercises highlighted;
- selectable exercise rows/cards;
- group progress;
- total planned vs selected progress;
- Finish Workout;
- Cancel Workout.

Example:

```text
Workout A                    42 min

Chest                         2 / 2
★ [x] Incline Dumbbell Press
★ [x] Crossover
  [ ] Bench Press
  [ ] Peck Deck

Shoulders                     1 / 2
★ [x] Cable Lateral Raise
★ [ ] Dumbbell Shoulder Press
  [ ] Lateral Raise

...

Selected: 5
Planned: 6

[ CANCEL ]              [ FINISH ]
```

Sections may be collapsible for usability.

Collapsed/expanded UI state does not need persistent storage.

The active workout itself does.

---

# 16. Finishing validation UX

FitFlow must calculate planned counts versus actual selected counts.

If everything matches, finish normally.

If there are deviations, display a confirmation summary.

Example:

```text
Finish Workout A?

Chest       planned 2 / performed 3
Shoulders   planned 2 / performed 1
Triceps     planned 1 / performed 1
Core        planned 1 / performed 1

Planned total: 6
Performed: 6

This workout differs from the configured plan.

[ GO BACK ] [ FINISH ANYWAY ]
```

No deviation blocks completion.

---

# 17. History screen

Read-only in the MVP.

Display newest first.

Example:

```text
12 Sep
Workout A
52 min • 6 exercises

11 Sep
Volleyball
90 min

09 Sep
Workout C
58 min • 6 exercises
```

Opening a workout record should show performed exercises.

Opening an activity record should show available metadata such as datetime and duration.

No edit/delete is required for v1.

---

# 18. Configuration UI

## Muscle Groups

Must support:

- list;
- create;
- rename;
- delete when safe.

## Exercises

Must support:

- list;
- create;
- edit;
- delete;
- muscle-group assignment;
- filter/group by muscle group where useful.

## Workouts

Must support:

- list;
- create;
- edit;
- delete;
- configure multiple muscle-group requirements;
- configure exercise quantity for each requirement.

The UI should display planned total exercise count calculated from requirements.

Example:

```text
Workout A

Chest       2
Shoulders   2
Triceps     1
Core        1
─────────────
Total       6
```

## Activities

Must support:

- list;
- create;
- rename/edit;
- delete when safe.

Examples: Volleyball, Running.

## Conflict Rules

Provide a clear directional editor.

Example table:

| Source | Target workout | Recovery |
|---|---|---:|
| Workout B | Workout D | 48h |
| Workout D | Workout B | 48h |
| Volleyball | Workout B | 24h |
| Volleyball | Workout D | 36h |
| Running | Workout B | 24h |

The UI must make directionality visually obvious.

---

# 19. Initial configuration / Config Flow

The integration must support standard Home Assistant UI setup through Config Flow.

The Config Flow itself should remain lightweight.

Its responsibility is primarily to create the FitFlow integration instance.

Detailed domain configuration belongs in the custom panel rather than trying to build the entire exercise/workout editor inside Config Flow.

For the MVP, only one FitFlow instance is necessary.

Multiple people/profiles are out of scope.

---

# 20. Persistence

FitFlow needs persistent integration-owned storage for:

- muscle groups;
- exercises;
- workouts;
- activities;
- conflict rules;
- active session;
- completed history.

Use Home Assistant-supported integration storage patterns rather than a standalone external database for the MVP.

Storage must be versioned to allow future migrations.

Suggested conceptual root:

```yaml
version: 1
config:
  muscle_groups: []
  exercises: []
  workouts: []
  activities: []
  conflict_rules: []
active_session: null
history: []
```

The implementation may split configuration/history into separate stores if that produces cleaner or safer persistence.

History may grow indefinitely in the initial version. The storage abstraction should nevertheless avoid requiring a complete domain redesign when retention/database changes are introduced later.

---

# 21. Internal architecture

Suggested Python structure:

```text
custom_components/fit_flow/
├── __init__.py
├── manifest.json
├── const.py
├── config_flow.py
├── sensor.py
├── services.yaml
├── strings.json
├── translations/
│   └── en.json
├── models/
│   ├── exercise.py
│   ├── muscle_group.py
│   ├── workout.py
│   ├── activity.py
│   ├── conflict.py
│   └── session.py
├── storage.py
├── history.py
├── recommendation.py
├── exercise_recommendation.py
├── services.py
├── coordinator.py
└── panel/
    └── ... frontend build/static files
```

Exact file organization is implementation-dependent, but business logic should not live inside sensor entities or frontend handlers.

Important domain services:

### RecommendationEngine

Responsible for:

- evaluating active conflict windows;
- finding eligible workouts;
- ranking workouts by last completion;
- explaining blocked workouts;
- producing next recommendation.

### ExerciseRecommendationEngine

Responsible for:

- resolving exercises by muscle group;
- determining last usage;
- ranking least-recently-used exercises;
- returning recommended choices for each workout requirement.

### HistoryManager

Responsible for:

- recording completed workouts;
- recording activities;
- querying latest performed item;
- querying latest workout occurrence;
- querying latest exercise occurrence;
- lifetime counts.

### SessionManager

Responsible for:

- starting workout;
- updating selected exercises;
- finishing workout;
- cancelling workout;
- restoring active session after restart.

---

# 22. Frontend/backend API

The custom panel will need richer data and mutations than Home Assistant state entities should carry.

Expose an integration-specific frontend API, preferably using Home Assistant websocket commands/patterns appropriate for custom panels.

Conceptual operations include:

```text
fit_flow/config/get
fit_flow/muscle_groups/create
fit_flow/muscle_groups/update
fit_flow/muscle_groups/delete
fit_flow/exercises/create
fit_flow/exercises/update
fit_flow/exercises/delete
fit_flow/workouts/create
fit_flow/workouts/update
fit_flow/workouts/delete
fit_flow/activities/create
fit_flow/activities/update
fit_flow/activities/delete
fit_flow/conflicts/create
fit_flow/conflicts/update
fit_flow/conflicts/delete

fit_flow/recommendation/get

fit_flow/session/start
fit_flow/session/update
fit_flow/session/finish
fit_flow/session/cancel

fit_flow/history/list
fit_flow/history/detail
```

These names are conceptual and may be adjusted to Home Assistant frontend conventions during implementation.

Do not use entity attributes as a substitute for the panel API.

---

# 23. Entity update strategy

Entities should update immediately after relevant mutations.

Events requiring recalculation include:

- workout finished;
- activity logged;
- workout configuration changed;
- activity configuration changed;
- conflict rule changed;
- history changed in future versions.

Time itself can also make a blocked workout become eligible.

Therefore the next-workout entity must account for recovery expiration without requiring a new activity to occur.

The implementation should schedule a refresh at the nearest conflict expiration time or use another efficient HA-native mechanism. Avoid aggressive polling.

---

# 24. Initial FitFlow data example

The integration must not necessarily hardcode this dataset, but it is a useful reference fixture/test dataset.

## Workout A — Push

Requirements:

| Group | Count |
|---|---:|
| Chest | 2 |
| Shoulders | 2 |
| Triceps | 1 |
| Core | 1 |

Example exercises:

| Group | Exercise |
|---|---|
| Chest | Barbell Bench Press |
| Chest | Incline Dumbbell Press |
| Chest | Pec Deck |
| Chest | Cable Crossover |
| Shoulders | Dumbbell Shoulder Press |
| Shoulders | Dumbbell Lateral Raise |
| Shoulders | Cable Lateral Raise |
| Shoulders | Machine Shoulder Press |
| Triceps | Cable Pushdown |
| Triceps | Rope Pushdown |
| Triceps | Overhead Triceps Extension |
| Core | Plank |

## Workout B — Legs / anterior emphasis

Requirements:

| Group | Count |
|---|---:|
| Quadriceps / Glutes | 3 |
| Hamstrings | 1 |
| Calves | 1 |
| Core | 1 |

Reference exercise catalog may include squat, leg press, leg extension, lunge, Bulgarian split squat, hack squat, leg curl variations, calf raises, cable crunch, and side plank.

## Workout C — Pull

Requirements:

| Group | Count |
|---|---:|
| Back | 3 |
| Rear Deltoid | 1 |
| Biceps | 1 |
| Biceps / Forearm / Grip | 1 |

Reference exercise catalog may include vertical pulldowns, rows, straight-arm pulldown, reverse fly, face pull, curls, hammer curl, and wrist/forearm work.

A future refinement may encode movement-pattern diversity such as requiring at least one vertical and one horizontal pull. This is **not required by the generic MVP workout model** unless explicitly implemented as a future rule system.

## Workout D — Legs / posterior emphasis

Requirements:

| Group | Count |
|---|---:|
| Hamstrings | 2 |
| Glutes / Legs | 2 |
| Calves | 1 |
| Core | 1 |

Reference exercise catalog may include Romanian deadlift, leg curl variations, hip thrust, glute bridge machine, reverse lunge, step-up, calf raises, leg raises, and Pallof press.

---

# 25. Important edge cases

## First use

If no workout has ever been performed, all eligible workouts tie as never performed.

Use a deterministic ordering so recommendation does not randomly change between refreshes.

## Exercise never performed

Prioritize it over previously performed exercises in the same muscle group.

## Activity registered in the past

Recalculate conflicts using the provided occurrence datetime, not registration time.

## Multiple matching conflict sources

If multiple historical occurrences/rules block a workout, the effective block lasts until the latest applicable `blocked_until`.

The explanation may expose the rule/source producing the latest expiration and optionally all active reasons.

## Configuration changes while session active

Avoid allowing destructive configuration changes that invalidate the active session.

At minimum, deletion of the active workout or selected exercises should be rejected while referenced by an active session.

## Home Assistant restart during workout

Restore active session.

Elapsed duration derives from persisted `started_at`, not an in-memory timer.

## Duplicate finish request

Finishing should be idempotent enough to avoid accidentally creating duplicate history entries from frontend retries/double-clicks.

## Unknown activity action input

Reject with clear validation error and do not mutate history/counters.

## All workouts blocked

Expose no recommendation cleanly and calculate nearest eligibility time where possible.

---

# 26. Future evolution

The data model should leave room for these features without implementing them now.

## Exercise performance

A performed exercise may eventually become:

```yaml
exercise_id: bench_press
sets:
  - weight: 60
    reps: 12
  - weight: 60
    reps: 10
  - weight: 55
    reps: 10
```

## Additional future possibilities

- weight × repetitions;
- sets;
- rest timer;
- progression suggestions;
- exercise notes;
- personal records;
- charts;
- workout duration statistics;
- configurable period counters;
- history editing/deletion;
- workout E / complementary training;
- cardio sessions;
- mobility and loaded carries;
- activity intensity/distance;
- exercise secondary muscle groups;
- workout movement-pattern rules;
- Recorder/statistics integration;
- dashboard cards;
- multiple profiles;
- data export/import.

These should not complicate the MVP implementation prematurely.

---

# 27. MVP acceptance criteria

The MVP is considered functional when the following scenario works end-to-end:

1. User installs FitFlow through Home Assistant.
2. User adds the integration through UI.
3. FitFlow custom panel appears.
4. User creates muscle groups.
5. User creates exercises and assigns each to a muscle group.
6. User creates workouts with group/count requirements.
7. User creates `Volleyball` and `Running` activities.
8. User creates directional conflict rules such as Volleyball -> Workout B for 24h and Volleyball -> Workout D for 36h.
9. FitFlow recommends an eligible workout using least-recently-performed logic.
10. User starts the workout.
11. FitFlow shows exercises grouped by requirement and highlights least-recently-used recommendations.
12. User selects exercises.
13. User can refresh/reopen the panel without losing the active session.
14. User finishes with exactly, fewer, or more exercises than planned.
15. FitFlow records the completed workout and updates counters/history/entities.
16. The next recommendation changes according to history.
17. A Home Assistant automation calls:

```yaml
action: fit_flow.log_activity
data:
  activity: volleyball
```

18. FitFlow validates `volleyball`, records it, increments its lifetime counter, and recalculates conflicts.
19. Workouts blocked by Volleyball stop being recommended until their configured recovery windows expire.
20. Once a recovery window expires, recommendation updates without requiring another workout/activity event.
21. `sensor.fit_flow_last_activity` reflects the latest workout/activity.
22. `sensor.fit_flow_next_workout` reflects the current recommendation.
23. Per-workout and per-activity lifetime count sensors reflect persisted history.
24. Cancelling an active workout leaves no completed history and increments no counter.

---

# 28. Product philosophy summary

FitFlow should behave as an **assistant for a flexible training routine**, not as a rigid workout enforcer.

The integration should answer three practical questions:

```text
What should I train next?

Which exercises make sense to rotate into this workout?

What have I actually done?
```

Conflict rules protect recovery by influencing recommendations. Workout requirements provide structure. History provides continuity. The custom panel makes the whole workflow usable without forcing the user into a fixed weekly calendar.

