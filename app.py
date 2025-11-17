import os
import json
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import piexif
from PIL import Image

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key')

UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def safe_extract_zip(zip_file, extract_path):
    abs_extract_path = os.path.abspath(extract_path)
    
    for member in zip_file.namelist():
        if os.path.isabs(member):
            raise ValueError(f"ZIP contains absolute path: {member}")
        
        member_path = os.path.abspath(os.path.join(extract_path, member))
        
        try:
            common = os.path.commonpath([abs_extract_path, member_path])
            if common != abs_extract_path:
                raise ValueError(f"ZIP contains path traversal: {member}")
        except ValueError:
            raise ValueError(f"ZIP contains unsafe path: {member}")
    
    zip_file.extractall(extract_path)

def cleanup_temp_dirs(temp_dirs):
    for temp_dir in temp_dirs:
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Error cleaning up {temp_dir}: {e}")

def parse_google_takeout_json(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        timestamp = None
        if 'photoTakenTime' in data:
            timestamp_data = data['photoTakenTime']
            if 'timestamp' in timestamp_data:
                timestamp = int(timestamp_data['timestamp'])
        elif 'creationTime' in data:
            timestamp_data = data['creationTime']
            if 'timestamp' in timestamp_data:
                timestamp = int(timestamp_data['timestamp'])
        
        return timestamp
    except Exception as e:
        print(f"Error parsing JSON {json_path}: {e}")
        return None

def get_apple_photos_metadata(image_path):
    try:
        img = Image.open(image_path)
        try:
            exif_dict = piexif.load(img.info.get('exif', b''))
            if piexif.ExifIFD.DateTimeOriginal in exif_dict.get('Exif', {}):
                date_str = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
                dt = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                return int(dt.timestamp())
        except:
            pass
        
        file_mtime = os.path.getmtime(image_path)
        return int(file_mtime)
    except Exception as e:
        print(f"Error getting Apple metadata for {image_path}: {e}")
        return None

def set_exif_datetime(image_path, timestamp):
    try:
        dt = datetime.fromtimestamp(timestamp)
        dt_str = dt.strftime('%Y:%m:%d %H:%M:%S')
        
        img = Image.open(image_path)
        
        try:
            exif_dict = piexif.load(img.info.get('exif', b''))
        except:
            exif_dict = {'0th': {}, 'Exif': {}, 'GPS': {}, '1st': {}, 'thumbnail': None}
        
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = dt_str.encode('utf-8')
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = dt_str.encode('utf-8')
        exif_dict['0th'][piexif.ImageIFD.DateTime] = dt_str.encode('utf-8')
        
        exif_bytes = piexif.dump(exif_dict)
        
        img.save(image_path, exif=exif_bytes, quality=95)
        
        os.utime(image_path, (timestamp, timestamp))
        
        return True
    except Exception as e:
        print(f"Error setting EXIF for {image_path}: {e}")
        return False

def detect_export_type(extract_path):
    has_json_files = False
    has_photos = False
    
    for root, dirs, files in os.walk(extract_path):
        for file in files:
            if file.lower().endswith('.json'):
                has_json_files = True
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.heic', '.heif')):
                has_photos = True
        
        if has_json_files and has_photos:
            return 'google_takeout'
    
    if has_photos:
        return 'apple_photos'
    
    return 'unknown'

def process_google_takeout(extract_path, output_path):
    stats = {
        'total_files': 0,
        'fixed_files': 0,
        'errors': 0
    }
    
    photo_extensions = {'.jpg', '.jpeg', '.png', '.heic', '.heif', '.gif', '.bmp', '.webp'}
    
    for root, dirs, files in os.walk(extract_path):
        for file in files:
            file_lower = file.lower()
            file_ext = Path(file_lower).suffix
            
            if file_ext in photo_extensions:
                stats['total_files'] += 1
                image_path = os.path.join(root, file)
                
                json_path = image_path + '.json'
                if not os.path.exists(json_path):
                    json_path = os.path.join(root, Path(file).stem + '.json')
                
                timestamp = None
                if os.path.exists(json_path):
                    timestamp = parse_google_takeout_json(json_path)
                
                if timestamp is None:
                    timestamp = int(os.path.getmtime(image_path))
                
                dt = datetime.fromtimestamp(timestamp)
                year_folder = os.path.join(output_path, str(dt.year))
                os.makedirs(year_folder, exist_ok=True)
                
                new_filename = f"{dt.strftime('%Y%m%d_%H%M%S')}_{stats['total_files']}{file_ext}"
                new_path = os.path.join(year_folder, new_filename)
                
                shutil.copy2(image_path, new_path)
                
                if file_ext in {'.jpg', '.jpeg'}:
                    if set_exif_datetime(new_path, timestamp):
                        stats['fixed_files'] += 1
                    else:
                        stats['errors'] += 1
                else:
                    os.utime(new_path, (timestamp, timestamp))
                    stats['fixed_files'] += 1
    
    return stats

def process_apple_photos(extract_path, output_path):
    stats = {
        'total_files': 0,
        'fixed_files': 0,
        'errors': 0
    }
    
    photo_extensions = {'.jpg', '.jpeg', '.png', '.heic', '.heif', '.gif', '.bmp', '.webp'}
    
    for root, dirs, files in os.walk(extract_path):
        for file in files:
            file_lower = file.lower()
            file_ext = Path(file_lower).suffix
            
            if file_ext in photo_extensions:
                stats['total_files'] += 1
                image_path = os.path.join(root, file)
                
                timestamp = get_apple_photos_metadata(image_path)
                if timestamp is None:
                    timestamp = int(os.path.getmtime(image_path))
                
                dt = datetime.fromtimestamp(timestamp)
                year_folder = os.path.join(output_path, str(dt.year))
                os.makedirs(year_folder, exist_ok=True)
                
                new_filename = f"{dt.strftime('%Y%m%d_%H%M%S')}_{stats['total_files']}{file_ext}"
                new_path = os.path.join(year_folder, new_filename)
                
                shutil.copy2(image_path, new_path)
                
                if file_ext in {'.jpg', '.jpeg'}:
                    if set_exif_datetime(new_path, timestamp):
                        stats['fixed_files'] += 1
                    else:
                        stats['errors'] += 1
                else:
                    os.utime(new_path, (timestamp, timestamp))
                    stats['fixed_files'] += 1
    
    return stats

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    temp_dirs = []
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only ZIP files are allowed'}), 400
        
        upload_dir = tempfile.mkdtemp(prefix='upload_')
        temp_dirs.append(upload_dir)
        extract_dir = tempfile.mkdtemp(prefix='extract_')
        temp_dirs.append(extract_dir)
        output_dir = tempfile.mkdtemp(prefix='output_')
        temp_dirs.append(output_dir)
        
        filename = secure_filename(file.filename or 'upload.zip')
        zip_path = os.path.join(upload_dir, filename)
        file.save(zip_path)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            safe_extract_zip(zip_ref, extract_dir)
        
        export_type = detect_export_type(extract_dir)
        
        if export_type == 'unknown':
            cleanup_temp_dirs(temp_dirs)
            return jsonify({'error': 'Could not detect export type. Please upload a valid Google Takeout or Apple Photos export.'}), 400
        
        if export_type == 'google_takeout':
            stats = process_google_takeout(extract_dir, output_dir)
        else:
            stats = process_apple_photos(extract_dir, output_dir)
        
        output_zip_path = os.path.join(upload_dir, 'fixed_photos.zip')
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, output_dir)
                    zipf.write(file_path, arcname)
        
        response = send_file(
            output_zip_path,
            as_attachment=True,
            download_name='fixed_photos.zip',
            mimetype='application/zip'
        )
        
        @response.call_on_close
        def cleanup():
            cleanup_temp_dirs(temp_dirs)
        
        response.headers['X-Export-Type'] = export_type
        response.headers['X-Total-Files'] = str(stats['total_files'])
        response.headers['X-Fixed-Files'] = str(stats['fixed_files'])
        response.headers['X-Errors'] = str(stats['errors'])
        
        return response
        
    except zipfile.BadZipFile:
        cleanup_temp_dirs(temp_dirs)
        return jsonify({'error': 'Invalid ZIP file'}), 400
    except ValueError as e:
        cleanup_temp_dirs(temp_dirs)
        return jsonify({'error': f'Security error: {str(e)}'}), 400
    except Exception as e:
        cleanup_temp_dirs(temp_dirs)
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
