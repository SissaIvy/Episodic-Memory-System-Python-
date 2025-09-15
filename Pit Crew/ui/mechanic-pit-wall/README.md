Mechanic Pit Wall (stub)

- Open index.html directly in a browser for a static preview.
- The page loads sample_health.json from the same folder.
- To preview real data, generate a health report and replace the sample file:

  1. python agents/mechanic_agent.py assess_crew_health --time-window 24h > reports/health/latest.json
  2. Copy reports/health/latest.json to ui/mechanic-pit-wall/sample_health.json

- For a richer interactive view, use the main PitCrew dashboard at ui/pitcrew-dashboard/.

