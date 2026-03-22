from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

HTML_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Crypto Transaction Analyzer</title>
    <style>
        :root {
            --bg-color: rgba(255, 255, 255, 0.5);
            --text-color: #333;
            --heading-color: #2c5364;
            --input-bg: #fff;
            --input-border: #ccc;
            --highlight: #2c5364;
            --error-color: navy;
            --li-bg: #f0f0f0;
            --li-hover: #e0e0e0;
        }

        body.dark-mode {
            --bg-color: rgba(0, 0, 0, 0.6);
            --text-color: #eee;
            --heading-color: #00bcd4;
            --input-bg: #222;
            --input-border: #555;
            --highlight: #00bcd4;
            --error-color: #ffcc00;
            --li-bg: #333;
            --li-hover: #444;
            background-color: #121212;
        }

        body, .container, h2, label, input, select, ul, li, p.error {
            transition: all 0.5s ease;
        }

        body {
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: url('/static/background.jpg') no-repeat center center fixed;
            background-size: cover;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            color: var(--text-color);
        }

        .container {
            background-color: var(--bg-color);
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
            text-align: center;
            width: 100%;
            max-width: 550px;
            animation: fadeInContainer 1.5s ease-in-out;
            position: relative;
        }

        @keyframes fadeInContainer {
            from { opacity: 0; transform: scale(0.95); }
            to { opacity: 1; transform: scale(1); }
        }

        .dark-toggle {
            position: absolute;
            top: 15px;
            right: 15px;
            font-size: 20px;
            cursor: pointer;
            user-select: none;
            color: var(--highlight);
        }

        h2 {
            margin-bottom: 25px;
            color: var(--heading-color);
            font-family: 'Brush Script MT', cursive;
            font-size: 32px;
            position: relative;
            overflow: hidden;
            white-space: nowrap;
            text-align: center;
            width: fit-content;
            margin-left: auto;
            margin-right: auto;
            border-right: 2px solid var(--heading-color);
            animation: typing 3s steps(30, end), blink 0.75s step-end infinite;
        }

        @keyframes typing {
            from { width: 0 }
            to { width: 100% }
        }

        @keyframes blink {
            from, to { border-color: transparent }
            50% { border-color: var(--heading-color) }
        }

        h2::after {
            content: '';
            position: absolute;
            left: 0;
            bottom: -5px;
            width: 100%;
            height: 2px;
            background-color: var(--heading-color);
            transform: scaleX(0);
            transform-origin: left;
            animation: underline 3s ease-out forwards;
            animation-delay: 3s;
        }

        @keyframes underline {
            to { transform: scaleX(1); }
        }

        label {
            font-weight: bold;
            display: block;
            margin-bottom: 8px;
            text-align: left;
        }

        input[type="text"], select {
            width: 100%;
            padding: 12px;
            background-color: var(--input-bg);
            border: 1px solid var(--input-border);
            border-radius: 6px;
            margin-bottom: 20px;
            font-size: 16px;
            box-shadow: 0 0 0 transparent;
            color: var(--text-color);
        }

        input[type="text"]:focus, select:focus {
            border-color: var(--highlight);
            box-shadow: 0 0 10px var(--highlight);
            outline: none;
        }

        input[type="submit"] {
            background-color: var(--highlight);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.2s ease;
        }

        input[type="submit"]:hover {
            background-color: #203a43;
            transform: scale(1.05);
        }

        ul {
            list-style-type: none;
            padding: 0;
            text-align: left;
        }

        li {
            background-color: var(--li-bg);
            margin: 8px 0;
            padding: 10px;
            border-radius: 6px;
            opacity: 0;
            animation: fadeInItem 0.6s ease forwards;
            color: var(--text-color);
        }

        @keyframes fadeInItem {
            to { opacity: 1; }
        }

        li:hover {
            background-color: var(--li-hover);
        }

        strong {
            color: #d9534f;
        }

        p.error {
            color: var(--error-color);
            font-weight: bold;
            font-size: 16px;
            font-family: 'Courier New', Courier, monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="dark-toggle" onclick="toggleDarkMode()" title="Toggle Dark Mode">🌙</div>
        <h2>Crypto Transaction Analyzer</h2>
        <form method="post">
            <label for="crypto">Select Cryptocurrency:</label>
            <select id="crypto" name="crypto" required>
                <option value="btc" {% if request.form.crypto == 'btc' %}selected{% endif %}>Bitcoin</option>
                <option value="eth" {% if request.form.crypto == 'eth' %}selected{% endif %}>Ethereum</option>
                <option value="ltc" {% if request.form.crypto == 'ltc' %}selected{% endif %}>Litecoin</option>
                <option value="doge" {% if request.form.crypto == 'doge' %}selected{% endif %}>Dogecoin</option>
            </select>

            <label for="tx_hash">Enter Transaction Hash:</label>
            <input type="text" id="tx_hash" name="tx_hash" required value="{{ request.form.tx_hash or '' }}">

            <input type="submit" value="Analyze">
        </form>

        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}

        {% if outputs %}
            <h3>Transaction Outputs:</h3>
            <ul>
                {% for address, value in outputs %}
                    <li style="animation-delay: {{ loop.index0 * 0.2 }}s;">
                        Address: {{ address }} - Value: {{ value }} satoshis
                        {% if address == likely_receiver %}
                            <strong>(Likely End Receiver)</strong>
                        {% endif %}
                    </li>
                {% endfor %}
            </ul>
        {% endif %}
    </div>

    <script>
    const body = document.body;
    const icon = document.querySelector('.dark-toggle');

    if (localStorage.getItem('darkMode') === 'enabled') {
        body.classList.add('dark-mode');
        icon.textContent = '☀️';
    }

    function toggleDarkMode() {
        body.classList.toggle('dark-mode');
        const isDark = body.classList.contains('dark-mode');
        icon.textContent = isDark ? '☀️' : '🌙';
        localStorage.setItem('darkMode', isDark ? 'enabled' : 'disabled');
    }
</script>
</body>
</html>
'''

def fetch_transaction_data(crypto, tx_hash):
    url = f"https://api.blockcypher.com/v1/{crypto}/main/txs/{tx_hash}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, str(e)

def validate_tx_hash(crypto, tx_hash):
    tx_hash = tx_hash.strip()
    if crypto == 'eth':
        if not (tx_hash.startswith('0x') and len(tx_hash) == 66):
            return False
    if crypto in ['btc', 'ltc', 'doge'] and (len(tx_hash) < 50 or len(tx_hash) > 70):
        return False
    return True

def truncate_error_message(message, max_length=120):
    if len(message) > max_length:
        return message[:max_length] + "..."
    return message

@app.route('/', methods=['GET', 'POST'])
def index():
    outputs = []
    likely_receiver = None
    error = None

    if request.method == 'POST':
        tx_hash = request.form.get('tx_hash', '').strip()
        crypto = request.form.get('crypto', '')
        
        if not validate_tx_hash(crypto, tx_hash):
            error = "Invalid transaction hash format for the selected cryptocurrency."
        else:
            data, error_msg = fetch_transaction_data(crypto, tx_hash)
            if data:
                raw_outputs = data.get("outputs", [])
                outputs = [(out["addresses"][0], out["value"]) for out in raw_outputs if "addresses" in out]
                if outputs:
                    likely_receiver = max(outputs, key=lambda x: x[1])[0]
                else:
                    error = "No outputs found in this transaction."
            else:
                error = f"Failed to fetch transaction data: {error_msg}"

    error = truncate_error_message(error) if error else None

    return render_template_string(HTML_TEMPLATE, outputs=outputs, likely_receiver=likely_receiver, error=error)

if __name__ == '__main__':
    app.run(debug=True)