from flask import Flask, render_template
import redis
import os
import socket
import time

app = Flask(__name__)

# Конфигурация Redis
redis_host = os.environ.get('REDIS_HOST', 'redis-service')
redis_port = int(os.environ.get('REDIS_PORT', 6379))
redis_password = os.environ.get('REDIS_PASSWORD', 'password123')

@app.route('/')
def index():
    try:
        # Подключение к Redis
        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2
        )
        
        # Увеличиваем счетчик
        visits = r.incr('page_visits')
        redis_status = "✅ Connected"
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        
    except Exception as e:
        visits = f"Error: {e}"
        redis_status = "❌ Disconnected"
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>K8s Flask + Redis</title>
        <style>
            body {{ font-family: Arial; margin: 40px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .counter {{ font-size: 48px; color: #2196F3; text-align: center; }}
            .info {{ background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 5px; }}
            .success {{ color: green; }}
            .error {{ color: red; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Kubernetes + Flask + Redis</h1>
            <div class="counter">{visits}</div>
            <p style="text-align: center;">Total visits to this page</p>
            
            <div class="info">
                <h3>📊 Pod Information:</h3>
                <p><strong>Hostname:</strong> {hostname}</p>
                <p><strong>IP Address:</strong> {ip}</p>
                <p><strong>Redis:</strong> <span class="{ 'success' if '✅' in redis_status else 'error' }">{redis_status}</span></p>
            </div>
            
            <div class="info">
                <h3>🔗 Test Endpoints:</h3>
                <ul>
                    <li><a href="/">Refresh Counter</a></li>
                    <li><a href="/health">Health Check</a></li>
                    <li><a href="/info">Pod Info</a></li>
                    <li><a href="/test-redis">Test Redis Connection</a></li>
                </ul>
            </div>
            
            <p><em>Refresh page to see load balancing between pods</em></p>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    try:
        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1
        )
        if r.ping():
            return {'status': 'healthy', 'redis': 'connected', 'timestamp': time.time()}, 200
    except:
        pass
    return {'status': 'unhealthy', 'redis': 'disconnected', 'timestamp': time.time()}, 500

@app.route('/info')
def info():
    return {
        'hostname': socket.gethostname(),
        'ip': socket.gethostbyname(socket.gethostname()),
        'pod': os.environ.get('HOSTNAME', 'unknown'),
        'timestamp': time.time()
    }

@app.route('/test-redis')
def test_redis():
    try:
        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=True,
            socket_connect_timeout=2
        )
        current = r.get('page_visits') or 0
        r.incr('test_counter')
        test_val = r.get('test_counter')
        
        return {
            'status': 'success',
            'redis': 'connected',
            'current_visits': current,
            'test_counter': test_val,
            'ping': r.ping()
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
