import os
from datetime import datetime
import dbHandler
from flask import Flask, render_template,jsonify,request
import requests
import dbHandler as db
from models import User as u,Asset as a
def signUp():
    try:
        data = request.get_json()

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')

        session = db.return_session()
        user= u.User(name=name, password=password, email=email, role="user")
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
        role=data.get('role')
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
        isAsset= request.form.get('isAsset')


        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # Save the image with the timestamp in the "assets" folder
        image.save(os.path.join('assets', f'{timestamp}_image.jpg'))
        session = db.return_session()
        asset = a.Asset(user_id=user_id,image=f'{timestamp}_image.jpg', isAsset=isAsset )

        session.add(asset)
        session.commit()
        return {"Message": "image added successfully"}, 200
    except Exception as e:
        return {'error': str(e)}, 500


def getUserProcessedImages(userId):
    return 'processed Images'

def getAsset(id):
        try:
            print(id)
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
                return asset_list, 200
            else:
                return {"Message": "No assets found for this user"}, 404
        except Exception as e:
            return {'error': str(e)}, 500


def RemoveAsset(asset_id):
    try:

        session = db.return_session()
        asset_to_delete = session.query(a.Asset).filter_by(id=asset_id).first()

        if asset_to_delete:
            image_name = asset_to_delete.image
            session.delete(asset_to_delete)
            os.remove(f'assets/{image_name}')
            session.commit()
            session.close()
            return {"Message": "asset deleted successfully"}, 200
        else:
            session.close()
            return {"Message": "asset not found"}, 404

    except Exception as e:
        return {'error': str(e)}, 500


