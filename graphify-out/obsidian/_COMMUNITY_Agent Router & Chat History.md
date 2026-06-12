---
type: community
cohesion: 0.06
members: 47
---

# Agent Router & Chat History

**Cohesion:** 0.06 - loosely connected
**Members:** 47 nodes

## Members
- [[Agent router — SSE-streaming AI coach chat.  Endpoints     POST   agentcha]] - rationale - api/routers/agent.py
- [[AgentDeps_4]] - code - api/routers/agent.py
- [[Append new messages to an existing session, creating it if necessary.      Cal]] - rationale - api/agent/history.py
- [[Async generator that yields SSE-formatted event strings.      Creates the shar]] - rationale - api/routers/agent.py
- [[ChatRequest]] - code - api/routers/agent.py
- [[Clear all in-memory conversation history for all sessions.      Useful for deb]] - rationale - api/routers/agent.py
- [[In-memory conversation history store.  Keeps ``ModelMessage`` lists keyed by `]] - rationale - api/agent/history.py
- [[LogSetRequest]] - code - api/models/workout.py
- [[ModelMessage]] - code - api/agent/history.py
- [[Request body for ``POST agentchat``.]] - rationale - api/routers/agent.py
- [[Return a callable that activates a plan by name for the user.]] - rationale - api/routers/agent.py
- [[Return a callable that fetches progression data for an exercise.]] - rationale - api/routers/agent.py
- [[Return a callable that fetches the weight trend for the given user.      Falls]] - rationale - api/routers/agent.py
- [[Return a callable that fetches today's mission list for the given user.]] - rationale - api/routers/agent.py
- [[Return a callable that fetches today's nutrition totals for the user.]] - rationale - api/routers/agent.py
- [[Return a callable that fetches today's workout for the given user.]] - rationale - api/routers/agent.py
- [[Return a callable that lists all saved workout plans for the user.]] - rationale - api/routers/agent.py
- [[Return a callable that logs a workout set for the given user.]] - rationale - api/routers/agent.py
- [[Return a callable that marks a mission complete for the given user.]] - rationale - api/routers/agent.py
- [[Return an async callable that AI-imports a workout from free-form text.]] - rationale - api/routers/agent.py
- [[Return the current time as ``HHMM`` in the given IANA timezone.]] - rationale - api/routers/agent.py
- [[Return the stored message history for a session.      Args         session_i]] - rationale - api/agent/history.py
- [[Return today's date as ``YYYY-MM-DD`` in the given IANA timezone.]] - rationale - api/routers/agent.py
- [[Run the Pydantic AI agent in a background task, pushing all events to the queue.]] - rationale - api/routers/agent.py
- [[Stream an AI coach response as Server-Sent Events.      Returns a ``textevent]] - rationale - api/routers/agent.py
- [[Wipe all in-memory session history.      Called by ``DELETE agenthistory``.]] - rationale - api/agent/history.py
- [[_local_hhmm()]] - code - api/routers/agent.py
- [[_local_today()]] - code - api/routers/agent.py
- [[_make_nutrition_getter()]] - code - api/routers/agent.py
- [[_make_plan_switcher()]] - code - api/routers/agent.py
- [[_make_plans_lister()]] - code - api/routers/agent.py
- [[_make_progression_getter()]] - code - api/routers/agent.py
- [[_make_set_logger()]] - code - api/routers/agent.py
- [[_make_task_completer()]] - code - api/routers/agent.py
- [[_make_task_status_getter()]] - code - api/routers/agent.py
- [[_make_today_workout_getter()]] - code - api/routers/agent.py
- [[_make_trend_getter()]] - code - api/routers/agent.py
- [[_make_workout_importer()]] - code - api/routers/agent.py
- [[_run_agent_to_queue()]] - code - api/routers/agent.py
- [[_sse_generator()]] - code - api/routers/agent.py
- [[agent.py_1]] - code - api/routers/agent.py
- [[chat_endpoint()]] - code - api/routers/agent.py
- [[clear_all_sessions()]] - code - api/agent/history.py
- [[clear_history_endpoint()]] - code - api/routers/agent.py
- [[get_session()]] - code - api/agent/history.py
- [[history.py]] - code - api/agent/history.py
- [[update_session()]] - code - api/agent/history.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Agent_Router__Chat_History
SORT file.name ASC
```

## Connections to other communities
- 6 edges to [[_COMMUNITY_Workout Models & Router Tests]]
- 5 edges to [[_COMMUNITY_Meal Models & Router Tests]]
- 5 edges to [[_COMMUNITY_Daily Task Service]]
- 5 edges to [[_COMMUNITY_Workout Service Queries]]
- 4 edges to [[_COMMUNITY_Logging Configuration]]
- 4 edges to [[_COMMUNITY_Weight Logging]]
- 4 edges to [[_COMMUNITY_Workout Plan Management]]
- 4 edges to [[_COMMUNITY_Meal Service Logic]]
- 4 edges to [[_COMMUNITY_Set Logging & Progression]]
- 3 edges to [[_COMMUNITY_Pydantic AI Agent Core]]
- 3 edges to [[_COMMUNITY_App Entry & Login]]
- 3 edges to [[_COMMUNITY_Settings Service & Router]]
- 2 edges to [[_COMMUNITY_Meal Analyzer Factory Tests]]
- 2 edges to [[_COMMUNITY_Weight Trend Computation]]
- 2 edges to [[_COMMUNITY_AI Workout Import]]
- 2 edges to [[_COMMUNITY_Weight REST Endpoints]]
- 1 edge to [[_COMMUNITY_Meals Router & Auth Dependency]]
- 1 edge to [[_COMMUNITY_Weight Validation Models]]
- 1 edge to [[_COMMUNITY_Workout REST Endpoints]]
- 1 edge to [[_COMMUNITY_Meal Macro Schemas]]
- 1 edge to [[_COMMUNITY_Meal Vision Service]]
- 1 edge to [[_COMMUNITY_Sheets Repo Helpers]]

## Top bridge nodes
- [[agent.py_1]] - degree 62, connects to 20 communities
- [[_sse_generator()]] - degree 20, connects to 4 communities
- [[LogSetRequest]] - degree 6, connects to 3 communities
- [[_make_set_logger()]] - degree 6, connects to 2 communities
- [[ChatRequest]] - degree 5, connects to 2 communities