⚠️ Important Restriction
Browsers block scripts from automatically navigating to different domains and running code for security reasons. To use the "Console Way" for a list of URLs, you have two options:

Semi-Automated: You open each URL in a new tab, paste the script, and it saves.
Sequential Automation (Same Domain): If you are already on LinkedIn, the script can navigate to each page one-by-one, wait for it to load, and then trigger the download.
Since these are all LinkedIn URLs, here is a sequential automation script you can run in your DevTools console while on any LinkedIn page:...

--- --- --- --- --- --- --- --- --- --- --- --- --- 

🚨 Crucial Notes:
Pop-up Blocker: Your browser will likely block this script from opening 60+ tabs. You must click "Always allow pop-ups from LinkedIn" in the address bar when you run it.
Throttling: LinkedIn has anti-scraping measures. If you download 60 pages in a row too fast, they might temporarily restrict your account or show a CAPTCHA.
Memory: Running this for 60 URLs might consume a lot of RAM. I recommend splitting the list into smaller chunks (e.g., 10 URLs at a time).