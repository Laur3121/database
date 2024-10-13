// フィルター機能の追加
function filterProducts() {
    const filterValue = document.getElementById('filter-input').value.toLowerCase();
    const products = document.querySelectorAll('.product-row');

    products.forEach(product => {
        const productName = product.querySelector('.product-name').textContent.toLowerCase();
        if (productName.includes(filterValue)) {
            product.style.display = '';
        } else {
            product.style.display = 'none';
        }
    });
}

// 入力フィールドのイベントリスナーを設定
document.getElementById('filter-input').addEventListener('input', filterProducts);
