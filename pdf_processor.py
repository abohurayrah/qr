import cv2
import fitz
import os
import logging

def scan_pdf_qr(pdf_path):
    """
    Process a PDF file and extract QR code from the first page
    """
    try:
        # Open PDF and render the first page to an image
        doc = fitz.open(pdf_path)
        temp = os.path.join(os.path.dirname(pdf_path), "temp_page.png")
        doc[0].get_pixmap().save(temp)
        doc.close()

        # Read the rendered image with OpenCV
        img = cv2.imread(temp)
        if img is None:
            raise Exception("Could not read the rendered image")

        # Use OpenCV's built-in QRCodeDetector
        qr_detector = cv2.QRCodeDetector()
        data, bbox, _ = qr_detector.detectAndDecode(img)

        # Clean up temporary file
        if os.path.exists(temp):
            os.remove(temp)

        # Return the QR code data if found
        if data:
            return data
        else:
            return "No QR code found"

    except Exception as e:
        logging.error(f"Error in scan_pdf_qr: {str(e)}")
        raise Exception(f"Failed to process PDF: {str(e)}")
