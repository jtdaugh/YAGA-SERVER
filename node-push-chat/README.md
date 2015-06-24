Firenode - processes firebase event data streams and queues push notifications via Celery

Run it - node index.js

Debug it - node index.js -r (opens a repl, with the firenode object in context)

Configure it - the config folder provides connection info/creds for postgres and firebase.

Test it - requires mocha. npm install -g mocha && mocha test