import io
from typing_extensions import Protocol
import segno
import qrcode


class QrCodeServiceProtocol(Protocol):

    async def create_qr_code(self, payload: str) -> bytes:
        ...


class QrCodeService_(QrCodeServiceProtocol):
    async def create_qr_code(self, payload: str) -> bytes:
        qr = segno.make_qr(content=payload)
        f = io.BytesIO()
        qr.save(out=f)
        f.seek(0)


        return f.read()


class QrCodeService(QrCodeServiceProtocol):
    async def create_qr_code(self, payload: str) -> bytes:
        qr = qrcode.QRCode()
        qr.add_data(payload)
        img = qr.make_image()
        image = img.get_image()
        b = io.BytesIO()
        image.save(b, format="png")
        b.seek(0)
        return b.read()