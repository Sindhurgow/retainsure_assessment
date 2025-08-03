# URL Shortener Service

A robust Flask-based URL shortener service with analytics, validation, and comprehensive error handling.

## Features

### Core Functionality
- **URL Shortening**: Convert long URLs to short 6-character codes
- **URL Redirection**: Redirect short codes to original URLs
- **Click Tracking**: Track and increment click counts for each redirect
- **Analytics**: Get detailed statistics for each shortened URL

### Technical Features
- **URL Validation**: Comprehensive URL format validation
- **Concurrent Request Handling**: Thread-safe database operations
- **Error Handling**: Proper HTTP status codes and error messages
- **Logging**: Comprehensive logging for debugging and monitoring
- **Database**: SQLite database with automatic table creation

## API Endpoints

### Health Checks
- `GET /` - Basic health check
- `GET /api/health` - API health check

### URL Shortening
- `POST /api/shorten` - Create a shortened URL

**Request Body:**
```json
{
    "url": "https://www.example.com/very/long/url"
}
```

**Response:**
```json
{
    "short_code": "abc123",
    "original_url": "https://www.example.com/very/long/url",
    "short_url": "http://localhost:5000/abc123"
}
```

### URL Redirection
- `GET /<short_code>` - Redirect to original URL

**Response:** HTTP 302 redirect to original URL

### Analytics
- `GET /api/stats/<short_code>` - Get URL statistics

**Response:**
```json
{
    "short_code": "abc123",
    "original_url": "https://www.example.com/very/long/url",
    "click_count": 5,
    "created_at": "2024-01-15 10:30:00"
}
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd url-shortener
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app/main.py
   ```

   The service will be available at `http://localhost:5000`

## Usage Examples

### Using curl

**Create a shortened URL:**
```bash
curl -X POST http://localhost:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com"}'
```

**Get URL statistics:**
```bash
curl http://localhost:5000/api/stats/abc123
```

**Visit shortened URL:**
```bash
curl -L http://localhost:5000/abc123
```

### Using Python requests

```python
import requests

# Create shortened URL
response = requests.post('http://localhost:5000/api/shorten', 
                        json={'url': 'https://www.example.com'})
data = response.json()
short_code = data['short_code']

# Get statistics
stats = requests.get(f'http://localhost:5000/api/stats/{short_code}').json()
print(f"Clicks: {stats['click_count']}")

# Visit URL (will redirect)
response = requests.get(f'http://localhost:5000/{short_code}', 
                       allow_redirects=False)
print(f"Redirect to: {response.headers['Location']}")
```

## Testing

### Run all tests
```bash
python run_tests.py
```

### Run specific test
```bash
python run_tests.py test_shorten_url_success
```

### Run with pytest directly
```bash
pytest tests/ -v
```

## Test Coverage

The test suite covers:

1. **Health Check Endpoints**
   - Basic health check
   - API health check

2. **URL Shortening**
   - Successful URL shortening
   - Missing URL field
   - Invalid URL format
   - Malformed JSON

3. **URL Redirection**
   - Successful redirects
   - Non-existent short codes
   - Invalid short code format

4. **Analytics**
   - Getting URL statistics
   - Click count tracking
   - Non-existent short codes
   - Invalid short code format

5. **Concurrency**
   - Concurrent request handling
   - Unique short code generation

6. **URL Validation**
   - Valid URL formats
   - Invalid URL formats

7. **Error Handling**
   - 404 errors
   - Malformed requests
   - Database errors

## Technical Details

### Database Schema

```sql
CREATE TABLE urls (
    short_code TEXT PRIMARY KEY,
    original_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    click_count INTEGER DEFAULT 0
);
```

### Short Code Generation

- **Length**: 6 characters
- **Characters**: Alphanumeric (A-Z, a-z, 0-9)
- **Uniqueness**: Automatically checked against database
- **Collision Handling**: Up to 10 attempts to generate unique code

### URL Validation

The service validates URLs using:
- Regular expression pattern matching
- URL parsing with `urllib.parse`
- Support for HTTP and HTTPS protocols
- Domain validation
- Port number support

### Concurrency Handling

- **Thread Safety**: SQLite operations are protected with locks
- **Database Connections**: Proper connection management
- **Transaction Safety**: Automatic rollback on errors

### Error Handling

- **HTTP Status Codes**: Proper status codes (200, 201, 400, 404, 500)
- **Error Messages**: Clear, descriptive error messages
- **Logging**: Comprehensive error logging
- **Graceful Degradation**: Service continues running on errors

## Configuration

### Environment Variables

- `FLASK_ENV`: Set to `development` for debug mode
- `PORT`: Application port (default: 5000)

### Database

- **File**: `url_shortener.db` (SQLite)
- **Location**: Project root directory
- **Auto-creation**: Tables created automatically on startup

## Security Considerations

- **Input Validation**: All URLs are validated before processing
- **SQL Injection Protection**: Parameterized queries
- **Error Information**: Limited error details in production
- **URL Sanitization**: URLs are sanitized before storage

## Performance

- **Database**: SQLite with proper indexing
- **Caching**: No caching implemented (can be added)
- **Concurrency**: Thread-safe operations
- **Memory**: Minimal memory footprint

## Limitations

- **Database**: SQLite (not suitable for high-scale production)
- **Caching**: No caching layer
- **Rate Limiting**: No rate limiting implemented
- **Authentication**: No authentication/authorization
- **HTTPS**: No HTTPS enforcement

## Future Enhancements

1. **Database**: Migrate to PostgreSQL/MySQL for production
2. **Caching**: Add Redis for caching
3. **Rate Limiting**: Implement rate limiting
4. **Authentication**: Add user authentication
5. **HTTPS**: Enforce HTTPS in production
6. **Monitoring**: Add metrics and monitoring
7. **API Documentation**: Add OpenAPI/Swagger docs
8. **Bulk Operations**: Add bulk URL shortening
9. **Custom Domains**: Support custom domains
10. **Analytics Dashboard**: Web-based analytics interface

## Troubleshooting

### Common Issues

1. **Database Locked**
   - Ensure no other process is using the database
   - Restart the application

2. **Port Already in Use**
   - Change the port in `app/main.py`
   - Kill the process using the port

3. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path

4. **Test Failures**
   - Ensure database is clean
   - Check for conflicting short codes

### Debug Mode

Enable debug mode for detailed error messages:
```bash
export FLASK_ENV=development
python app/main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License.