import base64
import os
from datetime import datetime

import cv2

import dbHandler
from flask import Flask, render_template, jsonify, request
import requests
import dbHandler as db
from models import User as u, Asset as a, History as h,Draft as d


def signUp():
    try:
        data = request.get_json()

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')

        session = db.return_session()
        user = u.User(name=name, password=password, email=email, role="user")
        session.add(user)
        session.commit()
        return {"Message": "user added successfully"}, 200
    except Exception as e:
        return {'error': str(e)}, 500


def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        session = db.return_session()

        user = session.query(u.User).filter_by(email=email, password=password).first()

        if user:
            return jsonify({"user_id": user.id, "email": user.email, "role": user.role}), 200
        else:
            return jsonify({"Message": "Invalid email or password"}), 401

    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500


def upoadImage():
    try:
        user_id = request.form.get('user_id')
        image = request.files['image']
        isAsset = request.form.get('isAsset')

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # Save the image with the timestamp in the "assets" folder
        image.save(os.path.join('assets', f'{timestamp}_image.jpg'))
        session = db.return_session()
        asset = a.Asset(user_id=user_id, image=f'{timestamp}_image.jpg', isAsset=isAsset)

        session.add(asset)
        session.commit()
        return {"Message": "image added successfully"}, 200
    except Exception as e:
        return {'error': str(e)}, 500


def getUserProcessedImages(id):
    try:
        session = db.return_session()
        histories = session.query(h.History).filter_by(user_id=id).all()

        history_list = []
        for history in histories:
            history_info = {
                "id": history.id,
                "image": history.image,
                "date": history.date,
                "user_id": history.user_id,
                "description": history.description
                }
            history_list.append(history_info)

        if history_list:
            for history_info in history_list:
                image_filename = history_info['image']
                image_path = os.path.join("History", image_filename)

                if os.path.exists(image_path):
                    with open(image_path, "rb") as image_file:
                        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

                        history_info['image'] = encoded_image
                else:
                    history_info['image'] = None

            return history_list, 200
        else:
            return {"Message": "No history found for this user"}, 404
    except Exception as e:
        return {'error': str(e)}, 500


def getAsset(id):
    try:

        session = db.return_session()
        assets = session.query(a.Asset).filter_by(user_id=id).all()

        asset_list = []
        for asset in assets:
            asset_info = {
                "id": asset.id,
                "user_id": asset.user_id,
                "image": asset.image,
                "isAsset": asset.isAsset
                # Add other attributes as needed
            }
            asset_list.append(asset_info)

        if asset_list:
            for temp_info in asset_list:
                image_filename = temp_info['image']
                image_path = os.path.join("user_assets", image_filename)

                if os.path.exists(image_path):
                    with open(image_path, "rb") as image_file:
                        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                        temp_info['image'] = encoded_image

                        # Calculate image height and width using OpenCV
                        img = cv2.imread(image_path)

                else:
                    temp_info['image'] = None


            return asset_list, 200
        else:
            return {"Message": "No asset found"}, 404
    except Exception as e:
        return {'error': str(e)}, 500




def addProcessedImage():
    try:
        image_base64 = request.form.get('image')  # Assuming image is sent as base64 string
        if not image_base64:
            raise ValueError("Image data is missing")

        image = base64.b64decode(image_base64)
        user_id = request.form.get('user_id')
        description = request.form.get('description')
        date = datetime.now().date()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        print(image, date, user_id, description)

        # Saving the image
        with open(os.path.join('History', f'{user_id}_{timestamp}_image.jpg'), 'wb') as f:
            f.write(image)

        session = db.return_session()
        history = h.History(image=f'{user_id}_{timestamp}_image.jpg', date=date, user_id=user_id, description=description)
        session.add(history)
        session.commit()

        return jsonify({'success': 'History added'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def RemoveAsset():
    try:
        asset_id = int(request.form.get('asset_id'))
        user_id = int(request.form.get('user_id'))
        print(user_id,asset_id)
        session = db.return_session()
        asset_to_delete = session.query(a.Asset).filter_by(id=asset_id,user_id=user_id).first()
        print("----",asset_to_delete)
        if asset_to_delete:
            image_name = asset_to_delete.image
            session.delete(asset_to_delete)
            os.remove(f'user_assets/{image_name}')
            session.commit()
            session.close()
            return {"Message": "asset deleted successfully"}, 200
        else:
            session.close()
            return {"Message": "asset not found"}, 404

    except Exception as e:
        return {'error': str(e)}, 500



def addAsset():
    try:
        user_id = int(request.form['user_id'])
        image = request.files['image']
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        image.save(os.path.join('user_assets', f'{timestamp}_image.jpg'))
        session = db.return_session()
        temp = a.Asset(user_id=user_id, image=f'{timestamp}_image.jpg', isAsset=1)
        session.add(temp)
        session.commit()
        return {"Message": "asset added successfully"}, 200
    except Exception as e:
        return {'error': str(e)}, 500

