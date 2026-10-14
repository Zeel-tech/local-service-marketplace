"""Profile-photo upload helpers."""
import os
import uuid
from flask import current_app

# extension -> accepted file signatures (checked on the real bytes, not just the filename)
_SIGNATURES = {
    'jpg': (b'\xff\xd8\xff',),
    'jpeg': (b'\xff\xd8\xff',),
    'png': (b'\x89PNG\r\n\x1a\n',),
    'webp': (b'RIFF',),
}


def save_profile_photo(file_storage):
    """Validate and save an uploaded image. Returns the stored filename, or None if invalid."""
    if not file_storage or not file_storage.filename:
        return None
    ext = file_storage.filename.rsplit('.', 1)[-1].lower() if '.' in file_storage.filename else ''
    if ext not in _SIGNATURES:
        return None
    head = file_storage.stream.read(12)
    file_storage.stream.seek(0)
    if not any(head.startswith(sig) for sig in _SIGNATURES[ext]):
        return None
    if ext == 'webp' and head[8:12] != b'WEBP':
        return None
    filename = f'{uuid.uuid4().hex}.{ext}'
    file_storage.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    return filename


def delete_profile_photo(filename):
    if not filename:
        return
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.basename(filename))
    try:
        os.remove(path)
    except OSError:
        pass
