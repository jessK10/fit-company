## Coach Service Migration – Using the Strangler Fig Pattern

context

Our application was originally built as a monolith, which worked fine in the beginning. But as the user base started growing, we noticed that some parts of the app were slowing things down — especially the WOD (Workout of the Day) generation. This route started becoming a bottleneck because it takes time to filter out exercises, apply logic, and generate new workouts for each user. On top of that, users were complaining that the workouts were getting repetitive.

At the same time, we knew the startup was aiming to scale fast and potentially grow into more features like diet plans, payments, etc. So it didn’t make sense to keep everything in one place anymore.



 We Decided to Do

Instead of rewriting the whole app or causing downtime, we followed the 'Strangler Fig pattern'. This means we slowly move one part of the system to a separate service while keeping everything else running.

We chose the WOD generation logic as the first piece to extract and created a new microservice for it — called the 'coach service'. This service would be responsible for just one thing: generating personalized workouts.



IMPLIMENTATION STEPS


1.COACH SERVICE (fastAPI) 
   We built a new FastAPI service that listens on '/wod' and expects two things:
    The user’s email
    A list of exercise IDs to exclude (to avoid repetition)

   It uses simple random logic to generate a new WOD from the remaining pool of exercises.


2.HISTORY STAYS IN MONOLIGHT 
   Since the microservice is only responsible for generating WODs, the user data and history remain in the monolith. This keeps responsibilities clean — no duplication of data.
 
 3.COMMUNICATION BETWEEN SERVIECIES
   When the user requests a WOD from the main app, the monolith checks the user’s history, selects the last 10–20 used exercises, and sends a request to the coach service via HTTP. The coach replies with a new set of exercises.

4.DOCKERIZED SETUP 
   Both the monolith and coach services are added to a Docker Compose file, so they run together as separate containers. This makes it easy to manage and test locally.

5.Scalability  
   Since the coach service is stateless (it doesn’t store anything), we can scale it horizontally by running multiple instances of it behind a load balancer in the future if needed.
 
   The frontend (or Postman tests) still hit the monolith — it now proxies the WOD call to the coach service in the background. No need to change external behavior.


 We avoided breaking the existing system or causing downtime.
 We didn’t try to refactor everything at once.
 The coach service is small, simple, and easy to maintain or scale.
 The monolith handles the user data, so we didn’t have to duplicate logic or sync two databases.
 Communication is clean and synchronous 
This opens the door to slowly migrating other parts in the future (diet plans, payments, etc.).

# K6 Load Test Summary

Users simulated (VUs): 50

Duration: 30 seconds

Total Requests: 1500

Success Rate: 100% (✓ status was 200)

Avg Request Duration: ~15ms

Max Duration: 234ms

No Failures: http_req_failed: 0.00%

Conclusion: current setup can easily handle at least 50 concurrent users, each doing ~1 request/sec, without any issues. 


# FINAL NOTE

This was a practical first step toward microservices. It made the system more modular and easier to manage, without overcomplicating things. The strangler fig pattern helped us modernize gradually and safely.
