# Vercel Deployment Guide

This guide will help you deploy the Certificate Generator Flask application to Vercel.

## Prerequisites

1. A [Vercel account](https://vercel.com/signup) (free tier works)
2. Git repository (GitHub, GitLab, or Bitbucket)
3. Vercel CLI (optional, for local testing)

## Deployment Steps

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Push your code to Git**
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Import Project to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New Project"
   - Import your Git repository
   - Vercel will automatically detect the Python project

3. **Configure Build Settings**
   - Framework Preset: Other
   - Build Command: (leave empty, Vercel handles Python automatically)
   - Output Directory: (leave empty)
   - Install Command: `pip install -r requirements.txt`

4. **Deploy**
   - Click "Deploy"
   - Wait for the build to complete
   - Your app will be live at `https://your-project.vercel.app`

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel
   ```

4. **For production deployment**
   ```bash
   vercel --prod
   ```

## Important Notes

### File Storage
- The application uses `/tmp` directory for file storage on Vercel (serverless environment)
- Files in `/tmp` are **ephemeral** and will be deleted after the function execution
- Generated certificates are only available during the request/response cycle
- Consider using external storage (S3, Cloudinary, etc.) for production if you need persistent storage

### Font Support
- System fonts (Arial, Times) should work on Vercel's Linux environment
- For Gujarati fonts, you may need to:
  - Bundle fonts with your application
  - Use web fonts (Google Fonts)
  - Or use a font service

### Limitations
- **Function Timeout**: Vercel has execution time limits (10s on Hobby, 60s on Pro)
- **File Size**: Maximum 50MB upload size (configurable in app.py)
- **Memory**: Limited memory per function execution
- **Cold Starts**: First request may be slower due to serverless cold starts

### Environment Variables
If you need to set environment variables:
1. Go to your project settings on Vercel
2. Navigate to "Environment Variables"
3. Add any required variables

## Troubleshooting

### Build Errors
- Ensure all dependencies in `requirements.txt` are compatible with Python 3.9+ (Vercel's default)
- Check that `pikepdf` and other native dependencies can build on Linux

### Runtime Errors
- Check Vercel function logs in the dashboard
- Ensure file paths use `/tmp` for writable directories
- Verify that templates directory is accessible

### Font Issues
- If fonts are missing, the app will fall back to default fonts
- Consider bundling required fonts in your project

## Production Considerations

For production use, consider:
1. **External Storage**: Use AWS S3, Cloudinary, or similar for file storage
2. **CDN**: Use Vercel's CDN for static assets
3. **Database**: Store session info in a database instead of filesystem
4. **Monitoring**: Set up error tracking (Sentry, etc.)
5. **Rate Limiting**: Implement rate limiting to prevent abuse

## Support

For Vercel-specific issues, check:
- [Vercel Python Documentation](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Vercel Community](https://github.com/vercel/vercel/discussions)

