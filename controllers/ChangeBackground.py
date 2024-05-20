import base64
import os
import tempfile
from operator import or_
import dbHandler as db
from models import Template as t
from io import BytesIO
import cv2
import numpy as np
from PIL import Image
from flask import request, send_file, make_response
from rembg import remove

def image_to_base64(image):
    image_np = np.array(image)
    print(type(image_np))
    _, buffer = cv2.imencode('.jpg', image_np)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    return image_base64
def getBackgroundById(id):
    try:
        session = db.return_session()
        result = session.query(t.Template).filter(
            t.Template.type == 'background',
            t.Template.id == id
        ).all()

        temp_list = []
        for temp in result:
            temp_info = {
                "id": temp.id,
                "name": temp.name,
                "type": temp.type,
                "category": temp.category,
                "image": temp.image,
            }
            temp_list.append(temp_info)

        if temp_list:
            for temp_info in temp_list:
                image_filename = temp_info['image']
                image_path = os.path.join("templates", image_filename)

                if os.path.exists(image_path):
                    with open(image_path, "rb") as image_file:
                        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                        temp_info['image'] = encoded_image
                else:
                    temp_info['image'] = None

            return temp_list, 200
        else:
            return {"Message": "No template found "}, 404
    except Exception as e:
        return {'error': str(e)}, 500

def merge_images(foreground, background,y=0):
    foreground_img = np.array(foreground)
    bg_img = np.array(background)
    foreground_ratio = foreground_img.shape[1] / foreground_img.shape[0]
    background_ratio = bg_img.shape[1] / bg_img.shape[0]

    if foreground_ratio > background_ratio:
        new_width = bg_img.shape[1]
        new_height = int(new_width / foreground_ratio)
    else:
        new_height = bg_img.shape[0]
        new_width = int(new_height * foreground_ratio)

    foreground_resized = cv2.resize(foreground_img, (new_width, new_height), interpolation=cv2.INTER_AREA)


    x_offset = (bg_img.shape[1] - new_width) // 2
    y_offset = (bg_img.shape[0] - new_height) // 2+y

    result = Image.new("RGBA", (bg_img.shape[1], bg_img.shape[0]))
    result.paste(Image.fromarray(bg_img), (0, 0))
    result.paste(Image.fromarray(foreground_resized), (x_offset, y_offset), Image.fromarray(foreground_resized))

    return result

def ChangeBackground():
    try:
        user_id = int(request.form['user_id'])
        background_id = int(request.form['background_id'])
        image_data = request.files['image'].read()
        img = remove(image_data)
        if img is None:
            print("Background Not Removed")
        foreground_img= Image.open(BytesIO(img)).convert('RGBA')
        background_info, status_code = getBackgroundById(background_id)
        if background_info and status_code == 200 and background_info[0]['image'] is not None:
            decoded_image = base64.b64decode(background_info[0]['image'])
            bg_img = Image.open(BytesIO(decoded_image)).convert('RGBA')
        else:
            print("Background Template Not Found")
        result_image = merge_images(foreground_img, bg_img)
        result_image.save(os.path.join("results", f"1_{user_id}.png"))
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        result_image.save(temp_file, format="PNG")
        temp_file_path = temp_file.name
        temp_file.close()
        response = make_response(send_file(temp_file_path, mimetype='image/png'))
        response.headers['Content-Disposition'] = f'attachment; filename="result_{user_id}.png"'

        return response

        return {'result_image_base64': result_image}



    except Exception as e:
        return str(e), 500

def getAllBackgrounds():
    try:
        session = db.return_session()
        result = session.query(t.Template).filter_by(type='background').all()
        temp_list = []

        for temp in result:
            temp_info = {
                "id": temp.id,
                "name": temp.name,
                "type": temp.type,
                "category": temp.category,
                "image": temp.image,  # assuming this is the image filename
            }

            temp_list.append(temp_info)

        if temp_list:
            for temp_info in temp_list:
                image_filename = temp_info['image']
                image_path = os.path.join("templates", image_filename)

                if os.path.exists(image_path):
                    with open(image_path, "rb") as image_file:
                        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                        temp_info['image'] = encoded_image
                else:
                    temp_info['image'] = None  # or handle missing image appropriately

            return temp_list, 200
        else:
            return {"Message": "No template found"}, 404
    except Exception as e:
        return {'error': str(e)}, 500


def getBackgroundBySearch(text):
    try:
        print(text)
        session = db.return_session()
        result = session.query(t.Template).filter(
            t.Template.type == 'background',
            or_(t.Template.category.like(f'%{text}%'), t.Template.name.like(f'%{text}%'))
        ).all()

        temp_list = []
        for temp in result:
            temp_info = {
                "id": temp.id,
                "name": temp.name,
                "type": temp.type,
                "category": temp.category,
                "image": temp.image,
                # Add other attributes as needed
            }
            temp_list.append(temp_info)

        if temp_list:
            for temp_info in temp_list:
                image_filename = temp_info['image']
                image_path = os.path.join("templates", image_filename)

                if os.path.exists(image_path):
                    with open(image_path, "rb") as image_file:
                        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                        temp_info['image'] = encoded_image
                else:
                    temp_info['image'] = None  # or handle missing image appropriately

            return temp_list, 200
        else:
            return {"Message": "No template found "}, 404
    except Exception as e:
        return {'error': str(e)}, 500


