import base64
import os
from operator import or_
import dbHandler as db
from models import Template as t

def changeBackground(userId,image,backgroundId):
    return 'change background'

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


