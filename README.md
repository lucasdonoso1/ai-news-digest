# AI News Digest

An automated service that sends daily AI news digests via email at 9:00 AM CET.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up SendGrid:
   - Create a SendGrid account at https://sendgrid.com
   - Create an API key with email sending permissions
   - Verify your sender email address

3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your SendGrid API key, verified sender email, and recipient email

## Running the Service

Start the service with:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The service will automatically:
- Scrape top AI news sources daily
- Generate a digest email
- Send it at 9:00 AM CET to your configured email address

## Deployment

For 24/7 operation, deploy this service to a cloud platform like Heroku, DigitalOcean, or AWS.
