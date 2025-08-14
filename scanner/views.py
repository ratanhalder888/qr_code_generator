from django.shortcuts import render
from scanner.models import QRCode
import qrcode
from django.core.files.storage import FileSystemStorage
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from pathlib import Path

# Create your views here.
def generate_qr(request):
    qr_image_url = None
    if request.method == 'POST':
        mobile_number = request.POST.get('mobile_number')
        data = request.POST.get('qr_data')

        if not mobile_number or len(mobile_number) != 11 or not mobile_number.isdigit():
            return render(request, 'scanner/generate.html',
                          {'error':'Invalid Mobile Number'})
        
        # Generate the QR code image with data and mobile number
        qr_content = f"{data}|{mobile_number}"
        qr = qrcode.make(qr_content)
        qr_image_io = BytesIO() # Create a BytesIO stream
        # Save the QR code image to qr_image_io
        qr.save(qr_image_io, format='PNG') # type: ignore
        qr_image_io.seek(0) # Reset the position of the stream
        # Define the storage location for the QR code images
        qr_storage_path = settings.MEDIA_ROOT / 'qr_codes'
        fs = FileSystemStorage(location=qr_storage_path, base_url='/media/qr_codes/')
        filename = f"{data}_{mobile_number}.png"
        qr_image_content = ContentFile(qr_image_io.read(), name=filename)
        filepath = fs.save(filename, qr_image_content)
        qr_image_url = fs.url(filename)
        
        # Save the QR code data and mobile number in the database
        QRCode.objects.create(data=data, mobile_number=mobile_number)
        

    return render(request, 'scanner/generate.html', {'qr_image_url': qr_image_url}) # type: ignore

def scan_qr(request):
    return render(request, 'scanner/scan.html')