This frontend is a lightweight React scaffold converted from the Flask Jinja templates in the repository.

How to run:
1. cd frontend
2. npm install
3. npm run dev

Notes:
- The React components call Flask endpoints (e.g. `/login`, `/register`, `/dashboard`, `/create_class`, etc.). You can either run Flask on the same origin (e.g., `http://localhost:5000`) and configure a proxy, or adjust the fetch URLs to include the Flask server base URL.
- Copy `static/images/school_logo.png` into `frontend/public/static/images/` or update the `img` src paths if you want the logo to be served by the React dev server.
- This scaffold focuses on structure and mapping of templates to components; you may want to add authentication state management and API endpoints to fully connect it to your Flask backend.
