Zooniverse Citizen Image Uploader

Welcome! This repository powers a community image upload system for citizen scientists participating in Zooniverse projects. You can drag and drop images through GitHub Issues — no coding required — and get back direct links you can paste into Zooniverse Talk.

📸 Anyone with a GitHub account can contribute. The system will automatically validate, process, and publish your images.


How It Works

Go to the Issues tab → Click New Issue → Choose Upload image(s).

Drag-and-drop 1–5 images (JPG/PNG/WebP).

Add an optional caption.

Submit the issue.

Within 1–2 minutes, a bot will reply with:

Direct links to your uploaded images

Markdown snippets ready to paste into Zooniverse Talk

Your images will appear in this repository under the /images directory and will be listed in images/index.json for programmatic access.


What Happens Under the Hood

Images are downloaded from the GitHub issue post.

(Optional) They are resized to save space (max width: 1600px by default).

Images are saved as JPEGs (unless configured otherwise).

A central index.json is updated to include uploader, timestamp, and alt-text.

A GitHub Actions bot posts a comment back on your issue with links.


Rules & Guidelines

✅ You must have the rights to share the images (e.g., you took the photo or it's CC BY).

🚫 Do not upload:

Copyrighted images without permission

Sensitive or private content

Any non-image files

🔍 Uploads are limited to:

Max 5 files per issue

Max ~6MB per image (adjustable)

We reserve the right to remove inappropriate content or abuse.
