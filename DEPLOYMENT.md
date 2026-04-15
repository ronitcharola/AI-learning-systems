# Deployment Guide: AI-Powered Personal Productivity OS 🚀

This application is split into a Python Flask REST API backend and a Vanilla JS Single-Page Application (SPA) frontend. Because they are decoupled, they should be deployed independently.

## 1. Backend Server Deployment (Render)

We recommend using **Render** as it has excellent native Python support and an easy GitHub integration.

### Preparation
1. Ensure your code is in a Git repository.
2. The `backend/requirements.txt` is already generated.
3. Render needs a WSGI server to start your app.
   - You need to add `gunicorn` to `backend/requirements.txt`.
   - Start command for Render: `gunicorn "app:create_app()"`

### Deployment Steps on Render
1. Create a New "Web Service" on [Render.com](https://render.com).
2. Connect your Git repository.
3. Configure the service:
   - **Root Directory**: `backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn "app:create_app()"`
4. Set Environment Variables under the "Environment" tab:
   - `SECRET_KEY`: A long, random string for JWT hashing.
   - `MONGODB_URI`: Connect to MongoDB Atlas (e.g., `mongodb+srv://<user>:<password>@cluster0.mongodb.net/ai_os?retryWrites=true&w=majority`)
   - `DB_NAME`: `ai_productivity_os`
5. Click **Deploy**. Render will give you a hosted URL (e.g., `https://ai-os-backend.onrender.com`).

---

## 2. Setting Up Database (MongoDB Atlas)

Since local MongoDB isn't accessible in the cloud, you need a cloud-managed database.
1. Create a free cluster on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
2. Create a Database User and save the password.
3. Go to "Network Access" and allow access from anywhere (`0.0.0.0/0`).
4. Copy the connection string and paste it into Render's `MONGODB_URI` environment variable.

---

## 3. Frontend Deployment (Vercel)

Vercel is incredibly fast and free for static frontends.

### Preparation
1. First, open `frontend/js/api.js`.
2. Find the constant at the top: `const API_URL = 'http://localhost:5000/api';`
3. Change it to your new Render Backend URL:
   `const API_URL = 'https://ai-os-backend.onrender.com/api';`
4. Commit and push this change to your repository.

### Deployment Steps on Vercel
1. Login to [Vercel.com](https://vercel.com) and click "Add New Project".
2. Import your Git repository.
3. Configure the project:
   - **Root Directory**: `frontend`
4. Click **Deploy**. Vercel will automatically build and host the static files.
5. Visit your new `https://your-project.vercel.app` URL to use the application!

---

## 4. CORS Finalization (Important Security Step)
Right now, `backend/app.py` has `CORS(app)` which allows traffic from anywhere.
Once your frontend is active on Vercel, secure it by restricting origins.

Modify `backend/app.py`:

```python
# Before deploying to production, secure CORS:
CORS(app, resources={r"/api/*": {"origins": "https://your-project.vercel.app"}})
```
