SendGrid + RQ mailer setup

This project now supports sending emails via SendGrid and enqueues jobs using RQ/Redis.

Quick start (development):

1. Install Python deps in your venv:

    source .venv/bin/activate
    pip install -r requirements.txt

2. Start Redis locally (macOS homebrew):

    brew install redis
    brew services start redis

3. Start the RQ worker from the project root:

    # uses worker.py which connects to localhost:6379
    python worker.py

   Or run the RQ CLI directly:

    rq worker default

4. Set environment variables (for SendGrid):

    export SENDGRID_API_KEY=your_sendgrid_key
    export EMAIL_SENDER=you@yourdomain.com

5. Start Flask and the frontend as usual.

Notes:
- If Redis or SendGrid are not available, the app will fall back to sending email via SMTP using the existing send_absence_email function (threaded). This is only a fallback for development.
- For production, configure SendGrid and run RQ workers and Redis.
