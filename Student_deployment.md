# Student Deployment Guide - Market Environment App

This guide will help you deploy your own copy of the Market Environment application using free services.

## Prerequisites
- GitHub account (use your student email for education benefits)
- Fork of this repository

## Step 1: Fork the Repository
1. Click the "Fork" button on the main repository page
2. This creates your own copy that you can modify and deploy

## Step 2: Apply for GitHub Student Developer Pack (if not done already)
1. Visit [education.github.com](https://education.github.com/pack)
2. Verify with your student email
3. This gives you access to many free/premium services

## Step 3: Deploy Backend on Railway

### Sign up for Railway
1. Go to [railway.app](https://railway.app)
2. Sign up with your GitHub account
3. Railway offers $5/month free credit (enough for this project)

### Deploy your backend
1. Click "New Project" in Railway
2. Select "Deploy from GitHub repo"
3. Choose your forked repository
4. Railway will automatically detect it's a Python app
5. Your backend will be deployed at: `https://your-app-name.railway.app`
6. **Copy this URL - you'll need it for the frontend!**

### Set environment variables (optional)
1. In Railway project dashboard, go to "Variables"
2. Add any needed environment variables

## Step 4: Deploy Frontend on Vercel

### Sign up for Vercel
1. Go to [vercel.com](https://vercel.com)
2. Sign up with your GitHub account
3. Completely free for personal/student projects

### Deploy your frontend
1. Click "New Project" in Vercel
2. Import your forked GitHub repository
3. **Important:** Set the root directory to `frontend`
4. Vercel will auto-detect it's a React app
5. Before deploying, add environment variable:
   - Key: `VITE_API_URL`
   - Value: Your Railway backend URL (from Step 3)

### Configure build settings
- Build Command: `npm run build`
- Output Directory: `dist`
- Root Directory: `frontend`

## Step 5: Update CORS Settings

After both deployments are live:

1. Copy your Vercel frontend URL (something like `https://your-app.vercel.app`)
2. In your GitHub repo, edit `backend/config.py`
3. Add your Vercel URL to the `cors_origins` list:
   ```python
   cors_origins: list = [
       "http://localhost:5173",
       "http://127.0.0.1:5173", 
       "https://your-app.vercel.app"  # Add your URL here
   ]
   ```
4. Commit and push - Railway will auto-redeploy

## Step 6: Test Your Deployment

1. Visit your Vercel frontend URL
2. Try generating a market
3. Check that the charts display correctly
4. Verify the API connection is working

## Troubleshooting

### Frontend can't connect to backend
- Check that `VITE_API_URL` environment variable is set in Vercel
- Ensure your frontend URL is in the CORS settings
- Check Railway logs for errors

### Backend won't start
- Check Railway build logs
- Ensure all dependencies are in `requirements.txt`
- Verify the Procfile is correct

### Common issues
- **CORS errors**: Add your frontend URL to backend CORS settings
- **API not found**: Check the `VITE_API_URL` environment variable
- **Build failures**: Check that all dependencies are properly listed

## What Students Should Submit

1. **Live URLs:**
   - Frontend URL (Vercel)
   - Backend URL (Railway)

2. **GitHub Repository:**
   - Link to your forked repository
   - Any modifications you made

3. **Screenshot:**
   - Working market simulation with charts

## Resources

- [Railway Documentation](https://docs.railway.app/)
- [Vercel Documentation](https://vercel.com/docs)
- [GitHub Student Pack](https://education.github.com/pack)

## Cost Breakdown
- **Railway**: $5/month free credit (more than enough for this project)
- **Vercel**: Completely free for personal projects
- **GitHub**: Free
- **Total monthly cost**: $0

## Need Help?
- Check the troubleshooting section above
- Review Railway and Vercel logs for error messages
- Ask questions in class or office hours