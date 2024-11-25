from flask import Flask, render_template, request, redirect, url_for, send_file, Response, flash
import sqlite3
import qrcode
import csv
import os
import re
from io import StringIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io

app = Flask(__name__)

# アップロードフォルダの設定
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# アップロードフォルダが存在しない場合は作成する
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 一意で安全な秘密鍵を設定
app.config['SECRET_KEY'] = 'Hirakegoma'

# ファイル名を安全に変換
def secure_filename(filename):
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)  # 不正な文字を置換
    return filename

# データベース接続
def get_db_connection():
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    return conn

# ホームページ
@app.route('/')
def index():
    return render_template('index.html')

# 在庫一覧ページ
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
        params.append(f'%{search_query}%')

    if item_number:
        query += ' AND item_number = ?'
        params.append(item_number)

    # ソート条件に応じてクエリを変更
    if sort == 'manufacturer':
        query += ' ORDER BY manufacturer'
    elif sort == 'purchase_date_asc':  # 購入日昇順
        query += ' ORDER BY purchase_date ASC'
    elif sort == 'purchase_date_desc':  # 購入日降順
        query += ' ORDER BY purchase_date DESC'

    products = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('inventory.html', products=products)




# QRコード生成処理
@app.route('/generate_qr/<int:product_id>')
def generate_qr(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM inventory WHERE id = ?', (product_id,)).fetchone()
    conn.close()

    if not product:
        flash('商品が見つかりません', 'error')
        return redirect(url_for('inventory'))

    # QRコード生成
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    product_url = url_for('inventory', _external=True)
    qr.add_data(product_url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    # ファイル保存
    qr_path = os.path.join(app.config['UPLOAD_FOLDER'], f'qr_{product_id}.png')
    img.save(qr_path)
    return send_file(qr_path, mimetype='image/png')





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
        # ファイルが送信されたか確認
        if 'file' not in request.files:
            flash('ファイルが選択されていません')
            return redirect(request.url)

        file = request.files['file']

        # ファイル名が空ではないか確認
        if file.filename == '':
            flash('ファイルが選択されていません')
            return redirect(request.url)

        # CSVファイルかどうか確認
        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)  # 安全なファイル名に変換
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)  # ファイルを保存

            # CSVを読み込み、データベースに挿入
            try:
                with open(file_path, newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    conn = get_db_connection()
                    for row in reader:
                        # 必要なカラムのデータを取得して挿入
                        name = row['商品名']  # CSVヘッダーに基づく
                        manufacturer = row['メーカー']
                        purchase_date = row['購入日']
                        item_number = row['物品管理番号']
                        description = row['説明']

                        conn.execute(
                            'INSERT INTO inventory (product_name, manufacturer, purchase_date, item_number, description) VALUES (?, ?, ?, ?, ?)', 
                            (name, manufacturer, purchase_date, item_number, description)
                        )
                    conn.commit()
                    conn.close()

                flash('CSVファイルからデータが正常にインポートされました')
            except Exception as e:
                flash(f'CSVの読み込み中にエラーが発生しました: {str(e)}')
            return redirect(url_for('upload_csv'))
        else:
            flash('CSVファイルのみアップロードできます')
            return redirect(request.url)

    return render_template('upload.html')  # アップロードページを表示
    





# CSVのエクスポート

@app.route('/export_csv')
def export_csv():
    conn = get_db_connection()
    cursor = conn.execute('SELECT * FROM inventory')
    data = cursor.fetchall()

    output = io.StringIO()
    csv_writer = csv.writer(output)

    # ヘッダー
    csv_writer.writerow(['','商品名', 'メーカー', '購入日', '物品管理番号', '説明'])

    # データを書き込み
    for row in data:
        csv_writer.writerow(row)

    conn.close()

    output.seek(0)
    return Response(output, mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment;filename=inventory.csv'})



# QRコード画像をPDFに追加する関数
@app.route('/generate_selected_qrs', methods=['POST'])
def generate_selected_qrs():
    # フォームから選択されたプロダクトIDを取得
    selected_product_ids = request.form.getlist('selected_products')
    
    # uploadsフォルダのパスを指定
    uploads_folder = 'static/uploads'
    
    # 出力するPDFのパス
    pdf_output_filename = 'output_qr_selected.pdf'
    pdf_output_path = os.path.join(uploads_folder, pdf_output_filename)
    
    # PDFキャンバスを作成
    pdf_canvas = canvas.Canvas(pdf_output_path)
    
    # QRコードを配置するための初期座標
    x_offset = 100
    y_offset = 500
    qr_size = 100
    
    # 選択されたプロダクトごとにQRコードを生成
    for product_id in selected_product_ids:
        # プロダクトのURLを取得（例えば、URLにproduct_idを含める）
        product_url = url_for('product_detail', product_id=product_id, _external=True)
        
        # QRコード生成
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(product_url)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        
        # QRコード画像を保存
        qr_image_filename = f'qr_{product_id}.png'
        qr_image_path = os.path.join(uploads_folder, qr_image_filename)
        img.save(qr_image_path)
        
        # QRコード画像をPDFに追加
        pdf_canvas.drawImage(qr_image_path, x_offset, y_offset, qr_size, qr_size)
        
        # 次のQRコードのy座標を調整
        y_offset -= (qr_size + 20)  # QRコード間隔を20に設定
    
    # PDFの保存
    pdf_canvas.save()
    
    # 最後に生成したPDFをユーザーに提供
    return send_file(pdf_output_path, as_attachment=True, mimetype='application/pdf')



@app.route('/qr_reader')
def qr_reader():
    return render_template('qr_reader.html') 



if __name__ == "__main__":
    app.run(ssl_context=('cert.pem', 'key.pem'), host='0.0.0.0', port=8001)




