from flask import Flask, request, jsonify, render_template_string
import datetime

app = Flask(__name__)

# Portfolio Tracker Engine
initial_capital = 10000.0
current_capital = 10000.0
in_position = False
entry_price = 0.0
trades = []

# HTML Dashboard layout
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Trading Strategy Dashboard</title>
    <meta http-equiv="refresh" content="10">
    <style>
        body { font-family: monospace; background: #0e1117; color: #00ff88; padding: 20px; }
        .card { background: #161b22; border: 1px solid #30363d; padding: 15px; margin-bottom: 15px; border-radius: 8px; }
        h1, h2 { color: #ffffff; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #30363d; padding: 8px; text-align: left; color: #c9d1d9; }
        th { background: #21262d; }
    </style>
</head>
<body>
    <h1>🚀 Live Strategy Dashboard</h1>
    <div class="card">
        <h2>Account Overview</h2>
        <p><strong>Equity:</strong> ${{ "%.2f"|format(capital) }}</p>
        <p><strong>Total Return:</strong> {{ "%.2f"|format(total_return) }}%</p>
        <p><strong>Position Status:</strong> {{ "IN LONG" if in_position else "FLAT" }}</p>
        <p><strong>Entry Price:</strong> ${{ "%.2f"|format(entry_price) }}</p>
    </div>
    <div class="card">
        <h2>Trade Log</h2>
        <table>
            <tr><th>Time</th><th>Action</th><th>Symbol</th><th>Price</th><th>Profit/Loss</th></tr>
            {% for trade in trades %}
            <tr>
                <td>{{ trade.time }}</td>
                <td>{{ trade.action }}</td>
                <td>{{ trade.symbol }}</td>
                <td>${{ "%.2f"|format(trade.price) }}</td>
                <td>{{ trade.pnl }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def dashboard():
    total_return = ((current_capital - initial_capital) / initial_capital) * 100
    return render_template_string(
        HTML_TEMPLATE, 
        capital=current_capital, 
        total_return=total_return, 
        in_position=in_position, 
        entry_price=entry_price, 
        trades=trades
    )

@app.route('/webhook', methods=['POST'])
def webhook():
    global current_capital, in_position, entry_price
    data = request.json or {}

    action = data.get("action", "").lower()
    symbol = data.get("symbol", "UNKNOWN")
    price = float(data.get("price", 0.0))
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    pnl_str = "-"
    if action == "buy" and not in_position:
        in_position = True
        entry_price = price
    elif action == "sell" and in_position:
        pnl = ((price - entry_price) / entry_price) * current_capital
        current_capital += pnl
        pnl_str = f"${pnl:.2f}"
        in_position = False

    trades.insert(0, {
        "time": timestamp,
        "action": action.upper(),
        "symbol": symbol,
        "price": price,
        "pnl": pnl_str
    })

    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)