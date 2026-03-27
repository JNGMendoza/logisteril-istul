import qrcode
import qrcode.image.svg
import io
import base64

def generar_qr_base64(url: str, size: int = 10) -> str:
    """
    Genera un QR code y lo devuelve como string base64 PNG.
    Listo para usar en <img src="data:image/png;base64,...">
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=size,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1a2035", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def generar_qr_svg(url: str) -> str:
    """
    Genera un QR code como SVG embebible directamente en HTML.
    """
    factory = qrcode.image.svg.SvgPathImage
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
        image_factory=factory,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()
    buffer = io.BytesIO()
    img.save(buffer)
    return buffer.getvalue().decode('utf-8')
