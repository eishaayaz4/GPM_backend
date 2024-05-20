from flask import Flask, render_template,jsonify,request
from controllers import CelebrityMerge,ChangeBackground,GroupManager,ImageRepository,Template,UserManagment

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello world"

@app.route('/MergeWithCelebrity',methods=['POST'])
def merge_with_celebrity_route():
    return CelebrityMerge.MergeWithCelebrity()

@app.route('/GetAllCelebrities',methods=['GET'])
def get_all_celebrities_route():
    return CelebrityMerge.getAllCelebrities()

@app.route('/GetCelebritiesBySearch/<string:text>',methods=['POST'])
def get_celebrities_by_search_route(text):
    return CelebrityMerge.getCelebrityBySearch(text)

@app.route('/SignUp',methods=['POST'])
def sign_up_route():
    return UserManagment.signUp()


@app.route('/Login',methods=['POST'])
def login_route():
    return UserManagment.login()

@app.route('/UploadImage',methods=['POST'])
def upload_image_route():
    return UserManagment.upoadImage()

@app.route('/GetUserProcessedImages/<int:id>',methods=['GET'])
def get_use_processed_images_route(id):
    return UserManagment.getUserProcessedImages(id)

@app.route('/addProcessedImage',methods=['POST'])
def add_processed_image_route():
    return UserManagment.addProcessedImage()

@app.route('/GetAsset/<int:id>',methods=['GET'])
def get_assets_route(id):
    return UserManagment.getAsset(id)

@app.route( '/RemoveAsset/<int:id>',methods=['POST'])
def Remove_asset_route(id):
    return UserManagment.RemoveAsset(id)

@app.route( '/AddAsset',methods=['POST'])
def Add_asset_route():
    return UserManagment.addAsset()
@app.route('/SaveImage',methods=['POST'])
def save_image_route():
    return ImageRepository.saveImage(1,'123')

@app.route('/DownloadImage',methods=['POST'])
def download_image_route():
    return ImageRepository.downloadImage(1,2)

@app.route('/addToGroup',methods=['POST'])
def addToGroup_route():
    return GroupManager.addToGroup()

@app.route('/RemoveFromGroupPhoto',methods=['POST'])
def remove_from_group_photo_route():
    return GroupManager.removeFromGroupPhoto()

@app.route('/ChangeBackground',methods=['POST'])
def change_background_route():
    return ChangeBackground.ChangeBackground()

@app.route('/getAllBackgrounds',methods=['GET'])
def get_all_backgrounds_route():
    return ChangeBackground.getAllBackgrounds()

@app.route('/GetBackgroundBySearch/<string:text>',methods=['POST'])
def get_backgrounds_by_search_route(text):
    return ChangeBackground.getBackgroundBySearch(text)

@app.route('/DeleteTemplate/<int:id>',methods=['DELETE'])
def delete_template_route(id):
    return Template.deleteTemplate(id)

@app.route('/UpdateTemplate/<int:id>',methods=['PUT'])
def update_template_route(id):
    return Template.updateTemplate(id)

@app.route('/AddTemplate',methods=['POST'])
def add_template_route():
    return Template.addTemplate()

@app.route('/GetAllTemplates',methods=['GET'])
def get_all_templates_route():
    return Template.getAllTemplates()

@app.route('/GetTemplateBySearch/<string:txt>',methods=['POST'])
def get_template_by_search_route(txt):
    return Template.getTemplateBySearch(txt)

if __name__ == '__main__':
    app.run(debug=True,use_reloader=True,host='0.0.0.0')
