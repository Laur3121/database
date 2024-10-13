import qrcode

img = qrcode.make('https://example.com')
img.save('example_qr.png')