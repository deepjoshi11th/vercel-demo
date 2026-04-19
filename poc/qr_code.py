import qrcode

def convert_link_to_qr(text:str, size=5, back_color=(0,0,0), fill_color=(255,255,255)):
    if not text.startswith("https://") and not text.startswith("http://"):
        text = "https://" + text        
    qr = qrcode.QRCode(version=size, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=3)
    qr.add_data(text)
    img = qr.make_image(back_color=back_color, fill_color=fill_color)
    return img

def main():
     img = convert_link_to_qr("www.facebook.com")
     img.save('sample_img.png')

if __name__ == "__main__":
    main()
