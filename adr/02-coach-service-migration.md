Coach Service Migration
What we changed
We moved the WOD (Workout of the Day) generation logic from the main Flask app into a new microservice built using FastAPI. The main goal was to improve scalability and reduce the response time, since generating workouts was starting to slow things down.

Why we did this
The monolith was doing too many things at once — handling users, history, and workout generation. Since WOD generation is CPU-heavy and needs to scale more often, it made sense to isolate it. This way, we can run multiple instances of the coach service without affecting other parts of the app.

How we did it
We created a new FastAPI service (coach) that has one job: generate workouts.

The main Flask app sends a POST request to the coach service with the user’s email and a list of past exercise IDs.

The coach service returns a fresh workout, avoiding those exercises.

The history is still saved by the Flask app — the coach service doesn't touch the database.

We used Docker Compose to run both services together locally.

We followed the strangler fig pattern — the new service replaces the old logic gradually without breaking the app.

Result
No downtime during the switch.

The WOD logic is now cleanly separated.

We can scale the coach service easily.

Everything works the same from the user’s point of view.