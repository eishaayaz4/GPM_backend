import base64
import os
from datetime import datetime
import dbHandler
from flask import Flask, render_template,jsonify,request
import requests
import dbHandler as db
from models import Template as t,User as u
def deleteTemplate(Id):
    try:
        session = db.return_session()
        template_to_delete = session.query(t.Template).filter_by(id=Id).first()

        if template_to_delete:
            image_name = template_to_delete.image
            print(image_name)
            session.delete(template_to_delete)
            os.remove(f'templates/{image_name}')
            session.commit()
            session.close()
            return {"Message": "Template deleted successfully"}, 200
        else:
            session.close()
            return {"Message": "Template not found"}, 404
    except Exception as e:
        return {'error': str(e)}, 500

def addTemplate():
    try:
        name = request.form.get('name')
        type = request.form.get('type')
        category = request.form.get('category')
        image = request.files['image']
        print(name,type,category,image)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # Save the image with the timestamp in the "templates" folder
        image.save(os.path.join('templates', f'{timestamp}_image.jpg'))
        session = db.return_session()
        temp = t.Template(name=name, type=type, category=category, image=f'{timestamp}_image.jpg')

        session.add(temp)
        session.commit()
        return {"Message": "template added successfully"}, 200
    except Exception as e:
        return {'error': str(e)}, 500


def getAllTemplates():
    try:
        session = db.return_session()
        template = session.query(t.Template).all()
        temp_list = []

        for temp in template:
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


def getTemplateBySearch(text):
    try:

        session = db.return_session()
        template = session.query(t.Template).filter(t.Template.category.like(f'%{text}%')|
                                                       t.Template.type.like(f'%{text}%')|
                                                       t.Template.name.like(f'%{text}%')).all()
        temp_list = []
        for temp in template:
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




def updateTemplate(id):
    try:
        session = db.return_session()

        name = request.form.get('name')
        type = request.form.get('type')
        category = request.form.get('category')
        image = request.files['image']

        row_to_update = session.query(t.Template).filter_by(id=id).first()
        if row_to_update:
            previousFileName=row_to_update.image
            print(previousFileName)
            os.remove(f'templates/{previousFileName}')

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

            row_to_update.name =name
            row_to_update.type =type
            row_to_update.image = f'{timestamp}_image.jpg'
            row_to_update.category =category

            # Save the image with the timestamp in the "templates" folder
            image.save(os.path.join('templates', f'{timestamp}_image.jpg'))
            session.commit()
            return {"Message": "template updated successfully"}, 200
        else:
            return {"Message": "No template found"}, 400

    except Exception as e:
        return {'error': str(e)}, 500
