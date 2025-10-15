# Vercel Deployment Guide

## Project Configuration

This project is configured to be deployed on Vercel with:

- **Backend**: FastAPI with Python
- **Frontend**: React + Vite + TypeScript

## Deployment Steps

### 1. Project Preparation

Make sure your project is in a GitHub, GitLab, or Bitbucket repository.

### 2. Environment Variable Configuration

In the Vercel dashboard, configure the following environment variables:

```bash
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anonymous_key
FRONTEND_URL=https://your-app.vercel.app
HOST=0.0.0.0
PORT=3000
```

### 3. Deploy to Vercel

#### Option A: Deploy from Vercel Dashboard

1. Go to [vercel.com](https://vercel.com) and create an account
2. Click "New Project"
3. Import your GitHub/GitLab/Bitbucket repository
4. Vercel will automatically detect the configuration
5. Configure environment variables in the "Environment Variables" section
6. Click "Deploy"

#### Option B: Deploy from Command Line

1. Install Vercel CLI:

```bash
npm i -g vercel
```

2. Login:

```bash
vercel login
```

3. Deploy the project:

```bash
vercel
```

### 4. Supabase Configuration

Make sure your Supabase project is configured correctly:

1. Create a project in [supabase.com](https://supabase.com)
2. Get your project credentials:
   - Project URL
   - Anonymous key (anon key)
3. Configure environment variables in Vercel with these values

### 5. Deployment Verification

Once deployed, verify that:

1. **Backend works**: Visit `https://your-app.vercel.app/api/health`
2. **Frontend works**: Visit `https://your-app.vercel.app`
3. **Authentication works**: Try registering and logging in

## Project Structure

```
webapp_python/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt      # Python dependencies
│   └── api/
│       └── index.py         # Entry point for Vercel
├── frontend/
│   ├── package.json         # Node.js dependencies
│   ├── vite.config.ts       # Vite configuration
│   └── vercel.json          # Frontend-specific configuration
├── vercel.json              # Main Vercel configuration
└── env.example              # Example environment variables
```

## Route Configuration

The `vercel.json` file is configured to:

- **Routes `/api/*`**: Directed to backend (FastAPI)
- **Routes `/*`**: Directed to frontend (React)

## Common Troubleshooting Issues

### Build Error

```bash
# Check build logs in Vercel dashboard
```

### CORS Error

- Make sure `FRONTEND_URL` is configured correctly
- Check that CORS routes include your Vercel domain

### Supabase Error

- Verify that `SUPABASE_URL` and `SUPABASE_ANON_KEY` are configured
- Make sure your Supabase project is active

### Build Error

- Check for missing dependencies in `requirements.txt` (backend) and `package.json` (frontend)

## Useful Commands

```bash
# Deploy to production
vercel --prod

# View environment variables
vercel env ls

# View deployment logs
vercel logs

# List deployments
vercel ls

# Inspect latest deployment
vercel inspect
```

## Important Notes

1. **Environment Variables**: Never upload `.env` files to the repository
2. **Supabase**: Make sure your Supabase project is in the same region as your deployment
3. **CORS**: CORS configurations are optimized for Vercel
4. **Build**: Frontend builds automatically during deployment

## Support

If you encounter problems:

1. Check logs in the Vercel dashboard
2. Verify environment variables
3. Test the project locally before deployment
4. Consult Vercel and Supabase documentation
