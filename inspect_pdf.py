import pdfplumber

with pdfplumber.open("dictionary.pdf") as pdf:
    page = pdf.pages[35]

    # Extract exact page bounding box coordinates (handles offset origin)
    x0, top, x1, bottom = page.bbox
    mid_x = (x0 + x1) / 2

    # Crop left and right columns using real boundaries
    left_crop = page.crop((x0, top, mid_x, bottom))
    right_crop = page.crop((mid_x, top, x1, bottom))

    left_text = left_crop.extract_text()
    right_text = right_crop.extract_text()

    print("=== LEFT COLUMN (Top to Bottom) ===")
    print(left_text[:600] if left_text else "Empty")
    
    print("\n=== RIGHT COLUMN (Top to Bottom) ===")
    print(right_text[:600] if right_text else "Empty")