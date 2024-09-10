from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

# SQLite veritabanına bağlanma fonksiyonu
def get_db_connection():
    conn = sqlite3.connect('UserDB.db')
    conn.row_factory = sqlite3.Row
    return conn

# Kullanıcının balance ve state bilgilerini dönen GET fonksiyonu
@app.route('/user/<username>', methods=['GET'])
def get_user_balance(username):
    conn = get_db_connection()
    user = conn.execute('SELECT username, balance, state FROM balance WHERE username = ?', (username,)).fetchone()
    conn.close()

    if user is None:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'username': user['username'],
        'balance': user['balance'],
        'state': user['state']
    })

# Kullanıcının balance değerini güncelleyen POST fonksiyonu
@app.route('/user/update_balance/<username>', methods=['POST'])
def update_user_balance(username):
    try:
        data = request.get_json()
        update_amount = data.get('balance_change')
        
        if update_amount is None:
            return jsonify({'error': 'balance_change not provided'}), 400

        conn = get_db_connection()
        
        # Kullanıcıyı bul
        user = conn.execute('SELECT balance FROM balance WHERE username = ?', (username,)).fetchone()
        if user is None:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        # Admin kullanıcısını bul
        admin = conn.execute('SELECT balance FROM balance WHERE username = ?', ('admin',)).fetchone()
        if admin is None:
            conn.close()
            return jsonify({'error': 'Admin user not found'}), 404

        # Yeni balance değerini güncelle
        new_user_balance = user['balance'] + update_amount
        conn.execute('UPDATE balance SET balance = ? WHERE username = ?', (new_user_balance, username))
        
        # Eğer güncelleme pozitifse admin'in balance'ından düş, negatifse ekle
        if update_amount > 0:
            new_admin_balance = admin['balance'] - update_amount
        else:
            new_admin_balance = admin['balance'] + abs(update_amount)
        
        # Admin balance güncelle
        conn.execute('UPDATE balance SET balance = ? WHERE username = ?', (new_admin_balance, 'admin'))
        conn.commit()
        conn.close()

        return jsonify({
            'message': f'{username} balance updated by {update_amount}. New balance: {new_user_balance}',
            'admin_balance': new_admin_balance
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

