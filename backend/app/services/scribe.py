from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

def overlay_message(image_path: str, message_text: str) -> str:
    try:
        # 1. Resolve and Load the Bouquet Image
        if image_path.startswith("/"):
            clean_path = image_path.replace("/assets/bouquets/", "").replace("/generated/", "")
            possible_path_1 = os.path.join("assets", "bouquets", clean_path)
            possible_path_2 = os.path.join("static", "generated", clean_path)
            
            if os.path.exists(possible_path_1):
                real_path = possible_path_1
            elif os.path.exists(possible_path_2):
                real_path = possible_path_2
            else:
                raise FileNotFoundError(f"Could not find bouquet image: {image_path}")
        else:
            real_path = image_path

        bouquet_img = Image.open(real_path).convert("RGBA")
        b_width, b_height = bouquet_img.size

        # 2. Load the Card Template
        template_path = os.path.join("assets", "templates", "card_template.png")
        if not os.path.exists(template_path):
            # Fallback for .jpg
            template_path = os.path.join("assets", "templates", "card_template.jpg")
            
        card_img = Image.open(template_path).convert("RGBA")
        
        # 3. Apply Pixellab Scaling (42% of bouquet width)
        target_card_width = int(b_width * 0.42)
        scale_ratio = target_card_width / card_img.width
        target_card_height = int(card_img.height * scale_ratio)
        
        card_img = card_img.resize((target_card_width, target_card_height), Image.Resampling.LANCZOS)
        c_width, c_height = card_img.size

        # 4. Setup Text Drawing (Done BEFORE rotation to keep it clean)
        draw = ImageDraw.Draw(card_img)
        font_path = os.path.join("assets", "fonts", "GreatVibes-Regular.ttf")
        
        try:
            # Scale font proportionally to the new card width
            font_size = max(40, int(c_width * 0.065))
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()
            font_size = 30

        # Format and Center the Text
        lines = textwrap.wrap(message_text, width=32)
        line_height = int(font_size * 1.4)
        total_text_height = len(lines) * line_height
        
        text_y = ((c_height - total_text_height) // 2) + int(c_height * 0.02)

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_w = bbox[2] - bbox[0]
            text_x = (c_width - text_w) // 2
            draw.text((text_x, text_y), line, font=font, fill=(50, 45, 45, 255))
            text_y += line_height

        # 5. Apply Pixellab Rotation (-7 degrees)
        # expand=True prevents the corners of the card from being cut off during rotation
        rotated_card = card_img.rotate(7, expand=True, resample=Image.Resampling.BICUBIC)
        rot_c_width, rot_c_height = rotated_card.size

        # 6. Apply Pixellab Coordinate Placement
        # Find the center of the base image
        center_x = b_width // 2
        center_y = b_height // 2
        
        # Pixellab center offsets
        offset_x = 200
        offset_y = 910
        
        # Find the target pixel for the center of the card
        target_cx = center_x + offset_x
        target_cy = center_y + offset_y
        
        # PIL paste() requires the TOP-LEFT coordinate, so we subtract half the card's width/height
        paste_x = target_cx - (rot_c_width // 2)
        paste_y = target_cy - (rot_c_height // 2)

        # 7. Combine the Images
        final_img = bouquet_img.copy() 
        # The third argument acts as an alpha mask so the transparent background doesn't overwrite the flowers
        final_img.paste(rotated_card, (paste_x, paste_y), rotated_card)

        # 8. Save the Result
        output_dir = os.path.join("static", "generated")
        os.makedirs(output_dir, exist_ok=True)
        
        filename = "generated-bouquet.png"
        save_path = os.path.join(output_dir, filename)
        final_img.save(save_path, format="PNG")

        return f"/generated/{filename}"

    except Exception as e:
        print(f"Scribe Error: {e}")
        return None