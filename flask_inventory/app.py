from flask import Flask, render_template, request, redirect, url_for, send_file,Response,flash 
import sqlite3
import qrcode
import io
import csv
import os
import pandas as pd

app = Flask(__name__)


# 一意で安全な秘密鍵を設定
app.config['SECRET_KEY'] = 'Hirakegoma'


# データベース接続
def get_db_connection():
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    return conn

# ホームページ
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventory')
def inventory():
    conn = get_db_connection()
    search_query = request.args.get('search')
    item_number = request.args.get('item_number')
    sort = request.args.get('sort')

    query = 'SELECT * FROM inventory WHERE 1=1'
    params = []

    if search_query:
        query += ' AND product_name LIKE ?'
        params.append('%' + search_query + '%')

    if item_number:
        query += ' AND item_number = ?'  # item_numberでフィルタリング
        params.append(item_number)

    if sort == 'manufacturer':
        query += ' ORDER BY manufacturer'

    products = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('inventory.html', products=products)




# 商品追加ページを表示
@app.route('/add_product', methods=['GET'])
def show_add_product():
    return render_template('add_product.html')

@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form['name']
    manufacturer = request.form['manufacturer']
    purchase_date = request.form['purchase_date']
    item_number = request.form['item_number']  # 物品管理番号を取得
    description = request.form['description']  # 説明を取得

    conn = get_db_connection()
    conn.execute('INSERT INTO inventory (product_name, manufacturer, purchase_date, item_number, description) VALUES (?, ?, ?, ?, ?)', 
                 (name, manufacturer, purchase_date, item_number, description))
    conn.commit()
    conn.close()
    
    return redirect(url_for('inventory'))


# 商品削除処理
@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM inventory WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('inventory'))

# テーブル更新するやつ
@app.route('/create_table')
def create_table():
    conn = get_db_connection()
    
    # まず、テーブルが存在すれば削除する
    conn.execute('DROP TABLE IF EXISTS inventory;')
    
    # 次に、テーブルを作成する
    conn.execute('''
        CREATE TABLE inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            manufacturer TEXT NOT NULL,
            purchase_date TEXT NOT NULL,
            item_number TEXT,  -- 物品管理番号
            description TEXT   -- 説明
        )
    ''')
    
    conn.commit()
    conn.close()
    return "テーブルを作成しました。商品を追加できます。"


# 商品編集ページを表示
@app.route('/edit_product/<int:product_id>', methods=['GET'])
def edit_product(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM inventory WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    return render_template('edit_product.html', product=product)

# 商品更新処理
@app.route('/update_product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    name = request.form['name']
    manufacturer = request.form['manufacturer']
    purchase_date = request.form['purchase_date']
    item_number = request.form['item_number']  # 物品管理番号を取得
    description = request.form['description']  # 説明を取得

    conn = get_db_connection()
    conn.execute('UPDATE inventory SET product_name = ?, manufacturer = ?, purchase_date = ?, item_number = ?, description = ? WHERE id = ?',
                 (name, manufacturer, purchase_date, item_number, description, product_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('inventory'))


# 商品詳細ページを表示
@app.route('/product_detail/<int:product_id>', methods=['GET'])
def product_detail(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM inventory WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    return render_template('product_detail.html', product=product)


# csvのアップロード

@app.route('/upload_csv', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('ファイルが選択されていません')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('ファイルが選択されていません')
            return redirect(request.url)
        
        if file and file.filename.endswith('.csv'):
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('CSVファイルがアップロードされました')
            return redirect(url_for('upload_csv'))
        else:
            flash('CSVファイルのみアップロードできます')
            return redirect(request.url)
        
    return redirect(url_for('inventory'))
    

  


# CSVのエクスポート

@app.route('/export_csv')
def export_csv():
    conn = get_db_connection()
    cursor = conn.execute('SELECT * FROM inventory')
    data = cursor.fetchall()

    output = io.StringIO()
    csv_writer = csv.writer(output)

    # ヘッダー
    csv_writer.writerow(['商品名', 'メーカー', '購入日', '物品管理番号', '説明'])

    # データを書き込み
    for row in data:
        csv_writer.writerow(row)

    conn.close()

    output.seek(0)
    return Response(output, mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment;filename=inventory.csv'})


# QRコード生成処理
@app.route('/generate_qr/<int:product_id>')
def generate_qr(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM inventory WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    
    if product is None:
        return "Product not found", 404

    # QRコードの生成
    qr_data = f"Product Name: {product['product_name']}\nManufacturer: {product['manufacturer']}\nPurchase Date: {product['purchase_date']}"
    qr = qrcode.make(qr_data)

    # QRコードをメモリに保存
    img = io.BytesIO()
    qr.save(img, format='PNG')
    img.seek(0)

    return send_file(img, mimetype='image/png')

# アプリを実行
if __name__ == '__main__':
    app.run(debug=True)




