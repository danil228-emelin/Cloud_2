
import os
from flask import Flask, render_template_string
import redis

app = Flask(__name__)


APP_VERSION = "v2"
BACKGROUND_COLOR = os.getenv('BACKGROUND_COLOR', 'lightblue')


redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_password = os.getenv('REDIS_PASSWORD', None)  


if redis_password:
    redis_client = redis.Redis(
        host=redis_host, 
        port=6379, 
        password=redis_password,  
        decode_responses=True,
        socket_connect_timeout=5
    )
else:
    redis_client = redis.Redis(
        host=redis_host, 
        port=6379, 
        decode_responses=True,
        socket_connect_timeout=5
    )


def check_redis_connection():
    try:
        redis_client.ping()
        return True
    except redis.exceptions.AuthenticationError:
        print("Redis authentication failed")
        return False
    except redis.exceptions.ConnectionError:
        print("Redis connection failed")
        return False

@app.route('/')
def index():
    
    if not check_redis_connection():
        visit_count = "Redis unavailable"
    else:
        try:
            visit_count = redis_client.incr('visit_count')
        except redis.exceptions.AuthenticationError:
            return "Redis authentication error. Check REDIS_PASSWORD.", 500
    
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flask App {{ version }}</title>
        <style>
            body {
                background-color: {{ bg_color }};
                font-family: Arial, sans-serif;
                text-align: center;
                padding-top: 50px;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                display: inline-block;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            .error {
                color: red;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Flask Application</h1>
            <h2>Version: {{ version }}</h2>
            <p>Background color: {{ bg_color }}</p>
            <h3>Visit count: {{ count }}</h3>
            <p>Pod: {{ pod_name }}</p>
            <p>Redis Status: {{ redis_status }}</p>
        </div>
    </body>
    </html>
    """
    
    redis_status = "Connected" if check_redis_connection() else "Disconnected"
    
    return render_template_string(
        html_template,
        version=APP_VERSION,
        bg_color=BACKGROUND_COLOR,
        count=visit_count,
        pod_name=os.getenv('HOSTNAME', 'unknown'),
        redis_status=redis_status
    )

@app.route('/health')
def health():
    redis_ok = check_redis_connection()
    return {
        "status": "healthy" if redis_ok else "degraded",
        "version": APP_VERSION,
        "redis": "connected" if redis_ok else "disconnected"
    }, 200 if redis_ok else 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)