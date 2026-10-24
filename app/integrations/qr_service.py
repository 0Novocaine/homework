import base64
from io import BytesIO

import qrcode


class QRCodeService:
    def create_data_url(self, url: str) -> str:
        image = qrcode.make(url)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
