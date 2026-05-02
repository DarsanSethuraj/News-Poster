# Admin Page WordPress Plugin + FastAPI Backend

A WordPress plugin that fetches article content from a FastAPI backend scraper and automatically creates WordPress posts from scraped news/article URLs.

---

## Features

* Fetch article title and content from external URLs
* Uses FastAPI backend scraper for parsing article pages
* Prevents duplicate posts using title check
* Secure admin form with WordPress nonce validation
* Automatically publishes fetched articles as WordPress posts
* Simple WordPress admin interface for testing/importing

---

## Project Structure

```bash
Backend-for-Auto-News-Post/
│
├── backend/
│   └── main.py              # FastAPI scraper backend
│
├── wordpress-plugin/
│   └── admin-page.php       # WordPress plugin file
│
└── README.md
```

---

## Requirements

### Backend

* Python 3.10+
* FastAPI
* Uvicorn
* BeautifulSoup4
* Requests

### WordPress Plugin

* WordPress 6+
* PHP 8+

---

## Backend Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/yourrepo.git
cd yourrepo/backend
```

2. Install dependencies:

```bash
pip install fastapi uvicorn beautifulsoup4 requests
```

3. Run FastAPI server:

```bash
uvicorn main:app --reload
```

Backend will run at:

```bash
http://127.0.0.1:8000
```

---

## WordPress Plugin Setup

1. Copy plugin file into:

```bash
wp-content/plugins/admin-page/
```

2. Activate plugin in WordPress Admin.

3. Ensure backend URL inside plugin matches your FastAPI server:

```php
http://127.0.0.1:8000/news?url=
```

---

## Usage

1. Open WordPress Admin
2. Navigate to **Backend Testing**
3. Enter an article/news URL
4. Click **Fetch News**
5. Plugin will:

   * Send URL to FastAPI backend
   * Scrape title/content
   * Create WordPress post automatically

---

## API Endpoint

### GET `/news`

Fetch scraped article data from URL.

**Query Parameter:**

| Name | Type   | Required | Description        |
| ---- | ------ | -------- | ------------------ |
| url  | string | Yes      | Target article URL |

**Example Request:**

```http
GET /news?url=https://example.com/article
```

**Example Response:**

```json
{
  "title": "Sample Article Title",
  "content": "<p>Paragraph 1</p><p>Paragraph 2</p>"
}
```

---

## Current Limitations

* Uses generic scraping heuristics (not site-specific parsing)
* Localhost backend only for development
* No authentication/API key system yet
* No async job queue for long scrapes
* Duplicate detection only checks by title

---

## Roadmap

* [ ] Deploy backend as hosted SaaS API
* [ ] Add API key authentication
* [ ] Add featured image extraction
* [ ] Add site-specific scraper rules
* [ ] Add subscription/usage limits
* [ ] Add cron-based automated imports
* [ ] Add watermark removal pipeline
* [ ] Add async scraping queue

---

## License

MIT License

---

## Author

Built by [Your Name]

Computer Science student building automated publishing tools / WordPress SaaS products.
