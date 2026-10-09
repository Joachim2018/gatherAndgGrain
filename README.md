# Gather & Grain

A responsive four-page restaurant website built with HTML, CSS, JavaScript, Bootstrap, Animate.css, Google Fonts, and Bootstrap Icons.

## Run locally

Python 3 is required. From this folder, run:

```powershell
python server.py
```

Open [http://localhost:3000](http://localhost:3000). The reservation form appends to `data/reservations.json`; the contact form appends to `data/messages.json`. These files are intentionally not served to visitors. Form submissions are stored locally and are not emailed automatically.

Photos, fonts, Bootstrap, icons, and Animate.css load from external services, so those assets require an internet connection.